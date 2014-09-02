from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
import datetime

# function to return an error message if a project is not active
def getProjectNotActiveRedirect(request, project):
        messages = ['Access to all pages of project %s is currently forbidden.' % project.short_name,
                    'Please contact support for any questions.'] 
        return render_to_response('cog/common/message.html', 
                                  {'mytitle':'Project Access Not Enabled', 
                                   'project':project,
                                   'messages':messages }, 
                                  context_instance=RequestContext(request))
        
# function to return an error message if a project is not public
def getProjectNotVisibleRedirect(request, project):
        messages = ['Access to all pages of project %s is restricted to members only.' % project.short_name,
                    'Please contact support for any questions.'] 
        return render_to_response('cog/common/message.html', 
                                  {'mytitle':'Project Access Restricted', 
                                   'project':project,
                                   'messages':messages }, 
                                  context_instance=RequestContext(request))
        
def set_openid_cookie(response, openid):
    '''Utility method to consistently set the openid cookie.'''
    
    print 'SETTING openid cookie to: %s' % openid
    
    response.set_cookie('openid', openid, 
                        expires = (datetime.datetime.now() + datetime.timedelta(days=3650)), # expires in 10 years
                        httponly=True)
