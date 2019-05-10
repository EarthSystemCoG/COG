from xml.etree.ElementTree import Element, ElementTree, SubElement, tostring, fromstring
from cog.models.search import SearchOutput, Record, Facet, FacetProfile

import logging

log = logging.getLogger(__name__)

# function that serializes a SearchOutput object into Solr XML
def serialize(input, output):
    
    # <response>
    responseEl = Element("response")
    
    # <result name="response" numFound="6" start="0" maxScore="1.0">
    resultEl = SubElement(responseEl, "result", attrib={ "name": "response", "numFound": str(output.counts), 
                                                     "start":str(input.offset), "maxScore":"1.0" })
    
    # loop over results
    for record in output.results:
        # <doc>
        docEl = SubElement(resultEl, "doc") 
        # <str name="id">obs4cmip5.NASA-JPL.AQUA.AIRS.mon</str>
        strEl = SubElement(docEl, "str", attrib={ "name":"id" } )
        strEl.text = record.id
        
        for key, values in record.fields.items():
            # <str name="type">Dataset</str>
            # single-valued fields (as from Solr schema)
            if key == 'url' or key=='type':
                strEl = SubElement(docEl, "str", attrib={ "name":key } )
                strEl.text = values[0]
            # <arr name="title"><str>AIRS L3 Monthly Data</str></arr>
            # multi-valued fields (as from Solr schema)
            else:
                arrEl = SubElement(docEl, "arr", attrib={ "name": key })
                for value in values:
                    strEl = SubElement(arrEl, "str")
                    strEl.text = value
               
    # <lst name="facet_counts">
    #     <lst name="facet_queries"/>
    #     <lst name="facet_fields">
    facetCountsEl  = SubElement(responseEl,    "lst", attrib={ "name": "facet_counts" })
    facetQueriesEl = SubElement(facetCountsEl, "lst", attrib={ "name": "facet_queries" })
    facetFieldsEl  = SubElement(facetCountsEl, "lst", attrib={ "name": "facet_fields" })
    
    # loop over facets
    for key, facet in output.facets.items():
        facetEl = SubElement(facetFieldsEl, "lst", attrib={ "name": key })
        for value, counts in facet.getValues().items():
            facetSubEl = SubElement(facetEl, "int", attrib={ "name": value })
            facetSubEl.text = str(counts)
    
    xml = tostring(responseEl, encoding="UTF-8")
    return xml

# function that deserializes Solr XML into objects
def deserialize(xml, facetProfile):
    
    output = SearchOutput()
        
    try:
    
        # <response>
        responseEl = fromstring(xml)
        
        # <result name="response" numFound="6" start="0" maxScore="1.0">
        for resultEl in responseEl.findall("result"):
            if resultEl.get("name", None)=='response':
                output.counts = int(resultEl.get("numFound", default=-1))
                
                # loop over results
                # <doc>
                #    <float name="score">1.0</float>
                #    <arr name="cf_variable"><str>Specific Humidity</str><str>Air Temperature</str></arr>
                #    <arr name="cmor_table"><str>Amon_obs</str></arr>
                #    <str name="id">obs4cmip5.NASA-JPL.AQUA.AIRS.mon</str>
                for docEl in resultEl.findall("doc"):
                    record = Record("") # no id yet
                    for subEl in docEl.findall("*"):
                        name = subEl.get("name", None)
                        if name=='id':
                            record.id = subEl.text
                        else:
                            # encode multiple values
                            if subEl.tag=='arr':
                                for child in list(subEl):
                                    _encode_field_value(record, name, child.text)
                            # encode single value
                            else:
                                _encode_field_value(record, name, subEl.text)
                    output.results.append(record)
            
        # loop over facets
        # <lst name="facet_counts">
        #     <lst name="facet_queries"/>
        #     <lst name="facet_fields">
        #         <lst name="cf_variable">
        #             <int name="Air Temperature">4</int>
        #             <int name="Mole Fraction of O3">2</int>
        #             <int name="Specific Humidity">2</int>
        #        </lst>
        for lstEl in responseEl.findall("lst"):
            if lstEl.get("name", None)=='facet_counts':
                for subLstEl in lstEl.findall("lst"):
                    if subLstEl.get("name", None)=='facet_fields':
                        for subSubLstEl in subLstEl.findall("lst"):
                            key = subSubLstEl.get("name", None)
                            try:                                
                                label = facetProfile.getLabel(key)
                                facet = Facet(key, label)
                                for intEl in subSubLstEl.findall("int"):
                                    value = intEl.get("name", None)
                                    counts = int( intEl.text )
                                    facet.addValue(value, counts) 
                                output.setFacet(facet)
                            except KeyError:
                                pass
                            
        
    except (ValueError, LookupError) as err:
        log.error("Error: %s" % str(err))
    return output

def _encode_field_value(record, name, value):
    
    if value is not None and len(value.strip())>0 and value.lower() != 'none':
                        
        parts = value.strip().split('|')
        
        # field encoded as URL triple: 'url'=(url, mimeType, serviceName) or 'xlink'=(url, text, 'summary')
        # Examples:
        # url = http://hydra.fsl.noaa.gov/thredds/esgcet/1/oc_gis_downscaling.bccr_bcm2.sresa1b.Prcp.v2.xml#oc_gis_downscaling.bccr_bcm2.sresa1b.Prcp.v2|application/xml+thredds|Catalog
        # url = http://hydra.fsl.noaa.gov/las/getUI.do?catid=C08322CA3EF1E2FEA6B02184320B3A6F_ns_oc_gis_downscaling.bccr_bcm2.sresa1b.Prcp.v2|application/las|LAS
        # xlink = https://vesg.ipsl.polytechnique.fr/thredds/fileServer/obs4MIPs_dataroot/obs-CFMIP/TechnicalNotes/CFMIP_CALIPSO_GOCCP.pdf|CALISPO-GOCCP Technical Notes|summary
        if len(parts)==3:
            # special processing
            if name=='url':
                [url, mimeType, serviceName] = parts[:]
                if mimeType=='application/xml+thredds':
                    # replace THREDDS XML URL with THREDDS HTML URL        
                    record.addField(name, (url.replace('xml','html'),  'application/html+thredds', serviceName) )
                else:
                    record.addField(name, (url, mimeType, serviceName))
            elif name=='xlink':
                # NOTE: 'xlink' metadata is renamed to 'url' metadata
                if parts[2] == 'pid':
                    record.addField('url', (parts[0], 'application/pid', 'PID'))
                elif parts[2] == 'citation':
                    record.addField('url', (parts[0], 'application/citation', 'Citation'))
                elif parts[2] == 'technote':
                    record.addField('url', (parts[0], 'application/pdf', 'Tech Note'))
                elif parts[2] == 'supdata':
                    record.addField('url', (parts[0], 'application/zip', 'Supplementary Data'))
                else:
                    record.addField('url', (parts[0], 'application/octet-stream', parts[2])) # default
            else:
                # default triple encoding
                record.addField(name, parts) # store full URL triple in list of values
                
        # field encoded as single string
        else:
            record.addField(name, value.strip())  

    