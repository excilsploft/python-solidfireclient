import logging
import six

from solidfireclient.v1 import solidfire_element_api as sfapi
from solidfireclient.v1 import object_utils

LOG = logging.getLogger(__name__)
logging.basicConfig()

# Handy:
# type(volumes[1]) is dict
# True
# type(vobs[1]) is dict
# False


class Volume(sfapi.SolidFireAPI):
    """ Volume methods for the SolidFire Cluster. """

    def __init__(self, *args, **kwargs):
        super(Volume, self).__init__(*args, **kwargs)

    def list_attributes(self):
        """
        Display a list of valid volume attributes.

        Note, this works by grabbing a volume object from the Cluster
        and iterating through its attributes and displaying the key
        names.  This requires that an active volume exist on the system.
        """

        try:
            volumes = self.list_active_volumes()
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex
        if len(volumes) < 1:
            # TODO(jdg): Raise here as we need at least one vol to interrogate
            # and return an empty list
            raise Exception

        return [k for k, v in six.iteritems(volumes[0])]

    def list(self, start_id=0, limit=0, account_id=None):
        """
        Retrieve a list of active volumes on the SolidFire Cluster.

        params: start_id Retrieve volumes starting with id == start_id
        params: limit Max number of volumes to return
        params: account_id Retrieve only those volumes associated
                With this account (NOTE: Ignores start_id and limit)

        """
        volumes = []

        if account_id is None:
            try:
                volumes = self.list_active_volumes(start_id, limit)
            except sfapi.SolidFireRequestException as ex:
                LOG.error(ex.msg)
                raise ex

        else:
            try:
                volumes = self.list_volumes_for_account(account_id)
            except sfapi.SolidFireRequestException as ex:
                LOG.error(ex.msg)
                raise ex

        snapshots = []
        try:
            snapshots = self.list_snapshots()
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex

        if len(volumes) == 0:
            return None

        # Meld the snapshot ID's into the volumes we got back
        for v in volumes:
            snap_ids = [entry['snapshotID'] for entry
                        in snapshots if entry['volumeID'] == v['volumeID']]
            v['snapshots'] = snap_ids

        volumes = sorted((volumes),
                         key=lambda k: k['volumeID'])
        if self.raw:
            return volumes
        else:
            return object_utils.convert_dict_to_object(volumes)

    def get(self, volid):
        """
        Retrieve details for the specified volume.

        param id: The ID of the Volume to retrieve

        Note if the Volume's current state is not Active
        it won't be returned.  (Use show_deleted)
        """

        try:
            response = self.list(volid, 1)
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex

        if len(response) != 1:
            raise Exception

        volume = response[0]
        if self.raw:
            return volume
        else:
            return object_utils.convert_dict_to_object(volume)

    def list_deleted(self):
        """
        Retrieve a list of deleted volumes on the SolidFire Cluster.

        """
        volumes = []

        try:
            volumes = self.list_deleted_volumes()
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex

        if self.raw:
            return volumes
        else:
            return object_utils.convert_dict_to_object(volumes)

    def get_deleted(self, volid):
        """
        Retrieve details for the specified deleted volume.

        param id: The ID of the Volume to retrieve

        Note: If the volume has been purged the return is None
        """

        volumes = []

        try:
            volumes = self.list_deleted_volumes()
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex

        if not any(v['VolumeID'] == volid for v in volumes):
            return None

    def delete(self, ids, purge):
        """
        Delete the specified volume from the SolidFire Cluster.

        param ids: List of Volume ID's to delete
        param purge: True or False, issues purge immediately after delete
        """

<<<<<<< HEAD
        try:
            self.delete_volume(volid)
            if purge:
                self.purge_deleted_volume(volid)
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex
=======
        for i in ids:
            try:
                self.delete_volume(i)
                if purge:
                    self.purge_deleted_volume(i)
            except Exception:
                pass
>>>>>>> 5293e4837e21ae09871c5607582cbcc2748f8b7b
        return None

    def delete_all(self, purge):
        """
        Delete all volumes on the SolidFire Cluster.

        param purge: True or False, issues purge immediately after delete
        """

        vlist = self.list()
        for v in vlist:
            self.delete(v.volumeID)
        if purge:
            dlist = self.list_deleted()
            for v in dlist:
                self.purge_deleted_volume(v.volumeID)

    def create(self, size, account_id, **kwargs):
        """
        Creates a Volume(s) on the SolidFire Cluster.

        param size: Size in Gig for the new volume
        param account_id: Account ID to assign volume to

        Optional keyword arguments
          name: Name of cloned volume (limited to 64 characters, default=None)
          count: Create multiple volumes with these settings
          attributes: Dict containting Key Value pairs (extra metadata)
          chap_secrets: Chap credentials to assign to volume
          emulation: Set equal to True to enable 512 byte emulation
          qos: Dict containing Key Value pairs to indicate QoS setings

        """
        volid_list = []
        name = kwargs.get('name', None)
        count = kwargs.get('count', 1)
        attributes = kwargs.get('attributes', {})
        enable512e = kwargs.get('emulation', False)
        qos = kwargs.get('qos', {})
<<<<<<< HEAD
        params = {'name': name,
                  'accountID': account_id,
                  'totalSize': int(size) * pow(10, 9),
                  'enable512e': enable512e,
                  'attributes': attributes,
                  'qos': qos}

        if name:
            params['name'] = name
        if attributes:
            params['attributes'] = attributes
        if qos:
            params['qos'] = qos
        if chap_secrets:
            params['chap_secrets'] = chap_secrets
        for i in xrange(0, int(count)):
            vname = name
            if i > 0:
                vname = name + "-" + str(i)
            try:
                response = self.create_volume(vname, account_id,
                                              int(size) * pow(10, 9),
                                              enable512e, qos, attributes)
            except sfapi.SolidFireRequestException as ex:
                LOG.error(ex.msg)
                raise ex
=======

        vname = name
        for i in xrange(0, int(count)):
            if name is not None and i > 0:
                vname = name + ('-%s' % i)
            response = self.create_volume(vname, account_id,
                                          int(size) * pow(10, 9),
                                          enable512e, qos, attributes)
>>>>>>> 5293e4837e21ae09871c5607582cbcc2748f8b7b
            volid_list.append(response['volumeID'])

        vlist = []
        for id in volid_list:
            vlist.append(self.show(id))
        return vlist

    def clone_volume(self, source_volid, name=None,
                     new_account_id=None, new_size=None, access=None,
                     attributes=None, qos=None, snapshot_id=None):
        """
        Creates a clone of an existing Volume.

        param source_volid: VolumeID for the Volume to be cloned

        Optional keyword arguments:
          name: Name of cloned volume (limited to 64 characters, default=None)
          account_id: New account ID to assign clone to
          new_size: New size of clone in bytes
          access: Can be readOnly, readWrite, locked or replicationTarget
          attributes: Dict containting Key Value pairs (extra metadata)
          qos: Dict containing Key Value pairs to indicate QoS setings
          snapshot_id: Indicates perform clone from a snapshot as
                       opposed to the original volume

          * Optional keywords default to copying values from source

        """
        try:
            return self.clone_volume(source_volid, name, new_account_id,
                                     int(new_size) * pow(10, 9), access,
                                     snapshot_id, attributes)['volumeID']
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex

    def list_snaps(self, volume_id=None):

        try:
            snapshots = self.list_snapshots(volume_id)
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex
        if self.raw:
            return snapshots
        else:
            return object_utils.convert_dict_to_object(snapshots)
