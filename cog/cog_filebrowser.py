#
# Module that extends django-filebrowser by imposing COG-specific access control.
#

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render

from cog.models.project import Project, getProjectsForUser
from cog.models.auth import userHasProjectRole

from cog.views.constants import PERMISSION_DENIED_MESSAGE
from cog.models.constants import ROLE_USER, ROLE_ADMIN, ROLE_CONTRIBUTOR

from django.template import RequestContext

SYSTEM_DIR = 'system'


def get_browsable_projects(request):
    '''Function to return a list of projects to browse for the current HTTP request.'''
    
    project_short_name = request.GET.get('project', None)
    if project_short_name:
        # show only selected project folder
        projects = [get_object_or_404(Project, short_name__iexact=project_short_name)]
    elif request.user.is_staff:
        # show all projects for administrators
        projects = Project.objects.all()
    else:
        # show only projects available to user
        projects = getProjectsForUser(request.user, False)  # includePending==False
    return projects


def project_filter(fileobject, user, projects):
    ''' Utility function to filter a file object instance through the user's member projects.
        Returns True if the file object passes the test (i.e. it is to be accepted).'''
            
    # extract project directory from fileobject path
    # example: filepject.path = 'projects/dcmip/folder1/123.gif'
    prjdir = fileobject.path.split('/')[1]
    
    for prj in projects:
        if prjdir == prj.short_name.lower():
            return True
    
    # reject this file object
    return False
        

class filebrowser_check(object):
    '''
    Decorator that wraps the filebrowser views by enforcing
    the desired access control policy for files and directories.
    '''   
    
    def __init__(self):
        pass
        
    def __call__(self, view):
        
        # method that wraps the view invocation - same signature as the view + the instance reference (_self)
        def wrapper(_self, *args, **kwargs):
            
            raise Exception("filebrowser_check was invoked")
        
            
    def _access_denied(self, request, messages):
        return render(request,
                      'cog/common/message.html', 
                      {'mytitle':'Action Restricted', 'messages': messages, })