
"Local Shard" Setup
===================

In many cases, data collections accessed through the ESGF system
comprise data that are hosted on distributed servers, and that must be
found by federated searches initiated at any node in the federation.
Such is the case for prominent data collections such as CMIP5/6, CORDEX,
obs4MIPs, ana4MIPs etc. For these collections, the search indexes are
distributed on multiple nodes, and replicated by the other nodes so that
a distributed search can retrieve the complete set of results.

In other cases, data collections are interesting only to specific
projects or institutions, and they only need to be exposed through a
single ESGF node for users to be able to find them and download the
data. In these cases, their metadata should not be replicated across all
ESGF nodes in the federarion, with the result of over-inflating all the
search indexes, and consequent reduction in performance.

It turns out that an ESGF node administrator can setup and publish data
to a “local shard” that is not shared with the rest of the ESGF
federation, following a few simple steps, as described below.

Note: local shard supports requires esg-search version 4.3.0 or above,
and CoG version 3.0.3 or above.

Step 1) Setup a “local shard”
-----------------------------

The following command will create a new Solr instance configuration
suitable for publishing and searching local data:


.. code:: console

    esg-node –add-replica-shard localhost:8982

(note that for various reasons it is best to choose “8982” as the local
shard port).

This command will:

-  Create a local shard configuration directory
   /usr/local/solr-home/localhost-8982
-  Create a local shard Solr index directory
   /esg/solr-index/localhost-8982
-  Insert the local shard in the file
   /esg/config/esgf_shards_static.xml, which is used by the local ESGF
   search service to create a list of shards to query. In other words,
   the local shard at port 8982 will be included by default in all
   searches executed by the local ESGF search service
-  Insert the local shard in the file /esg/config/esgf_shards.config, so
   that the corresponding Solr instance is always started/stopped
   together with the rest of the ESGF services (and shards) on that node

The local 8982 shard will be started by the esg-node command with
neither the option -Denable.master=true, nor with the option
-Denable.slave=true (instead, the flag -Denable.localhost=true is used):
this means that this shard will not replicate from any other shard, and
it will not expose itself to replication from other shards.

Step 2) Publish data collections to the “local shard”
-----------------------------------------------------

In general, data can be published to the local shard by following two
simple requirements:

-  Target the Solr index on port 8982
-  Include an additional piece of metadata: shard=localhost:8982 to all
   dataset-level records (this informatoin is used by search clients to
   efficiently find all files that belong to a given dataset).

If using the ESGF publisher client to publish data, the above
requirements can be fulfilled by a few simple changes in the esg.ini
file:

-  Change the URL of the target publishing service:

.. code:: console

    from: https://your.host.name/esg-search/remote/secure/client-cert/hessian/publishingService
    to: https://your.host.name/esg-search/remote/secure/client-cert/hessian/publishingServiceLocal

Add the “shard” metadata field as part of the specific project
configuration:

.. code:: console

    categories = 
          project | enum | true | true | 0
          ..............................................
          shard | string | true | true | 14

    category_default =
          project |
          ....................... 
          shard | localhost:8982

Step 3) Configure the CoG Search User Interface
-----------------------------------------------

With CoG, each project can configure its search space by targetting a
specific search URL and optionally adding other fixed search constraints
(such as project=XYZ). An ESGF administraor can configure a CoG project
to find data indexed on the local shard in two ways:

-  By targeting the local ESGF search service with no additional
   federation constraints: as mentioned before, the 8982 shard is
   contained in the esgf_shards_static.xml file and therefore will be
   picked up by the local ESGF search service by default. Specifically,
   configure the CoG project search as follows:

.. code:: console

    Search Service URL: http://your.host.name/esg-search/search/
    Constraints: do NOT add distrib=false and do NOT specifiy any shard constraint

By targeting the local ESGF search service AND adding a specific shard
constraint that includes that shard. In this case, the local ESGF
service will query only those shards that are specified in the
constraint. For example:

.. code:: console

    Search Service URL: http://your.host.name/esg-search/search/
    Constraints: shards=localhost:8983/solr,localhost:8982/solr

The first configuration will cause the CoG interface to return results
from ALL shards configured in the local file esgf_shards_static.xml
(which may include other ESGF nodes throughout the federation); the
second configuration will return results only from those shards that are
explicitely listed.
