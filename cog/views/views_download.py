import json
import requests

from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic import View
from social_django.utils import load_strategy


class WgetScriptView(View):
    """
    View for generating a wget shell script for downloading files from one or
    more datasets. The script includes a short-lived certificate retrieved from
    a social auth provider.
    """

    script_template = 'cog/download/wget_script.sh'
    search_limit = 10000

    def get(self, request, *args, **kwargs):
        """
        Get method for the view. Query parameters specify dataset IDs and which
        index to search on.
        """

        index_node = request.GET.get('index_node')
        index_node_url = 'http://{}/esg-search/search'.format(index_node)

        # Construct params for search request
        params = {
            'type': 'File',
            'format': 'application/solr+json',
            'offset': '0',
            'limit': self.search_limit
        }

        # Optional shard
        shard = request.GET.get('shard', '')
        if shard is not None and len(shard.strip()) > 0:
            params['shards'] = shard + '/solr'
        else:
            params['distrib'] = 'false'

        # Query index nodes for all file download urls for each dataset
        dataset_ids = request.GET.getlist('dataset_id')
        download_urls = []
        for dataset_id in dataset_ids:
            params['dataset_id'] = dataset_id
            response = requests.get(url=index_node_url, params=params)
            download_urls += self._parse_download_urls(response.json())

        # Request a short-lived certificate to be placed in the script
        certificate = self._get_certificate(request)

        script = render_to_string(self.script_template,
            { 'download_urls': download_urls, 'certificate': certificate }
        )
        response = HttpResponse(script, content_type='application/x-sh')

        # Specify downloaded file name
        script_timestamp = timezone.now().strftime('%Y%m%d%f')
        response['Content-Disposition'] = \
            'attachment; filename="wget-{}.sh"'.format(script_timestamp)

        return response

    @staticmethod
    def _parse_download_urls(data):
        """
        Parses the output of an index search request.

        Returns a list of urls
        """

        download_urls = []
        try:
            for doc in data['response']['docs']:
                download_urls.append(doc['url'][0].split('|')[0])
        except (KeyError, IndexError) as e:
            raise e

        return download_urls

    @staticmethod
    def _get_certificate(request):
        """
        Generates a short-lived certificate from the user's session.
        The user must have been authenticated with the 'esgf' social auth
        provider.

        Returns a pem-style certificate
        """

        social = request.user.social_auth.get(provider='esgf')
        access_token = social.extra_data['access_token']
        strategy = load_strategy()
        backend = social.get_backend_instance(strategy)

        key, cert, _ = backend.get_certificate(access_token)
        return key + cert
