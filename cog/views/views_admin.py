from cog.forms import *
from cog.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
import ast
from django.contrib.sites.models import Site  
from cog.models import PeerSite
from django.forms.models import modelformset_factory


def index(request):
        
    # redirect to 'cog' project hone page
    return HttpResponseRedirect(reverse('project_home', args=['cog']))
            
    # redirect to independent splash page
    #return render_to_response('cog/index.html', 
    #                          {'title':'Welcome to COG' }, 
    #                          context_instance=RequestContext(request))
    
# admin page for managing projects
@user_passes_test(lambda u: u.is_staff)
def admin_projects(request):
    '''Only lists local projects.'''
    
    # optional active=True|False filter
    active = request.GET.get('active', None)
    if active != None:
        project_list = Project.objects.filter(site=Site.objects.get_current()).filter(active=ast.literal_eval(active)).order_by('short_name')
    else:
        project_list = Project.objects.filter(site=Site.objects.get_current()).order_by('short_name')
    
    return render_to_response('cog/admin/admin_projects.html',
                              { 
                               # retrieve top-level projects, ordered alphabetically
                               'project_list': project_list, 
                               'title':'COG Projects Administration' 
                              }, 
                              context_instance=RequestContext(request))    
    
# admin page for managing peers
@user_passes_test(lambda u: u.is_staff)
def admin_peers(request):
    
    PeerSiteFormSet = modelformset_factory(PeerSite, extra=0, can_delete=False)
    
    if request.method=='GET':
        
        formset = PeerSiteFormSet(queryset=PeerSite.objects.exclude(site=Site.objects.get_current()))
        return render_to_response('cog/admin/admin_peers.html', {'formset':formset },
                                  context_instance=RequestContext(request))
        
    else:
        
        formset = PeerSiteFormSet(request.POST)
        
        if formset.is_valid():
            instances = formset.save()
            return HttpResponseRedirect( reverse('admin_peers')+"?status=success" )
        
        else:
            print formset.errors
            return render_to_response('cog/admin/admin_peers.html', {'formset':formset},
                                      context_instance=RequestContext(request))


