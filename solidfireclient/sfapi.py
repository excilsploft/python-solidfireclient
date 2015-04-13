import json
import logging
import time
import warnings

from six import wraps
import requests

LOG = logging.getLogger(__name__)

# retry_exc_tuple = (exception.SolidFireRetryableException,
retry_exc_tuple = (requests.exceptions.ConnectionError)
retryable_errors = ['xDBVersionMismatch',
                    'xMaxSnapshotsPerVolumeExceeded',
                    'xMaxClonesPerVolumeExceeded',
                    'xMaxSnapshotsPerNodeExceeded',
                    'xMaxClonesPerNodeExceeded']


def retry(exc_tuple, tries=5, delay=1, backoff=2):
    def retry_dec(f):
        @wraps(f)
        def func_retry(*args, **kwargs):
            _tries, _delay = tries, delay
            while _tries > 1:
                try:
                    return f(*args, **kwargs)
                except exc_tuple:
                    time.sleep(_delay)
                    _tries -= 1
                    _delay *= backoff
                    LOG.warning('Retrying %s, (%s attempts remaining)...',
                                (args, _tries))
            # NOTE(jdg): Don't log the params passed here
            # some cmds like createAccount will have sensitive
            # info in the params, grab only the second tuple
            # which should be the Method
            msg = (('Retry count exceeded for command: %s'),
                   args[1])
            LOG.error(msg)
            # raise exception.SolidFireAPIException(message=msg)

        return func_retry

    return retry_dec


class Resource(object):
    def __init__(self, dictionary, resource_name=None):
        self.__dict__ = dictionary


class API(object):
    def __init__(self,
                 endpoint_dict,
                 endpoint_version='1.0',
                 return_raw_data=False):
        self.endpoint_dict = endpoint_dict
        self.version = 6.0
        self.raw = return_raw_data

    def _convert_dict_to_resource_objects(self, resources):
        return [Resource(r) for r in resources]

    def issue_api_request(self, method, params=None,
                          version=None, endpoint_dict=None):
        if params is None:
            params = {}

        # NOTE(jdg): We allow passing in a new endpoint_dict to issue_api_req
        # to enable some of the multi-cluster features like replication etc
        if endpoint_dict is None:
            endpoint_dict = self.endpoint_dict
        payload = {'method': method, 'params': params}

        api_version = version if version else self.version
        url = '%s/json-rpc/%s/' % (endpoint_dict['url'], api_version)

        LOG.debug('Issue SolidFire API call: %s' % json.dumps(payload))

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            req = requests.post(url,
                                data=json.dumps(payload),
                                auth=(endpoint_dict['login'],
                                      endpoint_dict['passwd']),
                                verify=False,
                                timeout=30)
        response = req.json()
        req.close()

        LOG.debug('Raw response data from SolidFire API: %s' % response)

        if (('error' in response) and
                (response['error']['name'] in retryable_errors)):
            msg = ('Retryable error (%s) encountered during '
                   'SolidFire API call.' % response['error']['name'])
            LOG.warning(msg)
            # raise exception.SolidFireRetryableException(message=msg)

        if 'error' in response:
            msg = ('API response: %s'), response
            LOG.error(msg)
        return response['result']

    def ListActiveVolumes(self, start_volid=0, limit=0):
        """
        Used to retrieve a list of active volumes currently on the cluster.

        """
        params = {'startVolumeID': start_volid,
                  'limit': limit}
        return self.issue_api_request('ListActiveVolumes',
                                      params,
                                      endpoint_dict=None)

    def ListDeletedVolumes(self, endpoint=None):
        """
        Used to retrieve a list of deleted volumes that haven't been purged.

        Returns the entire list of volumes that have been marked as deleted
        and are scheduled to be purged from the system.

        """
        params = {}
        return self.issue_api_request('ListDeletedVolumes',
                                      params,
                                      endpoint_dict=endpoint)

    def ListVolumesForAccount(self, account_id):
        params = {'accountID': account_id}
        return self.issue_api_request('ListVolumesForAccount',
                                      params,
                                      endpoint_dict=None)

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

    def PurgeDeletedVolume(self, volumeID):
        """
        Used to immediately purge a deleted volume.

        param volumeID: The ID of the volume to delete.

        Immediately and permanently purges a Volume which has already
        been deleted.  Note that deleted Volumes are periodically purged
        by the cluster so this operation is typically not necessary.

        """

        params = {'volumeID': volumeID}
        return self.issue_api_request('PurgeDeletedVolume',
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

    def ListSnapshots(self, volume_id=None, endpoint_dict=None):
        params = {}
        if volume_id:
            params = {'volumeID': 'volume_id'}
        return self.issue_api_request('ListSnapshots',
                                      params,
                                      endpoint_dict=None)

    # #### Account Methods ### #
    def AddAccount(self, username,
                   initiator_secret=None, target_secret=None,
                   attributes=None):
        """ Create an account on the SolidFire Cluster.

        AddAccount is used to add a new account to the system.  New volumes
        can be created under the new account.  The CHAP settings specified for
        the account applies to all volumes owned by the account.

        """
        params = {'username': username}
        if initiator_secret:
            params['initiator_secret'] = initiator_secret
            params['target_secret'] = initiator_secret
        if target_secret:
            params['target_secret'] = target_secret
        return self.issue_api_request('AddAccount',
                                      params,
                                      endpoint_dict=None)

    def GetAccountByID(self, accountID):
        """ Get Account object by ID.

        GetAccountByID is used to obtain details about the specified
        account.

        """
        return self.issue_api_request('GetAccountByID',
                                      {'accountID': accountID},
                                      endpoint_dict=None)

    def GetAccountByName(self, username):
        """ Get Account object by username.

        GetAccountByName is used to obtain details about the specified
        account looked up by username.

        """
        return self.issue_api_request('GetAccountByName',
                                      {'username': username},
                                      endpoint_dict=None)

    def GetAccountEfficiency(self, accountID):
        """ Get Account Efficiency info for specified Account.

        GetAccountEfficiency is used to retrieve information about a volume
        account.  Only the account given as a parameter in this API method is
        used to compute the capacity.

        """
        return self.issue_api_request('GetAccountEfficiency',
                                      {'accountID': accountID},
                                      endpoint_dict=None)

    def RemoveAccount(self, accountID):
        """ Remove Account by ID.

        RemoveAccount is used to remove the specified account from
        the SolidFire Cluster.

        """
        return self.issue_api_request('RemoveAccount',
                                      {'accountID': accountID},
                                      endpoint_dict=None)

    def ListAccounts(self, startAccountID=0, limit=0):
        """ List Accounts that exist on the SolidFire Cluster.

        """

        params = {'startAccountID': startAccountID,
                  'limit': limit}
        return self.issue_api_request('ListAccounts',
                                      params,
                                      endpoint_dict=None)

    def ModifyAccount(self, accountID, status=None, initiatorSecret=None,
                      targetSecret=None, attributes=None):
        """ Modify an existing Account on the SolidFire Cluster.

        ModifyAccoutn is used to modify an existing account.  When locking an
        account, any existing connection from ath account are immediately
        terminated.  When changin CHAP settings, any existing connections
        continue to be active, and the new CHAP values are only used on
        subsequent connection or reconnection.

        """

        params = {'accountID': accountID}
        if status == 'active' or 'locked':
            params['status'] = status
        if initiatorSecret:
            params['initiator_secret'] = initiatorSecret
        if targetSecret:
            params['targetSecret'] = targetSecret
        if attributes:
            params['attributes'] = attributes

        return self.issue_api_request('ModifyAccount',
                                      params,
                                      endpoint_dict=None)

    # #### Node Methods ### #
    def ListActiveNodes(self):
        return self.issue_api_request('ListActiveNodes',
                                      {},
                                      endpoint_dict=None)

    def ListAllNodes(self):
        return self.issue_api_request('ListAllNodes',
                                      {},
                                      endpoint_dict=None)

    def ListPendingNodes(self):
        return self.issue_api_request('ListPendingNodes',
                                      {},
                                      endpoint_dict=None)

    def ListServices(self):
        return self.issue_api_request('ListServices',
                                      {},
                                      endpoint_dict=None)
