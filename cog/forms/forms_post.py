from cog.models import *
from django.forms import ModelForm, ModelMultipleChoiceField, NullBooleanSelect, ValidationError
from django.db import models
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from django.forms import ModelForm, Textarea, TextInput, Select
from django.core.exceptions import ObjectDoesNotExist
from os.path import basename
import re
from cog.utils import *
from cog.models.navbar import TABS
from django.db.models import Q

POST_TEMPLATES = (("cog/post/page_template_sidebar_center_right.html", "Left Menu, Main Content, Right Widgets"),
                  ("cog/post/page_template_sidebar_center.html", "Left Menu, Main Content"),
                  ("cog/post/page_template_center_right.html", "Main Content, Right Widgets"),
                  ("cog/post/page_template_center.html", "Main Content Only"),)


class PostForm(ModelForm):

    # extra field not present in Post model
    newtopic = forms.CharField(max_length=200, required=False)

    # save only flag: keeps form open
    save_only = forms.BooleanField(required=False, initial=False)

    # override __init__ method to provide extra arguments to customize the query set
    def __init__(self, type, project, *args, **kwargs):

        super(PostForm, self).__init__(*args, **kwargs)  # populates the post

        # filter parent posts by project and type
        queryset = Q(project=project) & Q(type=type)
        # include only top-level posts
        #queryset = queryset & Q(parent=None)
        if 'instance' in kwargs:
            instance = kwargs.get('instance')
            # exclude this post itself
            queryset = queryset & ~Q(id=instance.id)
        # get list of posts that can be a new post's parent page and alphabetize. Put the home page first.
        self.fields['parent'].queryset = Post.objects.filter(queryset).order_by('-is_home', 'title')

        #self.fields['parent'].queryset[0]=Q(is_home="true")
        self.fields['parent'].empty_label = "Top Level Page (no parent)"
        # limit topic selection to current project and post type(s)
        if type == Post.TYPE_PAGE or type == Post.TYPE_HYPERLINK:
            self.fields['topic'].queryset = Topic.objects.filter(Q(post__project=project))\
                                                         .filter(Q(post__type=Post.TYPE_PAGE) |
                                                                 Q(post__type=Post.TYPE_HYPERLINK))\
                                                         .distinct().order_by('name')
        else:
            self.fields['topic'].queryset = Topic.objects.filter(Q(post__project=project) &
                                                             Q(post__type=type)).distinct().order_by('name')
    
    # override form clean() method to execute combined validation on multiple fields
    def clean(self):

        cleaned_data = self.cleaned_data
        topic = cleaned_data.get("topic")
        newtopic = cleaned_data.get("newtopic")
        type = cleaned_data.get("type")
        
        # validate URL
        # must be null for home page, not null for other pages
        if type == Post.TYPE_PAGE:

            url = cleaned_data.get("url")
            project = cleaned_data.get("project")
                        
            # do NOT allow URLs that are part of templated URLs
            # url='contactus/' --> _url='contactus'
            _url = url.split('/')[0] # compare first part of user URL...
            # predefined_pages=[(u'TestProject Home', u'/projects/testproject/'), 
            #                   ('About Us', u'/projects/testproject/aboutus/'), 
            #                   ('Mission', u'/projects/testproject/mission/'), ...
            for ppage in project.predefined_pages():
                # [-1] location is empty string because templates URLs always end in '/'
                __url = str(ppage[1]).split("/")[-2] # to last part of project templated URL... 
                if _url == __url:
                    # MUST allow creation of the following template pages because they are wikis
                    if _url.lower() not in (TABS["LOGISTICS"], TABS["REGISTRATION"], TABS["LOCATION"],
                                            TABS["LODGING"], TABS["TRANSPORTATION"], TABS["COMPUTING"]):                          
                        self._errors["url"] = self.error_class(["The term '%s' is reserved for standard project URLs" % _url])
            
            # only allows letters, numbers, '-', '_' and '/'
            if re.search("[^a-zA-Z0-9_\-/]", url):
                self._errors["url"] = self.error_class(["Page URL contains invalid characters"])
            if self.instance.is_home:
                if len(url) > 0:
                    self._errors["url"] = self.error_class(["Invalid URL for project home: %s" % url])
            else:
                if url == '':
                    self._errors["url"] = self.error_class(["Invalid URL for project page"])
                elif '//' in url:
                    self._errors["url"] = self.error_class(["Invalid URL for project page: cannot have two consecutive '/'"])
                else:
                    # verify uniqueness: URL not used by any other existing instance
                    project = cleaned_data.get("project")
                    full_url = get_project_page_full_url(project, url)
                    # check this URL is unique
                    self._check_url_is_unique(full_url)
                    # also check with or without the trailing '/'
                    if full_url.endswith("/"):
                        self._check_url_is_unique(full_url[-1])
                    else:
                        self._check_url_is_unique(full_url+"/")

        # validate full URLs
        if type == Post.TYPE_HYPERLINK:
            url = cleaned_data.get("url").lower()
            if not url.startswith('http://') and not url.startswith('https://'):
                self._errors["url"] = self.error_class(["Invalid URL: must start with http(s)://..."])
            
        # validate "template"
        # must be not null for every page
        if type == Post.TYPE_PAGE:
            template = cleaned_data.get("template")
            if template == '':
                self._errors["template"] = self.error_class(["Invalid template"])
        
        # prevent <iframe>, <script> and <form> tags        
        if type == Post.TYPE_PAGE:
            body = cleaned_data.get("body")
            # execute validation on content without white spaces
            _body = body.replace(" ", "").lower()
            if "<iframe" in _body:
                self._errors["body"] = self.error_class(["Invalid content: cannot use <iframe> tag. Use the source "
                                                         "button to remove."])
            if "<script" in _body:
                self._errors["body"] = self.error_class(["Invalid content: cannot use <script> tag. Use the source "
                                                         "button to remove."])
            if "<form" in _body:
                self._errors["body"] = self.error_class(["Invalid content: cannot use <form> tag. Use the source "
                                                         "button to remove."])

        # validate "topic"
        # cannot set both 'topic' and 'newtopic'
        if topic and newtopic:
            errmsg = "Please either choose an existing topic OR create a new one"
            self._errors["topic"] = self.error_class([errmsg])
            del cleaned_data["topic"]
            del cleaned_data["newtopic"]

        # create new topic - if not existing already
        elif newtopic != '':
                        
            try:
                topic = Topic.objects.get(name__iexact=newtopic)
            except ObjectDoesNotExist:
                topic = Topic.objects.create(name=newtopic)

            cleaned_data["topic"] = topic

        # prevent XSS on fields 'title', 'label', 'newtopic'
        for key in ["title", "label", "newtopic"]:
            if key in cleaned_data:
                try:
                    xss_clean_field(self, key)
                except ValidationError as ve:
                    self._errors[key] = self.error_class([ve.message])

        # always return the full collection of cleaned data.
        return cleaned_data

    def _check_url_is_unique(self, full_url):
        '''Checks whether the provided URL already exists in the database.'''
        
        try:
            # perform case-insensitive lookup
            post = Post.objects.all().get(url__iexact=full_url)
            if post and (post.id != self.instance.id):
                self._errors["url"] = self.error_class(["URL already used"])
        except ObjectDoesNotExist:
            pass

        
    class Meta:
        model = Post
        exclude = ('author', 'publication_date', 'update_date',)

        widgets = {
            'title': TextInput(attrs={'size': '80'}),
            'label': TextInput(attrs={'size': '22'}),
            'url': TextInput(attrs={'size': '60'}),
            'template': Select(choices=POST_TEMPLATES),
            #'body': Textarea(attrs={'rows': 20}),
            # IMPORTANT: USE CKeditor to edit this field.
            'body': Textarea(attrs={'class': 'ckeditor'}),
        }
