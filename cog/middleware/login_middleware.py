'''
Middleware that intercepts the request/response during user authentication in order to:
a) enforce an IdP whitelist
b) detects the possible authentication errors,
and redirect to the authentication page with informative error messages.
'''

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from cog.plugins.esgf.registry import LocalWhiteList

import logging

log = logging.getLogger(__name__)

class LoginMiddleware(object):

    def __init__(self):

        
        try:
            # initialize the white list service
            self.whitelist = LocalWhiteList(settings.IDP_WHITELIST)
                
            # login URLs
            self.url1 = "/login/"
            self.url2 = "/openid/login/"
            
            self.init= True
            
        except AttributeError:
            # no entry in $COG_CONFIG_DIR/cog_settings.cfg
            self.init = False
        except OSError:
            # OSError: [Errno 2] No such file or directory: '/esg/config/esgf_idp_static.xml'
            self.init = False

    def process_request(self, request):
        '''
        Method called before processing of the view.
        Used to intercept the openid login request before it is sent to the remote IdP.
        '''

        if self.init:
            
            # intercept only these requests
            if request.path == self.url2:
    
                # DEBUG
                log.debug('OpenID login request: %s' % request)
    
                openid_identifier = request.GET.get('openid_identifier', None)
                next = request.GET.get('next', "/") # preserve 'next' redirection after successful login
                if openid_identifier is not None:
    
                    # invalid OpenID
                    if not openid_identifier.lower().startswith('https'):
                        return HttpResponseRedirect(reverse('openid-login')+"?message=invalid_openid&next=%s&openid=%s" % (next, openid_identifier))
    
                    # invalid IdP
                    if not self.whitelist.trust(openid_identifier):
                        return HttpResponseRedirect(reverse('openid-login')+"?message=invalid_idp&next=%s&openid=%s" % (next, openid_identifier) )

        # keep on processing this request
        return None


    def process_response(self, request, response):
        '''
        Method called after processing of the view.
        Used to intercept the login response in case of errors.
        '''
        
        if self.init:

            # request parameters to include when redirecting
            next = request.GET.get('next', "/") # preserve 'next' redirection after successful login
            openid_identifier = request.GET.get('openid_identifier', None)
            username = request.GET.get('username', None)
    
            # process errors from openid authentication
            if request.path == self.url2:
    
                if request.method=='POST' and not request.user.is_authenticated():
                    if response.status_code == 500:
                        log.error('Authentication Error: %s' % response)
                        if 'OpenID discovery error' in response.content:
                            return HttpResponseRedirect(reverse('openid-login')+"?message=openid_discovery_error&next=%s&openid=%s" % (next, openid_identifier) )
    
            # process errors from standard authentication
            elif request.path == self.url1:
    
                if request.method=='POST' and not request.user.is_authenticated():
                    return HttpResponseRedirect(reverse('login')+"?message=login_failed&next=%s&username=%s" % (next, username) )

        return response
