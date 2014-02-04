from django.db import models
from constants import APPLICATION_LABEL
from django.contrib.auth.models import User
from cog.models.search import Record

class DataCart(models.Model):
    
    user = models.OneToOneField(User, related_name='datacart')
    
    class Meta:
        app_label= APPLICATION_LABEL
        
class DataCartItem(models.Model):
    
    cart = models.ForeignKey(DataCart, related_name="items", blank=False, null=False)
    
    # used to enforce uniqueness within a single user datacart
    identifier =  models.CharField(max_length=200, blank=False, null=False)
    
    name =  models.CharField(max_length=200, blank=False, null=False)
    type =  models.CharField(max_length=50, blank=False, null=False)
        
    class Meta:
        app_label= APPLICATION_LABEL
        
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