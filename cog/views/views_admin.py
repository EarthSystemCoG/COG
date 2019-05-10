from cog.forms import *
from cog.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
import ast
from django.contrib.sites.models import Site  
from cog.models import PeerSite
from django.forms.models import modelformset_factory
from cog.views.utils import getAdminUsersThatMatch, get_projects_by_name, paginate, getQueryDict


def site_home(request):
    
    # redirect to HOME_PROJECT home
    return HttpResponseRedirect(reverse('project_home', args=[settings.HOME_PROJECT]))
        
    # redirect to 'cog' project hone page
    #return HttpResponseRedirect()
            
    # redirect to independent splash page
    #return render(request, 'cog/index.html', 
    #              {'title':'Welcome to COG' })


# admin page for managing projects
@user_passes_test(lambda u: u.is_staff)
def admin_projects(request):
    """
    Lists local projects in a table with links to edit or delete
    """
    site = Site.objects.get_current()

    # optional active=True|False filter
    active = request.GET.get('active', None)
    if active != None:
        project_list = Project.objects.filter(site=Site.objects.get_current()).filter(active=ast.literal_eval(active))\
            .order_by('short_name')
    else:
        if request.method == 'GET':
            project_list = Project.objects.filter(site=Site.objects.get_current()).order_by('short_name')
        else:
            # list project by search criteria. Search function located in utils.py
            # get list of all projects
            project_list = get_projects_by_name(request.POST['match'])
            # filter projects to include local site only
            project_list = project_list.filter(site=Site.objects.get_current()).order_by('short_name')

    # retrieve top-level projects, ordered alphabetically by short name. Only list those on the current site.
    return render(request,
                  'cog/admin/admin_projects.html',
                  {'project_list': paginate(project_list, request),
                   'title': '%s Projects Administration' % site.name})


# admin page for listing all system users
@user_passes_test(lambda u: u.is_staff)
def admin_users(request):

    # optional parameters (via GET or POST)
    queryDict = getQueryDict(request)
    sortby = queryDict.get('sortby', 'username')  # default to sort by 'username'
    match = queryDict.get('match', None)

    if match:
        users = getAdminUsersThatMatch(match, sortby=sortby)
    else:
        users = User.objects.all().order_by(sortby)  

    title = 'List System/Node Users'
    return render(request,
                  'cog/admin/admin_users.html',
                  {'users': paginate(users, request, max_counts_per_page=50), 'title': title})

    
# admin page for managing peers
@user_passes_test(lambda u: u.is_staff)
def admin_peers(request):
    
    PeerSiteFormSet = modelformset_factory(PeerSite, extra=0, can_delete=False, fields="__all__")
    
    if request.method == 'GET':
        
        formset = PeerSiteFormSet(queryset=PeerSite.objects.exclude(site=Site.objects.get_current()))
        return render(request,
                      'cog/admin/admin_peers.html', 
                      {'formset': formset})
        
    else:
        
        formset = PeerSiteFormSet(request.POST)
        
        if formset.is_valid():
            instances = formset.save()
            return HttpResponseRedirect(reverse('admin_peers')+"?status=success")
        
        else:
            log.debug(formset.errors)
            return render(request,
                          'cog/admin/admin_peers.html', {'formset': formset})