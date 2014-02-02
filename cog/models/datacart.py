from django.db import models
from constants import APPLICATION_LABEL
from django.contrib.auth.models import User

class DataCart(models.Model):
    
    # user
    user = models.OneToOneField(User, related_name='datacart')
    
    class Meta:
        app_label= APPLICATION_LABEL
        
class DataCartItem(models.Model):
    
    cart = models.ForeignKey(DataCart, related_name="items", blank=False, null=False)
    identifier =  models.CharField(max_length=200, blank=False, null=False)
    name =  models.CharField(max_length=200, blank=False, null=False)
    type =  models.CharField(max_length=50, blank=False, null=False)
    
    class Meta:
        app_label= APPLICATION_LABEL
