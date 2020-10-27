Restore from Backup
===================

Restoring CoG from backup
-------------------------

-  Stop CoG, then…
-  if using postgres:


.. code:: console

    psql -U postgres -p 5432 cogdb < cogdb_2014-03-12.sql

-  if using sqllite:

   -  simply copy the older django.data file to the DATABASE_PATH
      location.

-  Restart CoG
