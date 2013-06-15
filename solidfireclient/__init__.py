__all__ = ['__version__']

# We have a circular import problem when we first run python setup.py sdist
# It's harmless, so deflect it.
__version__ = '1'

