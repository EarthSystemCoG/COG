
Setup Federation
================

Setup federation with other CoG instances:
------------------------------------------

Choosing Peer Nodes
-------------------


ESGF maintains a list of available ESGF peer nodes in a file that is
located by default on each system at the path:
/esg/config/esgf_cogs.xml. This file is updated every time the ESGF
software stack is installed, or it can be updated manually by fatching
the latest version from the ESGF “config” repository on GitHub. An
alternate location can be specified using the PEER_NODES variable in the
configuration file.

At startup time, CoG reads this file and takes the following actions:

-  If a node with a new domain name is found, it will be inserted as a
   new peer node in the database (but NOT activated)
-  if a node with an existing domain name is found, its server name will
   be updated into the database with the new value read from the file
-  If an existing node has been removed from the file, it will NOT be
   deleted from the database automatically

The list of peer nodes can also be updated without having to restart the
local ESGF node. To do so, run the following django management command:

.. code:: console

   cd $COG_INSTALL_DIR 
   source $COG_DIR/venv/bin/activate
   export LD_LIBRARY_PATH=/opt/esgf/python/lib:`\ LD_LIBRARY_PATH
   python manage.py sync_sites

Just like when restarting CoG, this command will insert any missing
nodes in the local database (and update their names if they have
changed), but it will not activate the nodes by default. Note that the
same command can also be passed the ‘–delete’ option to delete stale
nodes that are found in the local database, but are missing from the
esgf_nodes.xml file:


.. code:: console

   python manage.py sync_sites –delete

Once the nodes are listed in the local database, they can be enabled by
logging in as a Node Administrator and clicking on the ‘Configure Peers’
link in the ‘Admin’ menu in the lower left navigation bar.

Loading Projects from Peer Nodes
--------------------------------

The local CoG application can be instructed to load the most recent list
of projects from the other federated instances in one of three ways:

-  By visiting the page “Configure Peers” and clicking on the lower link
   “Synchronize with Peer CoGs Now” (or directly invoking the URL
   "http://<your cog domain name>/share/sync/projects/")
-  By invoking the following django management command:

.. code:: console

   cd $COG_INSTALL_DIR 
   source $COG_DIR/venv/bin/activate
   export LD_LIBRARY_PATH=/opt/esgf/python/lib:$LD_LIBRARY_PATH
   python manage.py sync_projects

-  By setting up a cron job that executes the same command above. For
   example:

.. code:: console


   crontab -l
   0 * * * * source ~/.bashrc; 
   python/usr/local/cog/cog_install/manage.py sync_projects 
   >> /tmp/crontab.log 2>&1

will parse the user environment, and run the command at minute 0 of
every hour, appending the output to file.

NOTES:
~~~~~~

-  Projects will be updated only from peer nodes that are “enabled”.
   IMPORTANT: a node will only share projects correctly if its ‘Node’
   domain name {{site_name}} equals its real domain.
-  If its node domain has been recently updated, CoG must be restarted
   for that change to take effect, otherwise the other CoGs won’t see
   its projects.
-  A node will only share those projects that are ‘active’
-  If a peer node is disabled through the admin interface:

   -  Its projects won’t show up in the projects browser (for none of
      the tabs)
   -  Its projects will not be selectable as peers/parent/children in
      the project configuration panel
   -  Its data cart won’t show up in the current data cart page
   -  The node will not be queried for user projects updates
