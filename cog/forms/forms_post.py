from cog.models import *
from django.forms import ModelForm, ModelMultipleChoiceField, NullBooleanSelect
from django.db import models
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from django.forms import ModelForm, Textarea, TextInput, Select
from django.core.exceptions import ObjectDoesNotExist
from os.path import basename
import re
from cog.utils import *
from django.db.models import Q

POST_TEMPLATES = (
                   #("cog/post/page_template_center.html", "Full page"),
                   ("cog/post/page_template_sidebar_center.html", "Left Menu, Main Content"),
                   ("cog/post/page_template_sidebar_center_right.html", "Left Menu, Main Content, Right Widgets"),
                 )

class PostForm(ModelForm):

    # extra field not present in Post model
    newtopic = forms.CharField(max_length=200, required=False)

    # override __init__ method to provide extra arguments to customize the query set
    def __init__(self, type, project, *args,**kwargs):

        super(PostForm, self ).__init__(*args,**kwargs) # populates the post

        # filter parent posts by project and type
        queryset = Q(project=project) & Q(type=type)
        # include only top-level posts
        #queryset = queryset & Q(parent=None)
        if 'instance' in kwargs:
            instance = kwargs.get('instance')
            # exclude this post itself
            queryset = queryset & ~Q(id=instance.id)
        self.fields['parent'].queryset =  Post.objects.filter( queryset )
        self.fields['parent'].empty_label = "Top Level Page (no parent)"
        # limit topic selection to current project and post type
        self.fields['topic'].queryset = Topic.objects.filter( Q(post__project=project) & Q(post__type=type) ).distinct().order_by('name')

    # override form clean() method to execute combined validation on multiple fields
    def clean(self):

        cleaned_data = self.cleaned_data
        topic = cleaned_data.get("topic")
        newtopic = cleaned_data.get("newtopic")
        type  = cleaned_data.get("type")

        # validate URL
        # must be null for home page, not null for other pages
        if type==Post.TYPE_PAGE:

            url = cleaned_data.get("url")
            # only allows letters, numbers, '-', '_' and '/'
            if re.search("[^a-zA-Z0-9_\-/]", url):
                self._errors["url"] = self.error_class(["Page URL contains invalid characters"])
            if self.instance.is_home:
                if len(url)>0:
                    self._errors["url"] = self.error_class(["Invalid URL for project home: %s" % url])
            else:
                if url=='':
                    self._errors["url"] = self.error_class(["Invalid URL for project page"])
                else:
                    # verify uniqueness: URL not used by any other existing instance
                    project = cleaned_data.get("project")
                    full_url = get_project_page_full_url(project, url)
                    try:
                        # perform case-insensitive lookup
                        post = Post.objects.all().get(url__iexact=full_url)
                        if post and (post.id != self.instance.id):
                            self._errors["url"] = self.error_class(["URL already used"])
                    except ObjectDoesNotExist:
                        pass

        # validate "template"
        # must be not null for every page
        if type==Post.TYPE_PAGE:
            template = cleaned_data.get("template")
            if template=='':
                self._errors["template"] = self.error_class(["Invalid template"])

        # validate "topic"
        # cannot set both 'topic' and 'newtopic'
        if topic and newtopic:
            errmsg = u"Please either choose an existing topic OR create a new one"
            self._errors["topic"] = self.error_class([errmsg])
            del cleaned_data["topic"]
            del cleaned_data["newtopic"]

        # create new topic - if not existing already
        elif newtopic!='':
            try:
                topic = Topic.objects.get(name__iexact=newtopic)
            except ObjectDoesNotExist :
                topic = Topic.objects.create(name=newtopic)

            cleaned_data["topic"] = topic

        # always return the full collection of cleaned data.
        return cleaned_data

    class Meta:
        model = Post
        exclude = ('author','publication_date','update_date',)

        widgets = {
            'title': TextInput(attrs={'size':'80'}),
            'label': TextInput(attrs={'size':'22'}),
            'url': TextInput(attrs={'size':'60'}),
            'template': Select(choices=POST_TEMPLATES),
            #'body': Textarea(attrs={'rows': 20}),
            # IMPORTANT: USE CKeditor to edit this field.
            'body': Textarea(attrs={'class':'ckeditor'}),
        }