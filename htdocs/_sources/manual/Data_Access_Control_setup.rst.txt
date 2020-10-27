
Data Access Control Setup
=========================

This short tutorial will explain how to setup the ESGF Access Control
infrastructure for publishing and downloading a specific dataset. As an
example, we will consider the case of NASA “obs4MIPs” data.

Step 1: Configure the ESGF Postgres database
--------------------------------------------

Use the command line client to interact with the Postgres database:

.. code:: console

    psql -U dbsuper -d esgcet

(type in your Postgres super-user password).

Create a new group that will control all operations on the dataset (all
SQL commands below must be typed in only one line):

.. code:: console

    esgcet=# insert into esgf_security.group (id, name, description, visible, automatic_approval)
             values (2, ‘NASA OBS’, ‘NASA observations’, true, true);

Note that:

-  visible=true will cause the group to be exposed to the public for
   registration
-  automatic_approval=true will enroll users into the group (with
   READ-ONLY priileges) upon request, without the need for the group
   administrators to approve the request

Then, assign read/write privileges to one or more users who will be
publishing the data. In this case, we look up the “rootAdmin” user and
assign him/her priileges on the group just created:


.. code:: console

    esgcet=# select id from esgf_security.user where openid like ‘%rootAdmin%’;

    esgcet=# insert into esgf_security.permission (user_id, group_id, role_id, approved)
             values (1, 2, 4, true); # ‘publisher’ role, aka ‘write’ privileges

    esgcet=# insert into esgf_security.permission (user_id, group_id, role_id, approved)
             values (1, 2, 6, true); # ‘user’ role, aka ‘read’ privileges

Step 2: Edit the ESGF XML configuration files
---------------------------------------------

As root, edit the file /esg/config/esgf_policy_local.xml to specify one
or more policies for reading/writing the files of your dataset. For
example:

.. code:: console


    vi /esg/config/esgf_policies_local.xml

    <!-- URLs that contain NASA-JPL can be downloaed by users 
        with NASA-OBS "user" permission -->

    <policy resource=".*NASA-JPL.*" attribute_type="NASA OBS" 
        attribute_value="user" action="Read"/>

    <!-- datasets with ID that contain NASA-JPL can be published by users
         with NASA-OBS "publisher" permission -->
    <policy resource=".*NASA-JPL.*" attribute_type="NASA OBS" 
        attribute_value="publisher" action="Write"/>

Also, you must edit the file /esg/config/esgf_ats_static.xml to specify
the URLs of the Attribute and Registration services that manage
membership in the access control group. For example:


.. code:: console
   
   vi /esg/config/esgf_ats_static.xml
    
   <!-- NASA Obs4MIPs -->
   <attribute type="NASA OBS"               
   attributeService="https://esgf-node.llnl.gov/esgf-idp/saml/soap/secure/attributeService.htm"
   description="NASA Observational Data"
   registrationService="https://esgf-node.llnl.gov/esgf-idp/secure/registrationService.htm"/>


When done, you may restart the node, but there is really no need to as
the above files should be automatically reloaded.

Step 3 (optional): Publish the Group Registration URL
-----------------------------------------------------

CoG provides functionality for streamlining the user registration into
the ESGF access control groups. Whenever CoG is connected to an ESFG
“security” database back-end, it will automatically create an
appropriate registration page for each of the ESGF access control groups
read from the local database. These pages all have URLs of the form:


.. code:: console

    https://<hostname>/ac/subscribe/<group name>/

(for example: https://esgf-node.llnl.gov/ac/subscribe/NASA%20OBS/),
so as an node administrator you can embed this URL anywhere on your node
where content is allowed: for example, on the node home page, or on the
home page for the specific “NASA OBS” project. Users can visit the
registration page directly to request READ permission, without having to
go through the old ESGF data download workflow.

Additionally, the registration page can be “embedded” with a license for
the users to read before they request membership. To do so, place a file
called .html (in HTML format) or .txt (in plain text format) under your
local templates directory, specifically:


.. code:: console

    /usr/local/cog/cog_config/mytemplates/cog/access_control/licenses/.html
    or:
    /usr/local/cog/cog_config/mytemplates/cog/access_control/licenses/.txt

The figure below shows an example registration page with embedded HTML
license.


.. figure:: /images/ESGF-CoG_group_registration_page.png
   :scale: 45%
   :alt:

Figure1. Example ESGF-CoG registration page with optional license
agreement display.

Special Case: Unrestricted Data
-------------------------------

In some cases, the data might be available for download without any
restrictions at all, i.e. simply to guest users. In this case, the Node
administrator only needs to insert a policy statement in the file
/esg/config/esgf_policies_local.xml that matches the data URLs, and uses
the special attribute_type=“ANY”. Note that your will still want to have
a restricted access control group to enable publishing of the data. For
example:


.. code:: console

    vi /esg/config/esgf_policies_local.xml

    <!-- URLs that contain COUND can be downloaed by guest users 
        (no authentication or group membershp required) -->
    <policy resource=".*COUND.*" attribute_type="ANY" attribute_value="" action="Read"/>

    <!-- datasets with ID that contain COUND can be published by users
        with NASA-OBS "publisher" permission -->
    <policy resource=".*COUND.*" attribute_type="NASA OBS" attribute_value="publisher" action="Write"/>

Special Case: Authentication Only Data
--------------------------------------

In other cases, the data providers might want to require users to
authenticate before downloading the data, so they can capture their
openid for metrics reporting, but they don’t need users to enroll in any
group. In this case, they can use a policy statement with the special
attribute_type=“AUTH_ONLY”. For example:


.. code:: console

    vi /esg/config/esgf_policies_local.xml

    <!-- URLs that contain COUND can be downloaed by guest users (no authentication or group membershp required) -->
    <policy resource=".*COUND.*" attribute_type="ANY" attribute_value="" action="Read"/>
   
    <!-- datasets with ID that contain COUND can be published by users with NASA-OBS "publisher" permission -->
    <policy resource=".*COUND.*" attribute_type="NASA OBS" attribute_value="publisher" action="Write"/>



