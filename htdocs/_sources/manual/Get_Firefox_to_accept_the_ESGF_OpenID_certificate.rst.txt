
Getting Firefox to accept the ESGF OpenID certificate
=====================================================

CoG uses an ESGF OpenID as its authentication mechanism. The SSL
certificate used by ESGF is self-signed. Some browsers have difficulty
with this certificate and users will need to tell their browser to trust
it.

Every browser has a different mechanism for accepting SSL certificates
it does not trust. Below are the steps for Firefox.

Step 1: Enter your OpenID (or select your OpenID providing using the pulldown) in the login box and click “Login”
-----------------------------------------------------------------------------------------------------------------

.. figure:: /images/login.png
   :scale: 85%
   :alt:

Step 2: Click on “Advanced”
---------------------------

.. figure:: /images/ff_1.png
   :scale: 45%
   :alt:

Step 2: Click “Add Exception…”
------------------------------

.. figure:: /images/ff_2.png
   :scale: 45%
   :alt:

Step 3: Click “Confirm Security Exception”
------------------------------------------

.. figure:: /images/ff_3.png
   :scale: 45%
   :alt:

Step 4: Click “Resend”
----------------------

.. figure:: /images/ff_4.png
   :scale: 45%
   :alt:

Step 5: Proceed with authentication
-----------------------------------


