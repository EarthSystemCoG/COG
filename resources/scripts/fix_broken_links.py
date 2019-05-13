'''
Script to fix broken links in the database.

'''
import os
import sys

sys.path.append( os.path.abspath(os.path.dirname('.')) )
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
django.setup()

from cog.models import Post

BAD_LINK="http://cog-esgf.esrl.noaa.gov/"
GOOD_LINK="https://esgf.esrl.noaa.gov/"

# delete non-NOAA projects
for post in Post.objects.all():
    
    if BAD_LINK in post.body:
        print("Found bad link at URL: %s" % post.url)
        post.body = post.body.replace(BAD_LINK, GOOD_LINK)
        post.save()
        
