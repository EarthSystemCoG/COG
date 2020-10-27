
CoG Installation or Upgrade
===========================

Typically, CoG is installed on an ESGF node as part of the full ESGF
installation suite. Nevertheless, if desired CoG can be installed or
upgraded standalone by following the steps described in this document.

-  Stop the ESGF node, but restart postgres:

   -  sudo /usr/local/bin/esg-node stop
   -  sudo /etc/init.d/postgresql start

-  Backup the CoG source tree and data, so that you can recover in case
   anything goes wrong.:

   -  cd
   -  sudo cp -R /usr/local/cog/ ./cog
   -  export PATH=/usr/local/pgsql/bin:$PATH
   -  pg_dump -p 5432 -U dbsuper cogdb > ./cogdb_backup.sql (insert your
      dbsuper password)
   -  pg_dump -p 5432 -U dbsuper esgcet > ./esgcet_backup.sql (insert
      your dbsuper password)

-  Checkout the latest version of the CoG installation script from the
   devel branch (since the script is not going to be updated in the
   master branch untill the next ESGF release):

   -  cd
   -  wget
      ‘https://raw.githubusercontent.com/ESGF/esgf-installer/devel/cog/esg-cog’
   -  check that the script containes the desired CoG version - at this
      time:

      -  VERSION=v3.9.0

   -  sudo cp esg-cog /usr/local/bin

-  Run the script:

   -  cd /usr/local/bin
   -  sudo ./esg-cog

-  Let the installation complete, hopefully without errors. Then stop
   postgres and restart the node:

   -  sudo /etc/init.d/postgresql stop
   -  sudo /usr/local/bin/esg-node start
