'''
Script to backup a CoG project and all related objects.
'''

project_short_name = "NESII"
filename = "cog_project_backup.xml"

# add parent 'cog' directory to PYTHON path
import os, sys
parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)

# load Django/CoG settings
import cog
path = os.path.dirname(cog.__file__)
sys.path.append( path )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django
django.setup()

from django.core import serializers
from cog.models import Project

# instantiate serializer 
XMLSerializer = serializers.get_serializer("xml")
myserializer = XMLSerializer()

# open backup file
with open(filename, "w") as out:
    
    # backup project
    project = Project.objects.get(short_name=project_short_name)
    
    '''
        site = models.ForeignKey(Site, default=settings.SITE_ID)
    
    external_homepage = models.URLField(max_length=200, blank=True, null=True, help_text='External Home Page')
    

    
    
    # A project may have many parents. The relationship is not symmetrical.
    # The attribute parents_set contains the inverse relationship
    parents = models.ManyToManyField('self', blank=True, related_name='Parent Projects', symmetrical=False)
    
    # A project may have many peers. The relationship is not symmetrical.
    # The attribute peers_set contains the inverse relationship
    peers = models.ManyToManyField('self', blank=True, related_name='Peer Projects', symmetrical=False)
    
    # the initial requestor of the project, if any
    author = models.ForeignKey(User, blank=True, null=True, default=None)
    
    # the workspace of an inactive project is not accessible
    active = models.BooleanField(default=False, blank=False, null=False)
    
    # a private project is only visible to project members 
    # by default all projects are public, and must be explicitely made private
    private = models.BooleanField(default=False, blank=False, null=False)
    
    # optional custom logo
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    
    
    # list of available topics for this project
    topics =  models.ManyToManyField(Topic, blank=True, null=True, through='ProjectTopic')
    
    # list of project tags
    tags = models.ManyToManyField(ProjectTag, blank=True, null=True, related_name='projects')
            
    '''
    myserializer.serialize(Project.objects.filter(short_name=project_short_name), stream=out,
                           fields=('short_name',
                                   'long_name',
                                   'description',
                                   'mission',
                                   'vision',
                                   'values',
                                   'history',
                                   'governanceOverview',
                                   'developmentOverview',
                                   'taskPrioritizationStrategy',
                                   'requirementsIdentificationProcess',
                                   'software_features',
                                   'system_requirements',
                                   'license',
                                   'implementationLanguage',
                                   'bindingLanguage',
                                   'supportedPlatforms',
                                   'externalDependencies',
                                   'getting_started',
                                   'projectContacts',
                                   'technicalSupport',
                                   'meetingSupport',
                                   'getInvolved',
                                   'active',
                                   'private',
                                   'logo_url',
                                   'dataSearchEnabled',
                                   ),
                           use_natural_foreign_keys=True, use_natural_primary_keys=True)
