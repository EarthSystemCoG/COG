from copy import copy, deepcopy
from urllib2 import HTTPError
import json
import logging
import urllib, urllib2

from cog.config.search import SearchConfigParser
from cog.forms.forms_search import *
from cog.models.auth import userHasAdminPermission
from cog.models.auth import userHasUserPermission
from cog.models.search import *
from cog.models.search import SearchOutput, Record, Facet, FacetProfile, SearchInput
from cog.models.utils import get_or_create_default_search_group
from cog.services.SolrSerializer import deserialize
from cog.services.search import SolrSearchService
from cog.templatetags.search_utils import displayMetadataKey, formatMetadataKey
from cog.views.constants import PERMISSION_DENIED_MESSAGE, TEMPLATE_NOT_FOUND_MESSAGE
from cog.views.utils import getQueryDict
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound
from django.http.response import HttpResponseServerError
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.template.exceptions import TemplateDoesNotExist
from django.views.decorators.http import require_http_methods


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
# constraints excluded from bread crumbs display
SEARCH_PATH_EXCLUDE = ["limit","offset","csrfmiddlewaretoken","type","max_version", "min_version"]
TEMPLATE='template'

log = logging.getLogger(__name__)           
      
def search(request, project_short_name):
    """
    Entry point for all search requests (GET/POST).
    Loads project-specific configuration.
    """
    
    # store this URL at session scope so other pages can reload the last search
    request.session[LAST_SEARCH_URL] = request.get_full_path()  # relative search page URL + optional query string
    
    fromRedirectFlag = False
    if request.session.get(SEARCH_REDIRECT, None):
        fromRedirectFlag = True
        # remove POST redirect flag from session
        del request.session[SEARCH_REDIRECT]

    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
        
    # check permission
    if project.private:
        if request.user.is_anonymous():
            return HttpResponseRedirect(reverse('login')+"?next=%s" % request.path)
        else:
            if not userHasUserPermission(request.user, project):
                return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
   
    config = _getSearchConfig(request, project)
    if config:        
        # config.printme()
        # pass on project as extra argument to search
        # also include possible custom template
        return search_config(request, config, extra={'project': project, 
                                                     'title2': '%s Data Search'% project.short_name,
                                                     'template':getQueryDict(request).get(TEMPLATE,None) },
                             fromRedirectFlag=fromRedirectFlag)
    # search is not configured for this project
    else:
        messages = ['Searching is not enabled for this project.',
                    'Please contact the project administrators for further assistance.']
        return render(request,
                      'cog/common/message.html', 
                      {'project': project, 'messages': messages, 'title2': 'Data Search'})

def _addConfigConstraints(searchInput, searchConfig):
    '''Returns a COPY of the search input object with added project fixed constraints.'''
    
    _searchInput = deepcopy(searchInput)
    
    # add fixed constraints - but do NOT override previous values
    for key, values in searchConfig.fixedConstraints.items():
        if not _searchInput.hasConstraint(key):
            _searchInput.setConstraint(key, values)            
    return _searchInput
    

def _buildSearchInputFromHttpRequest(request, searchConfig):
    """Assembles the search input from the HTTP request only (NO project fixed constraints yet)."""
    
    queryDict = getQueryDict(request)
    
    # populate input with search constraints from HTTP request
    # only use facet keys from project configuration
    searchInput = SearchInput()
    for facetGroup in searchConfig.facetProfile.facetGroups:
        for key in facetGroup.getKeys():
            if queryDict.get(key, None):
                for value in queryDict.getlist(key):
                    if value:
                        searchInput.addConstraint(key, value)
                
    # text
    if queryDict.get('query', None):
        searchInput.query = queryDict['query']
    # type
    if queryDict.get('type', None):
        searchInput.type = queryDict['type']
    # replica=True/False
    if queryDict.get('replica', None) == 'on':
        searchInput.replica = True
    # latest=True/False
    if queryDict.get('latest', None) == 'on':
        searchInput.latest = False
    # local=True/False + replica=True
    if queryDict.get('local', None) == 'on':
        searchInput.local = True
        searchInput.replica = True # NEW: local search ALWAYS implies ALL replicas

    # offset, limit
    if queryDict.get('offset', 0):
        searchInput.offset = int(queryDict['offset'])
    if queryDict.get('limit', 0):
        searchInput.limit = int(queryDict['limit'])
        
    # max_version, min_version
    # NOTE: implies search on All Versions ( searchInput.latest = False )
    if queryDict.get('max_version', ''):
        searchInput.max_version = queryDict['max_version'].strip()
        searchInput.latest = False
    if queryDict.get('min_version', ''):
        searchInput.min_version = queryDict['min_version'].strip()
        searchInput.latest = False


    return searchInput


def search_config(request, searchConfig, extra={}, fromRedirectFlag=False):
    """
    Project-specific search view that processes all GET/POST requests.
    Parses GET/POST requests parameters and combines them with the project fixed constraints.
    Delegates to 'search_get' and 'search_post'.
    Pre-seeded search URLs are automatically processed (i.e. GET requests with additional HTTP parameters, but NOT after a POST redirect).
    """
        
    # print extra arguments
    #for key, value in extra.items():
    #    print 'extra key=%s value=%s' % (key, value)
    
    # create search input object from request parameters ONLY
    # NOTE: HTTP parameters MUST be part of project sarch configuration
    searchInput = _buildSearchInputFromHttpRequest(request, searchConfig)
            
    # GET/POST switch
    queryDict = getQueryDict(request)
    log.debug(
        "Search() view: HTTP Request method=%s fromRedirectFlag flag=%s HTTP parameters=%s" % (
            request.method, fromRedirectFlag, queryDict
        )
    )
    
    if request.method == 'GET':
        # GET pre-seeded search URL -> invoke POST immediately
        if len(queryDict.keys()) > 0 and not fromRedirectFlag: 
            return search_post(request, searchInput, searchConfig, extra)
        else:
            return search_get(request, searchInput, searchConfig, extra, fromRedirectFlag)
    else:
        return search_post(request, searchInput, searchConfig, extra)
        

def search_get(request, searchInput, searchConfig, extra={}, fromRedirectFlag=False):
    """
    View that processes search GET requests.
    If invoked directly, it executes a query for facets but no results.
    After a POST redirect, it retrieves results from the session.
    """
    
    facetProfile = searchConfig.facetProfile
    searchService = searchConfig.searchService
    
    # pass on all the extra arguments
    data = extra
    
    # GET request after POST redirection
    if fromRedirectFlag:
        
        log.debug("Retrieving search data from session")
        data = request.session.get(SEARCH_DATA)
            
    # direct GET request: must query for all facet values with project-specific constraints
    else:
        
        # reset the search path
        request.session[SEARCH_PATH] = []
        
        # add project fixed constraints
        log.debug('Search GET: adding fixed project constraints')
        _searchInput = _addConfigConstraints(searchInput, searchConfig)
        _searchInput.printme()
        
        # set retrieval of all facets in profile
        # but do not retrieve any results
        _searchInput.facets = facetProfile.getAllKeys()
        _searchInput.limit = 0  # don't query for results
        _searchInput.offset = 0
        
        try:
            (url, xml) = searchService.search(_searchInput)
            searchOutput = deserialize(xml, facetProfile)
            
            data[SEARCH_INPUT] = searchInput    # IMPORTANT: store in session the ORIGINAL search input WITHOUT project constraints
            data[SEARCH_OUTPUT] = searchOutput
            data[SEARCH_URL] = url
            data[FACET_PROFILE] = facetProfile
            # data[FACET_PROFILE] = sorted( facetProfile.getKeys() ) # sort facets by key
            
            # save data in session
            request.session[SEARCH_DATA] = data
            
        except HTTPError as error:
            log.error("HTTP Request Error: %s" % str(error))
            # data = request.session[SEARCH_DATA]
            data[SEARCH_INPUT] = searchInput

            data[ERROR_MESSAGE] = "Error: search may not be properly configured. Contact the Project " \
                                  "Administrator."

    # build pagination links
    offset = data[SEARCH_INPUT].offset
    limit = data[SEARCH_INPUT].limit
    if limit > 0 and data.get(SEARCH_OUTPUT, None):
        currentPage = offset/limit + 1
        numResults = len(data[SEARCH_OUTPUT].results)
        totResults = data[SEARCH_OUTPUT].counts
        data[SEARCH_PAGES] = []
            
        if offset > 0:
            data[SEARCH_PAGES].append(('<< Previous', offset-limit))
                
        for page in range(currentPage-5, currentPage+6):
            pageOffset = (page-1)*limit
            if page == currentPage:
                data[SEARCH_PAGES].append(('-%s-' % page, pageOffset))
            elif page > 0 and pageOffset < totResults:
                data[SEARCH_PAGES].append(('%s' % page, pageOffset))
            
        if offset+limit < totResults:
            data[SEARCH_PAGES].append(('Next >>', offset+numResults))
        
    # add configuration flags
    data[REPLICA_FLAG] = searchConfig.replicaFlag
    data[LATEST_FLAG] = searchConfig.latestFlag
    data[LOCAL_FLAG] = searchConfig.localFlag

    # render results        
    template = 'cog/search/search.html' # default template
    if data.get(TEMPLATE, None):
        template = 'cog/search/%s.html' % data[TEMPLATE] # custom template
        del data[TEMPLATE] # remove temp,ate from session

    try:
        return render(request, template, data)   
     
    except TemplateDoesNotExist:
        
        # invalidate this search session
        if request.session.get(SEARCH_DATA, None):
            del request.session[SEARCH_DATA]
        if request.session.get(SEARCH_REDIRECT, None):
            del request.session[SEARCH_REDIRECT]
            
        # redirect to project search page with error message
        return HttpResponseBadRequest(TEMPLATE_NOT_FOUND_MESSAGE)



def search_post(request, searchInput, searchConfig, extra={}):
    """
    View that processes a search POST request.
    Stores results in session, together with special SEARCH_REDIRECT session flag.
    Then redirects to the search GET URL.
    """
    
    facetProfile = searchConfig.facetProfile
    searchService = searchConfig.searchService
    queryDict = getQueryDict(request)
    
    # validate user input
    (valid, error_message) = searchInput.isValid()
    if valid:
                
        # add project fixed constraints
        log.debug('Search POST: adding fixed project constraints')
        _searchInput = _addConfigConstraints(searchInput, searchConfig)
        _searchInput.printme()
    
        # set retrieval of all facets in profile
        _searchInput.facets = facetProfile.getAllKeys()
    
        # execute query for results, facets
        try:
            (url, xml) = searchService.search(_searchInput)
            searchOutput = deserialize(xml, facetProfile)
            # searchOutput.printme()
            
            # initialize new session data from extra argument dictionary
            data = extra
            data[SEARCH_INPUT] = searchInput  # IMPORTANT: store in session the ORIGINAL search input WITHOUT project constraints
            data[SEARCH_OUTPUT] = searchOutput
            data[SEARCH_URL] = url
            data[FACET_PROFILE] = facetProfile
            # data[FACET_PROFILE] = sorted( facetProfile.getKeys() )  # sort facets by key
            
        except HTTPError as error:
            log.error("HTTP Request Error: %s" % str(error))
            data = request.session[SEARCH_DATA]
            data[SEARCH_INPUT] = searchInput

            data[ERROR_MESSAGE] = "Error: search may not be properly configured. Contact the Project " \
                                  "Administrator."
    # invalid user input
    else:
        log.debug("Invalid Search Input")
        # re-use previous data (output, profile and any extra argument) from session
        data = request.session[SEARCH_DATA]
        # override search input from request
        data[SEARCH_INPUT] = searchInput
        # add error
        data[ERROR_MESSAGE] = error_message
             
    # store data in session 
    request.session[SEARCH_DATA] = data
    
    # update search path
    sp = request.session.get(SEARCH_PATH, [])
    # for key, values in searchInput.constraints.items():
    # note: request parameters do NOT include the project fixed constraints
    req_constraints = []  # latest constraints from request
    for key, value in queryDict.items():
        if not key in SEARCH_PATH_EXCLUDE and value != 'on':  # value from 'checkbox_...'
            if value is not None and len(value) > 0:  # disregard empty facet
                log.debug('key=%s value=%s' % (key, value))
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
    #return HttpResponseRedirect(request.get_full_path())  # relative search page URL + optional query string
    
    # GET redirect
    if extra.get(TEMPLATE, None):
        return HttpResponseRedirect(request.get_full_path()) # keep the query parameters
    else:
        return HttpResponseRedirect(request.path) # remove query parameters


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
    params = [('type', type), ('id', id), ("format", "application/solr+json"), ("distrib", "false")]
    if type == 'File':
        params.append(('dataset_id', dataset_id))
                
    url = "http://"+index_node+"/esg-search/search?"+urllib.urlencode(params)
    log.debug('Metadata Solr search URL=%s' % url)
    fh = urllib2.urlopen(url)
    response = fh.read().decode("UTF-8")

    # parse JSON response (containing only one matching 'doc)
    jsondoc = json.loads(response)
    metadata = _processDoc(jsondoc["response"]["docs"][0])

    # retrieve parent metadata    
    parentMetadata = {}
    if type == 'File':
        params = [('type', 'Dataset'), ('id', dataset_id), ("format", "application/solr+json"), ("distrib", "false")]
        url = "http://"+index_node+"/esg-search/search?"+urllib.urlencode(params)
        # print 'Solr search URL=%s' % url
        fh = urllib2.urlopen(url)
        response = fh.read().decode("UTF-8")
        jsondoc = json.loads(response)
        parentMetadata = _processDoc(jsondoc["response"]["docs"][0])
    
    return render(request,
                  'cog/search/metadata_display.html', 
                  {'title': metadata.title, 'project': project, 'metadata': metadata,
                   'parentMetadata': parentMetadata, 'back': back})


class MetaDoc:
    """Utility class containing display metadata extracted from a Solr result document."""
    
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
    """Utility method to process the JSON metadata object before display."""
    
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
            pass  # ignore
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
                    metadoc.fields.append((formatMetadataKey(key), value))
                # single value - transform into list for consistency
                else:
                    metadoc.fields.append( (formatMetadataKey(key), [value]))
                        
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
    for search_group in profile.groups.all().order_by('order'):
        facets = []
        for facet in search_group.facets.all().order_by('order'):
            facets.append((facet.key, facet.label))
        facet_groups.append( FacetGroup(facets, search_group.name))
    # facets = []
    # for facet in project.searchprofile.facets():
    #    facets.append((facet.key,facet.label))
    facetProfile = FacetProfile(facet_groups)
    # facetProfile = FacetProfile( list(profile.searchgroup_set.all()))
    
    # configure fixed search constraints
    # fixedConstraints = { 'project': ['dycore_2009'], } 
    fixedConstraints = {}   
    if project.searchprofile.constraints:
        constraints = project.searchprofile.constraints.split('&')
        for constraint in constraints:
            (key, values) = constraint.strip().split('=')
            # IMPORTANT: DO NOT SPLIT 'localhost:8982/solr,localhost:8983/solr'
            # as 'shards=localhost:8982/solr&shards=localhost:8982/solr'
            if key == 'shards':
                _values = [values]
            else:
                _values = values.split(',')
            for value in _values:
                try:
                    fixedConstraints[key].append(value)
                except KeyError:
                    fixedConstraints[key] = [value]
            
    return SearchConfig(facetProfile, fixedConstraints, searchService,
                        profile.replicaSearchFlag, profile.latestSearchFlag, profile.localSearchFlag)
    
@user_passes_test(lambda u: u.is_staff)
@require_http_methods (["POST"])
def search_profile_export(request, project_short_name):

    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # security check
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)

    scp = SearchConfigParser(project)
    try:
        scp.write()
        message = 'search_config_exported'
    except Exception as e:
        log.error("ERROR: %s" % str(e))
        message = e       

    return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()])+"?message=%s" % message)

@user_passes_test(lambda u: u.is_staff)
@require_http_methods (["POST"])
def search_profile_import(request, project_short_name):

    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # security check
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    scp = SearchConfigParser(project)
    try:
        scp.read()
        message = 'search_config_imported'
    except Exception as e:
        log.error("ERROR: %s" % str(e))
        message = 'search_config_not_found'        

    return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()])+"?message=%s" % message)

@login_required
def search_profile_config(request, project_short_name):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # retrieve ordered list of search groups and facets
    search_groups = _get_search_groups(project)
    
    # security check
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)

    if request.method == 'GET':
        # retrieve project search profile
        try:
            profile = project.searchprofile
        # or create a new one
        except ObjectDoesNotExist:
            profile = create_project_search_profile(project)
            
        form = SearchProfileForm(instance=profile)
            
        return render_search_profile_form(request, project, form, search_groups)
        
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
            return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()]))
            
        else:
            log.debug('Form is invalid: %s' % form)
            return render_search_profile_form(request, project, form, search_groups)
            

def _queryFacets(request, project):
    """Executes a query for all available facets for a given project."""
    
    searchConfig = _getSearchConfig(request, project)
    # build input from HTTP parameters
    searchInput = _buildSearchInputFromHttpRequest(request, searchConfig)
    searchInput.limit = 0  # no results
    # add project fixed constraints
    _searchInput = _addConfigConstraints(searchInput, searchConfig)
    _searchInput.printme()
    searchService = searchConfig.searchService
    (url, xml) = searchService.search(_searchInput, allFacets=True)  # uses facets='*'
    searchOutput = deserialize(xml, searchConfig.facetProfile)
    #searchOutput.printme()
    
    return searchOutput.facets
    

# method to add a new facet
@login_required
def search_facet_add(request, project_short_name):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # security check
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if request.method == 'GET':

        # retrieve list of available facets by executing project-specific query
        facets = _queryFacets(request, project)
        
        # create default search group, if not existing already
        group = get_or_create_default_search_group(project)
        
        # assign facet to default search group
        order = group.size()
        facet = SearchFacet(order=order, group=group)
        form = SearchFacetForm(project, instance=facet)    
        
        return render_search_facet_form(request, project, form, facets)
        
    else:
        form = SearchFacetForm(project, request.POST)
        
        if form.is_valid():            
            facet = form.save()
            return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()])) 
        
        else:     
            log.debug('Form is invalid: %s' % form.errors)
            
            # must retrieve facets again
            facets = _queryFacets(request, project)
            
            return render_search_facet_form(request, project, form, facets)
        
@login_required
def search_group_add(request, project_short_name):
    '''View to add a search facet group.'''
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # security check
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if request.method == 'GET':

        search_profile = project.searchprofile
        order = len(search_profile.groups.all())

        form = SearchGroupForm(initial={'profile':search_profile, 'order':order, 'name':'' })
        return render_search_group_form(request, project, form)

    else:
        
        form = SearchGroupForm(request.POST)
        
        if form.is_valid():            
            form.save()
            return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()])) 
        
        else:     
            log.debug('Form is invalid: %s' % form.errors)
                        
            return render_search_group_form(request, project, form)

# method to update an existing search facet group
@login_required
def search_group_update(request, group_id):
    
    # retrieve group from database
    group = get_object_or_404(SearchGroup, pk=group_id)
       
    # security check
    project = group.profile.project
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
        
    if request.method == 'GET':
        form = SearchGroupForm(instance=group)    
        return render_search_group_form(request, project, form)
        
    else:
        
        form = SearchGroupForm(request.POST, instance=group)
        
        if form.is_valid():            
            group = form.save()
            return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()])) 
        
        else:     
            log.debug('Form is invalid: %s' % form.errors)
            return render_search_group_form(request, project, form)


# method to update an existing facet
@login_required
def search_facet_update(request, facet_id):
    
    # retrieve facet from database
    facet = get_object_or_404(SearchFacet, pk=facet_id)
       
    # security check
    project = facet.group.profile.project
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # retrieve list of available facets by executing project-specific query
    facets = _queryFacets(request, project)
    
    if request.method == 'GET':
        form = SearchFacetForm(project, instance=facet)    
        return render_search_facet_form(request, project, form, facets)
        
    else:
        
        form = SearchFacetForm(project, request.POST, instance=facet)
        
        if form.is_valid():            
            facet = form.save()
            return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()])) 
        
        else:     
            log.debug('Form is invalid: %s' % form.errors)
            return render_search_facet_form(request, project, form, facets)


@login_required
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
        
    # redirect to search profile configuration page (GET-POST-REDIRECT)
    return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()]))

@login_required
def search_group_delete(request, group_id):
         
    # retrieve group from database
    group = get_object_or_404(SearchGroup, pk=group_id)
        
    # retrieve associated project
    project = group.profile.project
    
    # security check
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
        
    # delete all facets in this group
    for facet in group.facets.all():
        facet.delete()
    
    # delete group
    group.delete()
    
    # re-order all groups in this project
    groups = SearchGroup.objects.filter(profile__project=project).order_by('order')
    count = 0
    for group in groups:
        group.order = count
        group.save()
        count += 1
        
    # redirect to search profile configuration page (GET-POST-REDIRECT)
    return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()]))

def search_files(request, dataset_id, index_node):
    """View that searches for all files of a given dataset, and returns the response as JSON"""
    
    # maximum number of files to query for
    limit = request.GET.get('limit', 20)
            
    params = [('type', "File"), ('dataset_id', dataset_id),
              ("format", "application/solr+json"), ('offset', '0'), ('limit', limit)]
    
    # optional query filter
    query = request.GET.get('query', None)
    if query is not None and len(query.strip()) > 0:
        # validate query value
        for c in INVALID_CHARACTERS:
            if c in query:
                # HttpResponseBadRequest Status Code = 400
                return HttpResponseBadRequest(ERROR_MESSAGE_INVALID_TEXT, content_type="text/plain")
        params.append(('query', query))
        
    # optional shard
    shard = request.GET.get('shard', '')
    if shard is not None and len(shard.strip()) > 0:
        params.append(('shards', shard+"/solr"))  # '&shards=localhost:8982/solr'
    else:
        params.append(("distrib", "false"))
 
    url = "http://"+index_node+"/esg-search/search?"+urllib.urlencode(params)
    log.debug('Searching for files: URL=%s' % url)
    fh = urllib2.urlopen(url)
    response = fh.read().decode("UTF-8")

    return HttpResponse(response, content_type="application/json")


def search_reload(request):
    """View that attempts to redirect to the last project-specific page,
       including constraints and results."""
    
    if request.session.get(LAST_SEARCH_URL, None):
        log.debug('Reloading search page: %s' % request.session[LAST_SEARCH_URL])
        request.session[SEARCH_REDIRECT] = True  # flag to retrieve constraints, results
        return HttpResponseRedirect(request.session[LAST_SEARCH_URL])  # just like after the last POST
        
    else:
        return render(request,
                      'cog/common/message.html', 
                      {'mytitle': 'An Error Occurred',
                       'messages': ['Your last search page could not be found.']})

def _get_search_groups(project):
    '''
    Builds a copy of the project search groups and facets 
    so their order can be changed without being persisted to the database.
    '''
    
    search_groups = OrderedDict()
    for group in project.searchprofile.groups.all().order_by('order'):
        search_groups[group] = list( group.facets.all().order_by('order') )
        
    return search_groups
    
@login_required
def search_profile_order(request, project_short_name):
    
    # must reflect name of select widgets in search_order_form.html
    SEARCH_GROUP_KEY = "group_name_"
    SEARCH_FACET_KEY = "_facet_key_"
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
            
    # check permission
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
        
    # current list of search groups
    groups = _get_search_groups(project)
    
    # GET
    if request.method == 'GET':
        
        return render(request,
                      'cog/search/search_order_form.html',
                      {'project': project, 
                       'groups': groups,
                       'title': 'Order Search Facets and Groups',
                       'errors':{} })

    # POST
    else:
        
        # map (group, new group order)
        groupOrderMap = {} 
        valid = True  # form data validation flag
        errors = {} # form validation errors
        
        for group, facets in groups.items():
                        
            group_key = SEARCH_GROUP_KEY + str(group.name)
            group_order = request.POST[group_key]
            group.order = int(group_order) # reassign the group orde WITHOUT saving to the database for now
            # validate group order
            if group_order in groupOrderMap.values():
                valid = False
                errors[group_key] = "Duplicate search facet number: %d" % int(group_order)
            else:
                groupOrderMap[group_key] = group_order
                
            facetOrderMap = {}
            for facet in facets:
                
                facet_key = group_key + SEARCH_FACET_KEY + str(facet.key)
                facet_order = request.POST[facet_key]
                facet.order = facet_order
                # validate facet order within this group
                if facet_order in facetOrderMap.values():
                    valid = False
                    errors[facet_key] = "Duplicate facet number: %d" % int(facet_order)
                else:
                    facetOrderMap[facet_key] = facet_order
                
        # form data is valid              
        if valid:
            
            # save new ordering for groups, facets
            for group, facets in groups.items():
                group.save()
                for facet in facets:
                    facet.save()
                            
            # redirect to search profile configuration (GET-POST-REDIRECT)
            return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()]))

        else:
            # return to form to fix validation errors
            return render(request,
                          'cog/search/search_order_form.html', 
                          {'project': project, 
                           'groups': groups,
                           'title': 'Order Search Facets and Groups', 
                           'errors':errors })
            
def render_search_profile_form(request, project, form, search_groups):
    return render(request,
                  'cog/search/search_profile_form.html', 
                  {'project': project, 
                   'form': form, 
                   'search_groups':search_groups,
                   'title': 'Project Search Configuration'})
    

def render_search_facet_form(request, project, form, facets):
    return render(request,
                  'cog/search/search_facet_form.html', 
                  {'project': project, 'form': form, 'title': 'Search Facet Configuration', 'facets': facets})

def render_search_group_form(request, project, form):
    return render(request,
                  'cog/search/search_group_form.html', 
                  {'project': project, 'form': form, 'title': 'Search Facet Group'})

def citation_display(request):

    # get citation info in json format
    url = request.GET.get('url', '')

    try:
        fh = urllib2.urlopen(url)
        response = fh.read()
        headers = fh.info().dict
    except HTTPError as e:
        log.debug('HTTPError %s for %s' % (str(e.code), url))
        return HttpResponseNotFound()

    if int(headers['x-cera-rc']) > 0:
        log.debug('Citation not found: %s' % url)
        return HttpResponseNotFound()

    try:
        json.loads(response)
    except ValueError as e:
        log.errpr('Citation not valid json: %s' % str(e))
        return HttpResponseNotFound()

    return HttpResponse(response, content_type="application/json")
