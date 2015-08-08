import logging

from solidfireclient.v1 import volumes
from solidfireclient.v1 import accounts

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
        self.endpoint_version = 7.0
        self.endpoint_dict = self._build_endpoint_dict()

        self.volumes = volumes.Volume(self.endpoint_dict, self.endpoint_version)
        self.accounts = accounts.Account(self.endpoint_dict, self.endpoint_version)


    def _build_endpoint_dict(self, **kwargs):
        endpoint = {}
        endpoint['mvip'] = self.mvip
        endpoint['login'] = self.login
        endpoint['passwd'] = self.password
        endpoint['port'] = self.api_port
        endpoint['url'] = 'https://%s:%s' % (endpoint['mvip'],
                                             endpoint['port'])
        return endpoint
