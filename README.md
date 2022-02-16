# What is CoG?

CoG is a multi-institutional project that seeks to examine, within the Earth sciences, 
the organizational characteristics of community software projects and to create software infrastructure 
to support their efficient governance and operation.

The name CoG comes from the idea of many gears interlocking in order to make a system work.  
CoG is also short for "Commodity Governance" - the idea that there are organizational and management characteristics that many projects share, 
and that exposing those characteristics and linking them is a way to make a complicated "community of communities" run effectively.

The CoG project created the CoG environment - this website - as a way of promoting good governance across numerous projects 
and organizations in the Earth system sciences.  Its structure encourages information sharing among projects, transparency and trust.

For more information, visit: http://esgf.github.io/COG

## Recent Updates

### v4.0.3

* Drop processing of use of next=url in add user query string.

### v4.0.2
* Bug fix for Show Citation (missing data from API causes all information not to display)

## Python3 Update

This is v4.0.3 of CoG that supports Python3 and Django 2.2.24.  Given that this Django 2.2 version has run in LLNL production for over eight months now, it is time that we release this version of COG as the master branch.  We strongly encourage all sites to upgrade their deployments to this version.

The last v3.x version of CoG running with Python2 is preserved for legacy.  This version is still needed to create the cogdb database (see below) for a standard legacy ESGF deployment using the Ansible playbooks (although a Postgres >9.5 supported version may be forthcoming....).

## Updating CoG

Use the Ansible playbook from the following branch: `python3_cog` - See https://esgf.github.io/esgf-ansible for instructions on how to run the playbooks. 
The installation must be performed on a server that already has the cogdb deployed to PostgreSQL.  In other words, in order to install CoG v4 from scratch, you must first run the latest Ansible playbook for ESGF, which will deploy CoG v3.15 (Python2) and create the cogdb database.  Then, run the  `python3_cog` branch playbook to setup CoG.  Note that this installation will create a distinct Python3 conda environment for which to run the CoG service in mod_wsgi_express `py3_cog`.  The previous `cog` environment will still be present, but is no longer used (and could be safely deleted).

