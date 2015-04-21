
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from nexus import GlobusOnlineRestClient
from cog.plugins.globus.transfer import submiTransfer, get_access_token
from getpass import getpass

import os

@login_required
def login(request):
	'''View that redirects to the GO authentication page.'''
	
	client_id = "jplesgnode"
	redirect_uri = request.build_absolute_uri( reverse("globus_token") )
	
	globus_url = "https://www.globus.org/OAuth?response_type=code&client_id=%s&redirect_uri=%s" % (client_id, redirect_uri)
	# FIXME: fake the Globus URL
	globus_url = request.build_absolute_uri( reverse("globus_oauth") ) + "?response_type=code&client_id=%s&redirect_uri=%s" % (client_id, redirect_uri)

	# redirect to Globus OAuth URL
	return HttpResponseRedirect(globus_url)

def oauth(request):
	'''Temporary view that mimics the Globus OAuth page.'''
	
	client_id = request.GET['client_id']
	redirect_uri = request.GET['redirect_uri']
	print 'Issuing request_token for client_id=%s' % client_id
	
	# token can be re-used multiple times
	token = get_access_token()

	# CoG portal
	user_client = GlobusOnlineRestClient(config_file=os.path.join(os.path.expanduser("~"), 'user_client_config.yml'))
	
	# human user
	alias_client = GlobusOnlineRestClient(config_file=os.path.join(os.path.expanduser("~"), 'alias_client_config.yml'))
	
	# Validate the token:
	try:
		alias, client_id, nexus_host = alias_client.goauth_validate_token(token)
		print "Using valid token for alias=%s" % alias
	except:
		print "That is not a valid authorization code"
	
	print("As " + alias + ", get a request token for client " + user_client.client + " using rsa authentication:")
	response = alias_client.goauth_rsa_get_request_token(alias, user_client.client, lambda: getpass("Private Key Password"))
	# code can only be used once
	code = response['code']
	print 'Obtained request code=%s for identity=%s' % (code, user_client.client )
	
	return HttpResponseRedirect( redirect_uri + "?code=%s" % code)

#FIXME: login required
#@login_required
def token(request):
	'''View that uses the request_token found in parameter 'code' to obtain an 'access_token' from Globus Online.'''
	
	# CoG portal
	user_client = GlobusOnlineRestClient(config_file=os.path.join(os.path.expanduser("~"), 'user_client_config.yml'))

	code = request.GET['code']
	print 'Using globus code=%s' % code
	
	access_token, refresh_token, expires_in = user_client.goauth_get_access_token_from_code(code)
	print 'Got access token=%s' % access_token

	# validate access_token
	alias, client_id, nexus_host = user_client.goauth_validate_token(access_token)
	message = nexus_host + " claims this is a valid token issued by " + alias + " for " + client_id
	
	# store token into session
	request.session['globus_access_token'] = access_token
		
	return HttpResponse(message, content_type="text/plain")

@login_required
def transfer(request):
	'''View to submit a Globus transfer request.'''
	
	# authentication parameters 
	# FIXME; retrieve parameters from previous web workflow
	username = "cinquiniluca"
	access_token = request.session['globus_access_token']
	
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
	