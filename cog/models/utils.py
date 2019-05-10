from project import Project
from collaborator import Collaborator
from project_topic import ProjectTopic
from search_profile import SearchProfile
from communication_means import CommunicationMeans
from search_facet import SearchFacet
from search_group import SearchGroup
from post import Post
from bookmark import Bookmark
from doc import Doc
from navbar import PROJECT_PAGES, DEFAULT_TABS
from django.conf import settings
from django.utils.timezone import now
from news import News
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from folder import Folder, getTopFolder, TOP_SUB_FOLDERS
from cog.models.constants import DEFAULT_SEARCH_FACETS
from project_tab import ProjectTab
import shutil
import os
from urllib import quote

import logging

log = logging.getLogger(__name__)

# method to retrieve all news for a given project, ordered by original publication date
def project_news(project):
    qset = Q(project=project) | Q(other_projects=project)
    return News.objects.filter(qset).distinct().order_by('-publication_date')


# method to return a list of project pages, organized by topic, and ordered by topic order first, page order second
def site_index(project):
    
    # initialize index if necessary
    #if len(project.topics.all())==0:
    #    init_site_index(project)
    
    index = []
    
    post_type_query = Q(type=Post.TYPE_PAGE) | Q(type=Post.TYPE_HYPERLINK)
    
    # first pages with no topic
    pages = Post.objects.filter(project=project).filter(parent=None).filter(post_type_query).\
        filter(topic=None).order_by('order')
    index.append(Project.IndexItem(None, 0, pages))
    
    # then pages by topic, ordered
    projectTopics = ProjectTopic.objects.filter(project=project).order_by('order')
    for projectTopic in projectTopics:
        pages = Post.objects.filter(project=project).filter(parent=None).filter(post_type_query)\
            .filter(topic=projectTopic.topic).order_by('order')
        # only display topics that have associated pages
        if pages.all():
            index.append(Project.IndexItem(projectTopic.topic, projectTopic.order, pages))
   
    return index


# method to initialize the project index
# this method will order all the existing pages and topics for this project
# NOTE:
# -) topic numbers start at 0 (for topic=None)
# -) page numbers start at 1 (for Home)
def init_site_index(project):
    
    log.debug('Initializing project index, project=%s' % project.short_name)
    project.topics.clear()
    
    # list all top-level project pages, order by topic first, then title
    pages = Post.objects.filter(project=project).filter(parent=None)\
        .filter(type='page').order_by('topic__name', 'title')

    topic_name = ''
    page_order = 0
    topic_order = 0
    for page in pages:
        # reset order with new topic
        if page.topic is not None and page.topic.name != topic_name:
            topic_name = page.topic.name
            page_order = 0
            topic_order = topic_order + 1
            # store new project-topic associaton
            pt = ProjectTopic(project=project, topic=page.topic, order=topic_order)
            pt.save()
        page_order = page_order + 1
        page.order = page_order
        page.save()


# Function to create and configure the project search profile with the default settings
def create_project_search_profile(project):
    
    # don't do anything if profile already exists
    try:
        profile = project.searchprofile
    except SearchProfile.DoesNotExist:
        log.debug('Configuring the project search, project=%s' % project.short_name)
        # assign default URL, if available
        url = getattr(settings, "DEFAULT_SEARCH_URL", "")
        profile = SearchProfile(project=project, url=url)
        profile.save()
        # create default search group, assign facets to it
        group = SearchGroup(profile=profile, name=SearchGroup.DEFAULT_NAME, order=0)
        group.save()
        # assign default facets
        facets = DEFAULT_SEARCH_FACETS
        for key, label in facets.items():
            facet = SearchFacet(key=key, label=label, group=group)
            facet.save()
        project.searchprofile = profile
        project.save()
        return profile


# function to create the project home page
# the home page fields are initialized to values obtained from the project object
def create_project_home(project, user):
    home = Post.objects.create(type=Post.TYPE_PAGE, 
                               author=user,
                               url=project.home_page_url(),
                               template="cog/post/page_template_sidebar_center_right.html",
                               title=project.long_name,
                               is_home=True,
                               update_date=now(),
                               #topic='Home Page',
                               project=project,
                               body=project.description,
                               is_private=False,
                               is_restricted=True)  # project home page is restricted by default
    home.save()
    return home


# Function to dynamically create a project page,
# if the given URL is one of the pre-defined URLs for a project.
# The new page is initialized to some properties (the template, content etc.) that can later be changed.
# This method assumes that the project home page exists already
# - in fact, the new page is created as a child of the home page.
def create_project_page(url, project):
    if project.active == True:
        home_url = project.home_page_url()
        home_page = Post.objects.get(url=home_url)
        if home_page:
            for _pages in PROJECT_PAGES:
                for _page in _pages:
                    if url == home_url + _page[1]:
                        page = Post.objects.create(type=Post.TYPE_PAGE, 
                                                   author=home_page.author,  # same author as home page
                                                   url=url,
                                                   template="cog/post/page_template_sidebar_center_right.html",
                                                   title='%s %s' % (project.short_name, _page[0]),
                                                   is_home=False,
                                                   update_date=now(),
                                                   parent=home_page,
                                                   #topic='Home Page',
                                                   project=project,
                                                   body='')
                        # SPECIAL CASE
                        if _page[0] == 'Logistics':
                            page.title = '%s Agenda' % project.short_name
                            page.save()
                        log.debug("Created project page: %s" % url)
                        return page
    return None


def get_project_communication_means(project, internal):
    return CommunicationMeans.objects.filter(project=project).filter(internal=internal)


def get_project_internal_communication_means(project):
    return get_project_communication_means(project, True)


def get_project_external_communication_means(project):
    return get_project_communication_means(project, False)


def listPeople(project):
    """
    Function to return a merged list of project public users, and project external collaborators.
    """
    
    pubUsers = project.getPublicUsers()
    collaborators = list(Collaborator.objects.filter(project=project))
    
    people = pubUsers + collaborators
    return sorted(people, key=lambda user: (user.last_name.lower(), user.first_name.lower()))


def get_or_create_default_search_group(project):
    
    profile = project.searchprofile
    try:
        group = SearchGroup.objects.filter(profile=profile).filter(name=SearchGroup.DEFAULT_NAME)[0]
    except IndexError:
        log.debug('Creating default search group for project=%s' % project.short_name)
        group = SearchGroup(profile=profile, name=SearchGroup.DEFAULT_NAME, order=len(list(profile.groups.all())))
        group.save()
    return group    


# Function to retrieve the project tabs in the order to be displayed.
# The tabs can be optionally created if not existing already.
# Each item in the list is itself a list, containing the top-level tab, 
# followed by all sub-tabs.
def get_or_create_project_tabs(project, save=True):
            
    tabs = []
    for pagelist in PROJECT_PAGES:
        tablist = []
        for i, page in enumerate(pagelist):
            # default values for label, url
            label = page[0]
            url = project.home_page_url() + page[1]
            if page[0] == "Home":
                # NESII Home
                label = "%s Home" % project.short_name                
            try:
                # try loading the project tab by its unique URL
                tab = ProjectTab.objects.get(url=url)
            except ProjectTab.DoesNotExist:
                # create the project tab if not existing already. 
                # select initial active state of tabs
                if page[0] in DEFAULT_TABS:
                    active = True
                else:
                    active = False
                tab = ProjectTab(project=project, label=label, url=url, active=active)
                if save:
                    log.debug("Creating tab=%s, project=%s" % (tab, project.short_name))
                    tab.save() 
                    # assign parent tab
                    if i > 0:
                        tab.parent = tablist[0]
                        tab.save()
                        log.debug("Assigned parent tab=%s to child tab=%s" % (tablist[0], tab))

            tablist.append(tab)
        tabs.append(tablist)
    return tabs           


# method to set the state of the project tabs from the HTTP request parameters
# note: tabs is a list of tabs (not a list of lists of tabs)
def setActiveProjectTabs(tabs, request, save=False):
        
    for tab in tabs:
        # Home tab MUST always be active
        if tab.label.endswith("Home"):
            tab.active = True
        elif "tab_%s" % tab.label in request.POST.keys():
            tab.active = True
        else:
            tab.active = False
            
        # persist latest state
        if save:
            # persist tab to database
            tab.save()
            #print "Saved project tab=%s to database" % tab
                        
    return tabs


def createOrUpdateProjectSubFolders(project, request=None):
    """
    Function to set the state of the top sub-folders, creating them if necessary.
    :param project:
    :param request:
    :return:
    """
    
    topFolder = getTopFolder(project)
    
    for name in TOP_SUB_FOLDERS.values():
        folder, created = Folder.objects.get_or_create(name=name, parent=topFolder, project=project)
        if created:
            log.debug('Project=%s: created top-level folder=%s' % (project.short_name, folder.name))
        if request is not None and ("folder_%s" % folder.name) in request.POST.keys():
            folder.active = True
        else:
            folder.active = False
        folder.save()
        
def getBookmarkFromDoc(doc):
    '''Returns the first Bookmark with URL matching the Document path.'''
    
    url_fragment = quote(doc.path, safe="%/:=&?~#+!$,;'@()*[]")
    log.debug('Looking for bookmark that contains URL fragment: %s' % url_fragment)
    bookmarks = Bookmark.objects.filter(url__contains=url_fragment)
    for bookmark in bookmarks:
        return bookmark
    return None # no Bookmark found

def getDocFromBookmark(bookmark):
    '''Returns the first Doc with path that matches the Bookmark URL.'''
    
    if 'site_media/' in bookmark.url:
        _, url_fragment = bookmark.url.split('site_media/', 1)
        log.debug('Looking for doc that contains path: %s' % url_fragment)
        docs = Doc.objects.filter(path__contains=url_fragment)
        for doc in docs:
            return doc
        return None
    

def delete_doc(doc):
    '''
    Utility method to properly delete a Doc object.
    '''
        
    # remove from possible associated posts
    posts = Post.objects.filter(docs__id=doc.id)
    for post in posts:
        post.docs.remove(doc)
        
    # remove possible associated resource
    bookmark = getBookmarkFromDoc(doc)
    if bookmark is not None:
        log.debug('Deleting associated bookmark: %s' % bookmark.url)
        bookmark.delete()
        
    # obtain document full path (before deleting object from database)
    fullpath = os.path.join(settings.MEDIA_ROOT, doc.path)
    fullpath2= os.path.join(settings.MEDIA_ROOT, 'projects/%s' % doc.path) # missing 'projects' in file path

    # delete document from database
    doc.delete()
    
    # delete document from file system
    for fp in [fullpath, fullpath2]:
        if os.path.exists(fp):
            log.debug('Deleting document=%s' % fp)
            os.remove(fp)
    
    # also delete possible thumbnail files (created by File Browser)
    # canberra_hero_image.jpg
    # canberra_hero_image_admin_thumbnail.jpg
    # canberra_hero_image_thumbnail.jpg
    (path, ext) = os.path.splitext(fullpath)
    for suffix in ['_thumbnail', '_admin_thumbnail']:
        auxpath = "%s%s%s" % (path, suffix, ext)
        if os.path.isfile(auxpath):
            os.remove(auxpath)

def deleteProject(project, dryrun=True, rmdir=False):
    """
    Utility method to delete a project and associated objects, media.
    """
    
    log.info("Deleting project=%s" % project.short_name)
           
    # delete project User group, permissions
    ug = project.getUserGroup()
    for p in ug.permissions.all():
        log.debug('Deleting permission: %s' % p)
        if not dryrun:
            p.delete()
    log.debug('Deleting group: %s' % ug)
    if not dryrun:
        ug.delete()
        
    # delete project Admin group, permissions
    ag = project.getAdminGroup()
    for p in ag.permissions.all():
        log.debug('Deleting permission: %s' % p)
        if not dryrun:
            p.delete()
    log.debug('Deleting group: %s' % ag)
    if not dryrun:
        ag.delete()

    # delete project Contributor group, permissions
    cg = project.getContributorGroup()
    for p in cg.permissions.all():
        log.debug('Deleting permission: %s' % p)
        if not dryrun:
            p.delete()
    log.debug('Deleting group: %s' % cg)
    if not dryrun:
        cg.delete()

    if rmdir:
        media_dir = os.path.join(settings.MEDIA_ROOT, settings.FILEBROWSER_DIRECTORY, project.short_name.lower())
        log.debug("Removing directory tree: %s" % media_dir)
        if not dryrun:
            try:
                shutil.rmtree(media_dir)
            except OSError as e:
                log.error(str(e))
    
    log.info('Deleting project: %s' % project)
    if not dryrun:
        project.delete()