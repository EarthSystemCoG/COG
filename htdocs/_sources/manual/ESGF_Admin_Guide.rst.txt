
ESGF/CoG Administrator Guide Overview
=====================================

The Earth System CoG Collaboration Environment has replaced the Web
Front End as the public face to ESGF. This page describes the steps
necessary to setup, configure, and maintain CoG for your ESGF node. It
is intended to be used by existing ESGF Node administrators with
root-level access.

Step 1a: Install CoG using the ESGF installer CoG is installed as part
of a standard ESGF Index Node by running the ESGF installer. Currently,
CoG is configured to run behind the Apache httpd server on the standard
port SSL port 443 (redirection from port 80 will be configured soon).
After the ESGF installer completes succesfully, check that you can
access the node by typing the following URL in your favorite browser

.. code:: console

    Open URL: https//<hostname>/
    Replace: <hostname> with your Node’s fully qualified domain name (note the “https” protocol).

This should redirect to https:////projects/testproject/

Step 1b: Upgrade CoG standalone
-------------------------------

Alternatively, if you already have a working ESGF/CoG setup, you can
upgrade CoG without running the full ESGF installer with the following
procedure (as root, or prepend commands with sudo):

.. code:: console

    Stop the ESGF node: # /usr/local/bin/esg-node stop
    But start Postgres: # /etc/init.d/postgresql start
    Checkout the latest esg-cog script from GitHub (devel branch): 
    # cd /usr/local/bin
    # wget 'https://github.com/ESGF/esgf-installer/blob/devel/cog/esg-cog'
    Execute the script: # ./esg-cog
    Stop Postgres: # /etc/init.d/postgresql stop
    Restart the ESGF node: # /usr/local/bin/esg-node start



Step 2: Configure CoG
---------------------

-  Once ESGF-COG is installed, the ESGF Node administrator must complete
   a sequence of one-time tasks to configure and customize the node.
-  These tasks can be completed at different times to progressively
   enhance the node functionality.
-  Please note that any configuration and content will be persisted
   across sub-sequent upgrades of the ESGF Node, but will be completely
   wiped out if the ESGF Node is re-installed from scratch (since CoG
   content is kept in the Postgres database, which will be erased by a
   total ESGF Node re-install). So, if you plan on later re-installing
   the whole Node from scratch, it is recommended to only follow steps
   1-3 below to execute some basic post-installation testing. Proceed
   with the additional steps only when you believe that your Node
   installation is final, about to go into production, and you will only
   have to upgrade the Node, not re-install it.


    1. `Login as ESGF/CoG Administrator <ESGF_Admin_Guide.html>`_
    2. `Setup the Node Home Project <COG/source.html#Home_Project_Setup>`_
    3. `Configure the Home Project Search <COG/source.html#Data_Search_Configuration>`_
    4. `Data Access Control Setup <COG/source.html#Data_Access_Control_Setup>`_
    5. Customize the Node Header and Footer
    6. Customize Google Analytics
    7. Setup the ESGF Node Federation
    8. Configure Globus Downloads
    9. `Setup Cron Jobs <COG/source.html#Cron_Jobs>`_
    10. `Local Shard Setup and Publishing <COG/source.html#Local_Shard_Setup>`_

Additionally, the following pages contain additional content related to
understanding and operating an ESGF-CoG node:

-  CoG-to-ESGF User Accounts
-  Restore from backup

Step 3: Upgrade CoG
-------------------

In general, CoG upgrades are best executed within a complete ESGF
release, by runinnig the full ESGF installer. But there might be
situations where an ESGF Node administrator might want to install a new
CoG version right away - for example, because a security patch or a new
piece of functionality must be installed as soon as possible. CoG can be
upgraded standalone by leveraging the ESGF installation infrastructure,
simply by editing and executing the esg-cog script (as root):

.. code:: console

    cd /usr/local/bin
    edit esg-cog: set VERSION=...whatever is the CoG version you want to install...
    execute esg-cog: ./esg-cog
    restart the node: ./esg-node restart



IMPORTANT: please note that the esg-cog script requires that the ESGF
Postgres database be running while it executes. So either leave the
whole ESGF node running, upgrade CoG, and then restart the node; or shut
down the node but start up the Postgres database alone before running
the upgrade script.
