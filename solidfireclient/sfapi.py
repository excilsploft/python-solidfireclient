import json
import logging
import time

from six import wraps
import requests

LOG = logging.getLogger(__name__)

retry_exc_tuple = (#exception.SolidFireRetryableException,
                   requests.exceptions.ConnectionError)
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
                    (args[1],))
            LOG.error(msg)
            #raise exception.SolidFireAPIException(message=msg)
        return func_retry
    return retry_dec

class API(object):
    def __init__(self, endpoint_dict, endpoint_version='1.0'):
        self.endpoint_dict = endpoint_dict
        self.version = '1.0'

    def issue_api_request(self, method, params, endpoint_dict=None):
        if params is None:
            params = {}

        # NOTE(jdg): We allow passing in a new endpoint_dict to issue_api_req
        # to enable some of the multi-cluster features like replication etc
        if endpoint_dict is None:
            endpoint_dict = self.endpoint_dict
        payload = {'method': method, 'params': params}

        url = '%s/json-rpc/%s/' % (endpoint_dict['url'], self.version)

        LOG.debug('Issue SolidFire API call: %s' % json.dumps(payload))

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
            #raise exception.SolidFireRetryableException(message=msg)

        if 'error' in response:
            msg = ('API response: %s'), response
            #raise exception.SolidFireAPIException(msg)
        return response
