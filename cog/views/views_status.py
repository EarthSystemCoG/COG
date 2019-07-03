from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.forms.models import modelformset_factory, inlineformset_factory
import string
import os, json
from django.conf import settings


def node_status(request):

    if not getattr(settings, 'HAS_DATANODE_STATUS', False):
        return	render(request, 'cog/status/node_status.html', { 'no_status' : True } )

    try:

        dnstatusfn = getattr(settings, 'DATANODE_STATUS_FILE', None)
        dnstatus = json.load(open(dnstatusfn))
    except Exception as e:
        return HttpResponseServerError("Error querying for files URL")

    status_arr = []

    for n in sorted(dnstatus):

    	status_arr.append((n, dnstatus[n]["status"], dnstatus[n]["time"]))

    return render(request, 'cog/status/node_status.html', { 'status_arr' : status_arr } )


