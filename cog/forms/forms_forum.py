'''
Module containing forms for CoG forum.

@author: cinquini
'''

from django.forms import ModelForm
from cog.models.forum import ForumThread

class ForumThreadForm(ModelForm):
    
    class Meta:
        model = ForumThread
        fields = ('title', 'is_private')
