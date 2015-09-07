import logging

from solidfireclient.v1 import accounts
from solidfireclient.v1 import cluster
from solidfireclient.v1 import solidfire_element_api
from solidfireclient.v1 import volumes

LOG = logging.getLogger(__name__)


class Client(object):
    def __init__(self, username, password, mvip=None, **kwargs):
        self.api_port = 443
        self.mvip = mvip
        self.login = username
        self.password = password
        self.client_version = '1'
        self.use_ssl = False
        self.verify_ssl = False
        self.verbose = False
        self.endpoint_version = 7
        self.endpoint_dict = self._build_endpoint_dict()
        sfapi = solidfire_element_api.SolidFireAPI(
            endpoint_dict=self.endpoint_dict)
        self.volumes = volumes.Volume(sfapi)
        self.accounts = accounts.Account(sfapi)
        self.cluster = cluster.Cluster(sfapi)

        # self.cluster = solidfire_element_api.SolidFireAPI(self)
        # self.cluster.endpoint_dict = self.endpoint_dict
        # self.cluster.debug = kwargs.get('debug', False)

    def _build_endpoint_dict(self, **kwargs):
        endpoint = {}
        endpoint['mvip'] = self.mvip
        endpoint['login'] = self.login
        endpoint['passwd'] = self.password
        endpoint['port'] = self.api_port
        endpoint['url'] = 'https://%s:%s' % (endpoint['mvip'],
                                             endpoint['port'])
        return endpoint
