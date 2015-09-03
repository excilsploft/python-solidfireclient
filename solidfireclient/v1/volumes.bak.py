from solidfireclient.v1 import solidfire_element_api as sfapi
from solidfireclient.v1 import object_utils

# class VolumeInfo():
# access
# accountID
# attributes
# enable512e
# iqn
# name
# qos
# scsiEUIDeviceID
# scsiNAADeviceID
# status
# totalSize
# volumeAccessGroups
# volumeID
#     def __init__(self, vlist):
#         for v in vlist:


class Volume(sfapi.SolidFireAPI):
    """ Volume methods for the SolidFire Cluster.

    """
    def _list_active_volumes(self, start_id=0, limit=0):
        return self._send_request('ListActiveVolumes',
                                  {'startVolumeID': start_id,
                                   'limit': limit},
                                  endpoint=None)

    def _list_deleted_volumes(self):
        return self._send_request('ListDeletedVolumes',
                                      {},
                                      endpoint=None)

    def _list_volumes_for_account(self, account_id):
        return self._send_request('ListVolumesForAccount',
                                      {'accountID': account_id},
                                      endpoint=None)

    def _filter_response(self, filter):
        pass

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
                volumes.extend(self.list_active_volumes(start_id, limit)['volumes'])
            except Exception:
                # TOOD(jdg): Catch exception and show error info
                pass

        else:
            try:
                volumes.extend(self.list_volumes_for_account(account_id)['volumes'])
            except Exception:
                # TOOD(jdg): Catch exception and show error info
                pass

        # NOTE(jdg): Make MikeT happy... add on snapshots
        try:
            snapshots = self.list_snapshots()['snapshots']
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
            vobs = object_utils.convert_dict_to_resource_objects(volumes)
        vobs = object_utils.dict_to_object(volumes)
        import pdb;pdb.set_trace()

    def __list(self, account=None, active_only=True,
             attributes=None, include_snapshot_info=True):
        volumes = []
        if account:
            volumes = self._list_volumes_for_account(account)['volumes']
        else:
            volumes = self._list_active_volumes()['volumes']

        if not active_only:
            deleted_volumes = self._list_deleted_volumes()['volumes']
            if account:
                for dv in deleted_volumes:
                    if dv.accountID:
                        volumes.append(dv)
            else:
                volumes.append(deleted_volumes)

        if attributes:
            # Filter on the requested attributes
            pass

        # Build a "snapshots" attribute list of snap ID's
        version = self.get_cluster_version_info()
        if include_snapshot_info:
            snapshots = self.list_snapshots()['snapshots']
            for snap in snapshots:
                for vol in volumes:
                    vol['snapshots'] = []
                    if snap['volumeID'] == vol['volumeID']:
                        vol['snapshots'].append(snap['snapshotID'])
        return volumes

    def get(self, id=[], account_id=[], name=[], attributes=[]):
        """
        Retrieve a list of all volumes on the SolidFire Cluster.

        params: account_id Retrieve only those volumes associated
                with this account
        params: filter Allows specification of items to include in the
                response
        """
        vlist = []
        deleted_vols = []
        active_vols = []

        if account_id is None:
            params = {}
            response = self._send_request('ListDeletedVolumes',
                                              params,
                                              endpoint=None)
            deleted_vols = [v for v in response['result']['volumes']]

            response = self._send_request('ListActiveVolumes',
                                              params,
                                              endpoint=None)
            active_vols = [v for v in response['result']['volumes']]
            vlist = sorted((deleted_vols + active_vols),
                           key=lambda k: k['volumeID'])
        else:
            params = {'accountID': account_id}
            response = self._send_request('ListVolumesForAccount',
                                              params,
                                              endpoint=None)
            vlist = [v for v in response['result']['volumes']]
            vlist = sorted(vlist, key=lambda k: k['volumeID'])
        return vlist

    def detail(self, id):
        """
        Retrieve details for the specified volume.

        param id: The VolumeID of the volume to be deleted
        """

        params = {}
        response = self._send_request('ListActiveVolumes',
                                          params,
                                          endpoint=None)
        vol = [v for v in response['result']['volumes']
               if v['volumeID'] == int(id)]
        return vol[0]

    def delete(self, id, purge, auto_delete_snapshots=False):
        """
        Delete the specified volume from the SolidFire Cluster.

        param id: The VolumeID of the volume to be deleted
        param purge: True or False, issues purge immediately after delete
        param auto_delete_snapshots True or False, Indicates we would like
                                    to auto delete any snapshots that belong
                                    to the volume automatically.
        """

        params = {'volumeID': id}
        response = self._send_request('DeleteVolume',
                                          params,
                                          endpoint=None)
        if purge:
            return self._send_request('PurgeDeletedVolume',
                                          params,
                                          endpoint=None)
        return response

    def delete_all(self, purge):
        """
        Delete all volumes on the SolidFire Cluster.

        param purge: True or False, issues purge immediately after delete
        """

        vlist = self.list()
        for v in vlist:
            params = {'volumeID': v['volumeID']}
            self._send_request('DeleteVolume',
                                   params,
                                   endpoint=None)
        if purge:
            for v in vlist:
                params = {'volumeID': v['volumeID']}
                self._send_request('PurgeDeletedVolume',
                                       params,
                                       endpoint=None)

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
            response = self._send_request('CreateVolume',
                                              params,
                                              endpoint=None)
            volid_list.append(response['result']['volumeID'])
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

        response = self._send_request('CloneVolume',
                                          params,
                                          endpoint=None)

        return(self.show(response['result']['volumeID']))

    def get_snapshots(self, id=[], account_id=[], name=[], attributes=[]):
        pass
