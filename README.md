Python SDK and CLI for SolidFire Storage Clusters
=================================================

This is a Command-Line Client and Python Library for the SolidFire API.
The Client Utility is intended to provide a quick and easy Command Line
interface to interact with the SolidFire API and is made of up
wrapper/helper methods to enable a user to do a number of things more
easily with their Cluster.

The Python Libraries implement the same methods that are used by the
Client, however in addition they also provide the ability to simply call
the SolidFire API method directly. In most cases each will simply take a
dictionary which is the API parameters. This should follow the Element
API Reference Guide, and simply provide some wrappers around the calls
to make automation easier.

Check out the specific sections and examples below.

NOTE: This is very much a work in progress, the idea started over a year
ago and just finally decided to try it out on a VERY cold and snowy day
after Christmas.

Installation
------------

These modules are still in early development and while available in
private git repo, they are not currently being published to PyPI
(hopefully they will be).

Best way to install is to clone the repository and use pip:

> pip install -e \<path-to-local-repository\>

Command-Line Usage
------------------

To use the Command-Line you will need to either provide your SolidFire
credentials on the command line, or set them as environment variable:

    export SF_USERNAME=admin
    export SF_PASSWORD=password
    export SF_MVIP=10.10.0.1

Help/Documentation for using the shell is also available by running

`solidfire --help`:

    usage: solidfire [--debug] [--verbose] [--sf-login <sf-login>]
                     [--sf-password <sf-password>] [--sf-mvip <cluster-mgmt-ip>]
                     [--sf-cluster-admin <cluster-admin-account>]
                     [--sf-admin-password <cluster-admin-password>]
                     [--solidfire-api-version <client-api-version-to-use>]
                     <subcommand> ...

    Command-line interface to the SolidFire API.

    Positional arguments:
      <subcommand>
        create
        volume-list         List volumes on a cluster.
        volume-show         Shows volume details.
        help                Display help about this program or one of its
                            subcommands.

    Optional arguments:
      --debug               Print debug output (shows raw SolidFire API call and response data)
      --verbose             Provides more verbose output, including json requests
                            and responses
      --sf-login <sf-login>
                            Defaults to env[SF_USERNAME]
      --sf-password <sf-password>
                            Defaults to env[SF_PASSWORD]
      --sf-mvip <cluster-mgmt-ip>
                            Defaults to env[SF_MVIP]
      --sf-cluster-admin <cluster-admin-account>
                            Defaults to env[SF_CLUSTER_ADMIN]
      --sf-admin-password <cluster-admin-password>
                            Defaults to env[SF_ADMIN_PASSWORD]
      --solidfire-api-version <client-api-version-to-use>
                            Defaults to 1

    See "solidfire help COMMAND" for help on a specific command.

Example command to show details on a specified volume:

    solidfire volume-show 30943
    +--------------------+--------------------------------------------------------------------------------+
    |      Property      |                                     Value                                      |
    +--------------------+--------------------------------------------------------------------------------+
    |       access       |                                   readWrite                                    |
    |     accountID      |                                     12661                                      |
    |     attributes     |                                       {}                                       |
    |     createTime     |                              2014-12-31T02:44:52Z                              |
    |     deleteTime     |                                                                                |
    |     enable512e     |                                      True                                      |
    |        iqn         | iqn.2010-01.com.solidfire:9kdb.uuid-56a2bab0-5223-4fc5-ba4d-0595820ec453.30943 |
    |        name        |                   UUID-56a2bab0-5223-4fc5-ba4d-0595820ec453                    |
    |     purgeTime      |                                                                                |
    |  scsiEUIDeviceID   |                        396b6462000078dff47acc0100000000                        |
    |  scsiNAADeviceID   |                        6f47acc100000000396b6462000078df                        |
    |     sliceCount     |                                       1                                        |
    |       status       |                                     active                                     |
    |     totalSize      |                                   1073741824                                   |
    | volumeAccessGroups |                                       []                                       |
    |      volumeID      |                                     30943                                      |
    |    volumePairs     |                                       []                                       |
    +--------------------+--------------------------------------------------------------------------------+

Python API/SDK
--------------

The Python libs are seperated by Cluster resources, volumes, accounts,
drivers etc. The same calls that are available via the Command-Line are
also available from the lib, the biggest difference however is that we
return that dictionary of the SolidFire API response directly.

NOTE: env variable reading isn't setup in the lib *yet* but will be

Example using the Python libs:

    >>> from solidfireclient import client as sfc
    >>> sf_client = sfc.Client('admin', 'admin', '192.168.139.103')
    >>> sf_client.volumes.show(23596)
    {u'status': u'active', u'enable512e': True, u'qos': {u'burstIOPS': 15000, u'curve': {u'8192': 160, u'32768': 500, u'4096': 100, u'1048576': 15000, u'131072': 1950, u'262144': 3900, u'16384': 270, u'65536': 1000, u'524288': 7600}, u'minIOPS': 100, u'burstTime': 60, u'maxIOPS': 15000}, u'name': u'UUID-a8a501cb-dd29-46d5-8506-56b652de6055', u'volumeAccessGroups': [], u'totalSize': 1073741824, u'scsiNAADeviceID': u'6f47acc100000000396b646200005c2c', u'purgeTime': u'', u'scsiEUIDeviceID': u'396b646200005c2cf47acc0100000000', u'volumeID': 23596, u'access': u'readWrite', u'iqn': u'iqn.2010-01.com.solidfire:9kdb.uuid-a8a501cb-dd29-46d5-8506-56b652de6055.23596', u'sliceCount': 1, u'attributes': {u'created_at': u'2014-12-23T07:15:19.000000', u'attached_to': None, u'is_clone': u'False', u'attach_time': None, u'uuid': u'a8a501cb-dd29-46d5-8506-56b652de6055'}, u'volumePairs': [], u'deleteTime': u'', u'createTime': u'2014-12-23T07:15:20Z', u'accountID': 9573}
    >>>
