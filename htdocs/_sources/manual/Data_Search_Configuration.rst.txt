
Data Search Configuration
=========================

Each CoG project can be configured to expose a data search page that
allows users to search the distributed ESGF metadata archives with
custom settings. To do so, the project administrator first needs to
enable the Data Search widget (see Step 1 below) for that project, then
use the “Configure Search” page to customize the search target and
constriaints (Step 2). The project search configuration can be
completely built using the web interface, or it can be
exported/imported/changed through text files that are stored on the Node
where CoG is running.

Step 1: Turn on the Data Search widget (Figure 1)
-------------------------------------------------

-  CoG has widgets that exist on the right side of the page.
-  The Data Search widget allows users to access an ESGF search.
-  The Data Search widget is OFF by default and must be enabled.

   -  View tutorial with screenshots on how to enable the widget https://www.earthsystemcog.org/projects/cog/doc/data_widget

-  The Data Search widget will always be the first widget in the right
   column.
-  Wiki pages have the option of turning off the right widgets.


.. figure:: /images/search_widget.png
   :scale: 95%
   :alt:


Figure 1: Screenshot of the Data Search widget

Step 2: Customize the Data Search Constraints
---------------------------------------------

-  By default, the search (for any CoG project) will be configured to
   query the local ESGF search services with no constraints (in
   particular, this means executing a distributed search across all
   federated ESGF Nodes). - Most likely, you will want to configure the
   search for the project specific audience. This can be done either
   through the web interface, or by importing an already existing search
   configuration file. These options are described in detail in the
   following pages:

   -  View tutorial on how to configure general search options https://www.earthsystemcog.org/projects/cog/doc/data_options
   -  View tutorial on how to configure the search facets https://www.earthsystemcog.org/projects/cog/doc/search_facet_config
   -  View tutorial on how to import/export the project search
      configuration https://www.earthsystemcog.org/projects/cog/search_import_export
- After saving your changes, access the project
      search page and test that results are returned as you expect.

Optional: Enable New Search Facets
----------------------------------

Because of security constraints, the ESGF Search Services can not be
queried with arbitrary facet names, although arbitrary facet names and
values can be ingested at publishing time into the Solr metadata
(provided they are valid and don’t create any conflicts). Nontheless, to
enable a new facet as a valid query parameter, the ESGF Node
administrator needs only insert that facet in the ESGF configuration
file:

/esg/config/facets.properties

and restart the Node.
