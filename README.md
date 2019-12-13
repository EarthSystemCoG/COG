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

For more information, visit: http://earthsystemcog.org/

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
