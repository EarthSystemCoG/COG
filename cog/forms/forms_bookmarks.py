from django.forms import Form, ModelForm, CharField
from cog.models import *
from cog.utils import default_clean_field, clean_url_field
from django import forms


class BookmarkForm(ModelForm):
    
    class Meta:
        model = Bookmark
        fields = "__all__" 
        
    # override __init__ method to provide a filtered list of options for the bookmark folder
    def __init__(self, project, *args, **kwargs):
        
        super(BookmarkForm, self).__init__(*args, **kwargs)
        
        # filter folders by project and active state
        # order by name in the form pull down
        self.fields['folder'].queryset = Folder.objects.filter(project=project).filter(active=True)\
            .distinct().order_by('name')
                
        # remove the empty option
        self.fields['folder'].empty_label = None
        
    def clean_url(self):
        return clean_url_field(self, 'url')
    
    def clean_name(self):
        return default_clean_field(self, 'name')
    
    def clean_description(self):
        return default_clean_field(self, 'description')


class FolderForm(ModelForm):
    
    # extra field for redirection to the 'add_doc' view, if needed
    redirect = CharField(required=False)

    class Meta:

        model = Folder
        exclude = ()
        
    # override __init__ method to provide a filtered list of options for the bookmark folder
    def __init__(self, project, *args, **kwargs):
        
        super(FolderForm, self).__init__(*args, **kwargs)
        self.project = kwargs.pop('project', None)
                
        # filter parent posts by project and type
        self.fields['parent'].queryset = Folder.objects.filter(project=project, active=True)\
	        .exclude(id=self.instance.id).distinct().order_by('order')
        # exclude the option for no parent - all folders created after the first must have parent
        self.fields['parent'].empty_label = None


    def clean_name(self):

        name = self.cleaned_data['name']
        project = self.cleaned_data['project']

        #make sure name is unique with the project
        try:
            n = Folder.objects.filter(project=project).get(name__iexact=name)
            raise forms.ValidationError("The folder name: %s already exists, please try again. "
                                        % n.name)
        except Folder.DoesNotExist:
            pass

        #looks for invalid characters
        name = default_clean_field(self, 'name')

        return name


