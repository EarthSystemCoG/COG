from django.db import models
from constants import APPLICATION_LABEL
from django.contrib.auth.models import User
from cog.models.search import Record
from django.utils import simplejson

class DataCart(models.Model):
    
    user = models.OneToOneField(User, related_name='datacart')
    
    def contains(self, item_identifier):
        '''Checks whether the data cart contains an item with the given identifier.'''
        
        return self.items.filter(identifier=item_identifier).exists()
    
    class Meta:
        app_label= APPLICATION_LABEL
        
class DataCartItem(models.Model):
    
    cart = models.ForeignKey(DataCart, related_name="items", blank=False, null=False)
    
    # used to enforce uniqueness within a single user datacart
    identifier =  models.CharField(max_length=200, blank=False, null=False)
    
    # date/time when the item was added
    date = models.DateTimeField('Date Time', auto_now_add=True)
                   
    @staticmethod 
    def fromJson(datacart, id, metadata):
        '''Factory method to create and persist a DataCartItem (and related objects) from JSON metadata.'''
        
        return DataCartItem.create(datacart, id, simplejson.loads(metadata))
                    
    @staticmethod 
    def fromRecord(datacart, record):
        '''Factory method to create and persist a DataCartItem (and related objects) from a search record.'''
        
        return DataCartItem.create(datacart, record.id, record.fields)
    
    @staticmethod 
    def create(datacart, id, metadata):
        '''Factory method to create and persist a DataCartItem (and related objects) from an identifier and a dictionary of metadata fields.'''

        # add item to the cart
        item = DataCartItem(cart=datacart, identifier=id)
        item.save()
        
        # save additional metadata            
        for key, values in metadata.items():
            itemKey = DataCartItemMetadataKey(item=item, key=key)
            itemKey.save()
            for value in values:
                # URL special case: 
                # example: "http://vesg.ipsl.polytechnique.fr/thredds/esgcet/1/obs4MIPs.IPSL.CALIOP.mon.v1.html#obs4MIPs.IPSL.CALIOP.mon.v1|application/html+thredds|Catalog"
                if key=='url':
                    val = "|".join(value)
                else:
                    val = value
                itemValue = DataCartItemMetadataValue(key=itemKey, value=val)
                itemValue.save()
                    
        return item

    def asRecord(self):
        '''Returns this data cart item as a search record object.'''
        
        record = Record(self.identifier)
        
        for keyobj in self.keys.all():
            for valueobj in keyobj.values.all():
                # URL special case
                if keyobj.key == 'url':
                    record.addField(keyobj.key, valueobj.value.split("|") ) # store full URL triple in list of values
                else:
                    record.addField(keyobj.key, str(valueobj.value))
                
        return record        
    
    class Meta:
        app_label= APPLICATION_LABEL

            
    def getValues(self, key):
        
        values = []
        _key = DataCartItemMetadataKey.objects.get(item=self,key=key)
        if _key is not None:
            for _value in  _key.values.all():
                values.append(_value.value)
        
        return values
    
    def getValue(self, key):
        
        values = self.getValues(key)
        if len(values) > 0:
            return values[0]
        else:
            return None

        
class DataCartItemMetadataKey(models.Model):

    item = models.ForeignKey(DataCartItem, related_name='keys', blank=False, null=False)
    key =  models.CharField(max_length=200, blank=False, null=False)
    
    class Meta:
        app_label= APPLICATION_LABEL
    
class DataCartItemMetadataValue(models.Model):

    key = models.ForeignKey(DataCartItemMetadataKey, related_name='values', blank=False, null=False)
    value =  models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        app_label= APPLICATION_LABEL