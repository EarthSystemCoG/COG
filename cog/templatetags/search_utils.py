from django import template
from cog.models.search import searchMappings
from cog.site_manager import siteManager
from string import replace
import json
from collections import OrderedDict
from django.conf import settings

register = template.Library()

# filter to access a dictionary value by key
@register.filter
def hash(h, key):
    return h.get(key,'')
    
# filter that returns the selection state of a given facet key
@register.filter
def getSelectedState(constraints, key):
    if constraints.get(key, None):
        return 'selected'
    else:
        return ''
        
# returns the list of constraints for a given facet key,
# or the empty array
@register.filter
def getConstraints(constraints, key):
    # example: Constraint key=realm value(s)=[u'atmos,ocean']
    # NOTE: must also add the original value so to match model=CESM1(CAM5.1,FV2)
    try:
        values = str(constraints[key][0])
        if ',' in values:
            return splitValue(values)
        else:
            return [values]
    except KeyError:
        return []
    
def splitValue(value):
    '''Method to split a list of values by comma, but keep intact a string like 'CESM1(CAM5.1,FV2)'.'''
    
    values = value.split(',')
    _values = []
    
    for i, value in enumerate(values):
        
        if i < len(values)-1:
            nextValue = values[i+1]
            if '(' in value and not ')' in value and ')' in nextValue and not '(' in nextValue:
                _values.append(value+","+nextValue)
            elif '[' in value and not ']' in value and ']' in nextValue and not '[' in nextValue:
                i += 1 # skip next value
            elif '{' in value and not '}' in value and '}' in nextValue and not '{' in nextValue:
                i += 1 # skip next value
            else:
                _values.append(value)
        else:
            _values.append(value)
            
    return _values

@register.filter
def getFacetOptionLabel(facet_key, facet_value):
    """Return the label to be displayed for a given (facet key, facet value) combination, 
       or the facet_value itself if a mapping is not found."""
    label = searchMappings.getFacetOptionLabel(facet_key, facet_value)
    return label.replace("_"," ")        

@register.filter 
def displayMetadataKey(key):
    """ Utility function to determine when a metadata field needs to be displayed """
    #return (key != 'score' and key != 'index_node' and key != 'data_node' \
    #        and key != 'dataset_id' and key != 'replica' and key!= 'latest')
    return (key != 'score' and key != 'description' and key != 'title' \
            and key != 'version' and key != '_version_' and key != 'further_info_url' \
            and key != 'url' and key != 'type' and key!= 'replica' and key != 'latest')
 
@register.filter    
def formatMetadataKey(key):
    '''Utility method to format a metadata key before display.'''
    #key = key.capitalize()
    #return replace(key,'_',' ').title()
    return key

@register.filter 
def toJson(record):
    '''Serializes the record metadata fields to JSON format.'''
    
    jsondoc = json.dumps(record.fields)
    return jsondoc

# function to custom order the URLs
def url_order(mtype):
    if mtype=='application/html+thredds':
        return 1
    elif mtype=='application/wget':
        return 2
    elif mtype=='application/las':
        return 3
    else:
        return 4
    
@register.filter
def recordUrls(record):
    '''
    Returns an ordered list of URL endpoints for this record.
    Note: the URL parts must match the values used by _services_js.html.
    '''
    
    urls = []
    
    #record.printme()
        
    # add all existing URL endpoints (THREDDS, LAS etc...)
    if 'url' in record.fields:
        for value in record.fields['url']:
            urls.append(value)
        
    # add special WGET endpoint
    urls.append( ("javascript:wgetScript('%s','%s','%s')" % (record.fields['index_node'][0], record.fields.get('shard', [''])[0], record.id) , 
                  "application/wget", 
                  "WGET Script") )
    
    # add Globus endpoints
    if siteManager.isGlobusEnabled():  # only if this node has been registered with Globus
        if 'access' in record.fields and 'index_node' in record.fields and 'data_node' in record.fields:
            index_node = record.fields['index_node'][0]
            data_node = record.fields['data_node'][0]
            
            for value in record.fields['access']:
            	if value.lower() == 'globus':
                	gurl = '/globus/download?dataset=%s@%s' %(record.id, index_node)
                	if record.fields.get('shard', None):
                		gurl += "&shard="+record.fields.get('shard')[0]
                	urls.append( (gurl, 'application/gridftp', 'GridFTP') )
                	            
    return sorted(urls, key = lambda url: url_order(url[1]))

@register.filter
def supplenoteUrls(record):

    ret = []
    return ret
    
@register.filter
def qcflags(record):
    '''
    Parses the record QC flags metadata into a dictionary indexed by the QC flag type.
    Input:
     "quality_control_flags": [
          "obs4mips_indicators:1:yellow",
          "obs4mips_indicators:2:red"
        ],
    Output:
        {'obs4mips_indicators': OrderedDict([(1, 'yellow'), (2, 'red')])}
    '''
    
    qcflags = {}
    if record.fields.get('quality_control_flags', None):
        for qcflag in record.fields['quality_control_flags']:
            # break up the list item into different parts
            # qcflag="obs4mips_indicators:1:yellow"
            (qcflag_name, qcflag_order, qcflag_value) = qcflag.split(':')
            try:
                qcflags[qcflag_name]
            except KeyError:
                qcflags[qcflag_name] = {}
            qcflags[qcflag_name][int(qcflag_order)] = qcflag_value
    # for each qcflag, sort dictionary of values by their key (i.e. by the QC flag value order)
    for key in qcflags:
        qcflags[key] = OrderedDict(sorted(qcflags[key].items(), key=lambda t: t[0]))
            
    # note: to enable easy access in html template, return the sorted set of (key, value) pairs
    # where the value is itself an ordered dictionary
    return sorted( qcflags.items() )

@register.filter
def qcflag_url(qcflag_name):
    """
    Returns the reference URL for a given quality control flag
    :param key:
    :return:
    """
    qcflag_urls = getattr(settings,'QCFLAGS_URLS', {})
    return qcflag_urls.get(qcflag_name, '') # return empty link by default

@register.filter
def getDataNodeStatus(data_node):

    if not getattr(settings, 'HAS_DATANODE_STATUS', None):
        return True

    try:

        dnstatusfn = getattr(settings, 'DATANODE_STATUS_FILE', None)
        dnstatus = json.load(open(dnstatusfn))
    except Exception as e:
        return True

    if data_node in dnstatus:
        return (dnstatus[data_node]['status'] == 1)
    return True

@register.filter
def sortResults(results, fieldName):
    
    return sorted(results, key = lambda result: result.fields.get(fieldName,""))


@register.filter
def showSearchConfigMessage(message, project):
    
    if message == "search_config_exported":
        return "The project search configuration has been exported to: " + _getProjectSearchConfigFilePath(project)
    
    elif message == "search_config_imported":
        return "The project search configuration has been imported from: " + _getProjectSearchConfigFilePath(project)
    
    elif message == "search_config_not_found":
        return "The project search configuration could not be imported from: " + _getProjectSearchConfigFilePath(project)

    else:
        raise Exception("Invalid Message")

def _getProjectSearchConfigFilePath(project):
    
    return "$MEDIA_ROOT/config/%s/search.cfg" % project.short_name.lower()
