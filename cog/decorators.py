from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response

from cog.models.project import Project, userHasProjectRole

from cog.views.constants import PERMISSION_DENIED_MESSAGE

from django.template import RequestContext

COMMON_DIR = 'common'

class filebrowser_check_project_role(object):
    '''
    Decorator that wraps the filebrowser views by checking that the user
    has the specified role within the project directory 
    where files are uploaded/browsed/deleted.
    '''
    
    def __init__(self, role):
        self.role = role
        
    def __call__(self, view):
        
        # method that wraps the view invocation - same signature as the view + the instance reference (_self)
        def wrapper(_self, *args, **kwargs):
            
            request = args[0]
            upload_dir = request.REQUEST.get('dir', None)
            if upload_dir is not None:
                print 'Upload directory=%s' % upload_dir
            
                # split directory path
                project_dir = upload_dir.strip().split('/')[0]
                print "project dir=%s" % project_dir
                
                # common upload directory
                if project_dir == COMMON_DIR:
                    return view(_self, *args, **kwargs)
                
                else:
                    project = get_object_or_404(Project, short_name__iexact=project_dir)
                    if userHasProjectRole(request.user, project, self.role):
                        return view(_self, *args, **kwargs)
            
            # by default, return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
            messages = ['Sorry, insufficient user permissions for the selected folder',
                        'Please contact support for any questions.'] 
            return render_to_response('cog/common/message.html', 
                                      {'mytitle':'Action Restricted', 
                                       'messages':messages }, 
                                       context_instance=RequestContext(request))    

    
        return wrapper
            