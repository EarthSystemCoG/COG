from django.db import models
from django.contrib.auth.models import User
from constants import APPLICATION_LABEL, RESEARCH_KEYWORDS_MAX_CHARS, RESEARCH_INTERESTS_MAX_CHARS
from django.conf import settings

from cog.utils import hasText
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from cog.utils import getJson
from cog.models.peer_site import getPeerSites
from cog.models.project_tag import ProjectTag
import datetime
import logging

log = logging.getLogger(__name__)

class UserProfile(models.Model):

    # user
    user = models.OneToOneField(User, related_name='profile')
    
    # node (using the django site object)
    site = models.ForeignKey(Site, default=1)

    # additional mandatory fields
    institution = models.CharField(max_length=100, blank=False, default='')
    city = models.CharField(max_length=100, blank=False, null=False, default='')
    country = models.CharField(max_length=100, blank=False, null=False, default='')

    # additional optional fields
    state = models.CharField(max_length=100, blank=True, null=True, default='')
    department = models.CharField(max_length=100, blank=True, null=True, default='')

    # opt-in mailing list (but defaults to true to migrate existing users)
    subscribed = models.BooleanField(verbose_name='Subscribe to COG mailing list?', default=True, null=False)

    # opt-out privacy option
    private = models.BooleanField(verbose_name='Do NOT list me among project members', default=False, null=False)

    # optional picture
    image = models.ImageField(upload_to='photos/', blank=True, null=True)

    # optional research information
    researchInterests = models.CharField(max_length=RESEARCH_INTERESTS_MAX_CHARS, blank=True, null=True, default='')
    researchKeywords = models.CharField(max_length=RESEARCH_KEYWORDS_MAX_CHARS, blank=True, null=True, default='')

    # clear text password - this field is NOT persisted to the database, but it is needed to execute MD5 encoding on the user-supplied password
    clearTextPwd = None

    # user (login) type: 1=COG, 2=ESGF
    type = models.IntegerField(null=False, blank=False, default=1)
    
    # datetime when password was last updated, used to trigger mandatory resets
    last_password_update = models.DateTimeField('Date and Time when Password was Last Updated', blank=True, null=True)
    
    # list of user-selected project tags
    tags = models.ManyToManyField(ProjectTag, blank=True, related_name='users')


    def __unicode__(self):
        return "%s" % self.user.get_full_name()
    
    def getAbsoluteUrl(self):
        '''Returns the absolute URL for this user profile, keeping the home node into account.'''
        
        return "http://%s%s?openid=%s" % (self.site.domain, reverse('user_byopenid'), self.openid())
    
    def hasPasswordExpired(self):
        
        if self.last_password_update is None:
            return True
        
        if settings.PWD_EXPIRATION_DAYS > 0:
            today = datetime.date.today()
            if (today - self.last_password_update).days > settings.PWD_EXPIRATION_DAYS:
                return True
            
        # default
        return False

    class Meta:
        app_label= APPLICATION_LABEL

    # utility method to return the user openids
    def openids(self):
        return [x.claimed_id for x in self.user.useropenid_set.all()]
    
    # utility method to return openids that match the local node
    def localOpenids(self):
        try:
            return [x for x in self.openids() if settings.ESGF_HOSTNAME in x]
        except AttributeError: # no 'ESGF_HOSTNAME' in settings
            return []
        
    # utility method to return the user first openid
    def openid(self):
        if len(self.user.useropenid_set.all()) > 0:
            return self.user.useropenid_set.all()[0].claimed_id
        else:
            return None
        
    # returns the first local openid, if existing
    def localOpenid(self):
        if len(self.localOpenids()) > 0:
            return self.localOpenids()[0]
        else:
            return None 

# Method to check whether a user object is valid
# (i.d. it has an associated profile, and its the mandatory fields are populated)
def isUserValid(user):

    if not hasText(user.first_name) or not hasText(user.last_name) or not hasText(user.username) or not hasText(user.email):
        return False

    if not hasText(user.profile.institution) or not hasText(user.profile.city) or not hasText(user.profile.country):
        return False

    return True

def isUserLocal(user):
    '''Method to determine whether a user home node is the current node.'''
    
    (profile, _) = UserProfile.objects.get_or_create(user=user)
    return profile.site == Site.objects.get_current()

def isUserRemote(user):
    '''
    Method to identify remote users as users that:
    a) do NOT have their home node as their current node
    b) do have an OpenID
    '''
    
    (profile, _) = UserProfile.objects.get_or_create(user=user)
    if profile.site == Site.objects.get_current():
        return False
    
    elif profile.openid is None:
        return False

    else:
        return True
    
# loops over the peer nodes to identify the home node for a given user
def discoverSiteForUser(openid):
    '''IMPORTANT: call this function ONLY at account creation as it makes requests to all peer nodes.'''
        
    for site in getPeerSites():  # loop over enabled peer nodes
        url = "http://%s/share/user/?openid=%s" % (site.domain, openid)
        jobj = getJson(url)
        if jobj is not None:
            for key, value in jobj['users'].items():
                if str(value['home_site_domain']) == site.domain:
                    return site  # node found
            
    # node not found
    return None
        
def isOpenidLocal(openid):
    '''Utility method to determine whether the given openid is issued by this node.'''
    
    return settings.ESGF_HOSTNAME in openid

# loops over the peer nodes to retrieve the data cart size
def getDataCartsForUser(openid):
        
    dcs = {}  # dictionary of (site_name, datacart_size) items
    
    #for site in Site.objects.all():  # loop over all sites (e.g. nodes) in database. Note: includes current node
    for site in getPeerSites():  # loop over nodes that are federated
        url = "http://%s/share/user/?openid=%s" % (site.domain, openid)
        log.debug('Querying for datacart: url=%s' % url)
        jobj = getJson(url)
        if jobj is not None:
            for key, value in jobj['users'].items():
                dcs[ site ] = int( value['datacart']['size'] )
            
    return dcs
        
        
def createUsername(username):
    '''Selects the first available username in the CoG database starting with a given string.'''
    
    for ext in [""] + [str(i) for i in range(1,100)]:
        username = username + ext
        try:
            # load user by username
            user = User.objects.get(username=username)
        except:
            # this username is available
            return username 
        
    return None
    
# NOTE: monkey-patch User __unicode__() method to show full name
User.__unicode__ = User.get_full_name
