import logging

from solidfireclient.v1 import cluster
from solidfireclient.v1 import volumes
from solidfireclient.v1 import accounts

LOG = logging.getLogger(__name__)


class Client(object):
    def __init__(self, username, password, mvip=None, **kwargs):
        self.api_port = 443
        self.mvip = mvip
        self.login = username
        self.password = password
        self.ap_version = '1'
        self.use_ssl = False
        self.verify_ssl = False
        self.verbose = False
        self.endpoint_dict = self._build_endpoint_dict()

        # TODO(jdg): Collapse the instantiation and the
        # setting of endpoint_dict var into a single call
        self.volumes = volumes.Volume(self)
        self.volumes.endpoint_dict = self.endpoint_dict
        self.volumes.debug = kwargs.get('debug', False)

        self.accounts = accounts.Account(self)
        self.accounts.endpoint_dict = self.endpoint_dict
        self.accounts.debug = kwargs.get('debug', False)

        self.cluster = cluster.Cluster(self)
        self.cluster.endpoint_dict = self.endpoint_dict
        self.cluster.debug = kwargs.get('debug', False)

    def _build_endpoint_dict(self, **kwargs):
        endpoint = {}
        endpoint['mvip'] = self.mvip
        endpoint['login'] = self.login
        endpoint['passwd'] = self.password
        endpoint['port'] = self.api_port
        endpoint['url'] = 'https://%s:%s' % (endpoint['mvip'],
                                             endpoint['port'])
        return endpoint
