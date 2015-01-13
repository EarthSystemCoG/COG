'''
Module containing forms for CoG forum.

@author: cinquini
'''

from django.forms import ModelForm
from cog.models.forum import ForumThread
from cog.utils import default_clean_field
from django.forms import Form, TextInput, Textarea, CharField

class ForumThreadForm(ModelForm):
    
    def clean_title(self):
        return default_clean_field(self, 'title')
    
    class Meta:
        model = ForumThread
        fields = ('title', 'is_private')
        
class MyCommentForm(Form):
    
    text = CharField(required=True, widget=Textarea(attrs={'rows':'10'}))