from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from cog.models import *
from cog.forms import *
from constants import PERMISSION_DENIED_MESSAGE
from os.path import basename

@login_required   
def doc_add(request, project_short_name):
    
     project = get_object_or_404(Project, short_name__iexact=project_short_name)
     
     # check permission
     if not userHasUserPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
     if (request.method=='GET'):
         
        # create empty document
        doc = Doc()
        
        # assign project
        doc.project = project
        
        # create form from instance
        form = DocForm(instance=doc)
        
        return render_doc_form(request, form, project)
    
     else:
        form = DocForm(request.POST, request.FILES)

        if form.is_valid():
            doc = form.save(commit=False)
            doc.author = request.user
            if doc.title is None or len(doc.title.strip())==0:
                doc.title = basename(doc.file.name)
            doc.save()
            
            # optional redirect
            redirect = form.cleaned_data['redirect']
            if (redirect):
                # add newly created doc id to redirect URL (GET-POST-REDIRECT)
                return HttpResponseRedirect( redirect + "?doc_id=%i"%doc.id )
            else:
                # (GET-POST-REDIRECT)
                return HttpResponseRedirect( reverse('doc_detail', kwargs={'doc_id': doc.id}) )
        else:
            #print form.errors
            return render_doc_form(request, form, project)

def doc_detail(request, doc_id):
    doc = get_object_or_404(Doc, pk=doc_id)
    return render_to_response('cog/doc/doc_detail.html', 
                              { 'doc': doc, 'project':doc.project, 'title': doc.title }, 
                               context_instance=RequestContext(request) )    
@login_required
def doc_remove(request, doc_id):
    
    # retrieve document from database
    doc = get_object_or_404(Doc, pk=doc_id)
    project = doc.project
    
    # check permission
    if not userHasUserPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)

    # delete document from database
    doc.delete()
    
    # redirect to project home page
    return HttpResponseRedirect( reverse('project_home', kwargs={'project_short_name': project.short_name.lower() } ) ) 
    

@login_required
def doc_update(request, doc_id):
    
    # retrieve document from database
    doc = get_object_or_404(Doc, pk=doc_id)
    
    # check permission
    if not userHasUserPermission(request.user, doc.project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if (request.method=='GET'):
        # create form from model
        form = DocForm(instance=doc)
        return render_doc_form(request, form, doc.project)
        
    else:
        # update existing database model with form data
        form = DocForm(request.POST, request.FILES, instance=doc)
        if (form.is_valid()):
            doc = form.save()
            # redirect to document detail (GET-POST-REDIRECT)
            return HttpResponseRedirect( reverse('doc_detail', kwargs={'doc_id':doc.id}) )
        else:
            return render_doc_form(request, form, doc.project)

def doc_list(request, project_short_name):
    
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # query by project
    qset = Q(project=project)
    list_title = 'All Documents'
    
    # optional query parameters
    query = request.GET.get('query', '')
    if query:
        qset = qset & (
            Q(title__icontains=query) |
            Q(description__icontains=query) 
        )
        list_title = "Search Results for '%s'" % query    
        
    order_by = request.GET.get('order_by', 'title')
    list_title += " (order by %s)" % order_by
    
    # execute query, order by descending update date
    results = Doc.objects.filter(qset).distinct().order_by( order_by )
   
    return render_to_response('cog/doc/doc_list.html', 
                              {"object_list": results, 'project': project, 'title':'%s Documents' % project.short_name, 
                               "query": query, "order_by":order_by, "list_title":list_title }, 
                              context_instance=RequestContext(request))
    
def render_doc_form(request, form, project):
    title = 'Upload %s Document' % project.short_name
    return render_to_response('cog/doc/doc_form.html', 
                             {'form': form, 'project':project, 'title':title}, 
                              context_instance=RequestContext(request))