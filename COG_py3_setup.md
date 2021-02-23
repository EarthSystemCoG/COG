
#  Manual CoG Upgrade Instructions for Python3/Django2

Use these steps if you need to upgrade an existing ESGF installation that is running Python2 CoG.  A key assumption is that CoG is already set up with the PostgreSQL database and settings file.



## Install required libraries for CoG
    yum install httpd-devel  sqlite-devel

## Update cog repo
    cd /usr/local/cog/cog_install
    Git checkout python3_cog  


## Create CoG conda env

   source /usr/local/conda/etc/profile.d/conda.sh
   conda create -y -n cog_py3 'python>=3.7,<3.9' pip

##  Activate Conda Env for COG. 
#### Note you should have the environment activated for all subsequent commands
    conda activate cog_py3


## Install CoG Requirments

    pip install 'mod_wsgi' 'git+https://github.com/edx-unsupported/django-openid-auth' -r requirements.txt

##  Clone Transfer API Client Repo
   cd /usr/local/cog
   git clone https://github.com/globusonline/transfer-api-client-python.git"


## Make and Install mkproxy
    
  cd transfer-api-client-python/mkproxy"
  conda activate cog_py3
  make && make install


## Install CoG into conda env

    python setup.py --quiet install


## Ensure old COG is stopped. move aside
    cd /etc

    cog-wsgi-8889/apachectl stop
    mv cog-wsgi-8889 cog-wsgi-8889-old

## Setup CoG mod_wsgi-express server
    cd /usr/local/cog/cog_install

    mod_wsgi-express setup-server apache/wsgi.py \
    --server-root /etc/cog-wsgi-8889 \
    --user apache --group apache \
    --host localhost --port 8889 \
    --url-alias /static /usr/local/cog/cog_install/static/


## Set Ownership

    chown -R apache:apache /usr/local/cog

