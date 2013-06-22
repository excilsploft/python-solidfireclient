import sys

def Client(version, *args, **kwargs):
    module = 'solidfireclient.v%s' % version
    module_str = '.'.join((module, 'client'))
    __import__(module_str)
    module = sys.modules[module_str]

    client_class = getattr(module, 'Client')
    return client_class(*args, **kwargs)
