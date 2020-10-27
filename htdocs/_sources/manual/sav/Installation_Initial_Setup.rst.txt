
Installation: Initial setup
============================

NOTE: If installing CoG through the ESGF Installer, all these steps will
be executed automatically. If not using the ESGF Installer, please read
on.

Step 1: Create the main CoG directory 
--------------------------------------

This will be the parent directory under which all CoG-related software
(Python, CoG installation, CoG configuration) will be installed.

-  For example, use = /usr/local/cog
-  But the directory can be located anywhere on the system if needed
   (e.g. you don’t have write permissions to /usr/local/cog).
-  The user executing the installation must have write permissions to
   this directory.

.. code:: ipython2

   mkdir <COG_DIR>

Step 2: Create a CoG configuration directory 
---------------------------------------------

This will create a directory to hold the node-specific configuration
file and external media sub-directories.

-  The default location for = /usr/local/cog/cog_config
-  Preferably, this directory should be located under
-  But the directory can be located anywhere on the system if needed.
-  The user executing the installation must have write permissions to
   this directory.

.. code:: ipython2

   mkdir <COG_CONFIG_DIR>r

Step 3: Create a CoG installation directory 
--------------------------------------------

This is where the source code will be located.

-  Preferably, this directory should be located under
-  For example, use = /usr/local/cog/cog_install

.. code:: ipython2

   mkdir <COG_INSTALL_DIR>

Step 4: Ensure all environment variables are set
------------------------------------------------

How environment variables are set varies from shell to shell. Below is
the example for Bash. These commands would be placed in the
~/.bash_profile or ~/.bashrc files. For example:

.. code:: ipython2

   export COG_DIR=/usr/local/cog
   export COG_CONFIG_DIR=$COG_DIR/cog_config
   export COG_INSTALL_DIR=$COG_DIR/cog_install

Step 5: Set up a Python virtual environment
-------------------------------------------

This will be the location for the CoG specific Python libraries and
related dependencies.

.. code:: ipython2

   cd virtualenv venv

This will create the sub-directory venv under with:

::

   copy of python executable in <COG_DIR>/venv/bin/python
   location for installation of additional needed packages in <COG_DIR>/venv/lib/python2.7/site-packages

Note, if you have multiple installations of python installed, you can
specify which python to use through the -p option. By default,
virtualenv will use the python used to install virtualenv.

.. code:: ipython2

   cd <COG_DIR>
   virtualenv -p /usr/bin/python venv


Results:
--------

After these steps, the directory structure will look like:

-  /usr/local/cog

   -  /cog_config
   -  /cog_install
   -  /venv
