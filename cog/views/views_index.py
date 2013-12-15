from cog.forms import *
from cog.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
import ast

# temporary notice of sites moved to new URLs
def thesitehasmoved(request):
    return thisprojecthasmoved(request, 'cog')
    
def thisprojecthasmoved(request, project_short_name):
    
    # retrieve project from database
    project = get_object_or_404(Project, short_name__iexact=project_short_name)

    return render_to_response('cog/thesitehasmoved.html',
                              { 'project': project },
                              context_instance=RequestContext(request))
    

#FIXME: remove
# temporary view to redirect from the old COG top-level URL
def earthsystemcog(request):
    return HttpResponseRedirect('http://earthsystemcog.org/')

#FIXME: remove
# temporary view to redirect from an old COG URL project home
def earthsystemcog_project(request, project_short_name):
    return HttpResponseRedirect('http://earthsystemcog.org/projects/%s' % project_short_name)

def index(request):
        
    # redirect to 'cog' project hone page
    #return HttpResponseRedirect(reverse('project_home', args=['cog']))
            
    # redirect to independent welcome page
    return render_to_response('cog/index.html', 
                              {'title':'Welcome to COG' }, 
                              context_instance=RequestContext(request))
    
# COG home page for administrative actions
@user_passes_test(lambda u: u.is_staff)
def admin_index(request):
    
    # optional active=True|False filter
    active = request.GET.get('active', None)
    if active != None:
        project_list = Project.objects.filter(active=ast.literal_eval(active)).order_by('short_name')
    else:
        project_list = Project.objects.all().order_by('short_name')
    
    return render_to_response('cog/admin/admin_index.html',
                              { 
                               # retrieve top-level projects, ordered alphabetically
                               'project_list': project_list, 
                               'title':'COG Administration Index' 
                              }, 
                              context_instance=RequestContext(request))    