from solidfireclient.common import http
from solidfireclient.v1 import events
from solidfireclient.v1 import resources
from solidfireclient.v1 import stacks


class Client(http.HTTPClient):
    """Client for the SolidFire v1 API.

    :param string endpoint: A user-supplied endpoint URL for the heat
                            service.
    :param string token: Token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the Heat v1 API."""
        super(Client, self).__init__(*args, **kwargs)
        self.stacks = stacks.StackManager(self)
        self.resources = resources.ResourceManager(self)
        self.events = events.EventManager(self)

