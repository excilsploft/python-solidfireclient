import argparse
import os
import sys
import time

from solidfireclient import exceptions
from solidfireclient import utils
from solidfireclient.v1.volumes import Volume as volumes


def _translate_volume_results(collection, convert):
    for item in collection:
        keys = item.__dict__.keys()
        for from_key, to_key in convert:
            if from_key in keys and to_key not in keys:
                setattr(item, to_key, item.__info[from_key])

def _reformat_qos_results(raw_qos):
    qos = {}
    iop_keys = ['minIOPS', 'maxIOPS', 'burstIOPS']
    for k in iop_keys:
        qos[k] = raw_qos[k]

    return (qos, raw_qos['curve'])

def _extract_kv_pairs(kvs):
    kvd = {}
    for items in kvs:
        if '=' in items:
            (k, v) = items.split('=', 1)
            kvd[k] = v
    return kvd

@utils.arg('--account',
           metavar='<account>',
           default=None,
           help='Filter results by account ID')
@utils.arg('--keys',
           metavar='<volumeID,status,totalSize,accountID,name...>',
           default='volumeID,status,totalSize,accountID,name',
           help='keys to display in resultant list, may be any valid SF '
                'Volume Object Key.'
                '  (--keys volumeID,status,accountID)\n')

def do_volume_list(self, args):
    """List volumes on a cluster."""
    if args.account:
        vols = self.volumes.list(account_id=args.account)
    else:
        vols = self.volumes.list()
    key_list = args.keys.split(',')
    utils.print_list(vols, key_list)

@utils.arg('volume', metavar='<volume>', help='Volume ID.')
def do_volume_show(self, args):
    """Shows volume details."""
    vol = self.volumes.show(args.volume)
    utils.print_dict(vol)

@utils.arg('volume', metavar='<volume>', help='Volume ID.')
@utils.arg('--purge',
           dest='purge',
           metavar='<0|1>',
           nargs='?',
           type=int,
           const=1,
           default=0,
           help='Issue purge immediately after delete.')
@utils.arg('--all',
           dest='all',
           metavar='<0|1>',
           nargs='?',
           type=int,
           const=1,
           default=0,
           help='Deletes all volumes on the cluster *DANGER*.')
def do_volume_delete(self, args):
    #  If a Volume is specified we ignore the all option
    if args.volume:
        self.volumes.delete(args.volume, args.purge)
    else:
        self.volumes.delete_all(args.purge)

@utils.arg('size',
           metavar='<volume-size>',
           default=None,
           help='Size of volume in Gigabytes to create.')
@utils.arg('--name',
           metavar='<volume-name>',
           help='Desired name for new volume.',
           default=None)
@utils.arg('--count',
           metavar='<volume-count>',
           help='Number of volumes to create.',
           default=1)
@utils.arg('--account-id',
           metavar='<account-id>',
           help='Account to assign ownership of the new volume.',
           default=None)
@utils.arg('--attributes',
           metavar='<volume-attributes>',
           help='Attributes to assign to volume.',
           default=None)
@utils.arg('--chap-secrets',
           metavar='<chap-secrets>',
           help='Chap secrets to assign to volume '
                '(if omitted randomly generated secrets will be used).',
           default=None)
@utils.arg('--emulation',
           metavar='<512-emulation>',
           help='Utilize 512 byte emulation.',
           default=False)
def do_volume_create(self, args):
    options = {'name': args.name,
               'count': args.count,
               'attributes': args.attributes,
               'chap_secrets': args.chap_secrets,
               'emulation': args.emulation}
    vlist = self.volumes.create(args.size, args.account_id, **options)
    for v in vlist:
        utils.print_dict(v)

@utils.arg('accountID',
           metavar='<accountID>',
           default=None,
           help='accountID to list volumes for')
@utils.arg('--keys',
           metavar='<volumeID,status,totalSize,accountID,name...>',
           default='volumeID,status,totalSize,accountID,name',
           help='keys to display in resultant list, may be any valid SF '
                'Volume Object Key.'
                '  (--keys volumeID,status,accountID)\n')
def do_ListVolumesForAccount(self, args):
    vlist = self.volumes.ListVolumesForAccount(args.accountID)
    if 'result' in vlist and len(vlist['result']['volumes']) > 0:
        key_list = args.keys.split(',')
        utils.print_list(vlist['result']['volumes'], key_list)
    elif 'error' in vlist:
        utils.print_dict(vlist['error'])

@utils.arg('--keys',
           metavar='<volumeID,status,totalSize,accountID,name...>',
           default='volumeID,status,totalSize,accountID,name',
           help='keys to display in resultant list, may be any valid SF '
                'Volume Object Key.'
                '  (--keys volumeID,status,accountID)\n')
@utils.arg('--startVolumeID',
           metavar='<startVolumeID>',
           default=0,
           help='Starting VolumeID to return.')
@utils.arg('--limit',
           metavar='<limit>',
           default=0,
           help='Max number of Volume info objects to return.')
def do_ListActiveVolumes(self, args):
    vlist = self.volumes.ListActiveVolumes(args.startVolumeID, args.limit)
    if 'result' in vlist and len(vlist['result']['volumes']) > 0:
        key_list = args.keys.split(',')
        utils.print_list(vlist['result']['volumes'], key_list)
    elif 'error' in vlist:
        utils.print_dict(vlist['error'])

@utils.arg('--show-curve',
           dest='curve',
           metavar='<0|1>',
           nargs='?',
           type=int,
           const=1,
           default=0,
           help='Show QoS Curve data in results.')
def do_GetDefaultQoS(self, args):
    qos_summary = {}
    qos = self.volumes.GetDefaultQoS()
    (qos_summary, curve_info) = _reformat_qos_results(qos['result'])
    if args.curve:
        qos_summary['curve'] = curve_info
    utils.print_dict(qos_summary)

@utils.arg('volumeID',
           metavar='<volumeID>',
           default=None,
           help='ID of volume to get stats for')
def do_GetVolumeStats(self, args):
    volume_stats = self.volumes.GetVolumeStats(args.volumeID)
    utils.print_dict(volume_stats['result']['volumeStats'])


@utils.arg('volumeAccessGroupID',
           metavar='<volumeAccessGroupID>',
           default=None,
           help='ID of VolumeAccessGroup to delete')
def do_DeleteVolumeAccessGroup(self, args):
    self.volumes.DeleteVolumeAccessGroup(
        args.volumeAccessGroupID)

@utils.arg('volumeID',
           metavar='<volumeID>',
           default=None,
           help='ID of volume to delete')
def do_DeleteVolume(self, args):
    self.volumes.DeleteVolume(args.volumeID)

@utils.arg('name',
            metavar='<name>',
            nargs='?',
            type=str,
            help='Name of the volume access group being created.')
@utils.arg('--initiators',
            metavar='<initiators>',
            default=[],
            help='List of IQNs/WWPNs to '
                 'include in the group (--initiators 1,2,3,4)')
@utils.arg('--volumes',
            metavar='<volumes>',
            default=[],
            help='List of volume IDs to '
                 'include in the group (--volumes 1,2,3,4)')
@utils.arg('--attributes',
            type=str,
            #action='append',
            metavar='key1=value1[,key2=value2]',
            help='Comma seperated list of attribute key/value '
                 'pairs (key1=val1,key2=val2)')
def do_CreateVolumeAccessGroup(self, args):
    vol_ids = []
    initiator_ids = []
    attributes = {}

    if args.attributes:
        attributes = _extract_kv_pairs(args.attributes.split(','))
    if args.volumes:
        vol_ids = args.volumes.split(',')
    if args.initiators:
        initiator_ids = args.initiators.split(',')
    self.volumes.CreateVolumeAccessGroup(args.name,
                                         initiators=initiator_ids,
                                         volumes=vol_ids,
                                         attributes=attributes)

@utils.arg('--startVAGID',
           metavar='<startVAGID>',
           default=0,
           help='Starting VolumeAccessGroupID to return.')
@utils.arg('--limit',
           metavar='<limit>',
           default=0,
           help='Max number of Volume Access Group info objects to return.')
def do_ListVolumeAccessGroups(self, args):
    vag_list = self.volumes.ListVolumeAccessGroups(args.startVAGID, args.limit)
    if 'result' in vag_list and len(vag_list['result']['volumeAccessGroups']) > 0:
        key_list = args.keys.split(',')
        utils.print_list(vag_list['result']['volumeAccessGroups'], key_list)
    elif 'error' in vag_list:
        utils.print_dict(vag_list['error'])

