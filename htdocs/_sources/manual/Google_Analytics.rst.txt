

Google Analytics
================

Customizing Federal Google Analytics
------------------------------------

-  Federally sponsored websites are required to have Google Analytics
   installed.
-  This version of Google Analytics sends information back to the Office
   of Management and Budget (OMB). It does not
   send information back to your agency, site, or node administrator.
-  CoG comes with pre-installed Google Analytics with options to set
   various variables for any particular agency.

The Default
-----------

-  By default, the CoG instance will load a file
   /templates/cog/common/google_analytics.html that is empty.

Overriding the Default
----------------------

-  Sites that want to insert their own Google Analytics must place a
   customized version of the default file into

   -  $COG_CONFIG_DIR/mytemplates/cog/common/google_analytics.html
