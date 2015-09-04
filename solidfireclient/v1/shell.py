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
        key_list = [k for k, v in six.iteritems(vols[0])]
    else:
        key_list = args.keys.split(',')
    utils.print_list(vols, key_list)


@utils.arg('volume', metavar='<volume>', help='Volume ID.')
@utils.arg('--name',
           default=None,
           help='Name for the new volume (1-64 chars)')
@utils.arg('account',
           default=None,
           help='Account ID to associate new volume with.')
@utils.arg('size',
           default=None,
           help='Size of the new volume (may be greater than original).')
@utils.arg('access',
           metavar='<readOnly|readWrite|locked|replicationTarget>',
           default='readWrite',
           help='Access setting for cloned volume.')
@utils.arg('attributes',
           default=None,
           help='Attributes to associate with the new clone.')
@utils.arg('snapshot',
           default=None,
           help='Snaphot ID to use as the source of the clone.')
def do_volume_clone(self, args):
    volid = self.volumes.clone(args.volume, args.name, args.size,
                               args.access, args.attributes, args.qos,
                               args.snapshot_id)
    vol = self.do_volume_show(volid)
    utils.print_dict(vol)


@utils.arg('volume', metavar='<volume>', help='Volume ID.')
def do_volume_show(self, args):
    """Shows volume details."""
    vol = self.volumes.show(args.volume)
    utils.print_dict(vol)


@utils.arg('volumes', metavar='<volids>', nargs='+', help='List of Volume IDs to delete.')
@utils.arg('--purge',
           dest='purge',
           metavar='<True|False>',
           nargs='?',
           type=bool,
           default=False,
           help='Issue purge immediately after delete.')
def do_volume_delete(self, args):
    """ Helper method to delete volumes on a SolidFire Cluster.
    """
    for v in args.volume:
        self.volumes.delete(v, args.purge)

@utils.arg('start', metavar='<start-id>', help='Volume ID to start.')
@utils.arg('end', metavar='<end-id>', help='Volume ID to end.')
@utils.arg('--purge',
           dest='purge',
           metavar='<True|False>',
           nargs='?',
           type=bool,
           default=False,
           help='Issue purge immediately after delete.')
def do_volume_delete_range(self, args):
    """ Delete volumes within given range.

    Builds a sequential list of Volume IDs including <start> through
    <end>, and deletes any existing volume within that range.
    """
    volumes = list(xrange(int(args.start), int(args.end) + 1))
    self.volumes.delete(volumes, args.purge)


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
@utils.arg('--emulation',
           metavar='<512-emulation>',
           help='Utilize 512 byte emulation.',
           default=True)
def do_volume_create(self, args):
    """ Helper method to create a volume on a SolidFire Cluster."""

    options = {'name': args.name,
               'count': args.count,
               'attributes': args.attributes,
               'emulation': args.emulation}
    vlist = self.volumes.create(args.size, args.account_id, **options)
    for v in vlist:
        del v['qos']['curve']
        del v['qos']['burstTime']
        utils.print_dict(v)

@utils.arg('volume',
           metavar='<volume-id>',
           default=None,
           help='Id of the volume to clone.')
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
@utils.arg('--emulation',
           metavar='<512-emulation>',
           help='Utilize 512 byte emulation.',
           default=False)
@utils.arg('--qos',
           type=str,
           nargs='*',
           metavar='<key=value>',
           help='QoS key=value pairs, minIOPS, maxIOPS and burstIOPS '
                '(Default=None, use \'--\' to indicate end of args)')
def do_volume_clone(self, args):
    qos = {}
    valid_keys = ['minIOPS', 'maxIOPS', 'burstIOPS']
    qos = dict(item.split("=") for item in args.qos)
    for k,v in qos.iteritems():
        if k not in valid_keys:
            print("Invalid key received: %s", k)
            raise Exception
    print "finish it"

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

    accounts = self.accounts.list()
    key_list = [k for k, v in six.iteritems(accounts[0])]
    utils.print_list(accounts, key_list)


@utils.arg('name',
           metavar='<account-name>',
           default=None,
           help='Name to assign to the newly created account.')
@utils.arg('--initiator-secret',
           metavar='<initiator-secret>',
           default=None,
           help='Initiator Secret (CHAP) to use for new account.')
@utils.arg('--target-secret',
           metavar='<target-secret>',
           default=None,
           help='Target Secret (CHAP) to use for new account.')
@utils.arg('--attributes',
           metavar='<account-attributes>',
           default=None,
           help='Attributes to assign to account.')
def do_account_create(self, args):
    account_id = self.accounts.create(args.name)
    self.do_account_get(account_id)


def do_account_attributes(self, args):
    """ List Account attributes."""
    attributes = self.accounts.list_attributes()
    attrs = [{'AccountAttribute': val} for val in attributes]
    utils.print_list(attrs, ['AccountAttribute'])


@utils.arg('acctid',
           metavar='<account-id>',
           default=None,
           help='ID of the account to retrieve.')
def do_account_get(self, args):
    """ Account get."""
    account = self.accounts.get(args.acctid)
    utils.print_dict(account)


@utils.arg('name',
           metavar='<name>',
           default=None,
           help='Name of the account to retrieve.')
def do_account_get_by_name(self, args):
    """ Account get."""
    account = self.accounts.get_by_name(args.name)
    utils.print_dict(account)


@utils.arg('acctid',
           metavar='<account-id>',
           default=None,
           help='ID of the account to modify.')
@utils.arg('--status',
           metavar='<active|locked>',
           default=None,
           help='New status, either active OR locked.')
@utils.arg('--initiator_secret',
           default=None,
           help='Initiator Secret (CHAP) to use for new account.')
@utils.arg('--target_secret',
           default=None,
           help='Target Secret (CHAP) to use for new account.')
@utils.arg('--attributes',
           metavar='<account-attributes>',
           default=None,
           help='Attributes to assign to account.')
def do_account_modify(self, args):
    account = self.accounts.modify(args.acctid, args.status,
                                   args.initiator_secret, args.target_secret)
    account = self.accounts.get(args.acctid)
    utils.print_dict(account)
