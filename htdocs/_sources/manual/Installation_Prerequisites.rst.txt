
Installation: Prerequisites
===========================

The following items are required to install CoG for developmental
purposes:

-  A system running a \*-nix operating system, including Cent-OS, Linux
   and MacOSX

Step 1: Install Python
----------------------

-  Install Anaconda
-  2.7.10 does not work with cog, you will need to downgrade

.. code:: console

   #downgrade python install conda install 
   conda install python=2.7.9

-  Python setup_tools (should come with python)

Step 2: Install Postgres
------------------------

-  http://postgresapp.com/
-  http://postgresapp.com/documentation/cli-tools.html
-  you may need to add the location of the pg_config file to your $PATH

Step 3: Set up git and github
-----------------------------

-  Install git: https://git-scm.com/download/mac
-  Generate SSH keys:
   https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/
-  Add the SSH keys to your github account:
   https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/
-  Setup username and email

.. code:: console

   git config –global user.name “username”

   git config –global email “email”

Step 4: Update pip
------------------

.. code:: console

    pip install -U pip


Step 5: Install virtualenv
--------------------------

.. code:: console

   pip install virtualenv

Step 6: (CentOS only) Install C-headers for sqlite-devel and freetype-devel
---------------------------------------------------------------------------

.. code:: console

   yum install sqlite-devel freetype-devel

Step 7: (MacOSX only) Copy image libraries
------------------------------------------

-  Ensure the following libraries are located in /usr/local/lib (copy
   from anaconda lib…requires sudo)

   -  libcrypto.1.0.0.dylib
   -  libjpeg.8.dylib
   -  libssl.1.0.0.dylib
   -  libtiff.5.dylib

.. code:: console  

   # example 
   sudo cp ~/anaconda/lib/libtiff.5.dylib /usr/local/lib

Step 8: Install Xcode command line tools
----------------------------------------

.. code:: console


   xcode-select –install

Step 9: Manually install Pillow
-------------------------------

-  Normally Pillow is automatically installed via the
   /cog_install/setup.py script
-  Modify this file and comment out that installation, and install
   manually
-  wheel may be required in the install


.. code:: console


   pip install wheel 
   pip install –use-wheel Pillow==2.8.2 
   #note 3.1.0 does not install w/o jpeg support, may cause install to fail
