import urllib, urllib2
from string import join

# search service that queries a Solr server through the ESGF RESTful search API
class SolrSearchService:
    
    def __init__(self, url, facets):
        self.url = url
        self.facets = facets
    
    def search(self, searchInput, allFacets=False):
        
        # debug
        searchInput.printme()
        
        # Note: use sequence of 2-tuples to allow for multiple values
        params = [ ('offset',searchInput.offset), ('limit',searchInput.limit) ]
        if searchInput.query:
            params.append( ('query', searchInput.query.strip()) )
        if searchInput.type:
            params.append( ('type', searchInput.type) )
        if not searchInput.replica: # service default: replica=True+False
            params.append( ('replica', "false") )
        if searchInput.latest:      # service default: latest=True+False
            params.append( ('latest', "true") )
        if searchInput.local: # service default: distrib='true'
            params.append( ('distrib', "false") )
        for key, values in searchInput.constraints.items():
            for value in values:
                params.append( (key, value) )

        # explicitely request counts for all configured facets (or used "*")
        if allFacets:
            params.append( ("facets", "*") )
        else:
            if len(self.facets)>0:
                facetlist = join([facet.key for facet in self.facets], ',')
                params.append( ("facets", facetlist) )
                
        url = self.url+"?"+urllib.urlencode(params)
        print 'ESGF search URL=%s' % url
        fh = urllib2.urlopen( url )
        xml = fh.read().decode("UTF-8")
   
        # return search URL and corresponding results as XML
        return (url, xml)