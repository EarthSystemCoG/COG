import urllib, urllib2
from string import join

# search service that queries a Solr server through the ESGF RESTful search API
class SolrSearchService:
    
    def __init__(self, url, facets):
        self.url = url
        self.facets = facets
    
    def search(self, input):
        
        # debug
        input.printme()
        
        # Note: use sequence of 2-tuples to allow for multiple values
        params = [ ('offset',input.offset), ('limit',input.limit) ]
        if input.text:
            params.append( ('query', input.text.strip()) )
        if input.type:
            params.append( ('type', input.type) )
        if not input.replica: # service default: replica=True+False
            params.append( ('replica', "false") )
        if input.latest:      # service default: latest=True+False
            params.append( ('latest', "true") )
        if input.local: # service default: distrib='true'
            params.append( ('distrib', "false") )
        for key, values in input.constraints.items():
            for value in values:
                params.append( (key, value) )

        # explicitely request counts for all configured facets (or used "*")
        #params.append( ("facets", "*") )
        if len(self.facets)>0:
            facetlist = join([facet.key for facet in self.facets], ',')
            params.append( ("facets", facetlist) )
                
        url = self.url+"?"+urllib.urlencode(params)
        print 'Solr search URL=%s' % url
        fh = urllib2.urlopen( url )
        xml = fh.read().decode("UTF-8")
   
        return xml