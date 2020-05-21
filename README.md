What is CoG?
============

CoG is a multi-institutional project that seeks to examine, within the Earth sciences, 
the organizational characteristics of community software projects and to create software infrastructure 
to support their efficient governance and operation.

The name CoG comes from the idea of many gears interlocking in order to make a system work.  
CoG is also short for "Commodity Governance" - the idea that there are organizational and management characteristics that many projects share, 
and that exposing those characteristics and linking them is a way to make a complicated "community of communities" run effectively.

The CoG project created the CoG environment - this website - as a way of promoting good governance across numerous projects 
and organizations in the Earth system sciences.  Its structure encourages information sharing among projects, transparency and trust.

For more information, visit: http://esgf.github.io/COG

Python3 Update
--------------

This branch migrates CoG to Python3 and Django2. (v4.0.0b) 

Updating CoG
------------

Use the Ansible playbook from the following branch: `python3_cog` - See https://esgf.github.io/esgf-ansible for instructions on how to run the playbooks. 
The installation must be performed on a server that already has the cogdb deployed to PostgreSQL.  In other words, in order to install CoG v4 from scratch, you must first run the latest Ansible playbook for ESGF, which will deploy CoG v3.15 (Python2) and create the cogdb database.  Then, run the  `python3_cog` branch playbook to setup CoG.  Note that this installation will create a distinct Python3 conda environment for which to run the CoG service in mod_wsgi_express `py3_cog`.  The previous `cog` environment will still be present, but is no longer used (and could be safely deleted).

