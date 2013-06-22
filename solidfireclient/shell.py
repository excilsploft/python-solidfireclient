#!/usr/bin/python

# Copyright 2013 SolidFire Inc.
# All Rights Reserved.
#

"""
Command-line interface to the SolidFire API.
"""

from __future__ import print_function

import argparse
import httplib2
import logging
import sys
from solidfireclient import client as solidfireclient
from solidfireclient import exceptions as exc
from solidfireclient import utils


logger = logging.getLogger(__name__)


class SolidFireShell(object):

    def get_base_parser(self):
        # TODO(jdg):  Add an option to read in json file?

        parser = argparse.ArgumentParser(prog='solidfire',
                                         description=__doc__.strip(),
                                         epilog='See "solidfire help COMMAND" '
                                                'for help on a specific '
                                                'command.',
                                         add_help=False,
                                         formatter_class=HelpFormatter, )

        parser.add_argument('-h', '--help',
                            action='store_true',
                            help=argparse.SUPPRESS, )

        parser.add_argument('--debug',
                            action='store_true',
                            default=utils.env('SFCLIENT_DEBUG',
                                              default=False),
                            help='Print debug output')

        parser.add_argument('--verbose',
                            default=False, action="store_true",
                            help="Provides more verbose output")

        parser.add_argument('--sf-login',
                            metavar='<sf-login>',
                            default=utils.env('SF_USERNAME'),
                            help='Defaults to env[SF_USERNAME]')
        parser.add_argument('--sf_login',
                            help=argparse.SUPPRESS)

        parser.add_argument('--sf-password',
                            metavar='<sf-password>',
                            default=utils.env('SF_PASSWORD'),
                            help='Defaults to env[SF_PASSWORD]')
        parser.add_argument('--sf_password',
                            help=argparse.SUPPRESS)

        parser.add_argument('--sf-mvip',
                            metavar='<cluster-mgmt-ip>',
                            default=utils.env('SF_MVIP'),
                            help='Defaults to env[SF_MVIP]')
        parser.add_argument('--sf_mvip',
                            help=argparse.SUPPRESS)

        parser.add_argument('--sf-cluster-admin',
                            metavar='<cluster-admin-account>',
                            default=utils.env('SF_CLUSTER_ADMIN'),
                            help='Defaults to env[SF_CLUSTER_ADMIN]')
        parser.add_argument('--sf_cluster_admin',
                            help=argparse.SUPPRESS)

        parser.add_argument('--sf-admin-password',
                            metavar='<cluster-admin-password>',
                            default=utils.env('SF_ADMIN_PASSWORD'),
                            help='Defaults to env[SF_ADMIN_PASSWORD]')
        parser.add_argument('--sf_admin_password',
                            help=argparse.SUPPRESS)

        parser.add_argument('--solidfire-api-version',
                            metavar='<client-api-version-to-use>',
                            default='1',
                            help='Defaults to 1')
        parser.add_argument('--sf_api_version',
                            help=argparse.SUPPRESS)

        return parser

    def get_subcommand_parser(self):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')
        submodule = utils.import_versioned_module('1', 'shell')
        self._find_actions(subparsers, submodule)
        self._find_actions(subparsers, self)


        return parser

    def _find_actions(self, subparsers, actions_module):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            # I prefer to be hypen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(command,
                                              help=help,
                                              description=desc,
                                              add_help=False,
                                              formatter_class=HelpFormatter)
            subparser.add_argument('-h', '--help',
                                   action='help',
                                   help=argparse.SUPPRESS, )
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def _set_debug(self, debug):
        if debug:
            logging.basicConfig(
                format="%(levelname)s (%(module)s:%(lineno)d) %(message)s",
                level=logging.DEBUG)
            httplib2.debuglevel = 1

    def main(self, argv):
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        self._set_debug(options.debug)

        api_version = options.solidfire_api_version
        subcommand_parser = self.get_subcommand_parser()
        self.parser = subcommand_parser

        # check top-level help
        if options.help or not argv:
            self.do_help(options)
            return 0

        # Now start the *real* parsing
        args = subcommand_parser.parse_args(argv)

        # deal with help straight away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0

        if not args.sf_login:
            raise exc.CommandError("You must provide a username via"
                                   " either --sf-login or env[SF_LOGIN]")

        if not args.sf_password:
            raise exc.CommandError("You must provide a password via"
                                   " either --sf-password or env[SF_PASSWORD]")

        kwargs = {
            'mvip': args.sf_mvip,
            'username': args.sf_login,
            'password': args.sf_password,
            'admin': args.sf_cluster_admin,
            'admin_password': args.sf_admin_password,
        }

        client = solidfireclient.Client('1', args.mvip, **kwargs)
        args.func(client, args)
        cluster_url = args.sf_mvip

    @utils.arg('command', metavar='<subcommand>', nargs='?',
               help='Display help for <subcommand>')
    def do_help(self, args):
        """
        Display help about this program or one of its subcommands.
        """
        if getattr(args, 'command', None):
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            self.parser.print_help()


class HelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)


def main():
    try:
        SolidFireShell().main(sys.argv[1:])

    except Exception as e:
        print ('%s' % e)
        sys.exit(1)

if __name__ == "__main__":
    main()
