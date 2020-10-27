

ESGF CoG User Accounts
======================

Migrating CoG User Accounts to ESGF
-----------------------------------

When a CoG instance is installed upon an existing ESGF node, user
accounts are seamlessly integrated between the two - no additional work
is required by the node administrator. Specifically:

-  If a user has an existing ESGF account, they can use their existing
   OpenID to log onto CoG. Upon their first login, they will be asked
   for a few pieces of missing information to complete their CoG profile
   (country and institution), after which a CoG account will be
   automatically created.
-  If a user creates a new CoG account, their information will be
   automatically transferred to the database of the local ESGF node. In
   particular, a new OpenID will be created for them, which they can use
   to log onto the local ESGF IdP and CoG instance.

