
import json
import logging
import  sys

from solidfireclient.common import base


class VolumeManager(base.Manager):
    def create(self, mvip, size, account_id, count=1, name=None, qos={}, attributes={}, enable_512e=True):
        import pdb;pdb.set_trace()
        body = {'name': name,
                'accountID': account_id,
                'totalSize': size,
                'enable512e': enable_512e,
                'attributes': attributes,
                'qos': qos}

        return self._create(mvip, body)
    #def create(self, mvip, login, password, size, name, **kwargs):
        #count = kwargs.get('count', 1)
        #account_id = kwargs.get('account_id', None)
        #account_name = kwargs.get('account_name', None)
        #qos = kwargs.get('qos', {})
        #attributes = kwargs.get('attributes', {})
        #chap_secrets = kwargs.get('chap_secrets', None)
        #emulation = kwargs.get('emulation', False)
        #cluster_client = ClusterManager(mvip, login, password)
        #if account_id is None:
        #    account = cluster_client.get_account_by_name(account_name)
        #    if account is None or 'accountID' not in account:
        #        logging.warning('Account name: %s not found, creating one now.' % account_name)
        #        account = cluster_client.add_account(account_name, chap_secrets)

        #    account_id = account['accountID']

        #created_volumes = []
        #for volnum in xrange(0, count):
        #    kwargs = {'name': name,
        #              'accountID': account_id,
        #              'totalSize': int(size * pow(10, 9)),
        #              'enable512e': emulation,
        #              'qos': qos}
        #    cluster_client.create_volume(**kwargs)


    def delete(self):
        pass

    def clone(self):
        pass

    def modify(self):
        pass

    def show(self):
        pass

    def get_qos(self):
        pass

    def get_stats(self):
        pass
