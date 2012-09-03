from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response

from cog.models.project import Project, userHasProjectRole

from cog.views.constants import PERMISSION_DENIED_MESSAGE
from cog.models.constants import ROLE_USER, ROLE_ADMIN

from django.template import RequestContext

SYSTEM_DIR = 'system'

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
            
            # extract HTTP request parameters
            request = args[0]
            upload_dir = request.REQUEST.get('dir', None)
            print 'Upload directory=%s' % upload_dir
            request_path = request.path
            print 'Request path=%s' % request_path
            filename = request.REQUEST.get('filename', None)
            print 'Filename=%s' % filename
            
            # site administrators can perform any action
            if request.user.is_staff:
                return view(_self, *args, **kwargs)
            
            # split directory path
            if upload_dir is not None:
                project_dir = upload_dir.strip().split('/')[0]
                print "project dir=%s" % project_dir
             
                # no action allowed by anybody on 'system/' folder (except site administrators)
                if project_dir == SYSTEM_DIR:
                    return render_to_response('cog/common/message.html', 
                                          {'mytitle':'Action Restricted', 
                                           'messages':['Sorry, the system folder can be changed only by the site administrators.'] }, 
                                            context_instance=RequestContext(request)) 
            
                # project associated with directory  
                project = get_object_or_404(Project, short_name__iexact=project_dir)
            
            # UPLOAD ('/admin/filebrowser/upload/')
            if 'upload' in request_path:
                
                if upload_dir is None:
                    return self._access_denied(request,
                                               ['Sorry, upload to the top-level folder is forbidden.',
                                                'Please upload to the project specific folder.'])
                if userHasProjectRole(request.user, project, ROLE_USER):
                    return view(_self, *args, **kwargs)           
                else:
                    # by default, return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
                    return self._access_denied(request, ['Sorry, this action is restricted to members of project: %s.' % project.short_name])
                
            # CREATE FOLDER ('/admin/filebrowser/createdir/')
            elif 'createdir' in request_path:
                if upload_dir is None:
                    return self._access_denied(request,
                                               ['Sorry, sub-folders can only be created by project administrators',
                                                'within the project top-level folder.'])
                else:
                    if userHasProjectRole(request.user, project, ROLE_ADMIN):
                        return view(_self, *args, **kwargs)           
                    else:
                        # by default, return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
                        return self._access_denied(request, ['Sorry, this action is restricted to administrators of project: %s.' % project.short_name])
                    
            # DELETE FOLDER, FILE ('/admin/filebrowser/delete_confirm/')
            elif 'delete' in request_path:
                if upload_dir is None:
                    return self._access_denied(request,
                                               ['Sorry, the project top-level folder cannot be deleted.'])
                else:
                    if userHasProjectRole(request.user, project, ROLE_ADMIN):
                        return view(_self, *args, **kwargs)           
                    else:
                        # by default, return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
                        return self._access_denied(request, ['Sorry, this action is restricted to administrators of project: %s.' % project.short_name])

                    
              
            # DEFAULT  
            else:
                return self._access_denied(request, ['Sorry, this action is not allowed.'])
                                                   
        return wrapper
            
    def _access_denied(self, request, messages):
        return render_to_response('cog/common/message.html', 
                                  {'mytitle':'Action Restricted', 'messages': messages, }, 
                                  context_instance=RequestContext(request))