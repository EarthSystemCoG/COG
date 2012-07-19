from django.db import models
from constants import APPLICATION_LABEL
from project import Project
from django.contrib.auth.models import User
from doc import Doc
from topic import Topic

# A web site post, which can be of different types
class Post(models.Model):
        
        # possible Post types
        TYPE_BLOG  = 'blog'
        TYPE_PAGE  = 'page'
        TYPE_NOTES = 'notes'
        POST_TYPES = ( (TYPE_BLOG, TYPE_BLOG.capitalize()), (TYPE_PAGE, TYPE_PAGE.capitalize()), (TYPE_NOTES, TYPE_NOTES.capitalize()) )
      
        author = models.ForeignKey(User, related_name='posts', verbose_name='Author', blank=False)
        title = models.CharField(max_length=200, verbose_name='Title', blank=False)
        label = models.CharField(max_length=25, verbose_name='Label', help_text='Short index label', blank=True, null=True)
        body = models.TextField(verbose_name='Content', blank=True, default="")
        publication_date = models.DateTimeField('Date Published', auto_now_add=True)
        update_date = models.DateTimeField('Date Updated', auto_now=True)
        # project context
        project = models.ForeignKey(Project)
        # order of post within project index
        order = models.IntegerField(blank=True, null=False, default=0)
        # optional topic
        topic = models.ForeignKey(Topic, blank=True, null=True)
        # optional parent post - must specify both blank=True (form validation) and null=True (model)
        parent = models.ForeignKey('self', verbose_name='Parent Post', blank=True, null=True)
        # optional attached documents - must specify both blank=True (form validation) and null=True (model)
        docs = models.ManyToManyField(Doc, verbose_name='Attachments', blank=True, null=True)
        
        # post type
        type = models.CharField(max_length=10, verbose_name='Type', blank=False, choices=POST_TYPES)
        # URL
        url = models.CharField(max_length=200, verbose_name='URL', blank=True, unique=True, default='')
        # layout template
        template = models.CharField(max_length=200, verbose_name='Template', blank=True)
        # home page flag
        is_home = models.BooleanField(verbose_name='Is Home Page ?', default=False, null=False)
        # public/private flag
        is_private = models.BooleanField(verbose_name='Private ?', default=False, null=False)
                
        # method to check whether this is one of the project predefined pages
        def is_predefined(self):
            home_page_url = self.project.home_page_url()
            for ppage in self.project.predefined_pages():
                # mus check both short and long version of the URL, 
                # depending on how where method is called
                if self.url==ppage[1] or (home_page_url + self.url) == ppage[1]:
                    return True
            return False
        
        def get_label(self):
            if self.label is not None and len(self.label)>0:
                return self.label
            else:
                return self.title
        
        def __unicode__(self):
            return self.title
        
        class Meta:
            app_label= APPLICATION_LABEL