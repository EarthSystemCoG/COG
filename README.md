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

CoG Administrator's Guide
-------------------------

The Guide is no longer accessible online. However you can open the guide through this repository.
Clone this repository and open `COG/htdocs/index.html` in your browser.


Installation of CoG
-------------------

The simplest way to install CoG is to do so as part of an ESGF index node deployment using ESGF Ansible, see: 
https://github.com/ESGF/esgf-ansible


Python 2 vs 3
-------------

CoG supports Python 3.  For the time being this is in its own branch.  Due to library and PostGreSQL Database compatibility issues, this version requires PG v9.6. Note that this PG version is not distibuted with CentOS/RHEL 7 standard yum repositories.  The esgf-ansible installation default only supports, but the playbooks could be modified to support more recent versions of PG.  Alternatively, we have found that Python 3 CoG can be installed following a successul deployment of the Python 2 version, where the CoG schema deployment is compatible with PostgreSQL v9.2, the version that is distributed with RHEL/CentOS 7.


Manual CoG update
-----------------

```
cd /usr/local/cog/cog_install
git fetch
git checkout v3.15.4 # or master, devel, etc.
/etc/cog-wsgi-8889/apachectl restart  # for ESGF > v4.0.0 
# previous versions restart node: esg-node restart 
```

Latest release: v3.15.4
-----------------------

 - Add link to clear data cart to appear on pages that import the "middle navbar"

Previous updates

 - Updates to templates for help information in preparation for the retirement of the CU CoG site.
