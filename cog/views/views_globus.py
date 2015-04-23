
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from nexus import GlobusOnlineRestClient
from cog.plugins.globus.transfer import submiTransfer, get_access_token, generateGlobusDownloadScript
from getpass import getpass
import urllib, urllib2
from cog.utils import getJson
from urlparse import urlparse
from cog.constants import SECTION_GLOBUS
from cog.site_manager import siteManager
import datetime
from constants import GLOBUS_NOT_ENABLED_MESSAGE

# download parameters
DOWNLOAD_METHOD_WEB = 'web'
DOWNLOAD_METHOD_SCRIPT = 'script'
DOWNLOAD_LIMIT = 10000 # default maximum number of files to download for each dataset

# session attribute keys
GLOBUS_DOWNLOAD_MAP = 'globus_download_map'
GLOBUS_ACCESS_TOKEN = 'globus_access_token'
GLOBUS_USERNAME = 'globus_username'

# external URLs
GLOBUS_NEXUS_URL = 'nexus.api.globusonline.org'
GLOBUS_OAUTH_URL = 'https://www.globus.org/OAuth'

# FIXME: map of (data_node:port, globus endpoint) pairs
GLOBUS_ENDPOINTS = {'esg-datanode.jpl.nasa.gov:2811':'esg#jpl',
				    'esg-vm.jpl.nasa.gov:2811':'esg#jpl'}

import os


@login_required
def download(request):
	'''
	View that initiates the Globus download workflow - either through the web, or through a script.
	This view collects the GridFTP URLs to be downloaded, then redirects to the view specific to the download method: web or script.
	Example URL: http://localhost:8000/globus/download/
	             ?dataset=obs4MIPs.NASA-JPL.AIRS.mon.v1%7Cesg-vm.jpl.nasa.gov@esg-datanode.jpl.nasa.gov
	             &dataset=obs4MIPs.NASA-JPL.MLS.mon.v1%7Cesg-datanode.jpl.nasa.gov@esg-datanode.jpl.nasa.gov
	             &method=web
	'''
	
	if not siteManager.isGlobusEnabled():
		return HttpResponseForbidden(GLOBUS_NOT_ENABLED_MESSAGE)
	
	# retrieve request parameters
	method = request.GET.get('method', DOWNLOAD_METHOD_WEB)
	datasets = request.GET.getlist('dataset', [])
	# maximum number of files to query for, if specified
	limit = request.GET.get('limit', DOWNLOAD_LIMIT)
	# optional query filter
	query = request.GET.get('query', None)
	
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
		for doc in jobj['response']['docs']:
			for url in doc['url']:
				# example URL: "gsiftp://esg-datanode.jpl.nasa.gov:2811//esg_dataroot/obs4MIPs/observations/atmos/husNobs/mon/grid/NASA-JPL/AIRS/v20110608/husNobs_AIRS_L3_RetStd-v5_200209-201105.nc|application/gridftp|GridFTP"
				parts = url.split('|')
				if parts[2].lower()=='gridftp':
					# example or urlparse output:
					# ParseResult(scheme=u'gsiftp', netloc=u'esg-datanode.jpl.nasa.gov:2811', path=u'//esg_dataroot/obs4MIPs/observations/atmos/husNobs/mon/grid/NASA-JPL/AIRS/v20110608/husNobs_AIRS_L3_RetStd-v5_200209-201105.nc', params='', query='', fragment='')
					o = urlparse(parts[0])
					hostname = str(o.netloc)
					if (hostname in GLOBUS_ENDPOINTS):
						gendpoint = GLOBUS_ENDPOINTS[hostname]
						if not gendpoint in download_map:
							download_map[gendpoint] = [] # insert empty list of URLs
						download_map[gendpoint].append( str(o.path).replace('//','/'))
					else:
						print 'WARNING: hostname %s is not mapped to any Globus Endpoint, URL %s cannot be downloaded' % (hostname, url)
						
	# store map in session
	request.session[GLOBUS_DOWNLOAD_MAP] = download_map
	print 'Stored Globus Download Map=%s at session scope' % download_map
	
	# redirect to Globus OAuth page
	if method==DOWNLOAD_METHOD_WEB:
				
		params = [ ('response_type','code'),
				   ('client_id', siteManager.get('PORTAL_GO_USERNAME', section=SECTION_GLOBUS)),
				   ('redirect_uri', request.build_absolute_uri(reverse("globus_token")) ),
				 ]
		
		globus_url = GLOBUS_OAUTH_URL + "?" + urllib.urlencode(params)
		
		# FIXME: fake the Globus URL
		globus_url = request.build_absolute_uri( reverse("globus_oauth") ) + "?" + urllib.urlencode(params)
	
		# redirect to Globus OAuth URL
		print "Redirecting to: %s" % globus_url
		#return HttpResponseRedirect(globus_url)
		return HttpResponse(download_map.items(), "text/plain") # FIXME
		
	# redirect to script generation view
	elif method==DOWNLOAD_METHOD_SCRIPT:
		return HttpResponseRedirect( reverse('globus_script') )
		
	# unknown download method request
	else:
		raise Exception("Unknown download method: %s" % method)
	
@login_required
def script(request):
	'''View to generate a Globus download script from the parameters stored at session scope.'''
	
	# retrieve files from session
	download_map = request.session[GLOBUS_DOWNLOAD_MAP]
	
	# return python script
	response = HttpResponse(content=generateGlobusDownloadScript(download_map))
	now = datetime.datetime.now()
	scriptName = "globus_download_%s.py" % now.strftime("%Y%m%d_%H%M%S")
	response['Content-Type']= "application/x-python"
	response['Content-Disposition'] = 'attachment; filename=%s' % scriptName
	return response
	
@login_required
# FIXME: not needed any more ?
def login(request):
	'''View that redirects to the GO authentication page.'''
	
	client_id = "jplesgnode"
	redirect_uri = request.build_absolute_uri( reverse("globus_token") )
	
	globus_url = "https://www.globus.org/OAuth?response_type=code&client_id=%s&redirect_uri=%s" % (client_id, redirect_uri)
	# FIXME: fake the Globus URL
	globus_url = request.build_absolute_uri( reverse("globus_oauth") ) + "?response_type=code&client_id=%s&redirect_uri=%s" % (client_id, redirect_uri)

	# redirect to Globus OAuth URL
	return HttpResponseRedirect(globus_url)

# FIXME: not needed any more when Globus web page is enabled
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
	
	# Note: 'code' is a one-time credential issued by Globus Nexus to CoG portal to act on the user behalf
	return HttpResponseRedirect( redirect_uri + "?code=%s" % code)

#FIXME: login required
#@login_required
def token(request):
	'''View that uses the request_token found in parameter 'code' to obtain an 'access_token' from Globus Online.'''
	
	# CoG portal
	# FIXME: instantiate at module scope ?
	#user_client = GlobusOnlineRestClient(config_file=os.path.join(os.path.expanduser("~"), 'user_client_config.yml'))
	user_client = GlobusOnlineRestClient(config={'server': GLOBUS_NEXUS_URL,
                                                 'client': siteManager.get('PORTAL_GO_USERNAME', section=SECTION_GLOBUS),
                                                 'client_secret': siteManager.get('PORTAL_GO_PASSWORD', section=SECTION_GLOBUS),
                                                 'verify_ssl':False,
                                                 'cache':{'class': 'nexus.token_utils.InMemoryCache', 'args': [],} 
                                             })

	code = request.GET['code']
	print 'Using globus code=%s' % code
	
	access_token, refresh_token, expires_in = user_client.goauth_get_access_token_from_code(code)
	print 'Got access token=%s' % access_token

	# validate access_token
	alias, client_id, nexus_host = user_client.goauth_validate_token(access_token)
	message = nexus_host + " claims this is a valid token issued by " + alias + " for " + client_id
	
	# store token into session
	request.session[GLOBUS_ACCESS_TOKEN] = access_token
	request.session[GLOBUS_USERNAME] = alias
	
	return HttpResponseRedirect( reverse('globus_transfer') )

@login_required
def transfer(request):
	'''View to submit a Globus transfer request.
	   The access token and files to download are retrieved from the session. '''
	
	# authentication parameters 
	# FIXME; retrieve parameters from previous web workflow
	#username = "cinquiniluca"
	username = request.session[GLOBUS_USERNAME]
	print 'globus username=%s' % username
	access_token = request.session[GLOBUS_ACCESS_TOKEN]
	
	# files to transfer
	# these are obtained from the GridFTP URls by removing the "gsiftp://<hostname:port>" part, which is implicit in the "esg#jpl" source endpoint configuration
	# FIXME: get file URLs from Data Cart
	#sourceFiles = ["/esg_dataroot/obs4MIPs/observations/atmos/husNobs/mon/grid/NASA-JPL/AIRS/v20110608/husNobs_AIRS_L3_RetStd-v5_200209-201105.nc",
	#				"/esg_dataroot/obs4MIPs/observations/atmos/taStderr/mon/grid/NASA-JPL/AIRS/v20110608/taStderr_AIRS_L3_RetStd-v5_200209-201105.nc"]
	
	download_map = request.session[GLOBUS_DOWNLOAD_MAP]
	print 'Downloading files=%s' % download_map.items()
	
	# loop over source endpoints, submit one transfer for each source endpoint
	task_ids = [] # list of submitted task ids
	for source_endpoint, source_files in download_map.items():
		print 'Download source=%s, %s' % (source_endpoint, source_files)

		# source endpoint - this is the JPL server
		# FIXME: get source_endppoint from GridFTP server name
		#source_endpoint = "esg#jpl"
		
		# target endpoint - this is the user own's laptop
		# FIXME: get target_endpoint from web workflow (user choice)
		target_endpoint = "cinquiniluca#mymac"
		
		# target directory to store files
		# FIXME: get target_endpoint from web workflow (user choice)
		target_directory = "/~" # is this a GO custom notation ?
	
		# submit transfer request
		task_id = submiTransfer(username, access_token, source_endpoint, source_files, target_endpoint, target_directory)
		
		task_ids.append(task_id)
	
	# return response
	text = "Task ids=%s submitted, monitor your task at: https://www.globus.org/xfer/ViewActivity" % task_ids
	return HttpResponse(text, content_type="text/plain")
	