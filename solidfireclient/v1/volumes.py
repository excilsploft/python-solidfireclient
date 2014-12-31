from solidfireclient import sfapi


class Volume(sfapi.API):
    """ Volume methods for the SolidFire Cluster.

    We have two groups of methods implemented here.

    1. Some methods defined specifically here for the client
    2. Methods named exactly as they appear in the API doc

    You can identify these two groups easily by the case used in
    the method name.  Those that are "specific to the client" use
    python method naming conventions (all lower case, and underscores).

    The methods that are just straight from the SolidFire API use the
    same naming convention as the SolidFire API (UpperCase).

    Why both?  Hmm... well there are some things that I like to do
    in a single call, like delete and purge volumes, or get not only
    all of the active volumes, but also all of the deleted volumes.

    Might make sense at some point to split these out into seperate
    modules.

    """

    ###############################################
    # Combination methods we made up for the client
    ###############################################
    def list(self, account_id=None):
        """
        Retrieve a list of all volumes on the SolidFire Cluster.

        params: account_id Retrieve only those volumes associated
                with this account
        """
        vlist = []
        deleted_vols = []
        active_vols = []

        if account_id is None:
            params = {}
            response = self.issue_api_request('ListDeletedVolumes',
                                              params,
                                              endpoint_dict=None)
            deleted_vols = [v for v in response['result']['volumes']]

            response = self.issue_api_request('ListActiveVolumes',
                                              params,
                                              endpoint_dict=None)
            active_vols = [v for v in response['result']['volumes']]
            vlist = sorted((deleted_vols + active_vols),
                           key=lambda k: k['volumeID'])
        else:
            params = {'accountID': account_id}
            response = self.issue_api_request('ListVolumesForAccount',
                                              params,
                                              endpoint_dict=None)
            vlist = [v for v in response['result']['volumes']]
            vlist = sorted(vlist, key=lambda k: k['volumeID'])
        return vlist

    def show(self, id):
        """
        Retrieve details for the specified volume.

        param id: The VolumeID of the volume to be deleted
        """

        params = {}
        response = self.issue_api_request('ListActiveVolumes',
                                          params,
                                          endpoint_dict=None)
        vol = [v for v in response['result']['volumes']
               if v['volumeID'] == int(id)]
        return vol[0]

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
            return self.issue_api_request('PurgeDeletedVolume',
                                          params,
                                          endpoint_dict=None)
        return response

    def delete_all(self, purge):
        """
        Delete all volumes on the SolidFire Cluster.

        param purge: True or False, issues purge immediately after delete
        """

        vlist = self.list()
        for v in vlist:
            params = {'volumeID': v['volumeID']}
            self.issue_api_request('DeleteVolume',
                                   params,
                                   endpoint_dict=None)
        if purge:
            for v in vlist:
                params = {'volumeID': v['volumeID']}
                self.issue_api_request('PurgeDeletedVolume',
                                       params,
                                       endpoint_dict=None)

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

        response = self.issue_api_request('CloneVolume',
                                          params,
                                          endpoint_dict=None)

        return(self.show(response['result']['volumeID']))

    ################################
    # Native SolidFire API methods #
    ################################
    def AddInitiatorsToVolumeAccessGroup(self,
                                         volumeAccessGroupID,
                                         initiators):
        """
        Add initiators to a specified volume access group.

        param volumeAccessGroupID: The ID of the volume access
                                   group to add the initiator(s) to
        param initiators: List of initiators (IQNs) to add to the volume
                          access group

        The accepted format of an initiator IQN:
        iqn.yyyy-mm where y and m are digits, followed by text which must
        only contain digits, lower-case alphabetic characters, a period (.),
        colon (:) or dash (-).

        iSCSI example:
        iqn.2010-01.com.solidfire:c2r9.fc0.2100000e1e09bb8b

        Fibre Channel WWPN example:
        21:00:00:0e:1e:11:f1:81
        """
        params = {'volumeAccessGroupID': volumeAccessGroupID,
                  'initiators': initiators}

        return self.issue_api_request('AddInitiatorsToVolumeAccessGroup',
                                      params,
                                      endpoint_dict=None)

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
        return self.issue_api_request('AddInitiatorsToVolumeAccessGroup',
                                      params,
                                      endpoint_dict=None)

    def CloneVolume(self, volumeID, name,
                    attributes={}, newAccountID=None,
                    newSize=None, access=None,
                    snapshotID=None):
        """
        Create a copy of the requested volume.

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

        return self.issue_api_request('CloneVolume',
                                      params,
                                      endpoint_dict=None)

    def CreateSnapshot(self, volumeID, attributes={},
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

        return self.issue_api_request('CreateSnapshot',
                                      params,
                                      endpoint_dict=None)

    def CreateVolume(self, name, accountID,
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

        return self.issue_api_request('CreateVolume',
                                      params,
                                      endpoint_dict=None)

    def CreateVolumeAccessGroup(self, name, initiators=[],
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
        return self.issue_api_request('CreateVolumeAccessGroup',
                                      params,
                                      endpoint_dict=None)

    def DeleteSnapshot(self, snapshotID):
        """
        Used to delete a snapshot.

        param snapshotID: The ID of the snapshot to delete.

        """

        params = {'snapshotID': snapshotID}
        return self.issue_api_request('DeleteSnapshot',
                                      params,
                                      endpoint_dict=None)

    def DeleteVolume(self, volumeID):
        """
        Used to delete a volume.

        param volumeID: The ID of the volume to delete.

        """

        params = {'volumeID': volumeID}
        return self.issue_api_request('DeleteVolume',
                                      params,
                                      endpoint_dict=None)

    def ListVolumeAccessGroups(self,
                               startVolumeAccessGroupID=0,
                               limit=0):
        """
        Retrieves a list of volume access groups currently on the cluster.

        """
        params = {'startVolumeAccessGroupID': startVolumeAccessGroupID,
                  'limit': limit}
        return self.issue_api_request('ListVolumeAccessGroups',
                                      params,
                                      endpoint_dict=None)

    def DeleteVolumeAccessGroup(self, volumeAccessGroupID):
        """
        Used to delete a volume access group.

        param volumeAccessGroupID: The ID of the volume access group
                                   to delete.

        """

        params = {'volumeAccessGroupID': volumeAccessGroupID}
        return self.issue_api_request('DeleteVolumeAccessGroup',
                                      params,
                                      endpoint_dict=None)

    def GetVolumeStats(self, volumeID):
        """
        Used to retrieve high-level activity measurements for a single volume.

        Values are cummulative from the creation of the volume.

        param volumeID: The ID of the volume for which statistics are to
                        be gathered.

        """

        params = {'volumeID': volumeID}
        return self.issue_api_request('GetVolumeStats',
                                      params,
                                      endpoint_dict=None)

    def GetDefaultQoS(self):
        """
        Used to retrieve the default QoS values.

        """

        params = {}
        return self.issue_api_request('GetDefaultQoS',
                                      params,
                                      endpoint_dict=None)

    def ListActiveVolumes(self, startVolumeID=0, limit=0):
        """
        Used to retrieve a list of active volumes currently on the cluster.

        """
        params = {'startVolumeID': startVolumeID,
                  'limit': limit}
        return self.issue_api_request('ListActiveVolumes',
                                      params,
                                      endpoint_dict=None)

    def ListVolumesForAccount(self, account_id):
        params = {'accountID': account_id}
        return self.issue_api_request('ListVolumesForAccount',
                                      params,
                                      endpoint_dict=None)
