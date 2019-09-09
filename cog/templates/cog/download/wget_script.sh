#!/bin/bash

{% for url in download_urls %}wget --certificate $0 {{ url }}
{% endfor %}

creds="
{{ certificate }}"
