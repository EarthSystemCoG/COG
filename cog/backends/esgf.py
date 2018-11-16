from social_core.backends.oauth import BaseOAuth2
from social_core.backends.open_id import OpenIdAuth, OPENID_ID_FIELD
from social_core.exceptions import AuthMissingParameter
from six.moves.urllib_parse import urlencode, unquote

import os
from base64 import b64encode
from OpenSSL import crypto
from urlparse import urlparse

from openid.yadis.services import getServiceEndpoints
from openid.yadis.discover import DiscoveryFailure

class ESGFOAuth2(BaseOAuth2):
    name = 'esgf'
    AUTHORIZATION_URL = 'https://slcs.ceda.ac.uk/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://slcs.ceda.ac.uk/oauth/access_token'
    CERTIFICATE_URL = 'https://slcs.ceda.ac.uk/oauth/certificate/'
    DEFAULT_SCOPE = ['https://slcs.ceda.ac.uk/oauth/certificate/']
    REDIRECT_STATE = True
    ACCESS_TOKEN_METHOD = 'POST'
    EXTRA_DATA = [
        ('access_token', 'access_token', True),
        ('expires_in', 'expires_in', True),
        ('refresh_token', 'refresh_token', True),
        ('openid', 'openid', True)
    ]


    def __init__(self, strategy=None, redirect_uri=None):
        super(ESGFOAuth2, self).__init__(strategy, redirect_uri)

        # Get openid_identifier added to the session by PSA. Requires
        # SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['openid_identifier',]
        # set in settings.py
        if strategy:
            openid = self.strategy.session_get(OPENID_ID_FIELD, None)
            self.set_urls(openid)


    # get XRDS and extract authorize, access token, and certificate service URLs
    def set_urls(self, openid):
        try:
            uri, endpoints = getServiceEndpoints(openid)
        except DiscoveryFailure:
            return
        for e in endpoints:
            if e.matchTypes(['urn:esg:security:oauth:endpoint:authorize']):
                self.AUTHORIZATION_URL = e.uri
            elif e.matchTypes(['urn:esg:security:oauth:endpoint:access']):
                self.ACCESS_TOKEN_URL = e.uri
            elif e.matchTypes(['urn:esg:security:oauth:endpoint:resource']):
                self.CERTIFICATE_URL = e.uri
                self.DEFAULT_SCOPE = [e.uri]



    def get_certificate(self, access_token):
        """ Generate a new key pair """
        key_pair = crypto.PKey()
        key_pair.generate_key(crypto.TYPE_RSA, 2048)
        self.private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key_pair).decode('utf-8')

        """ Generate a certificate request """
        cert_request = crypto.X509Req()
        cert_request.set_pubkey(key_pair)
        cert_request.sign(key_pair, 'md5')
        cert_request = crypto.dump_certificate_request(crypto.FILETYPE_ASN1, cert_request)

        headers = {'Authorization': 'Bearer {}'.format(access_token)}
        url = self.CERTIFICATE_URL

        request_args = {'headers': headers,
                        'data': {'certificate_request': b64encode(cert_request)}
        }
        try:
            response = self.request(url, method='POST', **request_args)
            response.raise_for_status()
        except Exception, err:
            print Exception, err
        self.cert = response.text
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, response.text)
        self.subject = cert.get_subject()
        return (self.private_key, self.cert, self.subject.commonName)


    # TO DO when OIDC is deployed on ESGF IdP nodes
    # extract user info from id_token (OpenID Connect)
#    def user_data(self, access_token, *args, **kwargs):
#        print 'user_data'
#        response = kwargs.get('response')
#        id_token = response.get('id_token')
#        try:
#            decoded_id_token = jwt_decode(id_token, verify=False)
#        except (DecodeError, ExpiredSignature) as de:
#            raise AuthTokenError(self, de)
#        for key in decoded_id_token:
#            print '%s:%s' % (key, decoded_id_token[key])
#
#        return {'uid': decoded_id_token.get('sub'),
#                'username': decoded_id_token.get('preferred_username'),
#                'name': decoded_id_token.get('name'),
#                'email': decoded_id_token.get('email')
#                }


    # return values that will be stored in the database as:
    # social_auth_usersocialauth.extra_data['openid'],
    # auth_user.username
    def get_user_details(self, response):
        access_token = response.get('access_token')
        pkey, cert, openid = self.get_certificate(access_token)
        username = os.path.basename(urlparse(openid).path)
        return {'openid': openid,
                'username': username,
                }


    # PSA compares returned value with social_auth_usersocialauth.uid (provider=='esgf')
    # if it's new, PSA creates a new user
    def get_user_id(self, details, response):
        return details['openid']


class ESGFOpenId(OpenIdAuth):
    name = 'esgf-openid'

    # Extend original openid.openid_url() to a case where openid_identifier is set in the session only
    def openid_url(self):
        """Return service provider URL.
        This base class is generic accepting a POST parameter that specifies
        provider URL."""
        if self.URL:
            return self.URL
        elif OPENID_ID_FIELD in self.data:
            return self.data[OPENID_ID_FIELD]
        elif self.strategy.session_get(OPENID_ID_FIELD, None):
            return self.strategy.session_get(OPENID_ID_FIELD, None)
        else:
            raise AuthMissingParameter(self, OPENID_ID_FIELD)


    def get_user_details(self, response):
        print response.identity_url
        username = os.path.basename(urlparse(response.identity_url).path)
        return {'openid': response.identity_url,
                'username': username,
                }


def associate_by_openid(backend, details, user=None, *args, **kwargs):
    """
    Associate current auth with a user with the same social.uid in the DB.
    """

    if user:
        return None

    openid = details.get('openid')
    if openid:
        # Try to associate accounts registered with the same OpenId.
        # Probably it is possible to get backend.strategy.storage from kwargs['storage'].
        if backend.name == 'esgf':
            social = backend.strategy.storage.user.get_social_auth(provider='esgf-openid', uid=kwargs['uid'])
        elif backend.name == 'esgf-openid':
            social = backend.strategy.storage.user.get_social_auth(provider='esgf', uid=kwargs['uid'])
        if social:
            return {'user': social.user, 'is_new': False}
    return None


def discover(openid):
    try:
        uri, endpoints = getServiceEndpoints(openid)
    except DiscoveryFailure:
        return None
    authorize = None
    access = None
    for e in endpoints:
        if e.matchTypes(['urn:esg:security:oauth:endpoint:authorize']):
            authorize = True
        elif e.matchTypes(['urn:esg:security:oauth:endpoint:access']):
            access = True
    if authorize and access:
        return 'OAuth2'
    return 'OpenID'
