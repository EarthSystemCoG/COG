from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from os import path
from string import Template
from models import *
from urllib import quote, unquote
from django.core.servers.basehttp import FileWrapper
import remap

# web for for browser-based invocation
def remap_form(request):
    
    weights_path = Template('${srcgrid}_${dstgrid}_${method}.nc')
    
    def form_view(request, form):
        return render_to_response('remap/remap_form.html',
                                  { 'title' : 'Grid Remapping Utility', 'form' : form, },
                                  context_instance=RequestContext(request))
    
    # before form submission
    if (request.method=='GET'):
         
         #job = RemapJob()
         #form = RemapForm(instance=job)
         return form_view(request, RemapForm() )
     
    # after form submission   
    else:
        form = RemapForm(request.POST)
        if form.is_valid(): 
            # override weights field value with file's full path
            #form.instance.weights = path.join(weights_path.substitute(srcgrid=path.splitext(form.cleaned_data['srcgrid'])[0],
            #                                                          dstgrid=path.splitext(form.cleaned_data['dstgrid'])[0],
            #                                                          method=form.cleaned_data['method'])
            #                                 )
                                            
            # return instance but do not save to database yet since object is incomplete
            remapjob = form.save(commit=False)              
            # assign weights field value with file's full path
            remapjob.weights = path.join(weights_path.substitute(srcgrid=path.splitext(form.cleaned_data['srcgrid'])[0],
                                                                 dstgrid=path.splitext(form.cleaned_data['dstgrid'])[0],
                                                                 method=form.cleaned_data['method']) )
            remapjob.save()

            return HttpResponseRedirect(reverse('remap_job', args=[quote(remapjob.srcgrid,''), 
                                                                   quote(remapjob.dstgrid,''), 
                                                                   quote(remapjob.method, ''),
                                                                   quote(remapjob.weights,'') ] ))
        else:
            print "Invalid Form %s" % form.errors
            return form_view(request, form)
        

# RESTful web service
def remap_job(request, srcgrid, dstgrid, weights, method):
    
    # must pass full paths to the remap function
    srcgrid = path.join(SRCGRID_DIR, unquote(srcgrid))
    dstgrid = path.join(DSTGRID_DIR, unquote(dstgrid))
    weights = path.join(WEIGHTS_DIR, unquote(weights))
    method  = unquote(method)
    
    status = remap.remap(srcgrid, dstgrid, weights, method=method)
    if status==0:

        # send the file as a binary attachment
        # the file wrapper turns the file into an iterator with 8KB chunks        
        wrapper = FileWrapper(file(weights))
        response = HttpResponse(wrapper, mimetype='application/octet-stream')
        response['Content-Length'] = path.getsize(weights)
        response['Content-Disposition'] = 'attachment; filename=%s' % path.basename(weights)
        return response

    else:
        return HttpResponse(status=500, content="An error occurred")
