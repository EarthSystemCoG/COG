from project import Project
from collaborator import Collaborator
from project_topic import ProjectTopic
from search_profile import SearchProfile
from communication_means import CommunicationMeans
from search_facet import SearchFacet
from search_group import SearchGroup
from post import Post
from navbar import PROJECT_PAGES, DEFAULT_TABS
from django.conf import settings
from django.utils.timezone import now
from news import News
from django.db.models import Q
from django.contrib.comments import Comment
from django.contrib.contenttypes.models import ContentType
from folder_conf import folderManager
from folder import Folder, getTopFolder, TOP_SUB_FOLDERS
from project_tab import ProjectTab

# method to retrieve all news for a given project, ordered by date
def news(project):
    qset = Q(project=project) | Q(other_projects=project)
    return News.objects.filter(qset).distinct().order_by('-update_date')

# method to return a list of project pages, organized by topic, and ordered by topic order first, page order second
def site_index(project):
    
    # initialize index if necessary
    #if len(project.topics.all())==0:
    #    init_site_index(project)
    
    index = []
    
    # first pages with no topic
    pages = Post.objects.filter(project=project).filter(parent=None).filter(type='page').filter(topic=None).order_by('order')
    index.append( Project.IndexItem(None, 0, pages) )
    
    # then pages by topic, ordered
    projectTopics = ProjectTopic.objects.filter(project=project).order_by('order')
    for projectTopic in projectTopics:
        pages = Post.objects.filter(project=project).filter(parent=None).filter(type='page').filter(topic=projectTopic.topic).order_by('order')
        # only display topics that have associated pages
        if pages.all():
            index.append( Project.IndexItem(projectTopic.topic, projectTopic.order, pages) )
   
    return index

# method to initialize the project index
# this method will order all the existing pages and topics for this project
# NOTE:
# -) topic numbers start at 0 (for topic=None)
# -) page numbers start at 1 (for Home)
def init_site_index(project):
    
    print 'Initializing project index'
    project.topics.clear()
    
    # list all top-level project pages, order by topic first, then title
    pages = Post.objects.filter(project=project).filter(parent=None).filter(type='page').order_by('topic__name','title')

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
        print 'Configuring the project search profile'
        # assign default URL, if available
        url = getattr(settings, "DEFAULT_SEARCH_URL", "")
        profile = SearchProfile(project=project, url=url)
        profile.save()
        # create default search group, assign facets to it
        group = SearchGroup(profile=profile, name=SearchGroup.DEFAULT_NAME, order=0)
        group.save()
        # assign default facets
        facets = getattr(settings, "DEFAULT_SEARCH_FACETS", {})
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
                               url= project.home_page_url(),
                               template="cog/post/page_template_sidebar_center_right.html",
                               title=project.long_name,
                               is_home=True,
                               update_date=now(),
                               #topic='Home Page',
                               project=project,
                               body=project.description)
    home.save()
    return home

# Function to dynamically create a project page,
# if the given URL is one of the pre-defined URLs for a project.
# The new page is initialized to some properties (the template, content etc.) that can later be changed.
# This method assumes that the project home page exists already - in fact, the new page is created as a child of the home page.
def create_project_page(url, project):
    if project.active==True:
        home_url = project.home_page_url()
        home_page = Post.objects.get(url=home_url)
        if home_page:
            for _pages in PROJECT_PAGES:
                for _page in _pages:
                    if url == home_url + _page[1]:
                        page = Post.objects.create(type=Post.TYPE_PAGE, 
                                                   author=home_page.author, # same author as home page
                                                   url= url,
                                                   template="cog/post/page_template_sidebar_center_right.html",
                                                   title='%s %s' % (project.short_name, _page[0]),
                                                   is_home=False,
                                                   update_date=now(),
                                                   parent=home_page,
                                                   #topic='Home Page',
                                                   project=project,
                                                   body='')
                        # SPECIAL CASE
                        if _page[0]=='Logistics':
                            page.title = '%s Agenda' % project.short_name
                            page.save()
                        print "Created project page: %s" % url
                        return page
    return None

def get_project_communication_means(project, internal):
    return CommunicationMeans.objects.filter(project=project).filter(internal=internal)

def get_project_internal_communication_means(project):
    return get_project_communication_means(project, True)

def get_project_external_communication_means(project):
    return get_project_communication_means(project, False)

def listPeople(project):
    '''
    Function to return a merged list of project public users, and project external collaborators.
    '''
    
    pubUsers = project.getPublicUsers()
    collaborators = list( Collaborator.objects.filter(project=project) )
    
    people = pubUsers + collaborators
    return sorted(people, key=lambda user: (user.last_name.lower(), user.first_name.lower()) )
    
def delete_comments(object):
    '''Function to delete comments associated with a generic object.'''
    
    object_type = ContentType.objects.get_for_model(object)
    comments =  Comment.objects.filter(object_pk=object.id).filter(content_type=object_type)
    for comment in comments:
        print 'Deleting associated comment=%s' % comment.comment
        comment.delete()

def get_or_create_default_search_group(project):
    
    profile = project.searchprofile
    try:
        group = SearchGroup.objects.filter(profile=profile).filter(name=SearchGroup.DEFAULT_NAME)[0]
    except IndexError:
        print 'Creating default search group for project=%s' % project.short_name
        group = SearchGroup(profile=profile, name=SearchGroup.DEFAULT_NAME, order=len(list(profile.groups.all())) )
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
            if page[0]=="Home":
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
                    print "Creating tab= %s" % tab
                    tab.save() 
                    # assign parent tab
                    if i>0:
                        tab.parent = tablist[0]
                        tab.save()
                        print "Assigned parent tab=%s to child tab=%s" % (tablist[0], tab)

            tablist.append(tab)
        tabs.append(tablist)
    return tabs           

# method to set the state of the project tabs from the HTTP request parameters
# note: tabs is a list of tabs (not a list of lists of tabs)
def setActiveProjectTabs(tabs, request, save=False):
    
    topFolderLabels = folderManager.getTopFolderLabels()
    
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

def setActiveFolders(project, request):
    '''Function to set the state of the to-subfolders, creatin them if necessary.'''
    
    topFolder = getTopFolder(project)
    
    for name in TOP_SUB_FOLDERS.values():
        folder, created = Folder.objects.get_or_create(name=name, parent=topFolder, project=project)
        if created:
            print 'Project=%s: created top-level folder=%s' % (project.short_name, folder.name)
        if ("folder_%s" % folder.name) in request.POST.keys():
            folder.active = True
        else:
            folder.active = False
        folder.save()

def getActiveFolders(project):
    '''Returns a list of active folders for this project (both top-level and nested) .'''
    
    # list of existing folders for this project
    folders = Folder.objects.filter(project=project)
        
    # list of active project tabs
    tabs = ProjectTab.objects.filter(project=project, active=True)
    activeLabels = [tab.label for tab in tabs]
    
    # select active folders
    activeFolders = []
    for folder in folders:
        # use the top-level parent
        topFolder = folder.topParent()
        label = folderManager.getFolderLabelFromName(topFolder.name)
        if label in activeLabels:
            activeFolders.append(folder)
            
    return activeFolders