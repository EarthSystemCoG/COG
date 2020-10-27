
Installation Testing: Initial Testing of the Installation
=========================================================

Step 1: Run CoG with the Django development server
--------------------------------------------------

Make sure you have defined the necessary environment variables and
activated the CoG Python virtual environment as described in the
previous steps:

.. code:: ipython2

   export COG_DIR=/usr/local/cog
   export COG_CONFIG_DIR=$COG_DIR/cog_config
   export COG_INSTALL_DIR=$COG_DIR/cog_install
   cd $COG_DIR
   source venv/bin/activate


Then, start the CoG application on the local host and specific port:

.. code:: ipython2

   cd $COG_INSTALL_DIR
   python manage.py runserver <host>:<port>
   # example: python manage.py runserver test-datanode.jpl.nasa.gov:8000

By default, =localhost and =8000, although you’ll be able to point a
browser at localhost only if you are installing CoG on your local
laptop.

Note: you might need to also define the following environment variable:

.. code:: ipython2

   export PYTHON_EGG_CACHE=/tmp

(or other directory that exists and is writable by the user running the
application).

Note: you might also need to insert the location of the postgres library
in the system dynamic library path, for example:

.. code:: ipython2

   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/pgsql/lib

Step 2: Open http://<host>:8000/
--------------------------

You should be presented with the CoG home page.

Step 3: Login
-------------

-  if an ESGF node is installed (e.g. –esgf=true), use the standard
   login URL http://:/login/ with the openid
   https:///esgf-idp/openid/rootAdmin and your usual ESGF rootAdmin
   password (or “changeit” if the usual password could not be found)
-  if an ESGF node is NOT installed (e.g. (–esgf=false), use the
   “hidden” local login URL http://:login2/ with username “rootAdmin”
   and the password “changeit”

Step 4: IMPORTANT: immediately change the “admin” password by:
--------------------------------------------------------------

If you logged in for the first time as user “rootAdmin” with password
“changeit”, you should really change the password right away:

-  clicking on “My Profile” -> “Change Password” or
-  directly accessing the URL "http://:8000/password/update/

Note: to fully test the password change, you need to log out of CoG AND
quit the browser and log-in as ‘admin’ again.

Changing the password is not necessary if you were able to login with
your usual ESGF password.

Step 5: Change all other “admin” data.
--------------------------------------

Ensure the information matches the local Node Administrator, especially
the email address where all node-level notifications will be sent.

Step 6: Start experimenting with creating other projects and registering new users.
-----------------------------------------------------------------------------------

-  Verify that email notification is working. The Node Administrator
   should get an email whenever a project is requested or a new user
   registers.


