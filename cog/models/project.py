from django.db import models
from constants import APPLICATION_LABEL, TYPE_TRACKER, TYPE_CODE, TYPE_POLICY, TYPE_ROADMAP, PROJECT_PAGES
from django.contrib.auth.models import User, Permission, Group
from topic import Topic
from membership import MembershipRequest
from django.db.models import Q
from cog.utils import smart_truncate
from django.contrib.contenttypes.models import ContentType
from os.path import basename
from urllib import quote, unquote
import re
from django.conf import settings

# Project
class Project(models.Model):
    
    short_name = models.CharField(max_length=20, unique=True, help_text="Short project acronym, 20 characters maximum, use only letters, numbers and '_', '-', no spaces" )
    long_name = models.CharField(max_length=200, unique=True, help_text='Fully spelled project name')
    description = models.TextField(blank=False, null=False, help_text='A short paragraph that describes the project')
    
    mission = models.TextField(blank=True, help_text='Succinctly describes why the project exists and what it does')
    vision  = models.TextField(blank=True, help_text='Outlines what a project wants to be, or how it wants the world in which it operates to be. It is a long-term view')
    values  = models.TextField(blank=True, help_text='Beliefs that are shared among the members of a project. Values influence culture and priorities and provide a framework for informing decisions')
    history = models.TextField(blank=True, help_text='A narrative describing the origination and evolution of the project')
    external_homepage = models.URLField(max_length=200, blank=True, null=True, help_text='External Home Page')
    
    taskPrioritizationStrategy = models.TextField(blank=True, null=True, verbose_name='Task Prioritization Strategy', \
                                                  help_text='A paragraph describing how tasks are prioritized. This description may include who participates, how often they meet, how they meet, and whether the results are public.')
    requirementsIdentificationProcess = models.TextField(blank=True, null=True, verbose_name='Requirements Identification Process', \
                                                  help_text='A paragraph describing how requirements are identified. This description may include who participates, what system is used to track requirements, and whether the results are public.')

    
    parent = models.ForeignKey('self', blank=True, null=True, related_name='Parent Project')
    peers = models.ManyToManyField('self', blank=True, related_name='Peer Projects')
    
    # the initial requestor of the project, if any
    author = models.ForeignKey(User, blank=True, null=True, default=None)
    
    # the workspace of an inactive project is not accessible
    active = models.BooleanField(default=False, blank=False, null=False)
    
    # a private project is only visible to project members 
    # by default all projects are public, and must be explicitely made private
    private = models.BooleanField(default=False, blank=False, null=False)
    
    # optional custom logo
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    
    # optional hyperlink for custom logo
    logo_url = models.CharField(max_length=200, blank=True, null=True, help_text='Optionl logo hyperlink URL')
    
    # list of available topics for this project
    topics =  models.ManyToManyField(Topic, blank=True, null=True, through='ProjectTopic')
        
    class Meta:
        app_label= APPLICATION_LABEL
    
    # group of standard users associated with this project
    def getUserGroup(self):
        groupName = getUserGroupName(self)
        return getOrCreateGroup(groupName)
       
    # group of project administrators 
    def getAdminGroup(self):
        groupName = getAdminGroupName(self)
        return getOrCreateGroup(groupName)
    
    # permission for standard users project
    def getUserPermission(self):
        pDescription = '%s User Permission' % self.short_name
        pCodeName = "%s_user_permission" % self.short_name.lower()
        return getOrCreateProjectPermission(pDescription, pCodeName, [self.getUserGroup(), self.getAdminGroup()])
    
    # permission for project administrators
    def getAdminPermission(self):
        pDescription = '%s Admin Permission' % self.short_name
        pCodeName = "%s_admin_permission" % self.short_name.lower()
        return getOrCreateProjectPermission(pDescription, pCodeName, [self.getAdminGroup()])
    
    # Method to return all project users 
    # (i.e. associated with either the project Users or Admins group)
    def getUsers(self):
        # users
        uset = set( self.getUserGroup().user_set.all() )
        # administrators
        aset = set( self.getAdminGroup().user_set.all() )
        # join the two groups
        users = list( uset.union( aset ) )
        # sort by username
        #users.sort(key=lambda x: x.last_name, reverse=True)
        users.sort(key=lambda x: x.last_name)
        return users
    
    def getGroups(self):
        return [ self.getUserGroup(), self.getAdminGroup() ]
    
    # returns true if user is enrolled in any of the project's groups
    def hasUser(self, user):
        if user in self.getUserGroup().user_set.all():
            return True
        elif user in self.getAdminGroup().user_set.all():
            return True
        else:
            return False
        
    # return true if the user is waiting membership approval in this project's group
    def hasUserPending(self, user):
        mrlist = MembershipRequest.objects.filter(group=self.getUserGroup()).filter(user=user)
        if len(mrlist) > 0:
            return True
        else:
            return False
        
    # return True if the user is allowed to view the project pages
    def isVisible(self, user):
        if self.private==False:
            return True
        elif userHasUserPermission(user, self):
            return True
        elif userHasAdminPermission(user, self):
            return True
        else:
            return False
    # return True is the user is NOT allowed to view the project pages
    def isNotVisible(self, user):
        return not self.isVisible(user)
    
    def children(self):
        return Project.objects.filter(parent=self).order_by('short_name')
    
    def full_name(self):
        return '%s : %s' % (self.short_name, self.long_name)
    
    # method to retrieve all news for this project, ordered by date
    def news(self):
        qset = Q(project=self) | Q(other_projects=self)
        #return News.objects.filter(qset).distinct().order_by('-update_date')
        return self.news_set.filter(qset).distinct().order_by('-update_date')
    
    # utility class to build the project index
    class IndexItem:
        def __init__(self, topic, order, pages):
            # the topic for all pages (may be None)
            self.topic = topic
            # the current topic order
            self.order = order
            # the pages for this topic, with their order
            self.pages = pages
    
    def trackers(self):
        return self.get_external_urls(TYPE_TRACKER)
    
    def roadmap(self):
        return self.get_external_urls(TYPE_ROADMAP)
    
    def code(self):
        return self.get_external_urls(TYPE_CODE)
    
    def policies(self):
        return self.get_external_urls(TYPE_POLICY)
    
    # generic method to return a list of the project's external URLs of a given type
    def get_external_urls(self, type):
        return self.externalurl_set.filter(project=self, type=type)
    
    # method to return the project home page URL
    def home_page_url(self):
        return '/projects/%s/' % self.short_name.lower()
    
    # method to return the relative URL of the project logo
    def get_logo(self):
        
        if self.logo:            
            return self.logo.url
        else: 
            url = getattr(settings, "STATIC_URL", "") + DEFAULT_LOGO
        return url
    
    # method to return an ordered list of the project predefined pages
    # the page URLs returned start with the project home page base URL
    def predefined_pages(self):
        predefpages = []
        home_page_url = self.home_page_url()
        #ppages.append( ( self.short_name + " Home",  home_page_url ) )
        for ppages in PROJECT_PAGES:
            for ppage in ppages:
                if ppage[1]=="":
                    predefpages.append( ( self.short_name + " " + ppage[0], home_page_url ) )
                else:
                    predefpages.append( ( ppage[0], home_page_url + ppage[1]  ) )
        return predefpages
    
    # method to determine if this project has been initialized,
    # currently based on the existence of any associated posts (such as the home page)
    def isInitialized(self):
        if (len(self.post_set.all())>0):
            return True
        else:
            return False
        
    # method to return a map of project tabs indexed by label
    def get_tabs_map(self):
    
        map = {}
        for tab in self.tabs.all():
            map[tab.label] = tab
        return map
             
    # method to retrieve all signals for this project, ordered by date
    def signals(self):
        return self.loggedevent_set.filter(project=self).distinct().order_by('-update_date')

    # return the "short name : description" up to 50 characters
    def __unicode__(self):
        return smart_truncate(self.full_name(), 50)  
    
# method to return a named permission from the database, 
# or create a new one for these groups if not existing already
def getOrCreateProjectPermission(pDesc, pCodeName, groups):
    try:       
        return Permission.objects.get(codename=pCodeName)
    except:
        return createProjectPermission(pDesc, pCodeName, groups)           

# method to create a project permission
# and assign it to the given groups
def createProjectPermission(pDesc, pCodeName, groups):
        projectContenType = ContentType.objects.get(app_label=APPLICATION_LABEL, model='project')
        permission = Permission(name=pDesc, codename=pCodeName, content_type=projectContenType)
        permission.save()
        print 'Created permission=%s...' % permission.codename
        for group in groups:
            group.permissions.add(permission)
            group.save()
            print '...and associated to group=%s' % group.name
        return permission

# method to build the group name of projects users
def getUserGroupName(project):
    return "%s_users" % project.short_name.lower()

# method to build the group name of project administrators
def getAdminGroupName(project):
    return "%s_admins" % project.short_name.lower()

# method to load a group from the database, or create a new one if not existing already
def getOrCreateGroup(group_name):
    try:       
        return Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return createGroup(group_name)

def createGroup(group_name):
    group = Group(name=group_name)
    group.save()
    print "Created group: %s" % group.name
    return group
    

# shortcut method to check for project user permission
# note: this method works on permissions, not groups: as a consequence, staff users have ALL permissions
def userHasUserPermission(user, project):
    return user.has_perm( getPermissionLabel(project.getUserPermission()) )

# shortcut method to check for project admin permission
# note: this method works on permissions, not groups: as a consequence, staff users have ALL permissions
def userHasAdminPermission(user, project):
    return user.has_perm( getPermissionLabel(project.getAdminPermission()) )

# method to return the full permission label: cog.<pCodeName>
def getPermissionLabel(permission):
    return "%s.%s" % (APPLICATION_LABEL, permission.codename)

# function to return the site administrators (aka web masters) for this site
def getSiteAdministrators():
    return User.objects.filter(is_staff=True)
    
# method to return an ordered list of projects the user belongs to, or has applied for.
def getProjectsForUser(user, includePending):
    
    # set of groups the user belongs to
    ugroups = set(user.groups.all())
    #for ugroup in ugroups:
    #    print "ugroup=%s" % ugroup
    if includePending==True:
        # list of groups the user has pending status for
        pgroups = [mr.group for mr in MembershipRequest.objects.filter(user=user)]
        # combine and order all groups
        groups = list(ugroups.union(pgroups))
    else:
        groups = list(ugroups)
    groups.sort(key=lambda x: x.name)
    projects = []
    for group in groups:
        try:
            project = getProjectForGroup(group)
            if not project in projects:
                projects.append(project)
        # in case he group has not been deleted with the project
        except Project.DoesNotExist:
            pass
    return projects


# method to return the project associated to a group
def getProjectForGroup(group):
    project_short_name = group.name.replace('_users','').replace('_admins','')
    return Project.objects.get(short_name__iexact=project_short_name)

# function to build the full page URL from the input value
def get_project_page_full_url(project, sub_url):
    return "%s%s" % (project.home_page_url(), quote(sub_url))

# value to extract the input value from the full page URL
def get_project_page_sub_url(project, full_url):
    #prefix = "/cog/%s/" % project_short_name.lower()
    home_url = project.home_page_url()
    if len(full_url)>len(home_url):
        sub_url = full_url[len(home_url):]
    else:
        sub_url = ''
    return unquote(sub_url)