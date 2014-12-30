from solidfireclient import sfapi


class Volume(sfapi.API):

    def list(self, account_id=None):
        vlist = []
        deleted_vols = []
        active_vols = []

        if account_id is None:
            params = {}
            response = self.issue_api_request('ListDeletedVolumes',
                                              params,
                                              version='1.0',
                                              endpoint_dict=None)
            deleted_vols = [v for v in response['result']['volumes']]

            response = self.issue_api_request('ListActiveVolumes',
                                              params,
                                              version='1.0',
                                              endpoint_dict=None)
            active_vols = [v for v in response['result']['volumes']]
            vlist = sorted((deleted_vols + active_vols),
                           key=lambda k: k['volumeID'])
        else:
            params = {'accountID': account_id}
            response = self.issue_api_request('ListVolumesForAccount',
                                              params,
                                              version='1.0',
                                              endpoint_dict=None)
            vlist = [v for v in response['result']['volumes']]
            vlist = sorted(vlist, key=lambda k: k['volumeID'])
        return vlist

    def show(self, id):
        params = {}
        response = self.issue_api_request('ListActiveVolumes',
                                          params,
                                          version='1.0',
                                          endpoint_dict=None)
        vol = [v for v in response['result']['volumes']
               if v['volumeID'] == int(id)]
        return vol[0]

    def delete(self, id, purge):
        params = {'volumeID': id}
        response = self.issue_api_request('DeleteVolume',
                                          params,
                                          version='1.0',
                                          endpoint_dict=None)
        if purge:
            response = self.issue_api_request('PurgeDeletedVolume',
                                              params,
                                              version='1.0',
                                              endpoint_dict=None)


    def delete_all(self, purge):
        vlist = self.list()
        for v in vlist:
            params = {'volumeID': v['volumeID']}
            response = self.issue_api_request('DeleteVolume',
                                              params,
                                              version='1.0',
                                              endpoint_dict=None)
        if purge:
            for v in vlist:
                params = {'volumeID': v['volumeID']}
                response = self.issue_api_request('PurgeDeletedVolume',
                                                  params,
                                                  version='1.0',
                                                  endpoint_dict=None)

    def create(self, size, account_id, **kwargs):
        volid_list = []
        name = kwargs.get('name', None)
        count = kwargs.get('count', 1)
        attributes = kwargs.get('attributes', {})
        chap_secrets = kwargs.get('chap_secrets', None)
        enable512e = kwargs.get('emulation', False)
        qos = kwargs.get('qos', {})
        params = {'name': name,
                  'accountID': account_id,
                  'totalSize': int(size) * pow(10,9),
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
                                              version='1.0',
                                              endpoint_dict=None)
            volid_list.append(response['result']['volumeID'])
            if name is not None:
                params['name'] = params['name'] + ('-%s' % i)

        vlist = []
        for id in volid_list:
            vlist.append(self.show(id))
        return vlist

    def AddInitiatorsToVolumeAccessGroup(volumeAccessGroupID, initiators):
        """
        Add initiators to a specified volume access group.

        param volumeAccessGroupID: The ID of the volume access
                                   group to add the initiator(s) to
        param initiators: List of initiators (IQNs) to add to the volume
                          access group
        """
        params = {'volumeAccessGroupID': volumeAccessGroupID,
                  'initiators': initiators}

    def AddVolumesToVolumeAccessGroup(self, volumeAccessGroupID, volumes):
        """
        Add volumes to a specified volume access group.

        param volumeAccessGroupID: The ID of the volume access
                                   group to add the initiator(s) to
        param volumes: List of volume ID's to add to the volume
                          access group
        """
        params = {'volumeAccessGroupID': volumeAccessGroupID,
                  'volumes': volumes}

    def CloneVolume(volumeID, name,
                    attributes={}, newAccountID=None,
                    newSize=None, access=None,
                    snapshotID=None):
        """
        Create a cop of the requested volume.

        This method is asynchronous and may take a variable amount of
        time to complete.

        GetAsyncResutls can be used to determine when the cloning process is
        completed and the new volume is available for connections.

        ListSyncJobs can be used to see the progress of creating the clone.

        param volumeID: VolumeID for the volume to be cloned
        param name: Name of the new cloned volume
                    (1 - 64 characters in length)
        param newAccountID: AccountID for the owner of the new volume.
                            If not speicfied the accountID of the owner
                            of the volume being cloned is used.
        #WTF, really... bytes vv
        param newSize: New size of the volume, in bytes
        param access: readOnly, readWrite, locked or replicationTarget
        param attribtutes: List of Name/Value pairs in JSON object format.
        param snapshotID: ID of the snapshot that is used as the source
                          of the clone.  If no ID is provided, the current
                          active volume is used.
        """

        params = {'volumeID': volumeID,
                  'name': name,
                  'attributes': attributes}
        if newAccountID:
            params['newAccountID'] = newAccountID
        if newSize:
            params['newSize'] = newSize
        if access:
            params['access'] = access
        if snapshotID:
            params['snapshotID'] = snapshotID

    def CreateSnapshot(volumeID, attributes={},
                       snapshotID=None, name=None):
        """
        Used to create a point-in-time copy of a volume.

        A snapshot can be created from any volume or from an existing
        snapshot.  If a SnapshotID is not provided with this AP method,
        a snapshot is created from the volume's active branch.

        param volumeID: Unique ID of the volume image from which to copy
        param snapshotID: Unique ID of a snapshot form which the new
                          snapshot is made.  The snapshotID must be
                          a sapshot on the given volume.
        param name: Name entered for the snapshot.  If no name is entered,
                    the date and time the snapshot was taken is used.
        param attributes: List of Name/Value pairs in JSON object format.
        """

        params = {'volumeID': volumeID,
                  'attributes': attributes}
        if snapshotID:
            params['snapshotID'] = snapshotID
        if name:
            params['name'] = name

    def CreateVolume(name, accountID,
                     totalSize, enable512e,
                     attributes={}, qos={}):
        """
        Used to create a new (empty) volume on the cluster.

        When the volume is created successfully is it immediately
        available fro connection.

        param name: Name of the volume
        param accountID: AccountID for the owner of this volume
        param totalSize: Total size of the volume in bytes. Size is
                         rounded up to the nearest 1MB size.
        param enable512e: Enable 512-byte sector emulation (True or False)
        param attributes: List of Name/Value pairs in JSON object format.
        param qos: Initial quality of service settings.

        """
        params = {'name': name,
                  'accountID': accountID,
                  'totalSize': totalSize,
                  'enable512e': enable512e,
                  'attributes': attributes,
                  'qos': qos}

    def CreateVolumeAccessGroup(name, initiators=[],
                                volumes=[], attributes={}):
        """
        Used to create a new volume access group.

        param name: Name of the volume access group.
        param initators: List of initiator names (iqns) to include
                         in the volume access group.
        param volumes: List of VolumeIDs to include in the volume
                       access group.
        param attributes: List of Name/Value pairs in JSON object format.

        """
        params = {'name': name,
                  'initiators': initiators,
                  'volumes': volumes,
                  'attributes': attributes}

    def DeleteSnapshot(snapshotID):
        """
        Used to delete a snapshot.

        param snapshotID: The ID of the snapshot to delete.

        """

        params = {'snapshotID': snapshotID}

    def DeleteVolume(volumeID):
        """
        Used to delete a volume.

        param volumeID: The ID of the volume to delete.

        """

        params = {'volumeID': volumeID}

    def DeleteVolumeAccessGroup(volumeAccessGroupID):
        """
        Used to delete a volume access group.

        param volumeAccessGroupID: The ID of the volume access group
                                   to delete.

        """

        params = {'volumeAccessGroupID': volumeAccessGroupID}

    def GetVolumeStats(volumeID):
        """
        Used to retrieve high-level activity measurements for a single volume.

        Values are cummulative from the creation of the volume.

        param volumeID: The ID of the volume for which statistics are to
                        be gathered.

        """

        params = {'volumeID': volumeID}

    def GetDefaultQoS():
        """
        Used to retrieve the default QoS values.

        """

        params = {}

    def ListActiveVolumes(startVolumeID=0, limit=0):
        """
        Used to retrieve a list of active volumes currently on the cluster.

        """
        params = {'startVolumeID': startVolumeID,
                  'limit': limit}

    def ListVolumesForAccount(self, account_id=None, filter=None):
        if account_id is None:
            account_id = self._get_account_by_name(self.username)
        params = {'accountID': account_id}
        response = self.issue_api_request('ListVolumesForAccount',
                                          params,
                                          version='1.0',
                                          endpoint_dict=None)
