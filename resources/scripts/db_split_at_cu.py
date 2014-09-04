'''
Script to perform database setup at CoG-CU after 2.6.1 deployment (CoG sites split).

'''
import os
import sys
import cog
import shutil
path = os.path.dirname(cog.__file__)
sys.path.append( path )
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from cog.models import UserProfile

from cog.models import Project


# load CU, NOAA Sites

# before DNS change
cuSite = Site.objects.get(domain='cog-cu.colorado.edu')
noaaSite = Site.objects.get(domain='www.earthsystemcog.org')

# after DNS change:
#cuSite = Site.objects.get(domain='www.earthsystemcog.org')
#noaaSite = Site.objects.get(domain='cog-esgf.esrl.noaa.gov')
if cuSite != Site.objects.get_current():
    raise Exception("Running script for wrong site, exiting")

dryrun = True

# loop over projects
noaaProjects = ['HIWPP', 'CMDTF', 'CoupledNEMS', 
                       'HIWPP_HurricaneNest', 'HIWPP_Hydrostatic', 'HIWPP_Internal',
                       'HIWPP_Management', 'HIWPP_NMME', 'HIWPP_NonHydrostatic', 'HIWPP_TestProgram',
                       ]
for project in Project.objects.all():
    
    if project.short_name in noaaProjects:
        
        print "Deleting project=%s" % project.short_name
           
        # delete project User group, permissions
        ug = project.getUserGroup()
        for p in ug.permissions.all():
            print '\tDeleting permission: %s' % p
            if not dryrun:
                p.delete()
        print '\tDeleting group: %s' % ug
        if not dryrun:
            ug.delete()
        
        # delete project Admin group, permissions
        ag = project.getAdminGroup()
        for p in ag.permissions.all():
            print '\tDeleting permission: %s' % p
            if not dryrun:
                p.delete()
        print '\tDeleting group: %s' % ag
        if not dryrun:
            ag.delete()
    
        # do NOT remove project media for now (so links will still work)
        #media_dir = os.path.join(settings.MEDIA_ROOT, settings.FILEBROWSER_DIRECTORY, project.short_name.lower())
        #print "\tRemoving directory tree: %s" % media_dir
        #if not dryrun:
        #    try:
        #        shutil.rmtree(media_dir)
        #    except OSError as e:
        #        print e
        
        print '\tDeleting project: %s' % project
        if not dryrun:
            project.delete()
    

# loop over users
for user in User.objects.all():
       
    try:
        p = user.profile
    except ObjectDoesNotExist:
        p = UserProfile.objects.create(user=user)
        
    if user.profile.site == cuSite:
        
        print "Processing CU user: %s" % user
        
        # remove User password
        user.password = ''
        
        # update profile fields
        user.profile.type = 2 # (no CoG password)
        
        # transfer user affiliation from CU to NOAA
        print "\tUser affiliation changed from: %s to: %s" % (cuSite, noaaSite)
        user.profile.site = noaaSite
        
        # save changes
        if not dryrun:
            user.save()
            user.profile.save()
    
    else:
        pass
        #print 'Disregarding user=%s site=%s site_id=%s' % (user, user.profile.site, user.profile.site.id)