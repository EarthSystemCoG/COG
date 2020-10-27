
Installation: Install or Upgrade
================================

NOTE: If installing CoG through the ESGF Installer, all these steps will
be executed automatically. If not using the ESGF Installer, please read
on.

Step 1: Activate the CoG Python virtual environment
---------------------------------------------------

.. code:: console

   cd $COG_DIR 
   source venv/bin/activate 
   which python 
   RESULT: ~/COG/venv/bin/python

This will show that the python installation used is located into the
venv sub-directory

Note: to later deactivate the Python virtual environment:

.. code:: console

   deactivate

Step 2: Checkout the CoG software stack
---------------------------------------

First time installation only: checkout CoG from the GitHub repository:

.. code:: console


   cd $COG_DIR 
   git clone git@github.com:EarthSystemCoG/COG.git cog_install
   or: 
   # cloning via https will prompt for username and password 
   git clone https://github.com/EarthSystemCoG/COG cog_install

Every time (first time installation or upgrade): checkout a specific CoG
tag or branch:


.. code:: console

   cd $COG_INSTALL_DIR 
   git checkout master 
   git pull 
   git checkout v2.6.2 
   # or if developing CoG, checkout the appropriate branch 
   # git checkout -b devel origin/devel

Step 3: Install CoG and dependencies
------------------------------------


.. code:: console

   cd $COG_INSTALL_DIR 
   python setup.py install

This will install MOST necessary CoG dependencies under the CoG python
installation in the location $COG_DIR/venv/lib/python2.7/site-packages,
but a few of them must be installed manually, see below.

Step 4: Install patched version of django-openid-auth
-----------------------------------------------------

The module django-openid-auth must be installed from a fork to be
compatible with Django 1.9+


.. code:: console

   cd $COG_DIR 
   git clone https://github.com/EarthSystemCoG/django-openid-auth.git 
   cd django-openid-auth 
   python setup.py install

Step 4a: Install mkproxy (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If enabling Globus support, the mkproxy executable (used to activate
Globus endpoints) must be manually compiled and installed:


.. code:: console

   cd $COG_DIR 
   git clone https://github.com/globusonline/transfer-api-client-python.git 
   cd transfer-api-client-python/mkproxy/ 
   make 
   cp mkproxy $COG_VIRTUALENV/lib/python2.7/site-packages/globusonline_transfer_ api_client-0.10.16-py2.7.egg/globusonline/transfer/api_client/x509_proxy/

Step 5: Configure CoG
---------------------

Step 5a: To configure CoG WITHOUT an ESGF node (e.g. –esgf=false)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: console

   cd $COG_INSTALL_DIR 
   python setup.py setup_cog –esgf=false


This will:

-  will create a startup sqllite database under $COG_CONFIG_DIR/django.data
-  if installing for the first time, it will create a "TestProject" and make that the CoG home project
-  if installing for the first time, it will create a super-user "rootAdmin" with password "changeit"

Step 5b: To configure CoG with an ESGF node (e.g. –esgf=true)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: console


   cd $COG_INSTALL_DIR
   python setup.py setup_cog --esgf=true


This will:

-  will create a CoG database onto the existing ESGF Postgres
   installation, if not existing already
-  if installing for the first time, it will create a “TestProject” and
   make that the CoG home project
-  if installing for the first time, it will create a super-user
   “rootAdmin” that matches the existing Node Administrator, if
   possible:

   -  the “rootAdmin” password is taken from the standard ESGF file
      /esg/config/.esgf_pass. If this file is not found, the “rootAdmin”
      password is set to “changeit”
   -  the “rootAdmin” openid is set to
      ’https:///esgf-idp/openid/rootAdmin in the CoG database. If this
      openid does NOT exist already in the ESGF database (which should
      NOT be the case), a corresponding ESGF “rootAdmin” account is
      created.

Either step will:

-  if installing for the first time, create the node configuration file
   underCOG_CONFIG_DIR/cog_settings.cfg; otherwise, it will read the
   latest values from the configuration file.
-  upgrade the CoG database to the latest version, if necessary
   (i.e. run “manage.py syncdb” and “manage.py migrate cog”)
-  copy all CoG system media to $COG_INSTALL_DIR/static (i.e. run
   “manage.py collectstatic”)
-  will also update the local node name as specified in the
   cog_settings.cfg file
-  will also update the list of available peer nodes from the file
   cog/management/commands/sites.xml

Step 6: Modify configuration file
---------------------------------


.. code:: console

   python setup.py setup_cog –esgf=true

-  SITE_DOMAIN = localhost:8000
-  DEBUG = True
-  PRODUCTION_SERVER = False
-  IDP_REDIRECT =
-  Run install again:


.. code:: console

   python setup.py install

Step 7: Check Django Admin for empty Site
-----------------------------------------

It is possible there will be an empty row in the Django Admin -> Sites
screen besides local host. If so remove this row.

Step 8: Remove potential Python conflicts
-----------------------------------------


.. code:: console

   rm -rf $COG_DIR/venv/lib/python2.7/site-packages/cog*

will remove CoG from the python site-packages library, to avoid
conflicts with the source installation in $COG_INSTALL_DIR
