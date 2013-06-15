import argparse
import os
import sys
import time

from solidfireclient import exceptions
from solidfireclient import utils
from solidfireclient import v1


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
def do_list(args):
    """List volumes on a cluster."""
    search_opts = {}
    volumes = v1.volumes.list(search_opts=search_opts)
    _translate_volume_results(volumes)
    utils.print_list(volumes, ['SF-ID', 'Name', 'Status', 'Account-ID'])

