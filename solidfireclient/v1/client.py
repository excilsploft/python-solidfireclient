#Copyright 2013 SolidFire Inc.
# All Rights Reserved.

from solidfireclient.common import http
from solidfireclient.v1 import accounts
from solidfireclient.v1 import clusters
from solidfireclient.v1 import drives
from solidfireclient.v1 import nodes
from solidfireclient.v1 import volumes


class Client(http.HTTPClient):
    """Client for the solidfire v1 API.

    :param string mvip: MVIP of the SolidFire Cluster
    :param string login: Admin login name to use.
    :param string pasword: Admin password for specified login.
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the solidfire v1 API."""
        super(Client, self).__init__(*args, **kwargs)
        self.volumes = volumes.VolumeManager(self)
        self.drives = drives.DriveManager(self)
        self.accounts = accounts.AccountManager(self)
        self.nodes = nodes.NodeManager(self)
        self.clusters = clusters.ClusterManager(self)

