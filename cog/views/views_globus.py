
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext
import urllib
from cog.utils import getJson
from urlparse import urlparse
from cog.constants import SECTION_GLOBUS
from cog.site_manager import siteManager
import datetime
from constants import GLOBUS_NOT_ENABLED_MESSAGE
from functools import wraps
from cog.plugins.esgf.registry import LocalEndpointDict
import os
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

# external URLs
GLOBUS_NEXUS_URL = 'nexus.api.globusonline.org'
GLOBUS_SELECT_DESTINATION_URL = 'https://www.globus.org/xfer/BrowseEndpoint'
GLOBUS_OAUTH_URL = 'https://www.globus.org/OAuth'

if siteManager.isGlobusEnabled():	
	from nexus import GlobusOnlineRestClient
	from getpass import getpass
	from cog.plugins.globus.transfer import submiTransfer, get_access_token, generateGlobusDownloadScript
	endpoints_filepath = siteManager.get('ENDPOINTS', section=SECTION_GLOBUS)
	GLOBUS_ENDPOINTS= LocalEndpointDict(endpoints_filepath)

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
		
		params = [ ('type',"File"), ('dataset_id',dataset_id), ("distrib", "false"),
				   ('offset','0'), ('limit',limit), ('fields','url'), ("format", "application/solr+json") ]
		if query is not None and len(query.strip())>0:
			params.append( ('query', query) )
			
		url = "http://"+index_node+"/esg-search/search?"+urllib.urlencode(params)
		print 'Searching for files at URL: %s' % url
		jobj = getJson(url)
		
		# parse response for GridFTP URls
		if jobj is not None:
			for doc in jobj['response']['docs']:
				for url in doc['url']:
					# example URL: "gsiftp://esg-datanode.jpl.nasa.gov:2811//esg_dataroot/obs4MIPs/observations/atmos/husNobs/mon/grid/NASA-JPL/AIRS/v20110608/husNobs_AIRS_L3_RetStd-v5_200209-201105.nc|application/gridftp|GridFTP"
					parts = url.split('|')
					if parts[2].lower()=='gridftp':
						# example or urlparse output:
						# ParseResult(scheme=u'gsiftp', netloc=u'esg-datanode.jpl.nasa.gov:2811', path=u'//esg_dataroot/obs4MIPs/observations/atmos/husNobs/mon/grid/NASA-JPL/AIRS/v20110608/husNobs_AIRS_L3_RetStd-v5_200209-201105.nc', params='', query='', fragment='')
						o = urlparse(parts[0])
						hostname = str(o.netloc)
						epDict = GLOBUS_ENDPOINTS.endpointDict()
						# {'esg-datanode.jpl.nasa.gov:2811':'esg#jpl',
						#  'esg-vm.jpl.nasa.gov:2811':'esg#jpl'}
						if (hostname in epDict):
							gendpoint_name = epDict[hostname].name
							gendpoint_path_out = epDict[hostname].path_out
							gendpoint_path_in = epDict[hostname].path_in
							if not gendpoint_name in download_map:
								download_map[gendpoint_name] = [] # insert empty list of URLs
							gfilepath = str(o.path).replace('//','/')
							if gendpoint_path_out is not None:
								gfilepath = gfilepath.replace(gendpoint_path_out, '')
							if gendpoint_path_in is not None:
								gfilepath = gendpoint_path_in + gfilepath
							download_map[gendpoint_name].append(gfilepath)
						else:
							print 'WARNING: hostname %s is not mapped to any Globus Endpoint, URL %s cannot be downloaded' % (hostname, url)
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
		return render_to_response('cog/globus/transfer.html', 
	    						  { GLOBUS_DOWNLOAD_MAP: download_map, 'title':'Globus Download' },
	    						  context_instance=RequestContext(request))	
		
	else:
						
		# redirect to Globus OAuth URL
		params = [ ('ep','GC'), ('method','get'), ('folderlimit','1'),
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
	request.session[TARGET_FOLDER] = getQueryDict(request).get('path','/~/') + getQueryDict(request).get('folder[0]','/~/')  # default value: user home directory
	print 'User selected destionation endpoint:%s, path:%s, folder:%s' % (request.session[TARGET_ENDPOINT], getQueryDict(request).get('path','/~/'), request.session[TARGET_FOLDER])
	
	params = [ ('response_type','code'),
		       ('client_id', siteManager.get('PORTAL_GO_USERNAME', section=SECTION_GLOBUS)),
		       ('redirect_uri', request.build_absolute_uri(reverse("globus_token")).replace('http:','https:') ),] # MUST force 'https' protocol
	
	globus_url = GLOBUS_OAUTH_URL + "?" + urllib.urlencode(params)
	# FIXME: fake the Globus URL
	#globus_url = request.build_absolute_uri( reverse("globus_oauth2") ) + "?" + urllib.urlencode(params)

	# redirect to Globus OAuth URL
	print "Redirecting to: %s" % globus_url
	return HttpResponseRedirect(globus_url)
	
@requires_globus
@login_required
def oauth2(request):
	'''View that mimics the Globus OAuth page. Not ordinarily invoked unless developing on localhost.'''
	
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
		raise Exception("That is not a valid authorization code")
	
	print("As " + alias + ", get a request token for client " + user_client.client + " using rsa authentication:")
	response = alias_client.goauth_rsa_get_request_token(alias, user_client.client, lambda: getpass("Private Key Password"))
	
	# code can only be used once
	code = response['code']
	print 'Obtained request code=%s for identity=%s' % (code, user_client.client )
	
	# Note: 'code' is a one-time credential issued by Globus Nexus to CoG portal to act on the user behalf
	return HttpResponseRedirect( redirect_uri + "?code=%s" % code)


@requires_globus
@login_required
def token(request):
	'''View that uses the request_token found in parameter 'code' (can only be used once) 
	   to obtain an 'access_token' from Globus (can be used multiple times).'''
	
	# CoG portal
	# FIXME: instantiate at module scope ?
	#user_client = GlobusOnlineRestClient(config_file=os.path.join(os.path.expanduser("~"), 'user_client_config.yml'))
	user_client = GlobusOnlineRestClient(config={'server': GLOBUS_NEXUS_URL,
                                                 'client': siteManager.get('PORTAL_GO_USERNAME', section=SECTION_GLOBUS),
                                                 'client_secret': siteManager.get('PORTAL_GO_PASSWORD', section=SECTION_GLOBUS),
                                                 'verify_ssl':False,
                                                 'cache':{'class': 'nexus.token_utils.InMemoryCache', 'args': [],} 
                                             })

	# use 'code' to obtain an 'access_token'
	code = request.GET['code']	
	access_token, refresh_token, expires_in = user_client.goauth_get_access_token_from_code(code)

	# validate access_token
	alias, client_id, nexus_host = user_client.goauth_validate_token(access_token)
	print "%s claims this is a valid token issued by %s for %s" % (nexus_host, alias, client_id)
	
	# store token into session
	request.session[GLOBUS_ACCESS_TOKEN] = access_token
	request.session[GLOBUS_USERNAME] = alias
	
	return HttpResponseRedirect( reverse('globus_submit') )

@requires_globus
@login_required
def submit(request):
	'''View to submit a Globus transfer request.
	   The access token and files to download are retrieved from the session. '''
	
	# retrieve all data transfer request parameters from session
	username = request.session[GLOBUS_USERNAME]
	access_token = request.session[GLOBUS_ACCESS_TOKEN]
	download_map = request.session[GLOBUS_DOWNLOAD_MAP]
	target_endpoint = request.session[TARGET_ENDPOINT]
	target_folder = request.session[TARGET_FOLDER]
	
	print 'Downloading files=%s' % download_map.items()
	print 'User selected destionation endpoint:%s, folder: %s' % (target_endpoint, target_folder)

	# loop over source endpoints, submit one transfer for each source endpoint
	task_ids = [] # list of submitted task ids
	for source_endpoint, source_files in download_map.items():
			
		# submit transfer request
		task_id = submiTransfer(username, access_token, source_endpoint, source_files, target_endpoint, target_folder)
		
		task_ids.append(task_id)
	
	# display confirmation page
	return render_to_response('cog/globus/confirmation.html', 
						     { 'task_ids':task_ids, 'title':'Globus Download Confirmation' },
						        context_instance=RequestContext(request))	

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