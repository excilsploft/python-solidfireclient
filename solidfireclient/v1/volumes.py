import logging
import six

from solidfireclient import sfapi

LOG = logging.getLogger(__name__)
logging.basicConfig()


class Volume(sfapi.API):
    """ Volume methods for the SolidFire Cluster. """

    def list_attributes(self):
        """
        Display a list of valid volume attributes.

        Note, this works by grabbing a volume object from the Cluster
        and iterating through its attributes and displaying the key
        names.  This requires that an active volume exist on the system.
        """

        try:
            volumes = self.ListActiveVolumes()['volumes']
        except Exception:
            # TOOD(jdg): Catch exception and show error info
            pass
        if len(volumes) < 1:
            # TODO(jdg): Raise here as we need at least one vol to interrogate
            pass
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
                volumes = self.ListActiveVolumes(start_id, limit)['volumes']
            except Exception:
                # TOOD(jdg): Catch exception and show error info
                pass

        else:
            try:
                volumes = self.ListVolumesForAccount(account_id)['volumes']
            except Exception:
                # TOOD(jdg): Catch exception and show error info
                pass

        # NOTE(jdg): Make MikeT happy... add on snapshots
        try:
            snapshots = self.ListSnapshots()['snapshots']
        except Exception:
            # TOOD(jdg): Catch exception and show error info
            pass

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
            return self._convert_dict_to_resource_objects(volumes)

    def show(self, volid):
        """
        Retrieve details for the specified volume.

        param id: The ID of the Volume to retrieve

        Note if the Volume's current state is not Active
        it won't be returned.  (Use show_deleted)
        """

        try:
            volume = self.ListActiveVolumes(volid, 1)['volumes']
        except Exception:
            # TOOD(jdg): Catch exception and show error info
            pass
        if self.raw:
            return volume
        else:
            return self._convert_dict_to_resource_objects(volume)

    def list_deleted(self):
        """
        Retrieve a list of deleted volumes on the SolidFire Cluster.

        """
        volumes = []

        try:
            volumes = self.ListDeletedVolumes()['volumes']
        except Exception:
            # TOOD(jdg): Catch exception and show error info
            pass

        if self.raw:
            return volumes
        else:
            return self._convert_dict_to_resource_objects(volumes)

    def show_deleted(self, volid):
        """
        Retrieve details for the specified deleted volume.

        param id: The ID of the Volume to retrieve

        Note: If the volume has been purged the return is None
        """

        volumes = []

        try:
            volumes = self.ListDeletedVolumes()['volumes']
        except Exception:
            # TOOD(jdg): Catch exception and show error info
            pass

        if not any(v['VolumeID'] == volid for v in volumes):
            return None

    def delete(self, volid, purge):
        """
        Delete the specified volume from the SolidFire Cluster.

        param id: The VolumeID of the volume to be deleted
        param purge: True or False, issues purge immediately after delete
        """

        try:
            self.DeleteVolume(volid)
            if purge:
                self.PurgeDeletedVolume(volid)
        except Exception:
            pass
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
                self.PurgeDeletedVolume(v.volumeID)

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
        chap_secrets = kwargs.get('chap_secrets', None)
        enable512e = kwargs.get('emulation', False)
        qos = kwargs.get('qos', {})
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
            response = self.issue_api_request('CreateVolume',
                                              params,
                                              endpoint_dict=None)
            volid_list.append(response['volumeID'])
            if name is not None:
                params['name'] = params['name'] + ('-%s' % i)

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
        params = {'volumeID': int(source_volid)}
        if name:
            params['name'] = name
        if new_account_id:
            params['newAccountID'] = int(new_account_id)
        if new_size:
            params['newSize'] = int(new_size)
        if new_account_id:
            params['newAccountID'] = new_account_id
        if access:
            if access not in ['readOnly', 'readWrite',
                              'locked', 'replicationTarget']:
                raise
            params['access'] = access
        if attributes:
            params['attributes'] = attributes
        if qos:
            params['qos'] = qos
        if snapshot_id:
            params['snapshotID'] = snapshot_id

        response = self.issue_api_request('CloneVolume',
                                          params,
                                          endpoint_dict=None)

        return(self.show(response['volumeID']))

    def list_snapshots(self, volume_id=None):

        try:
            response = self.ListSnapshots(volume_id)
        except:
            # TODO(jdg): Catch key not found
            pass
        if self.raw:
            return response['snapshots']
        else:
            return self._convert_dict_to_resource_objects(
                response['snapshots'])
