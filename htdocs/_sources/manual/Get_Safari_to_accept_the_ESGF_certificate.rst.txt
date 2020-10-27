
Getting Safari to accept the ESGF OpenID certificate
====================================================

CoG uses an ESGF OpenID as its authentication mechanism. The SSL
certificate used by ESGF is self-signed. Some browsers have difficulty
with this certificate and users will need to tell their browser to trust
it.

Every browser has a different mechanism for accepting SSL certificates
it does not trust. Below are the steps for Safari. If you still can not
display the ESGF login page after these steps AND you are using a Mac,
please contact support. Some institutions, e.g. NASA, preinstall the
ESGF certificate and this will have to be removed in order to be
trusted. You may also which to switch to FireFox or Chrome.

Step 1: Enter your ESGF OpenID (or select an OpenID provider from the pulldown) in the login box and click “Login”
------------------------------------------------------------------------------------------------------------------

.. figure:: /images/login.png
   :scale: 85%
   :alt:

Step 2: Click the “Show Certificate” button
-------------------------------------------

.. figure:: /images/untrusted_safari.png
   :scale: 85%
   :alt:

Step 3: Expand the Trust section
--------------------------------

.. figure:: /images/show_certificate_safari.png
   :scale: 85%
   :alt:

Step 4: Change the Trust settings
---------------------------------

.. figure:: /images/expand_trust_safari.png
   :scale: 85%
   :alt:

.. figure:: /images/trust_settings_safari.png
   :scale: 85%
   :alt:



Step 5: Authenticate
--------------------

.. figure:: /images/trust_password_safari.png
   :scale: 85%
   :alt:


Step 6: Proceed with authentication
-----------------------------------



