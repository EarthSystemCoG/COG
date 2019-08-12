import os
import urllib
import urllib2
import json

from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from social_django.utils import load_strategy

from cog.models.search import INVALID_CHARACTERS, ERROR_MESSAGE_INVALID_TEXT


def wget_script(request):
    
    certificate = get_certificate(request)
    
    dataset_id = request.GET.get('dataset_id')
    index_node = request.GET.get('index_node')
    shard = request.GET.get('shard')

    # maximum number of files to query for
    limit = request.GET.get('limit', 1000)

    params = [('type', "File"), ('dataset_id', dataset_id),
              ("format", "application/solr+json"), ('offset', '0'), ('limit', limit)]
    
    # optional query filter
    query = request.GET.get('query', None)
    if query is not None and len(query.strip()) > 0:
        # validate query value
        for c in INVALID_CHARACTERS:
            if c in query:
                return HttpResponseBadRequest(ERROR_MESSAGE_INVALID_TEXT, content_type="text/plain")
        params.append(('query', query))
        
    # optional shard
    shard = request.GET.get('shard', '')
    if shard is not None and len(shard.strip()) > 0:
        params.append(('shards', shard+"/solr"))
    else:
        params.append(("distrib", "false"))
 
    url = "http://"+index_node+"/esg-search/search?"+urllib.urlencode(params)
    fh = urllib2.urlopen(url)
    response = fh.read().decode("UTF-8")
    data = json.loads(response)

    download_urls = []
    try:
        for doc in data['response']['docs']:
            download_urls.append(doc['url'][0].split('|')[0])
    except (KeyError, IndexError) as e:
        raise e
    context = {
        'download_urls': download_urls,
        'certificate': certificate,
    }

    script = render_to_string('cog/download/wget_script.sh', context)

    response = HttpResponse(script, content_type='application/x-sh')
    response['Content-Disposition'] = 'attachment; filename="get_script.sh"'

    return response


def get_certificate(request):
    
    social = request.user.social_auth.get(provider='esgf')
    access_token = social.extra_data['access_token']
    strategy = load_strategy()
    backend = social.get_backend_instance(strategy)

    key, cert, _ = backend.get_certificate(access_token)
    return key + cert
