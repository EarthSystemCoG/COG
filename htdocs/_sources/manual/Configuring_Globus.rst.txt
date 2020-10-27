
Configuring Globus
==================

Configuring ESGF/CoG with Globus Downloads
------------------------------------------

This page is a guide for ESGF administrators about how to configure
their local node to enable downloads of both restricted and public data
through Globus.

This guide supports both a full node configuration (Index+IdP+Data) and
a split Index+IdP versus data node configuration. Each step below will
indicate on which node it needs to be executed.

Restricted datasets
-------------------

Step 1: (Preliminary) obtain Globus credentials for the node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Node: the same set of Globus credentials can be used when executing
   the ESGF installation on the Index+IdP and Data nodes.

The ESGF installer will install an up-to-date version of the Globus
Connect Server, but to do so it will require a valid Globus account to
associate with the node. This account will be used by the node to submit
a data transfer request on behalf of the user. So, prior to run the
installer, you must obtain a Globus username and password (by visiting
the `Globus <http://www.globus.org>`_/ website) that you will use at installation time. For example:

-  Globus username = jplnasagov
-  Globus password = secret

The choice of the Globus username is important, as it will be the first
part of all endpoints setup on the node. For example:

-  default public endpoint on the node: jplnasagov#esgf-node (#)

Step 2: Publish datasets with Globus enabled
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Node: Data node.

In order to be downloadable through Globus, datasets must be published
into the ESGF system with Globus URLs. This can be achieved by setting:


.. code:: console

    thredds_file_services =
            HTTPServer | /thredds/fileServer/ | TDSat \|fileservice
            OpenDAP | /thredds/dodsC/ | OpenDAPat | fileservice
            GridFTP | gsiftp://:2811/ | GRIDFTP | fileservice
            Globus | globus:/ | Globus | fileservice

in the esg.ini file, for example:
"globus:b7a8fa70-71d1-11e5-ba4c-22000b92c6ec/. A UUID of the Globus
endpoint can be obtained from the Globus website,
https://www.globus.org/app/endpoints?scope=my-endpoints.

Step 3: Add Globus URLs to already published datasets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you already have published some datasets without Globus URLs, you can
run the script,`GitHub `GitHub <https://github.com/ESGF/esgf-utils/blob/master/globus/add_globus_urls.py>`_
to add the Globus URLs to THREDDS catalogs and re-harvest them without
republishing all of the datasets again.

.. code:: console

    . /etc/esg.env 
    python add_globus_urls.py

Step 4: Register the URL with Globus
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Node: Index+IdP node.


The node where CoG is running must be registered as a client that is
authorized to submit data transfer requests to the Globus service on
behalf of the user. To register CoG app, go to
`CoG app <https://developers.globus.org/>`_, click “Register your app with Globus”,
create or add “ESGF” project. Click the “Manager Project” drop down and
select “Add new app” and fill out the registration form with the
following information:

-  App name: this is displayed to the user on the consent screen. “
   would like to” with a list of operations based on the scopes the
   client is asking. The client name should be in the form “ ESGF
   Portal” for the production ESGF node, and “ ESGF Portal Dev” for the
   development ESGF node.
-  Scopes: select “urn:globus:auth:scope:transfer.api.globus.org:all”
-  Redirects: use https:///globus/token/
-  Link to Privacy Policy (optional)
-  Link to Terms & Conditions (optional)

Submit the registration request by clicking “Create App”. Scroll down to
“Client secret”, enter “Globus download” and click “Generate Secret”.
Save the “Client Secret” and “Client ID” which will be needed in the
next step.

Step 5: Update the node configuration of Globus endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Node: Index+Idp node.

CoG needs access to the Globus client id and secret to be able to
request tokens. The following section must be added to the node
configuration file: /usr/local/cog/cog_config/cog_settings.cfg on the
Index+IdP node, where CoG is running (the values are just example,
please replace with your Globus client id and secret received from
Globus support):


.. code:: console

   [GLOBUS] OAUTH_CLIENT_ID = 12345678-9012-3456-7890-123456789012
   OAUTH_CLIENT_SECRET = 2345yujhbe3456yuhgfd45234yujhfd3Gev28gFWeBWE42=
   ENDPOINTS = /esg/config/esgf_endpoints.xml

Also an empty /esg/config/esgf_endpoints.xml file must be created:

.. code:: console

   <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
   <endpoints xmlns="http://www.esgf.org/whitelist">
   </endpoints>

The file is a part of a legacy implementation of mapping GridFTP URLs to
Globus URLs. The legacy implementation will be removed in the next
release.

Public datasets
---------------

Public datasets are served through so called “shared” Globus endpoint.
The shared endpoint is created from the Globus endpoint described above
for restricted datasets. All public datasets will be accessible and
downloaded on behalf of a selected ESGF user who has access to a project
with public datasets (is a member of the project group). In this
document, we assume that the user is https:///esgf-idp/openid/rootAdmin,
however it is strongly advised to create another dedicated ESGF user
account for accessing public datasets. To enable Globus downloads for
public datasets, some additional configuration changes are required,
besides steps 1, 2, and 5 described above for restricted datasets.

Step 1: Configure the Globus Connect Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Node: Data node.

At this time, the Globus Connect Server (GCS) installed by ESGF must be
specially configured to allow access to shared data.

-  Create the “sharer” local Unix account. By default, all ESGF users
   are mapped to the “globus” account. To separate privileges for public
   datasets, another account must be created, named "sharer for example.
-  Edit the file /etc/grid-security/grid-mapfile and insert one single
   line at the top of the file to map the “rootAdmin” DN to the local
   “sharer” Unix user

.. code:: console

    cat /etc/grid-security/grid-mapfile
    “/O=ESGF/OU=ESGF.ORG/CN=https:///esgf-idp/openid/rootAdmin” sharer
    "^.*$" globus

    for example:
    “/O=ESGF/OU=ESGF.ORG/CN=https://esgf-node.llnl.gov/esgf-idp/openid/rootAdmin” sharer
    "^.*$" globus

Note that the OpenId inside the DN refers to the rootAdmin account on
the Index+IdP node: X.509 credentials for “rootAdmin” must be obtained
from the IdP node, and they will be mapped to the “sharer” Unix account
on the Data node.

-  Create the following file to enable sharing on the GridFTP server:
   /etc/gridftp.d/globus-connect-server-sharing-esgf:

.. code:: console

    cat /etc/gridftp.d/globus-connect-server-sharing-esgf
    sharing_dn    “/C=US/O=Globus Consortium/OU=Globus Online/OU=Transfer User/CN=\ **transfer**”
    sharing_rp R/esg_dataroot/ 
    sharing_state_dir/etc/grid-security/sharing/$USER sharing_users_allow sharer
    sharing_users_deny globus

Step 3: Activate the default Globus Endpoint on the node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Node: Data node.

During Globus setup, the ESGF installer creates and registers a default
public endpopint for the node. This endpoint must be activated using any
ESGF account on the system, for example using the “rootAdmin” account
that is created at installation time (the account is only used to
retrieve valid credentials from the MyProxy server).

-  Visit the `Globus <http://www.globus.org/>`_ website, login with the Globus username and password
   used during installation
-  Click on Quick Links > Transfer Files > Endpoints
-  Select the endpoint named after the node host name, i.e. as
   globus_username#server_hostname
-  Click on Activate
-  Enter the ESGF user “rootAdmin” username and password (for the
   account created on the IdP)

Step 4: Create a shared Globus endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Node: Data node.

Once GCS is up and running on the node, the Node Administrator must
create a “shared” endpoint that users can use to download data without
any further authentication/authorization. In other words, a “shared”
endpoint is suitable for serving public data, and does not need to be
manually activated every time a user submits a data transfer request (it
is automatically activated by the node through cached credentials).

First, you must create a “sharer” home directory where the shared
endpoint information can be stored:

.. code:: console

    sudo mkdir -p /esg/gridftp_root/home/sharer
    sudo chown -R sharer:sharer /esg/gridftp_root/home/sharer

Then, you must create a shared endpoint using the Globus website:

-  Log onto the Globus website with the node Globus username and
   password
-  Click on Quick Links > Transfer Files > Manage Endpoints
-  Select the root endpoint for the node (for example
   “jplnasagov#esgf-node”)
-  Click on “Sharing” > “Add Shared Endpoint”.
-  In the panel that opens, select:

   -  Host Path = / (to serve publicly all data under that directory)
   -  New Endpoint Name: #public (for example: “jplnasagov#public”)
   -  Description: whatever appropriate (for example: "NASA/JPL data for
      public access)

-  Click on “Create and Manage Access”
-  Click on “Add Permission”
-  Create a Read only permission for All Users
-  Also, click “Edit Attributes” and change the “Legacy Name” attribute
   to match the Endpoint name ( in this example, “jplnasagov#public”).

Note that after the shared endpoint has been succesfully created, there
will be a new configuration file stored in the above directory, of the
form: /esg/gridftp_root/home/sharer/.globus/sharing/share-xxx….

Note that after the shared endpoint has been succesfully created, there
will be a new configuration file stored in the above directory, of the
form: /esg/gridftp_root/home/sharer/.globus/sharing/share-xxx….

Step 3: Publish public datasets with Globus enabled
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Node: Data node.

In order to be downloadable through Globus, datasets must be published
into the ESGF system with Globus URLs pointing to the shared endpoint.
This can be achieved by setting:

.. code:: console


    thredds_file_services = 
            HTTPServer | /thredds/fileServer/ | TDSat<node> | fileservice
            OpenDAP | /thredds/dodsC/ | OpenDAPat<node> | fileservice
            GridFTP | gsiftp://<hostname>:2811/ | GRIDFTP | fileservice 
            # Globus endpoint for restricted datasets 
            #Globus | globus:<UUID>/ | Globus | fileservice 
            # Globus shared endpoint for public datasets 
            Globus | globus:<UUID_of_the_shared_endpoint> | Globus | fileservice

in the esg.ini file, for example:
"globus:2854feb6-bb21-11e5-9a07-22000b96db58/. A UUID of the shared
Globus endpoint can be obtained from the `Globus website <https://www.globus.org/app/endpoints?scope=my-endpoints>`_
