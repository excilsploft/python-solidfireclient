from solidfireclient.v1 import solidfire_element_api as sfapi


class Snapshot(sfapi.SolidFireAPI):

    def _list_active_snapshots(self, start_id=0, limit=0):
        return self._send_request('ListSnapshots',
                                  {},
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

    def list(self, volid=None):
        """
        Retrieve a list of snapshots on the SolidFire Cluster.

        Default retieves all snapshots on the Cluster, can
        specify to return only those associated with a specified
        volume or group.

        Option keyword arguments:
            volid: Retrieve only those snapshots associated
                   with this volume ID
        """
        params = {}
        if volid:
            params['voumeID'] = int(volid)

        response = self._send_request('ListSnapshots',
                                      params,
                                      endpoint=None)

        # snapshots = [s for s in response['result']['snapshots']]
        snapshots = response['snapshots']
        return sorted(snapshots, key=lambda k: k['snapshotID'])

    def show(self, id):
        """
        Retrieve details for the specified snapshot.

        param id: The SnapshotID of the snapshot to be retrieved
        """

        snapshots = self.list()
        snap = [s for s in snapshots if int(s['snapshotID']) == int(id)]
        return snap[0]

    def group_list(self, volid_list):
        """
        Retrieve a list of group snapshots.

        param volid_list: list of volume ID's that comprise the group
        """

        volumes = [{'volumeID': int(id)} for id in volid_list]
        params = {'volumes': volumes}
        response = self._send_request('ListSnapshots',
                                      params,
                                      endpoint=None)

        # TODO(jdg): Might want to sort these in the future?
        return [s for s in response['result']['groupSnapshots']]

    def delete(self, id, purge):
        """
        Delete the specified volume from the SolidFire Cluster.

        param id: The VolumeID of the volume to be deleted
        param purge: True or False, issues purge immediately after delete
        """

        params = {'volumeID': id}
        self._send_request('DeleteVolume',
                           params,
                           endpoint=None)
        if purge:
            self._send_request('PurgeDeletedVolume',
                               params,
                               endpoint=None)

    def create(self, volid,
               name=None, snapshot_id=None,
               attributes=None):
        """
        Creates a snapshot of an existing volume.

        param volid: The volumeID of the existing volume to snapshot

        Optional keyword arguments
          name: Name of cloned volume (limited to 64 characters, default=None)
          snapshot_id: Indicates perform snapshot from another snapshot as
                       opposed to the original volume
          attributes: Dict containting Key Value pairs (extra metadata)

        """
        params = {'volumeID': int(volid)}
        if name:
            params['name'] = name
        if snapshot_id:
            params['snapshotID'] = int(snapshot_id)
        if attributes:
            params['attributes'] = attributes

        response = self._send_request('CreateSnapshot',
                                      params,
                                      endpoint=None)
        return self.show(response['result']['snapshotID'])
