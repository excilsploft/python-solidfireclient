# Copyright 2013 SolidFire Inc
# All Rights Reserved.

import httplib
import logging


LOG = logging.getLogger(__name__)


class HTTPClient(object):

    def __init__(self, host, port='443', **kwargs):
        self.host = host
        self.port = port
        self.header = {'content-type': 'application/json-rpc; charset=utf-8'}
        self.connection = httplib.HTTPSConnection(self.host, self.port)

    def request(self, payload):
        self.connection.request('POST', '/json-rpc/1.0', payload, self.header)

    def get_response(self):
        return self.connection.getresponse()
