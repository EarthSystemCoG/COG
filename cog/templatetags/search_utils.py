from django import template
from cog.models.search import searchMappings
from string import replace

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
    
@register.filter
def getFacetOptionLabel(facet_key, facet_value):
    """Return the label to be displayed for a given (facet key, facet value) combination, 
       or the facet_value itself if a mapping is not found."""
    label = searchMappings.getFacetOptionLabel(facet_key, facet_value)
    return label.replace("_"," ")

@register.filter 
def displayMetadataKey(key):
    """ Utility function to determine when a metadata field needs to be displayed """
    return (key != 'score' and key != 'index_node' and key != 'data_node' \
            and key != 'dataset_id' and key != 'replica' and key!= 'latest')
 
@register.filter    
def formatMetadataKey(key):
    '''Utility method to format a metadata key before display.'''
    key = key.capitalize()
    return replace(key,'_',' ').title()