#pylint: disable=bare-except,global-statement
'''Helper module for querying etcd for configuration options.'''

import etcd
import os

__CLIENT__ = None
__ETCD_HOST__ = ''
__ETCD_PORT__ = ''

def _get_hostname_and_port():
    '''Retrieves the hostname and port from the environmental variables.'''
    global __ETCD_HOST__
    global __ETCD_PORT__

    __ETCD_HOST__, __ETCD_PORT__ = os.environ.get('ETCD_ENDPOINT', '127.0.0.1:4001').split(':')

def _create_client():
    '''Creates a client if host and port exist.'''
    global __CLIENT__

    if __CLIENT__:
        return

    if __ETCD_HOST__ and __ETCD_PORT__:
        __CLIENT__ = etcd.Client(host=__ETCD_HOST__, port=int(__ETCD_PORT__), allow_redirect=True)

def get(key):
    '''Gets a key from the etcd store.'''
    if __CLIENT__:
        try:
            return __CLIENT__.get(key).value #pylint: disable=no-member
        except:
            return None

_get_hostname_and_port()
_create_client()
