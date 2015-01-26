'''
Module containing forms for CoG forum.

@author: cinquini
'''

from django.forms import ModelForm
from cog.models.forum import ForumThread, ForumTopic
from cog.utils import default_clean_field
from django.forms import Form, TextInput, Textarea, CharField

class ForumTopicForm(ModelForm):
    
    #def clean_title(self):
    #    return default_clean_field(self, 'title')
    
    #def clean_description(self):
    #    return default_clean_field(self, 'description')
    
    class Meta:
        model = ForumTopic
        fields = ('title', 'description', 'is_private')
        widgets = {'description': Textarea(attrs={'rows':3}) }

class ForumThreadForm(ModelForm):
    
    #def clean_title(self):
    #    return default_clean_field(self, 'title')
    
    class Meta:
        model = ForumThread
        fields = ('topic','title',)
        
class MyCommentForm(Form):
    
    text = CharField(required=True, widget=Textarea(attrs={'class': 'ckeditor'}))