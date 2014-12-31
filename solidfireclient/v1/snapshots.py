from solidfireclient import sfapi


class Snapsho(sfapi.API):

    def list(self, volid=None):
        """
        Retrieve a list of snapshots on the SolidFire Cluster.

        Default retieves all snapshots on the Cluster, can
        specify to return only those associated with a specified
        volume or group.

        Option keyword arguments:
            volid: Retrieve only those volumes associated
                   with this account
        """
        slist = []
        params = {}
        if volid:
            params['voumeID'] = int(volid)

        response = self.issue_api_request('ListSnapshots',
                                          params,
                                          endpoint_dict=None)

        snapshots = [s for s in response['result']['snapshots']]
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
        response = self.issue_api_request('ListSnapshots',
                                          params,
                                          endpoint_dict=None)

        # TODO(jdg): Might want to sort these in the future?
        return [s for s in response['result']['groupSnapshots']]

    def delete(self, id, purge):
        """
        Delete the specified volume from the SolidFire Cluster.

        param id: The VolumeID of the volume to be deleted
        param purge: True or False, issues purge immediately after delete
        """

        params = {'volumeID': id}
        response = self.issue_api_request('DeleteVolume',
                                          params,
                                          endpoint_dict=None)
        if purge:
            response = self.issue_api_request('PurgeDeletedVolume',
                                              params,
                                              endpoint_dict=None)

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

        response = self.issue_api_request('CreateSnapshot',
                                          params,
                                          endpoint_dict=None)
        return self.show(response['result']['snapshotID'])
