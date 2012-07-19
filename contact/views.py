from django.conf import settings
from django.core.mail import send_mail
from models import ContactForm
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

def contact_form(request):
    
    # GET
    if request.method == 'GET': 
         form = ContactForm() # unbound form
         return render_to_response('contact/contact.html', {'form': form,}, context_instance=RequestContext(request))
    # POST
    else: 
        form = ContactForm(request.POST) # bound form
        if form.is_valid():
            # user bound data in form.clean_data 
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            cc_myself = form.cleaned_data['cc_myself']
            recipients = [settings.CONTACT_EMAIL]
            if cc_myself:
                recipients.append(sender)
            send_mail(subject, message, sender, recipients, fail_silently=True)
            return HttpResponseRedirect( reverse('contact_thanks') )
        else:
            return render_to_response('contact/contact.html', {'form': form,}, context_instance=RequestContext(request))
        

