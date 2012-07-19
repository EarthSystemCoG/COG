#!/bin/sh

rm database/*
rm cog/migrations/*
python manage.py schemamigration cog --initial
python manage.py syncdb
python manage.py migrate cog
python manage.py createsuperuser --username=admin --email=Luca.Cinquini@jpl.nasa.gov
python manage.py migrate remap
#python manage.py schemamigration cog --auto
#python manage.py migrate cog
python init_projects.py
