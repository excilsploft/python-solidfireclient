# Copyright 2013 SolidFire Inc
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import sys


def import_class(import_str):
    mod_str, _sep, class_str = import_str.rpartition('.')
    __import__(mod_str)
    return getattr(sys.modules[mod_str], class_str)


def get_client_class(version):
    version_map = {'1': 'solidfireclient.v1.client.Client'}
    try:
        client_path = version_map[str(version)]
    except (KeyError, ValueError):
        # Invalid version specified
        # TODO(jdg): Proper exception needed
        raise Exception
    return import_class(client_path)


def Client(login, password, mvip, version=1, **kwargs):
    # NOTE(jdg): Currently this is irrelevant as we only
    # have v1 client implemented, but go ahead
    # and put the place-holder here
    client_class = get_client_class(version)
    return client_class(login, password, mvip, **kwargs)
