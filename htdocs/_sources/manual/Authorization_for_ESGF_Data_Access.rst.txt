
Authorization for ESGF Data Access
==================================

Why data access control groups?
-------------------------------

Often data users must accept a “terms of use” (e.g. agree to acknowledge
the data producers in publications) before downloading data. Therefore,
the creation of a ESGF-CoG account is normally not sufficient for data
access, you also need the authorization to access data. User’s must join
a data access control group for the project they wish to download data
from. If the right group is not joined, for example, Wget scripts will
prematurely fail with a “Forbidden” error message.

Which data access control groups currently exist in ESGF?
---------------------------------------------------------

Below is a list of access control groups by project:

.. csv-table::
   :header:  "Project", "Group Name"
   :widths:  40, 60
   :align:  left

   "CMIP5", "CMIP5 Research, CMIP5 Commercial"
   "EUCLIPSE", "CMIP5 Research"
   "GeoMIP", "CMIP5 Research"
   "LUCID", "CMIP5 Research"
   "Obs4MIPS", "CMIP5 Research NASA OBS"
   "PMIP3","CMIP5 Research"
   "TAMIP", "CMIP5 Research"

   "ACME", "ACME"
   "CORDEX", "CORDEX Research, CORDEX Commercial"
   "ISI-MIP", "ISI-MIPResearch, ISI-MIP Unrestricted"
   "specs","SPECS"

For example, if you need CMIP5 data, you will need to join either CMIP5
Research or CMIP5 Commercial. Which CMIP5 data are restricted to
non-commercial research and education and which data can also be used
for commercial purposes is tabulated in the CMIP5 document Modeling
Groups and their Terms of Use. A membership in CMIP5 Research is also
sufficient for download of data of other MIPs, not just CMIP5. An
exception is ISI-MIP. Other projects such as CORDEX have their own
groups. Which CORDEX data can only be used for non-commercial purposes
and which thoroughly is listed in the CORDEX Models overview.

Who has to join?
----------------

Everyone who has created a CoG account and wants to download data from
one of the projects listed in the table above must join the appropriate
access control group. This will need to be repeated for each ESGF OpenID
since ESGF cannot assign group memberships to persons, only to OpenIDs.
You will need to do this for each group you need data from. It is not
necessary to create a new CoG account for each group. It is possible to
have several memberships with one OpenID.

How to join?
------------

Two different ways to join a data access control group in ESGF:

1. View list of data access control groups

A comprehensive list of access control groups can be found at: ESGF Data
Access Control Groups , which contains a list of groups and links for
registration. Note, the home pages of ESGF nodes may list or exclude
groups based on their individual holdings.

2. Download a file with your browser

The easiest way to join a data access control group is a download a file
with your browser’s download manager. This process will automatically
present a window for group registration.

Step 2a: In an ESGF portal, select a dataset with data of the project
you are interested in and click on “Show Files” (Figure 1).

.. figure:: /images/group_registration_select_dataset.png
   :scale: 85%
   :alt:

Figure 1: Screenshot of the some search results showing the “Show Files”
link.

Step 2b: Click on “HTTPServer” (Figure 2).

-  After login you will be guided to the Group Registration Request page
   (Figure 3) if a group membership is missing.


.. figure:: /images/group_registration_filelist.png
   :scale: 85%
   :alt:

Figure 2: Screenshot of the search results expanded to show the
“HTTPServer” link.

.. figure:: /images/group_registration_groups.png
   :scale: 45%
   :alt:


Figure 3: Screen shot of the the group registration page.

Step 2c: Choose a group and click on “Register”.

-  A sub-window opens with the terms of use (Figure 4).
-  After accepting the terms, group membership is immediately active and
   the download window will open.

.. figure:: /images/group_registration_terms.png
   :scale: 85%
   :alt:

Figure 4: Screenshot of the terms of use window. It will be different
for each group.
