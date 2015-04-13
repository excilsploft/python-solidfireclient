import six

from solidfireclient import utils


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


def do_volume_attributes(self, args):
    """ List volume attributes."""
    attributes = self.volumes.list_attributes()
    attrs = [{'VolumeAttribute': val} for val in attributes]
    utils.print_list(attrs, ['VolumeAttribute'])


@utils.arg('--deleted',
           metavar='<True|False>',
           default=False,
           help='Displays a list of all/only the deleted Volumes '
                'on the Cluster. Default=False.')
@utils.arg('--verbose',
           metavar='<True|False>',
           default=False,
           help='Includes all available details associated with each volume. '
                'Default=False.')
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
    """ List volumes on a cluster."""
    if args.deleted:
        vols = self.volumes.list_deleted()
    elif args.account:
        vols = self.volumes.list(account_id=args.account)
    else:
        vols = self.volumes.list()
    if args.verbose:
        key_list = [k for k, v in six.iteritems(vols[0].__dict__)]
    else:
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
    """ Helper method to delete volumes on a SolidFire Cluster.
    """
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
    """ Helper method to create a volume on a SolidFire Cluster."""

    options = {'name': args.name,
               'count': args.count,
               'attributes': args.attributes,
               'chap_secrets': args.chap_secrets,
               'emulation': args.emulation}
    vlist = self.volumes.create(args.size, args.account_id, **options)
    for v in vlist:
        utils.print_dict(v)


@utils.arg('--keys',
           metavar='<accountID, status, name...>',
           default='',
           help='keys to display in resultant list, may be any valid SF '
                'Account Object Key.'
                '  (--keys accountID,status) Default: Show all keys\n')
@utils.arg('--sort',
           metavar='<key-name>',
           default='accountID',
           help='Account attribute to sort displayed results by. '
                'Default: accountID.')
def do_account_list(self, args):
    """ List accounts on a cluster."""

    accounts = self.accounts.list(args.sort)
    key_list = [k for k, v in six.iteritems(accounts[0].__dict__)]
    utils.print_list(accounts, key_list)


def do_account_attributes(self, args):
    """ List Account attributes."""
    attributes = self.accounts.list_attributes()
    attrs = [{'AccountAttribute': val} for val in attributes]
    utils.print_list(attrs, ['AccountAttribute'])
