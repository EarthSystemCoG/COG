
Cron Jobs
=========

Setup cron jobs to execute periodic administration tasks
--------------------------------------------------------

Following is a list of CoG tasks that should be executed periodically,
and are therefore best setup as cron jobs on the server hosting CoG:

1) Periodically update the projects around the federation
---------------------------------------------------------

Each CoG needs to periodically query its federated peers to obtain their
latest projects. An example script to accomplis this task is included in
the CoG source code itself: resources/scripts/sync_projects.sh - which
may need to be customized to your environment. For example, to
synchronize the projects every hour:

.. code:: console

    0 * * * * /esg/config/sync_projects.sh

The script sets up some needed environment variables. then executes the
“sync_project” management command that is included with the CoG
distribution:

.. code:: console

    #!/bin/sh

    #script to update the state of CoG projects around the federation

    #setup environment 
    source /usr/local/cog/venv/bin/activate
    export LD_LIBRARY_PATH=/opt/esgf/python/lib:$LD_LIBRARY_PATH
    # reference the COG installation
    export COG_INSTALL_DIR=/usr/local/cog/cog_install

    # reference the COG configuration
    export COG_CONFIG_DIR=/usr/local/cog/cog_config

    python $COG_INSTALL_DIR/manage.py sync_projects


2) Backup the postgres databases content every night
----------------------------------------------------

It is highly recommended that both the CoG and the ESGCET databases be
backed up daily. This can be accomplished by setting up a cron job to
run nightly as follows:

.. code:: console

    crontab -l
    0 0 * * * /esg/config/db_backups.sh

where the script has the following content:

.. code:: console

   #!/bin.sh 
   export PATH=/usr/local/pgsql/bin:PATH 
   pg_dump -p 5432 -U dbsuper cogdb > /tmp/cogdb_$ (date+%Y-%m-%d).sql 
   pg_dump -p 5432 -U dbsuper esgcet > /tmp/esgcet_$(date+%Y-%m-%d).sql

NOTE: for the script to run as cron, the postgres database password must
be located in file ~/.pgpass with the format:

.. code:: console

    host_name:port:database_name:database_user:database_password

Also the file permissions must be set as follows:

.. code:: console

    chmod 0600 ~/.pgpass

3) Remove stale user stubs from local database
----------------------------------------------

When a user from another CoG logs onto the local CoG with their OpenID,
a user object stub is created in the local database to store some needed
information. Unfortunately, if the user account is deleted on the remote
server, the local account is not. To remedy this situation, i.e. to
delete local user stubs of remote users that have been deleted, the ESGF
node administraor can run the following command (in the proper python
virtual environment):

.. code:: console

    cd $COG_iNSTALL_DIR 
    python manage.py sync_users

The same command can also be run as a cron job. An example such script
is provided as part of the CoG distribution:
resources/scripts/sync_users.sh, and may need to be customized to your
ESGF installation. For example, to run the script every night at
midnight:

.. code:: console

    0 0 * * * /esg/config/sync_users.sh

where the script content is:

.. code:: console

    #!/bin/sh

    #example script to delete stale user stubs from the local database

    #setup environment
    source /usr/local/cog/venv/bin/activate 
    export LD_LIBRARY_PATH=/opt/esgf/python/lib:$LD_LIBRARY_PATH

    # reference the COG installation
    export COG_INSTALL_DIR=/usr/local/cog/cog_install

    # reference the COG configuration
    export COG_CONFIG_DIR=/usr/local/cog/cog_config

    python $COG_INSTALL_DIR/manage.py sync_users
