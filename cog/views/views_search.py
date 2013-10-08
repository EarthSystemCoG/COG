from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from cog.forms.forms_search import *
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.utils import simplejson 
import urllib, urllib2


from cog.views.constants import PERMISSION_DENIED_MESSAGE
from cog.services.search import SolrSearchService, TestSearchService
from cog.models.search import SearchOutput, Record, Facet, FacetProfile
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from copy import copy, deepcopy
from urllib2 import HTTPError

from cog.models.search import *
from cog.services.search import TestSearchService, SolrSearchService
from cog.services.SolrSerializer import deserialize

from cog.templatetags.search_utils import displayMetadataKey, formatMetadataKey
from cog.models.utils import get_or_create_default_search_group


SEARCH_INPUT = "search_input"
SEARCH_OUTPUT = "search_output"
FACET_PROFILE = "facet_profile"
ERROR_MESSAGE = "error_message"
SEARCH_DATA = "search_data"
SEARCH_PAGES = "search_pages"

# singleton instance - instantiated only once
testSearchService = TestSearchService()

# method to configure the search on a per-request basis
def getTestSearchConfig(request):
    """
    Example of search configuration method that ties into a test search service and associated facets,
    and sets one fixed constraint.
    """
        
    facetProfile = FacetProfile([ 
                                 #('project','Project'),
                                 ('model','Model'),
                                 ('experiment','Experiment'),
                                 ('instrument','Instrument'),
                                 ])
    fixedConstraints = { 'project': ['Test Project'], }
    
    return SearchConfig(facetProfile, fixedConstraints, testSearchService)

#def search(request):
    """
    Default view entry point that configures the search with a test search configuration.
    """
    
#    config = getTestSearchConfig(request)
#    return search_config(request, config)

def search_config(request, searchConfig, extra={}):
    """
    View entry point for applications that need to provide their own
    per-request search configuration.
    """
    
    # print extra arguments
    for key, value in extra.items():
        print 'extra key=%s value=%s' % (key,value)
    
    # populate input with search constraints from HTTP request
    input = SearchInput()
    for facetGroup in searchConfig.facetProfile.facetGroups:
        for key in facetGroup.getKeys():
            if (request.REQUEST.get(key, None)):
                for value in request.REQUEST.getlist(key):
                    if value:
                        input.addConstraint(key, value)
    
    # add fixed constraints - override previous values
    for key, values in searchConfig.fixedConstraints.items():
            input.setConstraint(key, values)
    
    # text
    if request.REQUEST.get('text', None):
        input.text = request.REQUEST['text']
    # type
    if request.REQUEST.get('type', None):
        input.type = request.REQUEST['type']
    # offset, limit
    if request.REQUEST.get('offset', 0):
        input.offset = int(request.REQUEST['offset'])
        print 'OFFSET=%s' % input.offset
    if request.REQUEST.get('limit', 0):
        input.limit = int(request.REQUEST['limit'])
        print 'LIMIT=%s' % input.limit
        
    # GET/POST switch
    print "HTTP Request method=%s" % request.method
    if (request.method=='GET'):
        return search_get(request, input, searchConfig.facetProfile, searchConfig.searchService, extra)
    else:
        return search_post(request, input, searchConfig.facetProfile, searchConfig.searchService, extra)
        
def search_get(request, searchInput, facetProfile, searchService, extra={}):
    
    #data = {}
    # pass on all the extra arguments
    data = extra
    
    # after POST redirection
    if (request.GET.get(SEARCH_DATA)):
        print "Retrieving search data from session"
        data = request.session.get(SEARCH_DATA, None)
        if data.get(ERROR_MESSAGE,None):
            print "Found Error=%s" % data[ERROR_MESSAGE]
    
    # first GET invocation
    else:
        
        # set retrieval of all facets in profile
        searchInput.facets = facetProfile.getAllKeys()
        
        # execute query for facets
        #searchOutput = searchService.search(searchInput, False, True)
        try:
            xml = searchService.search(searchInput, False, True)
            searchOutput = deserialize(xml, facetProfile)
            #FIXME
            #searchOutput.printme()
            
            data[SEARCH_INPUT] = searchInput
            data[SEARCH_OUTPUT] = searchOutput
            data[FACET_PROFILE] = facetProfile
            #data[FACET_PROFILE] = sorted( facetProfile.getKeys() ) # sort facets by key
            data['title'] = 'Advanced Data Search'
            
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
        
    return render_to_response('cog/search/search.html', data, context_instance=RequestContext(request))    

def metadata_display(request, project_short_name):
    
    project = request.GET.get('project', None)
    id = request.GET.get('id', None)
    dataset_id = request.GET.get('dataset_id', None)
    type = request.GET.get('type', None)
    subtype = request.GET.get('subtype', None)
    index_node = request.GET.get('index_node', None)
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    config = getSearchConfig(request, project)

    # retrieve result metadata
    params = [ ('type', type), ('id', id), ("format", "application/solr+json"), ("distrib", "false") ]
    if type == 'File':
        params.append( ('dataset_id', dataset_id) )
                
    url = "http://"+index_node+"/esg-search/search?"+urllib.urlencode(params)
    print 'Solr search URL=%s' % url
    fh = urllib2.urlopen( url )
    response = fh.read().decode("UTF-8")
    #return HttpResponse(response, mimetype="application/json")

    # parse JSON response (containing only one matching 'doc)
    json = simplejson.loads(response)
    metadata = _processDoc( json["response"]["docs"][0] )

    # retrieve parent metadata    
    parentMetadata = {}
    if type == 'File':
        params = [ ('type', 'Dataset'), ('id', dataset_id), ("format", "application/solr+json"), ("distrib", "false") ]
        url = "http://"+index_node+"/esg-search/search?"+urllib.urlencode(params)
        #print 'Solr search URL=%s' % url
        fh = urllib2.urlopen( url )
        response = fh.read().decode("UTF-8")
        json = simplejson.loads(response)
        parentMetadata = _processDoc( json["response"]["docs"][0] )
    
    return render_to_response('cog/search/metadata_display.html', 
                              {'title':metadata.title, 'project' : project, 'metadata':metadata, 'parentMetadata':parentMetadata }, 
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
    
    
def search_post(request, searchInput, facetProfile, searchService, extra={}):
    
    # valid user input
    if (searchInput.isValid()):
        
        # set retrieval of all facets in profile
        searchInput.facets = facetProfile.getAllKeys()
    
        # execute query for results, facets
        #searchOutput = searchService.search(searchInput, True, True)
        try:
            xml = searchService.search(searchInput, True, True)
            searchOutput = deserialize(xml, facetProfile)
            #searchOutput.printme()
            
            # initialize new session data from extra argument dictionary
            data = extra
            data[SEARCH_INPUT] = searchInput
            data[SEARCH_OUTPUT] = searchOutput
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
        data[ERROR_MESSAGE] = "Error: search text cannot contain any of the characters: %s" % INVALID_CHARACTERS;
         
    # store data in session 
    data['title'] = 'Advanced Data Search'
    request.session[SEARCH_DATA] = data
    
    # use POST-REDIRECT-GET pattern with additional parameter "?search_data"
    #return HttpResponseRedirect( reverse('cog_search')+"?%s=True" % SEARCH_DATA )
    return HttpResponseRedirect( request.path+"?%s=True" % SEARCH_DATA )




# Note: all the facets available through the REST API are defined by the Search Services and returned by an unbound query
# Each client application (such as this controller) is responsible for using a sub-set of these facets, and providing appropriate labels
# (labels could be provided by the REST API, but there is no Solr schema for encoding the information)
"""
facetProfile = FacetProfile([ 
                             ('project','Data Project'),
                             ('model','Model'),
                             ('experiment','Experiment'),
                             ('cf_variable','CF Standard Name'), 
                             ('resolution','Resolution'), 
                             #'institute':'Institute', 
                              #'instrument':'Instrument', 
                              #'obs_project':'Mission', 
                              #'obs_structure':'Data Structure',
                              #'obs_type':'Measurement Type',
                              #'product':'Product', 
                              #'time_frequency':'Time Frequency',
                              #'realm':'Realm',  
                             ('variable','Variable'),
                           ])
"""


# method to configure the search on a per-request basis
def getSearchConfig(request, project):
    
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
    # FIXME
    #facetGroup = FacetGroup(facets,'My Facets')
    facetProfile = FacetProfile(facet_groups)
    #facetProfile = FacetProfile( list(profile.searchgroup_set.all()) )
    
    # configure fixed search constraints
    # fixedConstraints = { 'project': ['dycore_2009'], } 
    fixedConstraints = {}   
    if project.searchprofile.constraints:
        constraints = project.searchprofile.constraints.split(',')
        for constraint in constraints:
            (key,value) = constraint.strip().split('=')
            try:
                fixedConstraints[key].append(value)
            except KeyError:
                fixedConstraints[key] = [value]
            
    # How to use TestSerachService instead
    #searchService = TestSearchService()
    #facets = []
    #for key, facet in searchService.myfacets.items():
    #    facets.append((facet.key,facet.label))

    return SearchConfig(facetProfile, fixedConstraints, searchService)
                
def search(request, project_short_name):
    """
    COG-specific search-view that configures the back-end search engine on a per-project basis.
    """
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    config = getSearchConfig(request, project)

    if config:        
        config.printme()
        # pass on project as extra argument to search
        return search_config(request, config, extra = {'project' : project} )
    # search is not configured for this project
    else:
        messages = ['Searching is not enabled for this project.',
                    'Please contact the project administrators for further assistance.']
        return render_to_response('cog/common/message.html', {'project' : project, 'messages':messages }, context_instance=RequestContext(request))

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
            

    
# method to add a new facet
def search_facet_add(request, project_short_name):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # security check
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if request.method=='GET': 
        
        # create default search group, if not existing already
        group = get_or_create_default_search_group(project)
        
        # assign facet to default search group
        order = group.size()
        facet = SearchFacet(order=order, group=group)
        form = SearchFacetForm(instance=facet)    
        
        return render_search_facet_form(request, project, form)
        
    else:
        form = SearchFacetForm(request.POST)
        
        if form.is_valid():            
            facet = form.save()
            return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()])) 
        
        else:     
            print 'Form is invalid: %s' % form.errors
            return render_search_facet_form(request, project, form)
        
# method to update an existing facet
def search_facet_update(request, facet_id):
    
    # retrieve facet from database
    facet = get_object_or_404(SearchFacet, pk=facet_id)
       
    # security check
    project = facet.group.profile.project
    if not userHasAdminPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if request.method=='GET':    
        form = SearchFacetForm(instance=facet)    
        return render_search_facet_form(request, project, form)
        
    else:
        
        form = SearchFacetForm(request.POST, instance=facet)
        
        if form.is_valid():            
            facet = form.save()
            return HttpResponseRedirect(reverse('search_profile_config', args=[project.short_name.lower()])) 
        
        else:     
            print 'Form is invalid: %s' % form.errors
            return render_search_facet_form(request, project, form)

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
    
    params = [ ('type',"File"), ('dataset_id',dataset_id), ("format", "application/solr+json"), ("distrib", "false") ]
 
    url = "http://"+index_node+"/esg-search/search?"+urllib.urlencode(params)
    #print 'Solr search URL=%s' % url
    fh = urllib2.urlopen( url )
    response = fh.read().decode("UTF-8")

    return HttpResponse(response, mimetype="application/json")

            
def render_search_profile_form(request, project, form):
    return render_to_response('cog/search/search_profile_form.html', 
                              {'project' : project, 'form':form, 'title':'Project Search Configuration' }, 
                               context_instance=RequestContext(request))
    
def render_search_facet_form(request, project, form):
    return render_to_response('cog/search/search_facet_form.html', 
                              {'project' : project, 'form':form, 'title':'Search Facet Configuration' }, 
                              context_instance=RequestContext(request))