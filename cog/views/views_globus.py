from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import render
from django.template import RequestContext
import urllib
from cog.utils import getJson
from urlparse import urlparse
from cog.constants import SECTION_GLOBUS
from cog.site_manager import siteManager
import datetime
from constants import GLOBUS_NOT_ENABLED_MESSAGE
from functools import wraps
import os
import re
from openid.yadis.services import getServiceEndpoints
from openid.yadis.discover import DiscoveryFailure
from cog.views.utils import getQueryDict

# download parameters
DOWNLOAD_METHOD_WEB = 'web'
DOWNLOAD_METHOD_SCRIPT = 'script'
DOWNLOAD_LIMIT = 10000 # default maximum number of files to download for each dataset

# session attribute keys
GLOBUS_DOWNLOAD_MAP = 'globus_download_map'
GLOBUS_ACCESS_TOKEN = 'globus_access_token'
GLOBUS_USERNAME = 'globus_username'
TARGET_ENDPOINT = 'target_endpoint'
TARGET_FOLDER = 'target_folder'
ESGF_USERNAME = 'username'
ESGF_PASSWORD = 'password'

# external URLs
GLOBUS_SELECT_DESTINATION_URL = 'https://app.globus.org/file-manager'
GLOBUS_AUTH_URL = 'https://auth.globus.org'

if siteManager.isGlobusEnabled():

	from base64 import urlsafe_b64encode
	from oauth2client import client as oauth_client
	from cog.plugins.globus.transfer import activateEndpoint, submitTransfer, generateGlobusDownloadScript
	from globusonline.transfer.api_client import TransferAPIClient

	client_id = siteManager.get('OAUTH_CLIENT_ID', section=SECTION_GLOBUS)
	client_secret = siteManager.get('OAUTH_CLIENT_SECRET', section=SECTION_GLOBUS)


def discover_myproxy(openid):
	try:
		uri, endpoints = getServiceEndpoints(openid)
	except DiscoveryFailure:
		return None
	for e in endpoints:
		if e.matchTypes(['urn:esg:security:myproxy-service']):
			myproxy_url_parsed = urlparse(e.uri)
			return myproxy_url_parsed.hostname
	return None


def establishFlow(request):
	basic_auth_str = urlsafe_b64encode("{}:{}".format(client_id, client_secret))
	auth_header = "Basic " + basic_auth_str
	return oauth_client.OAuth2WebServerFlow(
		client_id = client_id,
		authorization_header = auth_header,
		scope = ['openid', 'profile', 'urn:globus:auth:scope:transfer.api.globus.org:all'],
		redirect_uri = request.build_absolute_uri(reverse("globus_token")).replace('http:','https:'),
		auth_uri = GLOBUS_AUTH_URL + '/v2/oauth2/authorize',
		token_uri = GLOBUS_AUTH_URL + '/v2/oauth2/token')


def requires_globus(view_func):
	'''
	Custom decorator that prevents a view to be invoked unless this node
	is configured with a [Globus] section in cog_settings.py.
	'''
	
	def _decorator(request, *args, **kwargs):
		
		if siteManager.isGlobusEnabled():
			return view_func(request, *args, **kwargs)
		else:
			return HttpResponseForbidden(GLOBUS_NOT_ENABLED_MESSAGE)
	
	return wraps(view_func)(_decorator)
	

@requires_globus
@login_required
def download(request):
	'''
	View that initiates the Globus download workflow by collecting and optionally sub-selecting the GridFTP URLs to be downloaded.
	This view can be invoked via GET (link from search page, one dataset only) or POST (link from data cart page, multiple datasets at once).
	Example URL: http://localhost:8000/globus/download/
	             ?dataset=obs4MIPs.NASA-JPL.AIRS.mon.v1%7Cesg-vm.jpl.nasa.gov@esg-datanode.jpl.nasa.gov,obs4MIPs.NASA-JPL.MLS.mon.v1%7Cesg-datanode.jpl.nasa.gov@esg-datanode.jpl.nasa.gov
	             &method=web
	'''
		
	# retrieve request parameters
	datasets = getQueryDict(request).get('dataset','').split(",")
	# optional query filter
	query = getQueryDict(request).get('query',None)
	# maximum number of files to query for, if specified
	limit = request.GET.get('limit', DOWNLOAD_LIMIT)
	
	# map of (data_node, list of GridFTP URLs to download)
	download_map = {}
	
	# loop over requested datasets
	for dataset in datasets:
		
		# query each index_node for all files belonging to that dataset
		(dataset_id, index_node) = str(dataset).split('@')
		
		params = [ ('type',"File"), ('dataset_id',dataset_id),
				   ('offset','0'), ('limit',limit), ('fields','url'), ("format", "application/solr+json") ]
		
		if query is not None and len(query.strip())>0:
			params.append( ('query', query) )
			
		# optional shard
		shard = request.GET.get('shard', '')
		if shard is not None and len(shard.strip()) > 0:
			params.append(('shards', shard+"/solr"))  # '&shards=localhost:8982/solr'
		else:
			params.append(("distrib", "false"))

			
		url = "http://"+index_node+"/esg-search/search?"+urllib.urlencode(params)
		print 'Searching for files at URL: %s' % url
		jobj = getJson(url)
		
		# parse response for GridFTP URls
		if jobj is not None:
			for doc in jobj['response']['docs']:
				access = {}
				for url in doc['url']:
					# example URLs:
					# 'http://esg-datanode.jpl.nasa.gov/thredds/fileServer/esg_dataroot/obs4MIPs/observations/atmos/husNobs/mon/grid/NASA-JPL/AIRS/v20110608/husNobs_AIRS_L3_RetStd-v5_200209-201105.nc|application/netcdf|HTTPServer'
					# 'http://esg-datanode.jpl.nasa.gov/thredds/dodsC/esg_dataroot/obs4MIPs/observations/atmos/husNobs/mon/grid/NASA-JPL/AIRS/v20110608/husNobs_AIRS_L3_RetStd-v5_200209-201105.nc.html|application/opendap-html|OPENDAP'
					# 'globus:8a3f3166-e9dc-11e5-97d6-22000b9da45e//esg_dataroot/obs4MIPs/observations/atmos/husNobs/mon/grid/NASA-JPL/AIRS/v20110608/husNobs_AIRS_L3_RetStd-v5_200209-201105.nc|Globus|Globus'
					# 'gsiftp://esg-datanode.jpl.nasa.gov:2811//esg_dataroot/obs4MIPs/observations/atmos/husNobs/mon/grid/NASA-JPL/AIRS/v20110608/husNobs_AIRS_L3_RetStd-v5_200209-201105.nc|application/gridftp|GridFTP'
					parts = url.split('|')
					access[parts[2].lower()] = parts[0]
				if 'globus' in access:
					m = re.match('globus:([^/]*)(.*)', access['globus'])
					if m:
						gendpoint_name = m.group(1)
						path = m.group(2)
						if not gendpoint_name in download_map:
							download_map[gendpoint_name] = [] # insert empty list of paths
						download_map[gendpoint_name].append(path)
				else:
					print 'The file is not accessible through Globus'
		else:
			return HttpResponseServerError("Error querying for files URL")
						
	# store map in session
	request.session[GLOBUS_DOWNLOAD_MAP] = download_map
	print 'Stored Globus Download Map=%s at session scope' % download_map
	
	# redirect after post (to display page)
	return HttpResponseRedirect( reverse('globus_transfer') )

@requires_globus
@login_required
def transfer(request):
	'''View that initiates a Globus data transfer request.'''
	
	if request.method=='GET':
		
		# retrieve files from session
		download_map = request.session[GLOBUS_DOWNLOAD_MAP]

		# display the same page as resulting from data cart invocation
		return render(request,
                      'cog/globus/transfer.html', 
	    			  { GLOBUS_DOWNLOAD_MAP: download_map, 'title':'Globus Download' })	
		
	else:
						
		# redirect to Globus OAuth URL
		params = [ ('method','get'), ('folderlimit','1'),
				   # ('lock', 'ep'), # do NOT allow the user to change their endpoint
				   ('action', request.build_absolute_uri(reverse("globus_oauth")) ), # redirect to CoG Oauth URL
				 ]
		globus_url = GLOBUS_SELECT_DESTINATION_URL + "?" + urllib.urlencode(params)
		print "Redirecting to: %s" % globus_url
		return HttpResponseRedirect(globus_url)
		# replacement URL for localhost development
		#return HttpResponseRedirect( request.build_absolute_uri(reverse("globus_oauth")) ) # FIXME
		
		
@requires_globus
@login_required
def oauth(request):
	
	# retrieve destination parameters from Globus redirect
	# example URL with added parameters from Globus redirect: 
	# /globus/oauth/?label=&verify_checksum=on&submitForm=&folder[0]=tmp&endpoint=cinquiniluca#mymac&path=/~/&ep=GC&lock=ep&method=get&folderlimit=1&action=http://localhost:8000/globus/oauth/
	request.session[TARGET_ENDPOINT] = getQueryDict(request).get('endpoint','#')
	request.session[TARGET_FOLDER] = getQueryDict(request).get('path','/~/') + getQueryDict(request).get('folder[0]', '')  # default value: user home directory
	print 'User selected destionation endpoint:%s, path:%s, folder:%s' % (request.session[TARGET_ENDPOINT], getQueryDict(request).get('path','/~/'), getQueryDict(request).get('folder[0]', ''))

	# Redirect the user to Globus OAuth server to get an authorization code if the user approves the access request.
	globus_authorize_url = establishFlow(request).step1_get_authorize_url()
	print "Redirecting to: %s" % globus_authorize_url
	return HttpResponseRedirect(globus_authorize_url)


@requires_globus
@login_required
def token(request):
	'''View that uses the request_token found in parameter 'code' (can only be used once) 
	   to obtain an 'access_token' from Globus (can be used multiple times).'''

	# use 'code' to obtain an 'access_token'
	globus_auth_code = request.GET['code']
	#print 'Globus OAuth code: %s' % globus_auth_code

	globus_credentials = establishFlow(request).step2_exchange(globus_auth_code)
	id_token = globus_credentials.id_token
	access_token = None
	other_tokens = globus_credentials.token_response['other_tokens']
	for token in other_tokens:
		if token['scope'] == 'urn:globus:auth:scope:transfer.api.globus.org:all':
			access_token = token['access_token']
			break
	#print 'id_token: %s, access_token: %s' % (id_token, access_token)

	# store token into session
	request.session[GLOBUS_ACCESS_TOKEN] = access_token
	request.session[GLOBUS_USERNAME] = id_token['preferred_username']

	return HttpResponseRedirect( reverse('globus_submit') )


@requires_globus
@login_required
def submit(request):
	'''View to submit a Globus transfer request.
	   The access token and files to download are retrieved from the session. '''

	openid = request.user.profile.openid()
	openid_parsed = urlparse(openid)
	hostname = openid_parsed.hostname
	# get a username and password if autoactivation failed and a user was asked for a password
	if hostname == "ceda.ac.uk":
		myproxy_server = discover_myproxy(openid)
		esgf_username = request.POST.get(ESGF_USERNAME)
	else:
		myproxy_server = hostname
		esgf_username = os.path.basename(openid_parsed.path)
	esgf_password = request.POST.get(ESGF_PASSWORD)
	# retrieve all data transfer request parameters from session
	username = request.session.get(GLOBUS_USERNAME)
	access_token = request.session.get(GLOBUS_ACCESS_TOKEN)
	download_map = request.session.get(GLOBUS_DOWNLOAD_MAP)
	target_endpoint = request.session.get(TARGET_ENDPOINT)
	target_folder = request.session.get(TARGET_FOLDER)

	#print 'Downloading files=%s' % download_map.items()
	print 'User selected destionation endpoint:%s, folder: %s' % (target_endpoint, target_folder)

	api_client = TransferAPIClient(username, goauth=access_token)
	# loop over source endpoints and autoactivate them
	# if the autoactivation fails, redirect to a form asking for a password
	activateEndpoint(api_client, target_endpoint)
	for source_endpoint, source_files in download_map.items():
		status, message = activateEndpoint(
			api_client, source_endpoint,
			myproxy_server=myproxy_server, username=esgf_username, password=esgf_password)
		if not status:
                        print hostname
			return render(request,
                          'cog/globus/password.html',
                          { 'openid': openid, 'username': hostname=='ceda.ac.uk', 'message': message })

	# loop over source endpoints, submit one transfer for each source endpoint
	task_ids = []  # list of submitted task ids
	for source_endpoint, source_files in download_map.items():
			
		# submit transfer request
		task_id = submitTransfer(
			api_client, source_endpoint, source_files,
			target_endpoint, target_folder)
		task_ids.append(task_id)
	
	# display confirmation page
	return render(request,
                  'cog/globus/confirmation.html',
				  { 'task_ids':task_ids, 'title':'Globus Download Confirmation' })	


@requires_globus
@login_required
def script(request):
	'''View to generate a Globus download script from the parameters stored at session scope.'''
		
	# retrieve files from session
	download_map = request.session[GLOBUS_DOWNLOAD_MAP]
	
	# return python script
	content = generateGlobusDownloadScript(download_map)
	response = HttpResponse( content )
	now = datetime.datetime.now()
	scriptName = "globus_download_%s.py" % now.strftime("%Y%m%d_%H%M%S")
	response['Content-Type']= "application/x-python"
	response['Content-Disposition'] = 'attachment; filename=%s' % scriptName
	response['Content-Length'] = len(content)
	return response
