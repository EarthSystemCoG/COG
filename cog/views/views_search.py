from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from cog.forms.forms_search import *
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
import json
import urllib, urllib2


from cog.views.constants import PERMISSION_DENIED_MESSAGE
from cog.services.search import SolrSearchService
from cog.models.search import SearchOutput, Record, Facet, FacetProfile
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from copy import copy, deepcopy
from urllib2 import HTTPError

from cog.models.search import *
from cog.services.SolrSerializer import deserialize

from cog.templatetags.search_utils import displayMetadataKey, formatMetadataKey
from cog.models.utils import get_or_create_default_search_group
from django.http.response import HttpResponseServerError


SEARCH_INPUT  = "search_input"
SEARCH_OUTPUT = "search_output"
FACET_PROFILE = "facet_profile"
ERROR_MESSAGE = "error_message"
SEARCH_DATA   = "search_data"
SEARCH_REDIRECT = "search_redirect"
SEARCH_PAGES  = "search_pages"
REPLICA_FLAG  = "replica_flag"
LATEST_FLAG   = "latest_flag"
LOCAL_FLAG    = "local_flag"
SEARCH_PATH   = "search_path"
SEARCH_URL    = 'search_url'         # stores ESGF search URL
LAST_SEARCH_URL = "last_search_url"  # stores CoG last search URL (including project)
# constraints excluded from bread crums display
SEARCH_PATH_EXCLUDE = ["limit","offset","csrfmiddlewaretoken","type"]
              
      
def search(request, project_short_name):
    """
    Entry point for all search requests (GET/POST).
    Loads project-specific configuration.
    """
    
    # store this URL at session scope so other pages can reload the last search
    request.session[LAST_SEARCH_URL] = request.get_full_path()  # relative search page URL + optional query string
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
        
    # check permission
    if project.private:
        if request.user.is_anonymous():
            return HttpResponseRedirect(reverse('login')+"?next=%s" % request.path )
        else:
            if not userHasUserPermission(request.user, project):
                return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
   
    config = _getSearchConfig(request, project)
    if config:        
        #config.printme()
        # pass on project as extra argument to search
        return search_config(request, config, extra = {'project' : project, 'title2':'%s Data Search' % project.short_name} )
    # search is not configured for this project
    else:
        messages = ['Searching is not enabled for this project.',
                    'Please contact the project administrators for further assistance.']
        return render_to_response('cog/common/message.html', {'project' : project, 'messages':messages, 'title2':'Data Search' }, context_instance=RequestContext(request))

def _buildSearchInput(request, searchConfig):
    '''Assembles the search input from the HTTP request and the project specific configuration.'''
    
    # populate input with search constraints from HTTP request
    searchInput = SearchInput()
    for facetGroup in searchConfig.facetProfile.facetGroups:
        for key in facetGroup.getKeys():
            if (request.REQUEST.get(key, None)):
                for value in request.REQUEST.getlist(key):
                    if value:
                        searchInput.addConstraint(key, value)
    
    # add fixed constraints - override previous values
    for key, values in searchConfig.fixedConstraints.items():
            searchInput.setConstraint(key, values)
            
    # text
    if request.REQUEST.get('query', None):
        searchInput.query = request.REQUEST['query']
    # type
    if request.REQUEST.get('type', None):
        searchInput.type = request.REQUEST['type']
    # replica=True/False
    if request.REQUEST.get('replica', None) == 'on':
        searchInput.replica = True
    # latest=True/False
    if request.REQUEST.get('latest', None) == 'on':
        searchInput.latest = False
    # local=True/False
    if request.REQUEST.get('local', None) == 'on':
        searchInput.local = True

    # offset, limit
    if request.REQUEST.get('offset', 0):
        searchInput.offset = int(request.REQUEST['offset'])
    if request.REQUEST.get('limit', 0):
        searchInput.limit = int(request.REQUEST['limit'])

    return searchInput
    
def search_config(request, searchConfig, extra={}):
    """
    Project-specific search view that processes all GET/POST requests.
    Parses GET/POST requests parameters and combines them with the project fixed constraints.
    Delegates to 'search_get' and 'search_post'.
    Pre-seeded search URLs are automatically processed (i.e. GET requests with additional HTTP parameters, but NOT after a POST redirect).
    """
        
    # print extra arguments
    for key, value in extra.items():
        print 'extra key=%s value=%s' % (key,value)
    
    # create search input object
    searchInput = _buildSearchInput(request, searchConfig)
        
    # GET/POST switch
    print "Search() view: HTTP Request method=%s search_redirect flag=%s HTTP parameters=%s" % (request.method, 
                                                                                                request.session.get(SEARCH_REDIRECT, None), 
                                                                                                request.REQUEST)
    if (request.method=='GET'):
        if len(request.REQUEST.keys()) > 0 and request.session.get(SEARCH_REDIRECT, None) is None: 
            # GET pre-seeded search URL -> redirect to POST immediately
            return search_post(request, searchInput, searchConfig, extra)
        else:
            return search_get(request, searchInput, searchConfig, extra)
    else:
        return search_post(request, searchInput, searchConfig, extra)
        
def search_get(request, searchInput, searchConfig, extra={}):
    '''
    View that processes search GET requests.
    If invoked directly, it executes a query for facets but no results.
    After a POST redirect, it retrieves results from the session and removes the SEARCH_REDIRECT flag.
    '''
    
    facetProfile = searchConfig.facetProfile
    searchService = searchConfig.searchService
    
    # pass on all the extra arguments
    data = extra
    
    # GET request after POST redirection
    if (request.session.get(SEARCH_REDIRECT, None)):
        
        print "Retrieving search data from session"
        data = request.session.get(SEARCH_DATA)
        
        # remove POST redirect flag
        del request.session[SEARCH_REDIRECT]
    
    # direct GET request
    else:
        
        # reset the search path
        request.session[SEARCH_PATH] = []
        
        # set retrieval of all facets in profile
        # but do not retrieve any results
        searchInput.facets = facetProfile.getAllKeys()
        searchInput.limit = 0  # don't query for results
        searchInput.offset = 0
        
        try:
            (url, xml) = searchService.search(searchInput)
            searchOutput = deserialize(xml, facetProfile)
            
            data[SEARCH_INPUT] = searchInput
            data[SEARCH_OUTPUT] = searchOutput
            data[SEARCH_URL] = url
            data[FACET_PROFILE] = facetProfile
            #data[FACET_PROFILE] = sorted( facetProfile.getKeys() ) # sort facets by key
            
            # save data in session
            request.session[SEARCH_DATA] = data
            
        except HTTPError:
            print "HTTP Request Error"
            data = request.session[SEARCH_DATA]
            data[SEARCH_INPUT] = searchInput
            data[ERROR_MESSAGE] = "Error: HTTP request resulted in error, search may not be properly configured "
            
            
    # build pagination links
    offset = data[SEARCH_INPUT].offset
    limit = data[SEARCH_INPUT].limit
    if limit > 0:
        currentPage = offset/limit + 1
        numResults = len(data[SEARCH_OUTPUT].results)
        totResults = data[SEARCH_OUTPUT].counts
        data[SEARCH_PAGES] = []
            
        if offset > 0:
            data[SEARCH_PAGES].append( ('<< Previous', offset-limit ) )
                
        for page in range(currentPage-5, currentPage+6):
            pageOffset = (page-1)*limit
            if page==currentPage:
                data[SEARCH_PAGES].append( ('-%s-' % page, pageOffset) )
            elif page > 0 and pageOffset < totResults:
                data[SEARCH_PAGES].append( ('%s' % page, pageOffset) )
            
        if offset+limit < totResults:
            data[SEARCH_PAGES].append( ('Next >>', offset+numResults ) )
        
    # add configuration flags
    data[REPLICA_FLAG] = searchConfig.replicaFlag
    data[LATEST_FLAG] = searchConfig.latestFlag
    data[LOCAL_FLAG] = searchConfig.localFlag
        
    return render_to_response('cog/search/search.html', data, context_instance=RequestContext(request))    

def search_post(request, searchInput, searchConfig, extra={}):
    '''
    View that processes a search POST request.
    Stores results in session, together with special SEARCH_REDIRECT session flag.
    Then redirects to the search GET URL.
    '''
    
    facetProfile = searchConfig.facetProfile
    searchService = searchConfig.searchService
    
    # valid user input
    if (searchInput.isValid()):
        
        # set retrieval of all facets in profile
        searchInput.facets = facetProfile.getAllKeys()
    
        # execute query for results, facets
        try:
            (url, xml) = searchService.search(searchInput)
            searchOutput = deserialize(xml, facetProfile)
            #searchOutput.printme()
            
            # initialize new session data from extra argument dictionary
            data = extra
            data[SEARCH_INPUT] = searchInput
            data[SEARCH_OUTPUT] = searchOutput
            data[SEARCH_URL] = url
            data[FACET_PROFILE] = facetProfile
            #data[FACET_PROFILE] = sorted( facetProfile.getKeys() ) # sort facets by key
            
        except HTTPError:
            print "HTTP Request Error"
            data = request.session[SEARCH_DATA]
            data[SEARCH_INPUT] = searchInput
            data[ERROR_MESSAGE] = "Error: HTTP request resulted in error, search may not be properly configured "

            
    # invalid user input
    else:
        print "Invalid Search Input"
        # re-use previous data (output, profile and any extra argument) from session
        data = request.session[SEARCH_DATA]
        # override search input from request
        data[SEARCH_INPUT] = searchInput
        # add error
        data[ERROR_MESSAGE] = "Error: search query text cannot contain any of the characters: %s" % INVALID_CHARACTERS;
             
    # store data in session 
    #data['title'] = 'Advanced Data Search'
    request.session[SEARCH_DATA] = data
    
    # update search path
    sp = request.session.get(SEARCH_PATH, [])
    #for key, values in searchInput.constraints.items():
    # note: request parameters do NOT include the project fixed constraints
    req_constraints = [] # latest constraints from request
    for key, value in request.REQUEST.items():
        if not key in SEARCH_PATH_EXCLUDE and value != 'on': # value from 'checkbox_...'
            if value is not None and len(value)>0: # disregard empty facet
                print 'key=%s value=%s' % (key, value)
                constraint = (key, value)     
                req_constraints.append(constraint)
                if not constraint in sp:
                    sp.append(constraint)
                    
    # remove obsolete constraints
    sp = [item for item in sp if item in req_constraints]
    request.session[SEARCH_PATH] = sp
    
    # use POST-REDIRECT-GET pattern
    # flag the redirect in session
    request.session[SEARCH_REDIRECT] = True
    return HttpResponseRedirect( request.get_full_path() ) # relative search page URL + optional query string

def metadata_display(request, project_short_name):
    
    project = request.GET.get('project', None)
    id = request.GET.get('id', None)
    dataset_id = request.GET.get('dataset_id', None)
    type = request.GET.get('type', None)
    subtype = request.GET.get('subtype', None)
    index_node = request.GET.get('index_node', None)
    back = request.GET.get('back', None)
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    config = _getSearchConfig(request, project)

    # retrieve result metadata
    params = [ ('type', type), ('id', id), ("format", "application/solr+json"), ("distrib", "false") ]
    if type == 'File':
        params.append( ('dataset_id', dataset_id) )
                
    url = "http://"+index_node+"/esg-search/search?"+urllib.urlencode(params)
    print 'Metadata Solr search URL=%s' % url
    fh = urllib2.urlopen( url )
    response = fh.read().decode("UTF-8")

    # parse JSON response (containing only one matching 'doc)
    jsondoc = json.loads(response)
    metadata = _processDoc( jsondoc["response"]["docs"][0] )

    # retrieve parent metadata    
    parentMetadata = {}
    if type == 'File':
        params = [ ('type', 'Dataset'), ('id', dataset_id), ("format", "application/solr+json"), ("distrib", "false") ]
        url = "http://"+index_node+"/esg-search/search?"+urllib.urlencode(params)
        #print 'Solr search URL=%s' % url
        fh = urllib2.urlopen( url )
        response = fh.read().decode("UTF-8")
        jsondoc = json.loads(response)
        parentMetadata = _processDoc( jsondoc["response"]["docs"][0] )
    
    return render_to_response('cog/search/metadata_display.html', 
                              {'title':metadata.title, 'project' : project, 'metadata':metadata, 'parentMetadata':parentMetadata, 'back': back }, 
                              context_instance=RequestContext(request))
    
class MetaDoc:
    ''' Utility class containing display metadata extracted from a Solr result document.'''
    
    def __init__(self):
        # special fields
        self.id = ''
        self.title = ''
        self.description = ''
        self.type = ''
        self.subtype = ''
        self.url = ''
        self.mime_type = ''
        self.thumbnail = ''
        # container for all other metadata as (key, values[]) tuples ordered by key
        self.fields = []
        
def _processDoc(doc): 
    '''Utility method to process the JSON metadata object before display.'''
    
    metadoc = MetaDoc()
    for key in sorted(doc.keys()):
        value = doc[key]
        
        if key == 'id':
            metadoc.id = value       
        elif key == 'title':
            metadoc.title = value
        elif key == 'description':
            metadoc.description = value[0]
        elif key == 'type':
            metadoc.type = value
        elif key == 'subtype':
            metadoc.subtype = value[0].capitalize()
        elif key == 'number_of_files':
            pass # ignore
        elif key == 'url':
            for val in value:
                parts = val.split('|')
                if parts[2] == 'Thumbnail':
                    metadoc.thumbnail = parts[0]
                else:
                    metadoc.url = parts[0]
                    metadoc.mime_type = parts[1]
        else:
            # fields NOT to be displayed
            if displayMetadataKey(key):
                # multiple values
                if hasattr(value, '__iter__'):
                    metadoc.fields.append( (formatMetadataKey(key), value) )
                # single value - transform into list for consistency
                else:
                    metadoc.fields.append( (formatMetadataKey(key), [value]) )
                        
    return metadoc
    
# method to configure the search on a per-request basis
def _getSearchConfig(request, project):
    
    # configure project search profile, if not existing already
    try:
        profile = project.searchprofile
    except SearchProfile.DoesNotExist:
        profile = create_project_search_profile(project)
                        
    # configure URL of back-end search service
    searchService = SolrSearchService(profile.url, profile.facets())
    
    # configure facet profile
    facet_groups = []
    for search_group in profile.groups.all():
        facets = []
        for facet in search_group.facets.all():
            facets.append( (facet.key, facet.label) )
        facet_groups.append( FacetGroup(facets, search_group.name ) )
    #facets = []
    #for facet in project.searchprofile.facets():    
    #    facets.append((facet.key,facet.label))
    facetProfile = FacetProfile(facet_groups)
    #facetProfile = FacetProfile( list(profile.searchgroup_set.all()) )
    
    # configure fixed search constraints
    # fixedConstraints = { 'project': ['dycore_2009'], } 
    fixedConstraints = {}   
    if project.searchprofile.constraints:
        constraints = project.searchprofile.constraints.split('&')
        for constraint in constraints:
            (key,values) = constraint.strip().split('=')
            _values = values.split(',')
            for value in _values:
                try:
                    fixedConstraints[key].append(value)
                except KeyError:
                    fixedConstraints[key] = [value]
            
    return SearchConfig(facetProfile, fixedConstraints, searchService,
                        profile.replicaSearchFlag, profile.latestSearchFlag, profile.localSearchFlag)
    


def search_profile_config(request, project_short_name):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # security check
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)

    if request.method=='GET':
        # retrieve project search profile
        try:
            profile = project.searchprofile
        # or create a new one
        except ObjectDoesNotExist:
            profile = create_project_search_profile(project)
            
        form = SearchProfileForm(instance=profile)
            
        return render_search_profile_form(request, project, form)
        
    else:
        
        # create form object from request parameters and existing search profile
        try:
            form = SearchProfileForm(request.POST, instance=project.searchprofile)
        # or create a new object
        except ObjectDoesNotExist:
            form = SearchProfileForm(request.POST)
        
        if form.is_valid():
            
            # save profile to the database
            profile = form.save()
                        
            # redirect to project home (GET-POST-REDIRECT)
            return HttpResponseRedirect(reverse('project_home', args=[project.short_name.lower()]))
            
        else:
            print 'Form is invalid: %s' % form
            return render_search_profile_form(request, project, form)
            
def _queryFacets(request, project):
    '''Executes a query for all available facets for a given project.'''
    
    searchConfig = _getSearchConfig(request, project)
    searchInput = _buildSearchInput(request, searchConfig)
    searchInput.limit = 0 # no results
    searchService = searchConfig.searchService
    (url, xml) = searchService.search(searchInput, allFacets=True) # uses facets='*'
    searchOutput = deserialize(xml, searchConfig.facetProfile)
    searchOutput.printme()
    
    return searchOutput.facets
    
# method to add a new facet
def search_facet_add(request, project_short_name):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # security check
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if request.method=='GET': 
        
        # retrieve list of available facets by executing project-specific query
        facets = _queryFacets(request, project)
        
        # create default search group, if not existing already
        group = get_or_create_default_search_group(project)
        
        # assign facet to default search group
        order = group.size()
        facet = SearchFacet(order=order, group=group)
        form = SearchFacetForm(instance=facet)    
        
        return render_search_facet_form(request, project, form, facets)
        
    else:
        form = SearchFacetForm(request.POST)
        
        if form.is_valid():            
            facet = form.save()
            return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()])) 
        
        else:     
            print 'Form is invalid: %s' % form.errors
            
            # must retrieve facets again
            facets = _queryFacets(request, project)
            
            return render_search_facet_form(request, project, form, facets)
        
# method to update an existing facet
def search_facet_update(request, facet_id):
    
    # retrieve facet from database
    facet = get_object_or_404(SearchFacet, pk=facet_id)
       
    # security check
    project = facet.group.profile.project
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # retrieve list of available facets by executing project-specific query
    facets = _queryFacets(request, project)
    
    if request.method=='GET':    
        form = SearchFacetForm(instance=facet)    
        return render_search_facet_form(request, project, form, facets)
        
    else:
        
        form = SearchFacetForm(request.POST, instance=facet)
        
        if form.is_valid():            
            facet = form.save()
            return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()])) 
        
        else:     
            print 'Form is invalid: %s' % form.errors
            return render_search_facet_form(request, project, form, facets)

def search_facet_delete(request, facet_id):
         
    # retrieve facet from database
    facet = get_object_or_404(SearchFacet, pk=facet_id)
    
    # facet group
    group = facet.group
    
    # retrieve associated project
    project = group.profile.project
    
    # security check
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
        
    # delete facet
    facet.delete()
    
    # re-order all group facets
    facets = SearchFacet.objects.filter(group=group).order_by('order')
    count = 0
    for facet in facets:
        facet.order = count
        facet.save()
        count += 1
        
    # redirect to project home (GET-POST-REDIRECT)
    return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()]))

def search_files(request, dataset_id, index_node):
    """View that searches for all files of a given dataset, and returns the response as JSON"""
    
    # maximum number of files to query for
    limit = request.GET.get('limit', 20)
    
    # optional query filter
    query = request.GET.get('query', None)
    
    params = [ ('type',"File"), ('dataset_id',dataset_id), ("format", "application/solr+json"), ("distrib", "false"),
               ('offset','0'), ('limit',limit) ]
    if query is not None and len(query.strip())>0:
        params.append( ('query', query) )
 
    url = "http://"+index_node+"/esg-search/search?"+urllib.urlencode(params)
    print 'Searching for files: URL=%s' % url
    fh = urllib2.urlopen( url )
    response = fh.read().decode("UTF-8")

    return HttpResponse(response, content_type="application/json")

def search_reload(request):
    '''View that attempts to redirect to the last project-specific page,
       including constraints and results.'''
    
    if request.session.get(LAST_SEARCH_URL, None):
        print 'Reloading search page: %s' % request.session[LAST_SEARCH_URL]
        request.session[SEARCH_REDIRECT] = True # flag to retrieve constraints, results
        return HttpResponseRedirect(request.session[LAST_SEARCH_URL]) # just like after the last POST
        
    else:
        return render_to_response('cog/common/message.html', 
                                  {'mytitle': 'An Error Occurred',
                                   'messages': ['Your last search page could not be found.'] },
                                   context_instance=RequestContext(request))

            
def render_search_profile_form(request, project, form):
    return render_to_response('cog/search/search_profile_form.html', 
                              {'project' : project, 'form':form, 'title':'Project Search Configuration' }, 
                               context_instance=RequestContext(request))
    
def render_search_facet_form(request, project, form, facets):
    return render_to_response('cog/search/search_facet_form.html', 
                              {'project' : project, 'form':form, 'title':'Search Facet Configuration', 'facets':facets }, 
                              context_instance=RequestContext(request))