
Getting Chrome to accept the ESGF OpenID certificate
====================================================

CoG uses an ESGF OpenID as its authentication mechanism. The SSL
certificate used by ESGF is self-signed. Some browsers have difficulty
with this certificate and users will need to tell their browser to trust
it.

Every browser has a different mechanism for accepting SSL certificates
it does not trust. Below are the steps for Chrome and Aviator, which is
based on Chrome.


Step 1: Insert your OpenID (or select an OpenID provider using the pulldown) in the login box and press “Login”
---------------------------------------------------------------------------------------------------------------


.. figure:: /images/login.png
   :scale: 85%
   :alt:


Step 2: Click “Advanced” on the warning page
--------------------------------------------

.. figure:: /images/chrome_untrusted.png
   :scale: 85%
   :alt:


Step 3: Click “Proceed to $node (unsafe)”
-----------------------------------------

.. figure:: /images/chrome_advanced.png
   :scale: 85%
   :alt:


Step 4: Proceed with authentication.
------------------------------------
