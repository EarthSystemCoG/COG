from django.db import models
from constants import APPLICATION_LABEL
from django.contrib.auth.models import User
from project_tab import ProjectTab
from datetime import datetime, timedelta

# default lock lifetime: 15 minutes
EXPIRATION_LENGTH_IN_SECONDS = 900 

class Lock(models.Model):
    """Class that represents a lock on a generic object instance."""
    
    object_type = models.CharField(max_length=100, verbose_name='Object Type', blank=False)
    object_id = models.IntegerField(verbose_name='Object Identifier', blank=False)
    timestamp = models.DateTimeField('Last Update Date', auto_now_add=True,  auto_now=True)    
    owner = models.ForeignKey(User, verbose_name='Owner', blank=False)
        
    def __unicode__(self):
        return "Object type=%s id=%s expiration=%s owner=%s" % (self.object_type, self.object_id, self.get_expiration(), self.owner.get_full_name())
    
    def is_expired(self):
        return (datetime.now() - self.timestamp) > timedelta (seconds = EXPIRATION_LENGTH_IN_SECONDS)
    
    def get_expiration(self):
        return self.timestamp + timedelta (seconds = EXPIRATION_LENGTH_IN_SECONDS)
        
    class Meta:
        app_label= APPLICATION_LABEL
        unique_together = (("object_type", "object_id"),)

def getLock(object):
    """Function to return an existing lock on an object, if found."""
        
    try:
        lock = Lock.objects.get(object_type=object.__class__.__name__, object_id=object.id)
        return lock
    except Lock.DoesNotExist:
        return None
    
def isLockedOut(user, lock):
    """Function to check whether a user is locked from accessing a given object."""
    
    if lock is not None and lock.is_expired()==False and lock.owner!=user:
        return True
    else:
        return False
            
def createLock(object, owner):
    """Function to create a new lock, if not existing already and not expired. """
    
    lock = getLock(object)
    
    if lock is None:
        # create new lock
        lock = Lock(object_type=object.__class__.__name__, object_id=object.id, owner=owner)
        lock.save()
        print "Lock created"
        return lock
    
    elif lock.owner == owner:
        # refresh lock
        lock.save()
        print "Lock refreshed"
        return lock
    
    elif lock.is_expired():
        # reassign existing lock
        lock.owner = owner
        lock.save()
        print "Lock reassigned"
        return lock
    
    else:
        print "Lock already existing"
        return None
    
def deleteLock(object):
    """Function to delete an existing lock."""
    
    lock = getLock(object)
    if lock is not None:
        lock.delete()
        print "Lock removed"