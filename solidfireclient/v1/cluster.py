import logging

from solidfireclient.v1 import solidfire_element_api as sfapi
from solidfireclient.v1 import object_utils

LOG = logging.getLogger(__name__)
logging.basicConfig()


class Cluster(sfapi.SolidFireAPI):
    """ Cluster methods for the SolidFire Cluster. """

    def __init__(self, sfapi):
        super(Cluster, self).__init__(sfapi)
        self.sfapi = sfapi

    def get_capacity(self):
        """
        Get the current capacity values for the Cluster.
        """
        try:
            cluster_capacity = (
                self.sfapi.get_cluster_capacity()['clusterCapacity'])
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex
        if self.raw:
            return cluster_capacity
        else:
            return object_utils.convert_dict_to_object(cluster_capacity)

    def get_version(self):
        try:
            version_info = self.sfapi.get_cluster_version_info()
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex
        if self.raw:
            return version_info
        else:
            return object_utils.convert_dict_to_object(version_info)

    def get_limits(self):
        try:
            limits = self.sfapi.get_limits()
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex
        if self.raw:
            return limits
        else:
            return object_utils.convert_dict_to_object(limits)

    def list_services(self):
        try:
            services = self.sfapi.list_services()
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex
        if self.raw:
            return services
        else:
            return object_utils.convert_dict_to_object(services)

    def get_async_result(self, handle):
        try:
            status = self.sfapi.get_async_result(handle)
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex
        if self.raw:
            return status
        else:
            return object_utils.convert_dict_to_object(status)
