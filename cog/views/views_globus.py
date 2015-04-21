
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from nexus import GlobusOnlineRestClient
from cog.plugins.globus.transfer import submiTransfer, get_access_token

import os

@login_required
def login(request):

	# FIXME: must redirect to Globus OAuth instead
	
	# FIXME: read token from file
	code = 'xxx'
	return HttpResponseRedirect(reverse('globus_token')+'?code=%s' % code)

@login_required
def token(request):
	
	#code = request.GET['code']
	#code = ''
	#print 'Globus: code=%s' % code
	
	# use 'code' to get an access token
	#pwd = os.path.dirname(__file__)
	# FIXME: use dictionary instead
	#user_client = GlobusOnlineRestClient(config_file=os.path.join(pwd, 'user_client_config.yml'))
	#print("As " + user_client.client + ", get an access key from code:")
	
	#access_token = 'xyz'
	#access_token, refresh_token, expires_in = user_client.goauth_get_access_token_from_code(code)
	#print 'Globus: access token=%s' % access_token
	
	return HttpResponse("This is the CoG-Globus token page", content_type="text/plain")

@login_required
def transfer(request):
	'''View to submit a Globus transfer request.'''
	
	# authentication parameters 
	# FIXME; retrieve parameters from previous web workflow
	username = "cinquiniluca"
	access_token = get_access_token()
	
	# files to transfer
	# these are obtained from the GridFTP URls by removing the "gsiftp://<hostname:port>" part, which is implicit in the "esg#jpl" source endpoint configuration
	# FIXME: get file URLs from Data Cart
	sourceFiles = ["/esg_dataroot/obs4MIPs/observations/atmos/husNobs/mon/grid/NASA-JPL/AIRS/v20110608/husNobs_AIRS_L3_RetStd-v5_200209-201105.nc",
				   "/esg_dataroot/obs4MIPs/observations/atmos/taStderr/mon/grid/NASA-JPL/AIRS/v20110608/taStderr_AIRS_L3_RetStd-v5_200209-201105.nc"]

	# source endpoint - this is the JPL server
	# FIXME: get source_endppoint from GridFTP server name
	source_endpoint = "esg#jpl"
	
	# target endpoint - this is the user own's laptop
	# FIXME: get target_endpoint from web workflow (user choice)
	target_endpoint = "cinquiniluca#mymac"
	
	# target directory to store files
	# FIXME: get target_endpoint from web workflow (user choice)
	target_directory = "/~" # is this a GO custom notation ?

	# submit transfer request
	task_id = submiTransfer(username, access_token, source_endpoint, sourceFiles, target_endpoint, target_directory)
	
	# return response
	text = "Task id=%s submitted, monitor your task at: https://www.globus.org/xfer/ViewActivity" % task_id
	return HttpResponse(text, content_type="text/plain")
	