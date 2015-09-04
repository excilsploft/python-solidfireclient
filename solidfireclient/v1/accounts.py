import logging
import six

from solidfireclient.v1 import solidfire_element_api as sfapi
from solidfireclient.v1 import object_utils

LOG = logging.getLogger(__name__)
logging.basicConfig()

# Handy:
# type(volumes[1]) is dict
# True
# type(vobs[1]) is dict
# False


class Account(sfapi.SolidFireAPI):
    """ Account methods for the SolidFire Cluster. """

    def list_attributes(self):
        """
        Display a list of valid account attributes.

        Note, this works by grabbing an account object from the Cluster
        and iterating through its attributes and displaying the key
        names.  This requires that an active account exist on the system.
        """

        try:
            accounts = self.list_accounts()
        except Exception:
            # TOOD(jdg): Catch exception and show error info
            pass
        if len(accounts) < 1:
            # TODO(jdg): Raise here as we need at least one vol to interrogate
            # and return an empty list
            raise Exception

        return [k for k, v in six.iteritems(accounts[0])]

    def create(self, username, initiator_secret=None,
               target_secret=None, attributes=None, **kwargs):
        """
        Creates an account on the SolidFire Cluster.

        param username: Unique username for this account.
            (1 - 64 characters in length)

        Optional keyword arguments
            param username: Unique username for this account.
              (1 - 64 characters in length)
            param initiator_secret: CHAP secret to use for the initiator.
              Should be 12 - 16 characters in length.
            param target_secret: CHAP secret to use for the target.  Should be
              12 - 16 characters in length.
            attributes: Dict containting Key Value pairs (extra metadata)

        Returns: ID of the newly created account

        """
        try:
            response = self.add_account()
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex
        return response['accountID']

    def list(self):
        """
        Display a list of accounts on the cluster.

        """

        try:
            accounts = self.list_accounts()
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex

        accounts = sorted((accounts),
                          key=lambda k: k['accountID'])
        if self.raw:
            return accounts
        else:
            return object_utils.convert_dict_to_object(accounts)

    def get(self, account_id):
        """ Fetch the specified account object by id.

        param account_id: SolidFire acountID
        returns: SolidFire account
        """
        account = None
        try:
            account = self.get_account_by_id(account_id)['account']
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex

        if self.raw:
            return account
        else:
            return object_utils.convert_dict_to_object(account)

    def get_by_name(self, account_name):
        """ Fetch the specified account object by name.

        param account_name: SolidFire acountName
        returns: SolidFire account
        """

        try:
            account = self.get_account_by_name(account_name)['account']
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex

        if self.raw:
            return account
        else:
            return object_utils.convert_dict_to_object(account)

    def modify(self, account_id, status=None, initiator_secret=None,
               target_secret=None, attributes=None):
        account_id = None
        try:
            self.modify_account(account_id, status, initiator_secret,
                                target_secret, attributes)
        except sfapi.SolidFireRequestException as ex:
            LOG.error(ex.msg)
            raise ex

        return
