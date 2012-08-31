from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response

from cog.models.project import Project, userHasProjectRole

from cog.views.constants import PERMISSION_DENIED_MESSAGE

from django.template import RequestContext

COMMON_DIR = 'common/'

class filebrowser_check_project_role(object):
    
    def __init__(self, role):
        self.role = role
        
    def __call__(self, func):
        
        def wrapper(_self, *args, **kwargs):
            
            request = args[0]
            # path=/admin/filebrowser/upload/
            #print 'path=%s' % request.path 
            upload_dir = request.REQUEST.get('dir', None)
            if upload_dir is None:
                print 'No permission'
           
            else:    
                print 'Upload directory=%s' % upload_dir
                print "role=%s" % self.role            
                # split directory path
                project_dir = upload_dir.strip().split('/')[0]
                print "project dir=%s" % project_dir
                
                try:
                    project = Project.objects.get(short_name__iexact=project_dir)
                    
                    if userHasProjectRole(request.user, project, self.role):
                        return func(_self, *args, **kwargs)
                except Project.DoesNotExist:
                    pass
            
            #return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
            messages = ['This action is restricted to member of project %s with role %s'  % (project.short_name, self.role) ,
                         'Please contact support for any questions.'] 
            return render_to_response('cog/common/message.html', 
                                      {'mytitle':'Action Restricted', 
                                       'project': project,
                                       'messages':messages }, 
                                       context_instance=RequestContext(request))    

    
        return wrapper
            