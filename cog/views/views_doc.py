from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from cog.models import *
from cog.forms import *
from constants import PERMISSION_DENIED_MESSAGE
from os.path import basename
from django.views.decorators.csrf import csrf_exempt
from cog.forms import UploadImageForm
from cog.models.constants import DOCUMENT_TYPE_ALL, DOCUMENT_TYPES, SYSTEM_DOCS, SYSTEM_IMAGES
from django.conf import settings
from django.views.static import serve
from cog.models.auth import userHasUserPermission, userHasContributorPermission
from cog.models.doc import get_upload_path
from cog.models.utils import delete_doc
from cog.views.constants import VALID_ORDER_BY_VALUES, VALID_FILTER_BY_VALUES
import os
from cog.views.utils import getQueryDict, paginate

import logging

log = logging.getLogger(__name__)

@csrf_exempt
@login_required
def doc_upload(request, project_short_name):
    """
    View to support upload of documents (images) from CKeditor
    """
        
    # retrieve project
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
                
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            # create 'Doc' instance with required fields
            # the HTTP parameter name 'upload' is assigned by CKeditor
            file = request.FILES['upload']
            path = "%s/%s" % (project_short_name.lower(), file.name)
            instance = Doc(file=file, author=request.user, project=project, title=file.name, path=path)
            instance.save()
            #print 'uploaded document path=%s' % instance.path
            # retrieve the file URL (after it has been saved!), 
            # pass it on to the view for use by CKeditor
            url = instance.file.url
            error = ''
            
        else:
            log.debug('Form errors:%s' % form.errors)
            error = 'The file uploaded is not an image. Valid files include PNG, JPG, and PDF.'
            url = "%s%s" % (settings.STATIC_URL, 'cog/img/error.jpeg')
    
        return render(request,
                      'cog/doc/doc_upload.html', 
                      {'title': 'File Upload', 'url': url, 'error': error})


@login_required   
def doc_add(request, project_short_name):
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
     
    # check permission
    if not userHasContributorPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if request.method == 'GET':
         
        # create empty document
        doc = Doc()
        
        # assign project
        doc.project = project

        # change form such that if a project is private, the Private? checkbox is checked by default
        if doc.project.private:
            doc.is_private = True
        
        # create form from instance
        form = DocForm(project, instance=doc)
        
        return render_doc_form(request, form, project)
    
    else:
        form = DocForm(project, request.POST, request.FILES)

        if form.is_valid():
                        
            doc = form.save(commit=False)
            doc.author = request.user
            if doc.title is None or len(doc.title.strip()) == 0:
                doc.title = basename(doc.file.name)
            # save the document so to assign path in project directory: 'projects/<this project>/<filename>'
            doc.save()
            # store path explicitly in the database so it can be used for searching
            doc.path = doc.file.name
            # must save again
            doc.save()
            
            # optionally create Resource in selected Folder
            folder = form.cleaned_data['folder']
            if folder is not None:
                # must use full URL since Bookmark.url is of type URLField
                url = request.build_absolute_uri(doc.file.url)
                bookmark = Bookmark.objects.create(name=doc.title, url=url, folder=folder, 
                                                   description=doc.description, order=len(folder.bookmark_set.all()))

            # optional redirect
            redirect = form.cleaned_data['redirect']
            if redirect:
                # add newly created doc id to redirect URL (GET-POST-REDIRECT)
                return HttpResponseRedirect(redirect + "?doc_id=%i" % doc.id)
            else:
                # (GET-POST-REDIRECT)
                return HttpResponseRedirect(reverse('doc_detail', kwargs={'doc_id': doc.id}))
        else:
            #print form.errors
            return render_doc_form(request, form, project)


def doc_detail(request, doc_id):
    doc = get_object_or_404(Doc, pk=doc_id)
    return render(request,
                  'cog/doc/doc_detail.html', 
                  {'doc': doc, 'project': doc.project, 'title': doc.title})


def doc_download(request, path):
    """
    Method to serve project media.
    This is a wrapper around the standard django media view to enable CoG access control.
    """
    
    # extract project path from download request
    # print 'Download document path=%s' % path
    # example: path='nesii/myimage.jpg'
    project_short_name_lower = path.split("/")[0]
    
    # media in legacy storage locations
    if project_short_name_lower == SYSTEM_DOCS or project_short_name_lower == SYSTEM_IMAGES:
        return serve(request, path, document_root=settings.PROJECTS_ROOT)
        
    # load document by path
    #print 'looking for doc ending in path=%s' % path
    doc = Doc.objects.get(path__endswith=path)
    
    # public documents
    if doc.is_private:
        return doc_download_private(request, path, doc)
    else:
        return serve(request, path, document_root=settings.PROJECTS_ROOT)


def data_download(request, path):
    """Method to serve project data to authorized users."""
    
    project_short_name = path.split("/")[0]
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    log.debug('Data for project=%s' % project)
    
    # TODO: check if data is public before forcing login
    return secure_data_download(request, path, project)


@login_required   
def secure_data_download(request, path, project):
    
    # TODO: generalize authorization by looking up regular expressions matching path
    if userHasUserPermission(request.user, project):
        return serve(request, path, document_root=settings.DATA_ROOT)
    else:
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)    


@login_required   
def doc_download_private(request, path, doc):
    """Download view that requires user to login, then checks authorization."""
    
    if userHasUserPermission(request.user, doc.project):
        return serve(request, path, document_root=settings.PROJECTS_ROOT)
    else:
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)


@login_required
def doc_remove(request, doc_id):
        
    # retrieve document from database
    doc = get_object_or_404(Doc, pk=doc_id)
    project = doc.project
    
    # check permission
    if not userHasContributorPermission(request.user, project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    # delete doc altogether
    delete_doc(doc)
        
    # redirect to original page, or to project home if not found
    redirect = getQueryDict(request).get('redirect', None)
    if redirect is None:
        redirect = reverse('project_home', kwargs={'project_short_name': project.short_name.lower()})
    
    # redirect to project home page
    #return HttpResponseRedirect( reverse('doc_list', kwargs={'project_short_name': project.short_name.lower() } ) ) 
    return HttpResponseRedirect(redirect)
    

@login_required
def doc_update(request, doc_id):
    
    # retrieve document from database
    doc = get_object_or_404(Doc, pk=doc_id)
    
    # check permission
    if not userHasContributorPermission(request.user, doc.project):
        return HttpResponseForbidden(PERMISSION_DENIED_MESSAGE)
    
    if request.method == 'GET':
        # create form from model
        form = DocForm(doc.project, instance=doc)
        return render_doc_form(request, form, doc.project)
        
    else:
        
        form = DocForm(doc.project, request.POST, request.FILES, instance=doc)
        
        if form.is_valid():
            
            # update existing database model with form data
            doc = form.save()
            
            # update associated Bookmar, if any
            bookmark = getBookmarkFromDoc(doc)
            if bookmark is not None:
                bookmark.name = doc.title
                bookmark.description = doc.description
                bookmark.save()
                log.debug('Updated associated bookmark: %s' % bookmark)
            
            # redirect to document detail (GET-POST-REDIRECT)
            return HttpResponseRedirect(reverse('doc_detail', kwargs={'doc_id': doc.id}))
        
        else:
            return render_doc_form(request, form, doc.project)


def doc_list(request, project_short_name):
    
    project = get_object_or_404(Project, short_name__iexact=project_short_name)
    
    # query by project
    qset = Q(project=project)
    #list_title = 'All Documents'
    
    # do not list private documents unless user is a project member
    if request.user.is_anonymous() or not userHasUserPermission(request.user, project):
        qset = qset & Q(is_private=False)
    
    # optional query parameters
    query = request.GET.get('query', '')
    if query:
        qset = qset & (
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(path__icontains=query) 
        )
        #list_title = "Search Results for '%s'" % query    
        
    # document type        
    filter_by = request.GET.get('filter_by', DOCUMENT_TYPE_ALL)
    # validate 'filter_by' value
    if filter_by.lower() not in VALID_FILTER_BY_VALUES:
        raise Exception("Invalid 'filter_by' value")
    
    if filter_by != DOCUMENT_TYPE_ALL:
        types = DOCUMENT_TYPES[filter_by]
        _qset = Q(path__iendswith=types[0])
        for type in types[1:]:
            _qset = _qset | Q(path__iendswith=type)
        #list_title += ", type: %s, " % filter_by
        qset = qset & _qset
    
    order_by = request.GET.get('order_by', 'title')
    # validate 'order_by' value
    if order_by.lower() not in VALID_ORDER_BY_VALUES:
        raise Exception("Invalid 'order_by' value")
    #list_title += ", order by %s" % order_by
        
    # execute query, order by descending update date
    results = Doc.objects.filter(qset).distinct().order_by(order_by)
    list_title = "Total Number of Matching Documents: %d" % len(results)
   
    return render(request,
                  'cog/doc/doc_list.html', 
                  {"object_list": paginate(results, request, max_counts_per_page=100),
                   'project': project, 'title': '%s Files' % project.short_name,
                   "query": query, "order_by": order_by, "filter_by": filter_by, 
                   "list_title":list_title})


def render_doc_form(request, form, project):
    title = 'Upload %s File' % project.short_name
    return render(request,
                  'cog/doc/doc_form.html', 
                  {'form': form, 'project':project, 'title':title})