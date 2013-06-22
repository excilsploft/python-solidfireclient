import argparse
import os
import sys
import time

from solidfireclient import exceptions
from solidfireclient import utils
from solidfireclient.v1.volumes import VolumeManager as volumes


def _translate_volume_results(collection, convert):
    for item in collection:
        keys = item.__dict__.keys()
        for from_key, to_key in convert:
            if from_key in keys and to_key not in keys:
                setattr(item, to_key, item.__info[from_key])

@utils.arg('--all',
           metavar='<True|False>',
           help='Optional flag to get all volumes '
                'on a cluster regardless of account. '
                'NOTE: Requires setting <sf_cluser_admin> '
                'and <sf_admin_password>.',
                default=False)
@utils.arg('--name',
           metavar='<name>',
           default=None,
           help='Filter results by name')
@utils.arg('--status',
           metavar='<status>',
           default=None,
           help='Filter results by status')
@utils.arg('--account-name',
           metavar='<account-name>',
           default=None,
           help='Filter results by account-name')
def do_list(args):
    """List volumes on a cluster."""
    search_opts = {}
    import pdb;pdb.set_trace()

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
@utils.arg('--account-name',
           metavar='<account-name>',
           help='Name of account (if None or DNE one will be created).',
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
def do_create(args):
    volumes().create(args.sf_mvip, args.sf_login, args.sf_password, args.size, args.name)
