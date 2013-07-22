from project import Project
from collaborator import Collaborator
from project_topic import ProjectTopic
from search_profile import SearchProfile
from communication_means import CommunicationMeans
from search_facet import SearchFacet
from post import Post
from constants import PROJECT_PAGES
from django.conf import settings
from django.utils.timezone import now
from news import News
from django.db.models import Q
from django.contrib.comments import Comment
from django.contrib.contenttypes.models import ContentType

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
        # assign default facets
        facets = getattr(settings, "DEFAULT_SEARCH_FACETS", {})
        for key, label in facets.items():
            facet = SearchFacet(key=key, label=label, profile=profile)
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
                                                   template="cog/post/page_template_sidebar_center.html",
                                                   title='%s %s' % (project.short_name, _page[0]),
                                                   is_home=False,
                                                   update_date=now(),
                                                   parent=home_page,
                                                   #topic='Home Page',
                                                   project=project,
                                                   body='')
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
