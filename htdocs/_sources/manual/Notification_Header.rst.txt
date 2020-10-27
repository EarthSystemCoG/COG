
Notification Header
===================

Release 3.1 of CoG introduced the ability for organizations to create a
customized notification header. These header allows for node-wide
announcements above the project space (Figure 1).


.. figure:: /images/notification_header.png
   :scale: 85%
   :alt:

Figure 1: Screenshot of a node showing the notification header.

The Defaults
------------

The CoG distribution comes with a default header and footer that have
been only partially customized. Action must be taken to override these
defaults.

-  The default files are:

   -  cog/templates/cog/common/cog_notification_custom.html

Overriding the Defaults
-----------------------

The default notification header can be overridden by placing a custom
template with the same name under the root level directory
/mytemplates/. Note that the /mytemplates directory is the equivilant to
the /templates in the path below.

-  COG_CONFIG_DIR=/usr/local/cog by default

For example, to override the template
/cog/templates/cog/common/cog_notification_custom.html, which comes with
the distribution, create the a custom file:

-  /usr/local/cog/mytemplates/cog/common/cog_notification_custom.html

Edit the message inside the template to your needs, and make sure to
chahne the HTML attribute “display:none” to “display:block” to make the
header visible.
