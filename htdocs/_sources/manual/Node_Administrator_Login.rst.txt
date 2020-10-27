
ESGF/CoG Administrator Login
============================

One of the first checks to perform after a successfull ESGF-CoG
installation is that you can login as the Node administrator, using the
credentials specified in the ESGF installer. There are two ways to
login:

Option 1: Username/Password login
---------------------------------

.. code:: console

    Open URL:https://<hostname>/login2/ 
    username: rootAdmin 
    password: chosen root password set during the ESGF-CoG Node installation

-  rootAdmin is the user name for all ESGF nodes (established by the
   ESGF Node installer).
-  This page is not hyperlinked anywhere on the node.
-  This non-OpenID login is intended as an alternative for the Node
   administrator to login when the primary OpenID login doesn’t work
   (for any possible reason), and will work ONLY for the “rootAdmin”
   username, because that account is created into the Django database
   when CoG is first installed. All other ESGF accounts are NOT mirrored
   into the Django database, so all other ESGF users MUST login with
   OpenID.
-  The rootAdmin account is NOT synced between ESGF and Django - any
   password change in ESGF or Django will NOT be reflected into the
   other database.

Option 2: OpenID login
----------------------

-  Click on the “Login” link in the upper bar menu (Figure 1)
-  This accesses the URL https://<hostname>/login/ 


.. figure:: /images/login_link.png
   :scale: 95%
   :alt:

Figure 1: Screenshot of the Login link in the upper right corner of CoG.


.. code:: console

    OpenID: https://<hostname>/esgf-idp/openid/rootAdmin

-  The “rootAdmin” user and OpenID is generated when the ESGF Node is
   first installed.
-   must be replaced by the Node’s fully qualified name.
-  Clicking on “Login” will take you to the ESGF Identity Provider page
   for the Node, where you can enter the same ESGF root administrator
   password as described above.
-  Upon successfull login, you should be redirected back to CoG.
