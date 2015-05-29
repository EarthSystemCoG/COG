
from cog.utils import smart_truncate
from constants import *
from navbar import *
from django.conf import settings
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.forms import Textarea
from membership import MembershipRequest
from os.path import basename
from cog.models.user_profile import UserProfile
from cog.models.topic import Topic
from cog.models.project_tag import ProjectTag
from urllib import quote, unquote
import os
import sys
import re
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from collections import OrderedDict
from django.core.exceptions import ObjectDoesNotExist


# Project
class Project(models.Model):
        
    # mandatory attributes
    short_name = models.CharField(max_length=20, unique=True, help_text="Short project acronym, 20 characters maximum, "
                                                                        "use only letters, numbers and '_', '-', "
                                                                        "no spaces.")
    long_name = models.CharField(max_length=120, unique=True, help_text='Fully spelled project name.')
    description = models.TextField(blank=False, null=True, help_text='A short paragraph that describes the project.')
    
    site = models.ForeignKey(Site, default=settings.SITE_ID)
    
    # optional attributes
    mission = models.TextField(blank=True, help_text='Succinctly describes why the project exists and what it does.')
    vision = models.TextField(blank=True, help_text='Outlines what a project wants to be, or how it wants the world '
                                                    'in which it operates to be. It is a long-term view.')
    values = models.TextField(blank=True, help_text='Beliefs that are shared among the members of a project. '
                                                    'Values influence culture and priorities and provide a framework '
                                                    'for informing decisions.')
    history = models.TextField(blank=True, help_text='A narrative describing the origination and evolution of the '
                                                     'project.')
    external_homepage = models.URLField(max_length=200, blank=True, null=True, help_text='External Home Page')
    
    governanceOverview = models.TextField(blank=True, null=True, verbose_name='Governance Overview',
                                          help_text='One or more paragraphs providing a general overview of the '
                                                    'governance structure for the project.')
    
    developmentOverview = models.TextField(blank=True, null=True, verbose_name='Development Overview',
                                           help_text='One or more paragraphs providing a general overview of the '
                                                     'development processes for the project.')
    
    taskPrioritizationStrategy = models.TextField(blank=True, null=True, verbose_name='Task Prioritization Strategy.',
                                                  help_text='A paragraph describing how tasks are prioritized. '
                                                            'This description may include who participates, how often '
                                                            'they meet, how they meet, and whether the results are '
                                                            'public.')
    requirementsIdentificationProcess = models.TextField(blank=True, null=True,
                                                         verbose_name='Requirements Identification Process',
                                                         help_text='A paragraph describing how requirements are '
                                                                   'identified. This description may include who '
                                                                   'participates, what system is used to track '
                                                                   'requirements, and whether the results are public.')

    # Software
    software_features = models.TextField(blank=True, null=True, verbose_name='Software Features', help_text=None)
    system_requirements = models.TextField(blank=True, null=True, verbose_name='Software System Requirements',
                                           help_text=None)
    license = models.TextField(blank=True, null=True, verbose_name='License',
                               help_text='Name of license used for the software, if any.')
    implementationLanguage = models.TextField(blank=True, null=True, verbose_name='Implementation Language',
                                              help_text='The implementation language(s) of the software code.')
    bindingLanguage = models.TextField(blank=True, null=True, verbose_name='Binding Language',
                                       help_text='The binding language(s) of the software code.')
    supportedPlatforms = models.TextField(blank=True, null=True, verbose_name='Supported Platforms',
                                          help_text='The computing platforms that the software can run on.')
    externalDependencies = models.TextField(blank=True, null=True, verbose_name='External Dependencies',
                                            help_text='The major libraries and packages the software depends on.')

    # Users
    getting_started = models.TextField(blank=True, null=True, verbose_name='Getting Started',
                                       help_text='Describe how users can get started with this project.')
    
    # Contact Us
    projectContacts = models.TextField(blank=True, null=True, verbose_name='Project Contacts', default="",
                                       help_text='Describe how to contact the project.')
    technicalSupport = models.TextField(blank=True, null=True, verbose_name='Technical Support',
                                        help_text='Email address for technical questions.')
    meetingSupport = models.TextField(blank=True, null=True, verbose_name='Meeting Support',
                                      help_text='Describe how to setup meetings.')
    getInvolved = models.TextField(blank=True, null=True, verbose_name='Get Involved',
                                   help_text='Describe how to participate in the project.')
    
    # A project may have many parents. The relationship is not symmetrical.
    # The attribute parents_set contains the inverse relationship
    parents = models.ManyToManyField('self', blank=True, related_name='Parent Projects', symmetrical=False)
    
    # A project may have many peers. The relationship is not symmetrical.
    # The attribute peers_set contains the inverse relationship
    peers = models.ManyToManyField('self', blank=True, related_name='Peer Projects', symmetrical=False)
    
    # the initial requester of the project, if any
    author = models.ForeignKey(User, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    
    # the workspace of an inactive project is not accessible
    active = models.BooleanField(default=False, blank=False, null=False)
    
    # a private project is only visible to project members 
    # by default all projects are public, and must be explicitly made private
    private = models.BooleanField(default=False, blank=False, null=False)
    
    # optional custom logo
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    
    # optional hyperlink for custom logo
    logo_url = models.CharField(max_length=200, blank=True, null=True, help_text='Optional logo hyperlink URL.')
    
    # list of available topics for this project
    topics = models.ManyToManyField(Topic, blank=True, null=True, through='ProjectTopic')
    
    # list of project tags
    tags = models.ManyToManyField(ProjectTag, blank=True, null=True, related_name='projects')
    
    # flag to enable the search widget
    dataSearchEnabled = models.BooleanField(default=False, blank=False, null=False, help_text='Enable data search?')
    
    # flag to enable forum notifications
    forumNotificationEnabled = models.BooleanField(default=False, blank=False, null=False,
                                                   help_text='Enable forum notifications to project administrators ?')
    
    maxUploadSize = models.IntegerField(default=52428800, blank=True, null=False,
                                        help_text='Maximum upload size in bytes')
        
    class Meta:
        app_label = APPLICATION_LABEL
                
    def getAbsoluteUrl(self):
        """
        Returns the absolute home page URL for this project, keeping its site into account.
        """
        
        return "http://%s%s" % (self.site.domain, reverse('project_home', args=[self.short_name.lower()]))
    
    # group of standard users associated with this project
    def getUserGroup(self):
        groupName = getUserGroupName(self)
        return getOrCreateGroup(groupName)
       
    # group of project administrators 
    def getAdminGroup(self):
        groupName = getAdminGroupName(self)
        return getOrCreateGroup(groupName)
    
    # returns the project group for the specified role
    def getGroup(self, roleName):
        
        if roleName.lower() == 'user':
            return self.getUserGroup()
        elif roleName.lower() == 'admin':
            return self.getAdminGroup()
        else:
            return None
    
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
    def getUsers(self, exclude_superuser=False):
        if exclude_superuser:
            # users
            uset = set(self.getUserGroup().user_set.all().exclude(is_superuser=True))
            # administrators
            aset = set(self.getAdminGroup().user_set.all().exclude(is_superuser=True))
        else:
            # users
            uset = set(self.getUserGroup().user_set.all())
            # administrators
            aset = set(self.getAdminGroup().user_set.all())

        # join the two groups
        users = list(uset.union( aset ))
        # sort by username
        #users.sort(key=lambda x: x.last_name, reverse=True)
        users.sort(key=lambda x: x.last_name)
        return users
    
    # Method to return the project users that are not private
    def getPublicUsers(self):
        users = self.getUsers(exclude_superuser=False)
        pubUsers = []
        for user in users:
            try:
                print 'Checking user=%s' % user  # TODO:FixME
                if not user.get_profile().private:
                    pubUsers.append(user)
            except ObjectDoesNotExist:
                pass # non user profile
        return pubUsers

    def getGroups(self):
        return [self.getUserGroup(), self.getAdminGroup()]
    
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
        if self.active == False:
            return False
        elif self.private == False:
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
        return Project.objects.filter(parents__id=self.id).order_by('short_name')
    
    def full_name(self):
        return '%s : %s' % (self.short_name, self.long_name)
        
    # utility class to build the project index
    class IndexItem:
        def __init__(self, topic, order, pages):
            # the topic for all pages (may be None)
            self.topic = topic
            # the current topic order
            self.order = order
            # the pages for this topic, with their order
            self.pages = pages
        
    # generic method to return a list of the project's external URLs of a given type, ordered by their title.
    # unfortunately, external_url has no date created function or other field we can order by. Before 2.10, modification
    # of an external_url could result in random ordering. This at least forces them to be alphabetical.
    def get_external_urls(self, type):
        if type == 'release_schedule':
            return self.externalurl_set.filter(project=self, type=type).order_by('-title')
        else:
            return self.externalurl_set.filter(project=self, type=type).order_by('title')
        
    # method to return the project home page URL
    def home_page_url(self):
        return '/projects/%s/' % self.short_name.lower()
    
    # method to check whether the project is local
    def isLocal(self):
        return self.site == Site.objects.get_current()
    
    def isRemoteAndDisabled(self):
        """
        Returns True if the project is NOT local and its remote site is disabled.
        """
        return not self.isLocal() and not self.site.peersite.enabled
    
    # method to return an ordered list of the project predefined pages
    # the page URLs returned start with the project home page base URL
    def predefined_pages(self):
        predefpages = []
        home_page_url = self.home_page_url()
        #ppages.append( ( self.short_name + " Home",  home_page_url ) )
        for ppages in PROJECT_PAGES:
            for ppage in ppages:
                if ppage[1] == "":
                    predefpages.append((self.short_name + " " + ppage[0], home_page_url))
                else:
                    predefpages.append((ppage[0], home_page_url + ppage[1]))
        return predefpages
    
    # method to determine if this project has been initialized,
    # currently based on the existence of any associated posts (such as the home page)
    def isInitialized(self):
        if len(self.post_set.all()) > 0:
            return True
        else:
            return False
        
    # method to return a map of project tabs indexed by suburl
    def get_tabs_map(self):
    
        map = {}
        for tab in self.tabs.all():
            map[tab.suburl()] = tab
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
# old note: this method works on permissions, not groups: as a consequence, staff users have ALL permissions
# new note: now this method works directly on groups: a local staff user may NOT be in the user group for a remote project
def userHasUserPermission(user, project):
    #return user.is_staff or user.has_perm(getPermissionLabel(project.getUserPermission()))
   
    if userHasAdminPermission(user, project): # NOTE: the 'admin' role automatically garantees 'user' privileges
        return True
    else:
        return (user.is_staff and project.isLocal()) or project.getUserGroup() in user.groups.all()


# shortcut method to check for project admin permission
# old note: this method works on permissions, not groups: as a consequence, staff users have ALL permissions
# new note: now this method works directly on groups: a local staff user may NOT be in the admin group for a remote project
def userHasAdminPermission(user, project):
    #return user.is_staff or user.has_perm(getPermissionLabel(project.getAdminPermission()))
    return (user.is_staff and project.isLocal()) or project.getAdminGroup() in user.groups.all()

def userHasProjectRole(user, project, role):
    if user.is_staff:
        return True
    elif role == ROLE_USER:
        return userHasUserPermission(user, project) or userHasAdminPermission(user, project)
    elif role == ROLE_ADMIN:
        return userHasAdminPermission(user, project)
    else:
        return False


# method to return the full permission label: cog.<pCodeName>
def getPermissionLabel(permission):
    return "%s.%s" % (APPLICATION_LABEL, permission.codename)


# function to return the site administrators (aka web masters) for this site
def getSiteAdministrators():
    return User.objects.filter(is_staff=True)


# Method to return an ordered list of projects the user belongs to, or has applied for.
# Inactive projects are NOT included.
def getProjectsForUser(user, includePending):
    
    # set of groups the user belongs to
    ugroups = set(user.groups.all())
    #for ugroup in ugroups:
    #    print "ugroup=%s" % ugroup
    if includePending == True:
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
            if not project in projects and project.active == True:
                projects.append(project)
        # in case he group has not been deleted with the project
        except Project.DoesNotExist:
            pass
    return projects


# method to return an ordered dictionary of (project_short_name, user_roles[]) pairs for a given user
# pending projects are NOT included
def getProjectsAndRolesForUsers(user, includeRemote=True):
    
    projects = OrderedDict()
    
    # ordered list of all user groups
    groups = list(user.groups.all())
    groups.sort(key=lambda x: x.name)
    
    for group in groups:
        try:
            project = getProjectForGroup(group)
            if includeRemote or project.isLocal():
                # add this project to the dictionary
                if not project.short_name in projects:
                    projects[project.short_name] = []
                # add this role to this project
                if group.name.endswith('_admins'):
                    projects[project.short_name].append('admin')
                elif group.name.endswith('_users'):
                    projects[project.short_name].append('user')
        except ObjectDoesNotExist:
            print "WARNING: cannot retrieve project for group=%s" % group
            pass
        
    return projects


# method to return the project associated to a group
def getProjectForGroup(group):
    project_short_name = group.name.replace('_users', '').replace('_admins', '')
    return Project.objects.get(short_name__iexact=project_short_name)


# function to build the full page URL from the input value
def get_project_page_full_url(project, sub_url):
    return "%s%s" % (project.home_page_url(), quote(sub_url))


# value to extract the input value from the full page URL
def get_project_page_sub_url(project, full_url):
    #prefix = "/cog/%s/" % project_short_name.lower()
    home_url = project.home_page_url()
    if len(full_url) > len(home_url):
        sub_url = full_url[len(home_url):]
    else:
        sub_url = ''
    return unquote(sub_url)


def create_upload_directory(project):
    
    # create filebrowser upload directory
    fb_upload_dir = os.path.join(settings.MEDIA_ROOT, settings.FILEBROWSER_DIRECTORY, project.short_name.lower())
    if not os.path.exists(fb_upload_dir):
        os.makedirs(fb_upload_dir)
        print 'Project Upload directory created: %s' % fb_upload_dir



