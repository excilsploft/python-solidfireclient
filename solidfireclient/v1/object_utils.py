class Resource(object):
    def __init__(self, dictionary, resource_name=None):
        self.__dict__ = dictionary


def dict_to_object(resources):
    return [Resource(r) for r in resources]
