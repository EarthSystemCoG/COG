
Header and Footer
=================

Customizing the header and footer
---------------------------------

Release 2.5 of CoG introduced the ability for organizations to create a
customized header and footer around their ESGF-CoG installation. These
elements allow organizations to brand their installation with
organzational logos and links.

The Defaults
------------

The CoG distribution comes with a default header and footer that have
been only partially customized. Action must be taken to override these
defaults.

-  The default files are:

   -  cog/templates/cog/common/cog_header_custom.html
   -  cog/templates/cog/common/cog_footer_custom.html

-  It is hoped that the specified styling will be retained. This
   maintains a continuity of styling across federated CoG instances:

   -  Institutional logos are on the left.
   -  The ESGF logo, which comes with the distribution is on the right.
   -  {{site.name}} is automatically added to the header. {{site.name}}
      is set in the vcog_settings.cfg file (see the installation
      instructions for details).
   -  The color of the banner is set within the cogstyle.css. It shoudl
      not be overridden.


.. figure:: /images/default_header_1503.png
   :scale: 65%
   :alt:

Figure 1: Screenshot of the default header. Note the placeholder for
organizational logos. This is the default as of v2.11 of CoG.

.. figure:: /images/default_footer.png
   :scale: 65%
   :alt:


Figure 2: Screenshot of the default footer. Note the placeholder for
organizational links.

Overridding the Defaults
------------------------

The default header and footer can be overridden by placing a custom
temaplate with the same name under the root level directory
/mytemplates/. Note that the /mytemplates directory is the equivilant to
the /templates in the path below.

-  COG_CONFIG_DIR=/usr/local/cog/cog_config by default

For example, to override the template
/cog/templates/cog/common/cog_header_custom.html and
/cog/templates/common/cog_footer_custom.html which come with the
distribution, create the two custom files:

-  /usr/local/cog/cog_config/mytemplates/cog/common/cog_header_custom.html
-  /usr/local/cog/cog_config/mytemplates/cog/common/cog_footer_custom.html

Images and other media should be located under the directory /mymedia/
and referenced from within the template as “/mymedia/”.

For example, the file located at /usr/local/cog/mymedia/nasa.jpeg can be
loaded by any template as src=“/mymedia/nasa.jpeg” (please note the
first leading ‘/’).

Example code
------------

-  Several example files come with the distribution.
-  They are located in /resources/noaa/mytemplates/cog/common.

.. figure:: /images/header_example_1503.png
   :scale: 65%
   :alt:
