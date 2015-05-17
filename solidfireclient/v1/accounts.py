import logging
import six

from solidfireclient import sfapi

LOG = logging.getLogger(__name__)
logging.basicConfig()


class Account(sfapi.API):
    """ Account methods for the SolidFire Cluster. """

    def list_attributes(self):
        """
        Display a list of valid Account attributes.

        Note, this works by grabbing a Account object from the Cluster
        and iterating through its attributes and displaying the key
        names.  This requires that an Account exist on the system.
        """

        try:
            accounts = self.ListAccounts()['accounts']
        except Exception:
            # TOOD(jdg): Catch exception and show error info
            pass
        if len(accounts) < 1:
            # TODO(jdg): Raise here as we need at least one vol to interrogate
            pass
        return [k for k, v in six.iteritems(accounts[0])]

    def list(self, sort_key='accountID', start_id=0, limit=0):
        """
        Retrieve a list of Accounts on the SolidFire Cluster.

        params: sort Parameter to sort results list by
        params: start_id Retrieve accounts starting with id == start_id
        params: limit Max number of accounts to return

        """
        accounts = []

        try:
            accounts = self.ListAccounts(start_id, limit)['accounts']
        except Exception:
            # TOOD(jdg): Catch exception and show error info
            pass

        if sort_key not in accounts[0]:
            sort_key = 'accountID'

        accounts = sorted((accounts),
                          key=lambda k: k[sort_key])
        if self.raw:
            return accounts
        else:
            return self._convert_dict_to_resource_objects(accounts)
