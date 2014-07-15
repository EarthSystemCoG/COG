from random import choice
import urllib, urllib2
from string import join
from cog.models.search import SearchOutput, Record, Facet, FacetProfile
from cog.services.SolrSerializer import serialize

# search service that queries a Solr server through the ESGF RESTful search API
class SolrSearchService:
    
    def __init__(self, url, facets):
        self.url = url
        self.facets = facets
    
    def search(self, input, doResults, doFacets):
        
        # debug
        input.printme()
        
        # Note: use sequence of 2-tuples to allow for multiple values
        params = [ ('offset',input.offset), ('limit',input.limit) ]
        if input.text:
            params.append( ('query', input.text.strip()) )
        if input.type:
            params.append( ('type', input.type) )
        if not input.replica: # service default: replica='false'
            params.append( ('replica', "false") )
        if input.latest:      # service default: no 'latest' specified
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
        # FIXME
        #print xml
        return xml

# Test search service that acts on a simulated pool of records
class TestSearchService:
    
    NUM_RECORDS = 40
    
    # initialization method generated the records and facets
    def __init__(self):
       
        # initialize facets
        self.myfacets = {} # (facet key, facet)
        
        projectFacet = Facet('project','Project')
        projectFacet.addValue('Test Project')
        self.myfacets[projectFacet.key] = projectFacet

        modelFacet = Facet('model','Model')
        modelFacet.addValue('GFDL CM 2.0')
        modelFacet.addValue('INCM4')
        self.myfacets[modelFacet.key] = modelFacet
        
        instrumentFacet = Facet('instrument','Instrument')
        instrumentFacet.addValue('AIRS')
        instrumentFacet.addValue('MLS')
        self.myfacets[instrumentFacet.key] = instrumentFacet
              
        experimentFacet = Facet('experiment','Experiment')
        experimentFacet.addValue('Experiment #1')
        experimentFacet.addValue('Experiment #2')
        self.myfacets[experimentFacet.key] = experimentFacet
                    
        # initialize records
        self.myrecords = []
        for i in range(1, self.NUM_RECORDS+1):
            record = Record("record.id.%d" % i)
            record.addField('url', 'http://localhost/record_%s' % i)
            record.addField('title', 'This is record # %s' % i)
            record.addField('description', 'This is a long description for record #%s' % i)
            record.addField('type', 'Dataset')
            
            # assign records to facets
            for facet in self.myfacets.values():
                value = choice(facet.getValues().keys())
                record.addField(facet.key, value)
                # increase facet count
                facet.addCount(value)
                
            self.myrecords.append(record)
                        
    def matches(self, record, input):
        
        if input.isEmpty():
            return True
        
        # record must match at least one of the constraint values
        #record.printme()
        #input.printme()
        for key, values in input.constraints.items():
            found = False
            for value in values:
                if value in record.fields[key]:
                    found = True
            if not found:
                return False
        
        # record fields must match text in case-insensitive comparison
        if input.text:
            ltext = input.text.lower()
            print 'input query=%s' % ltext
            found = False
            for values in record.fields.values():
                for value in values:
                    parts = value.lower().split()
                    if ltext in parts:
                        found = True
            if not found:
                return False
            
        return True
            
    def search(self, input, doResults, doFacets):
        
        # debug
        input.printme()

        output = SearchOutput()
        
        # copy facet hierarchy
        for key, facet in self.myfacets.items():
            _facet = Facet(facet.key, facet.label)
            # facet was constrained
            if key in input.constraints.keys():
                for value in input.constraints[key]:
                    _facet.addValue(value)
            # facet was not constrained     
            else:
                for value in facet.getValues().keys():
                    _facet.addValue(value)
            output.setFacet( _facet )
                        
        # loop over all records
        nmatches = 0
        for record in self.myrecords:    
           
            if self.matches(record, input):
                nmatches = nmatches + 1
                if nmatches>input.offset and nmatches<=input.offset+input.limit:
                    # add this record to the returned results
                    output.results.append(record)
            
                # count the facets
                for key, values in record.fields.items():
                    if key != 'url' and key != 'description' and key != 'title' and key!= 'type':
                        facet = output.facets[key]
                        for value in values: 
                            facet.addCount(value)                        
               
        output.counts = nmatches
        #output.printme()
        xml = serialize(input, output)
        return xml
        #return output
