

CoG Installation from Docker
============================

The recommended way to install and run CoG in in development environment
is to use Docker. Docker is a software containerization platform. Docker
containers wrap software in a complete filesystem that contains
everything needed to run: code, runtime, system tools, system libraries,
etc. This guarantees that the software will always run the same,
regardless of its environment.

CoG has been packaged to work with Docker and starting and running a
Docker container based on one of the publicly available CoG Docker
images is a simple process, and allows to CoG to be restared from a
completely clean state (no projects or users), or upgrad an already
populated CoG instance.

Prerequisites (for installation and general operation)
------------------------------------------------------

-  You must have the Docker Engine installed on your personal machine
   (MacOSX, Windows or Linux). See the Docker Documentation for
   instructions on how to install Docker on different platforms. Basic
   familiarity with Docker is also recommended - this can be achieved by
   following one of the many training seminars available on the site
-  The Docker Engine MUST BE RUNNING. On a Mac this is done by clicking
   on the icon (Figure 1).

Figure 1: Mac Docker icon.

Download
--------

Images for several CoG versions are publicly available on DockerHub
(project esgfhub/esgf-cog). To download a specific version issue the
following command:

.. code:: ipython2
   $ docker pull esgfhub/esgf-cog:

   For example:

   $ docker pull esgfhub/esgf-cog:v3.7.RC2



To download the latest development version (built at some unspecified
time from the github ‘devel’ branch):

.. code:: ipython2

   $ docker pull esgfhub/esgf-cog:latest

Run CoG from the container installation directory
-------------------------------------------------

Start a Docker terminal, then use the following command to create a new
Docker container based on CoG image you have downloaded, start the
container, and start CoG within the container (enter the command below
in only one line):


.. code:: ipython2

   $ docker run -ti -p 8000:8000 –name mycog esgfhub/esgf-cog: ``docker-machine ip`` false true

The command line arguments are explained below:

-  -ti : creates an interactive terminal to the Docker container, so
   that you can view the Django logs, and stop the Django server when
   desired
-  -p 8000:8000 : maps port 8000 on the Docker Host to port 8000 in the
   Docker container, i.e. makes port 8000 reachable on the Docker Host
-  –name:mycog : the container is given the name “mycog” - Docker
   containers must have unique names. You must delete a named container
   before attempting to create a new one with the name name, for
   example: docker rm mycog
-  ``docker-machine ip`` : this command retrieves the current IP address
   of the Docker host and passes it as an argument to the container
   startup. This IP address must be configured in the ALLOWED_HOST
   directive in cog_settings.cfg to enable HTTP requests to that host
-  false : run without ESGF configuration, i.e. with a sqllite database
   back-end
-  true : start the django development server on port 8000 (otherwise
   the Docker container will exit…)

By default, the Docker entrypoint script will start CoG from the
installation directory $COG_INSTALL_DIR = /usr/local/cog/cog_install,
and will run CoG as the non-privileged user “cogadmin” (instead of the
“root” user).

After the container has started, you can access the CoG site at the
following URL:

-  http://:8000/

For example:

-  http://192.168.99.100:8000/

You can log in at http://:8000/login2/ with the temporary credentials:

-  username = rootAdmin
-  password = changeit

Stop CoG
--------

To stop the CoG container, and the CoG application running within,
simply type ^C in the Docker terminal window. This will stop but NOT
delete the “mycog” container.

Restart CoG
-----------

To restart the same CoG container, using the same configuration,
database, and data, issue the following command at a Docker terminal:

.. code:: ipython2

   $ docker start -ai mycog


- ai : attaches the Docker container to the terminal STDIN, STDOUT and STDERR

To restart CoG from a completely clean slate, first delete the previous container:

.. code:: ipython2

   $ docker rm  mycog


then use the “docker run…” command again with the same container name.
Or, use the “docker run…” command with a different container name.

Run CoG from the local source directory
---------------------------------------

If you are doing CoG development, you may want to startup CoG from your local source code directory, so that you can work with Git to commit and push changes to GitHub.

First, clone the CoG repository to a location on your system, here named $COG_SRC_DIR:

.. code:: ipython2

   $ git clone https://github.com/EarthSystemCoG/COG.git
   # optionally, check out a branch or tag
   $ git checkout -b devel origin/devel
   $ export COG_SRC_DIR=`pwd`
   

Then run the CoG Docker container by mounting the local source directory on top of the image CoG installation directory:


.. code:: ipython2

   $ docker run -ti -p 8000:8000 –name mycog -v $COG_SRC_DIR:/usr/local/cog/cog_install esgfhub/esgf-cog: ``docker-machine ip`` false true

Inside the container, CoG will still be started from $COG_INSTALL_DIR,
but this directory is now a copy of the local source directory
$COG_SRC_DIR. Any changes to the code in $COG_SRC_DIR will be
immediately reflected onto the running web application. Additionally,
using a local terminal, these changes can be committed to GitHub, if
desired.

Note that every time the CoG container is restarted, the CoG
installation is automatically upgraded to the latest database schema
version, and all static files are collected into the standard directory
tree.
