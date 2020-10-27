
Getting Internet Explorer to accept the ESGF OpenID certificate
===============================================================

CoG uses an ESGF OpenID as its authentication mechanism. The SSL
certificate used by ESGF is self-signed. Some browsers have difficulty
with this certificate and users will need to tell their browser to trust
it.

Every browser has a different mechanism for accepting SSL certificates
it does not trust. Below are the steps for Internet Explorer.

Step 1: Enter your OpenID in the box and click “Login”
------------------------------------------------------

.. figure:: /images/login.png
   :scale: 85%
   :alt:

Step 2: Click the "Continue to this website (not recommended) link.
-------------------------------------------------------------------

.. figure:: /images/ie_untrusted.png
   :scale: 85%
   :alt:

Step 3: Enter your password in the box provided
-----------------------------------------------

.. figure:: /images/chrome_sucess.png
   :scale: 85%
   :alt:

