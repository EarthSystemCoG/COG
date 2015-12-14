#!/bin/sh

# script to dump the content of the database to file
# NOTE: to run as cron, the script must access the postgres user password from file ~/.pgpass
# cat ~/.pgpass
# host_name:port:database_name:database_user:database_password

export PATH=/usr/local/pgsql/bin:$PATH
pg_dump -p 5432 -U dbsuper cogdb > /tmp/cogdb_$(date +%Y-%m-%d).sql
#pg_dump -p 5432 -U dbsuper esgcet > /tmp/esgcet_$(date +%Y-%m-%d).sql
