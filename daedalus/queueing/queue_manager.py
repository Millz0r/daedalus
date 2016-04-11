'''Constant queues.'''

import daedalus.exceptions
import kombu
import re
import sys

__QUEUE_NAMES__ = ['response', 'xlstransform', 'valuation', 'validation']
__QUEUES__ = {}

__CHANNEL_POOL__ = None
__CONNECTION__ = None
__CONNECTED__ = False

def _bind_queue(queue):
    '''Binds a queue to a channel.'''
    queue.maybe_bind(__CHANNEL_POOL__.acquire())
    queue.declare()

def _tcp_to_amqp(connection_string, username=None, password=None):
    '''Changes the tcp connection string to an amqp connection string.'''
    match = re.match('tcp://(.*)', connection_string)
    if not match:
        raise daedalus.exceptions.BadConnectionString('Not a valid TCP connection string: %s' % connection_string)
    if (username and not password) or (password and not username):
        raise daedalus.exceptions.MissingFields('Need both username and password')
    if username and password:
        return 'amqp://%s:%s@%s//' % (username, password, match.group(1))
    return 'amqp://%s//' % match.group(1)

def _is_amqp_connection_string(connection_string):
    '''Checks to see if a given connection string is valid.'''
    return bool(re.match(r'amqp://(\w+:\w+@)?(\d+(\.\d+){3}|[\w\.]([\-\.\w])*):\d+/?([/\w]*)', connection_string))

def _is_tcp_connection_string(connection_string):
    '''Checks to see if a given connection string is a tcp string.'''
    return bool(re.match(r'tcp://(\d+(\.\d+){3}|[\w\.]([\-\.\w])*):\d+', connection_string))

def _create_connection_from_string(connection_string):
    '''Helper function to create a kombu connection from a connection string.'''
    if _is_amqp_connection_string(connection_string):
        return kombu.Connection(connection_string)
    if _is_tcp_connection_string(connection_string):
        return _create_connection_from_string(_tcp_to_amqp(connection_string))
    raise daedalus.exceptions.BadConnectionString('Not a valid connection string: %s' % connection_string)

def _setup_connection(connection):
    '''Creates a connection from a connection object or a connection_string.'''
    if isinstance(connection, basestring):
        return _create_connection_from_string(connection)
    elif not (isinstance(connection, kombu.connection.Connection) or connection is None):
        raise daedalus.exceptions.BadConnectionObject('Not a valid connection object: %s' % str(connection))
    else:
        return connection

def get_response_queue():
    '''Returns a reference to the response queue.'''
    return get_queue('response')

def get_queue(queue_name, temp=False):
    '''Returns a reference to a given queue.

    This method will create the queue if it doesn't exist. If temp is not specified and the queue is not a common queue it will
    throw an error. If there is a connection available it will bind the queue to a channel from that connection.
    '''
    if __QUEUES__.get(queue_name):
        return __QUEUES__.get(queue_name)
    elif queue_name in __QUEUE_NAMES__:
        queue = kombu.Queue(queue_name)
    elif temp:
        queue = kombu.Queue(queue_name, durable=False, auto_delete=True)
    else:
        raise daedalus.exceptions.MissingQueue('Cannot find queue %s' % queue_name)

    __QUEUES__[queue_name] = queue

    if __CONNECTED__:
        _bind_queue(queue)

    return queue

def get_producer(on_return=None):
    '''Returns a producer bound to a channel. Must be run after a connection has been specified.'''
    if __CONNECTED__:
        return kombu.Producer(__CHANNEL_POOL__.acquire(), on_return=on_return)
    else:
        raise daedalus.exceptions.NotConnected('Must be connected to create a producer')

def set_connection(connection):
    '''Sets the connection, and binds any unbound queues.'''
    global __CONNECTED__ # pylint: disable=W0603
    global __CONNECTION__ # pylint: disable=W0603
    global __CHANNEL_POOL__ # pylint: disable=W0603

    if __CONNECTION__:
        raise daedalus.exceptions.ConnectionExists('The connection has already been set')

    __CONNECTION__ = _setup_connection(connection)
    __CHANNEL_POOL__ = __CONNECTION__.ChannelPool()
    for queue in __QUEUES__.values():
        _bind_queue(queue)
    __CONNECTED__ = True

def get_connection():
    '''Returns the connection of the manager.'''
    return __CONNECTION__

def close_connection(*args, **kwargs): # pylint: disable=W0613
    '''Closes the connection to the queue and subsequently closes the child channels.'''
    if __CONNECTED__:
        __CHANNEL_POOL__.force_close_all()
        __CONNECTION__.release()
    sys.exit(0)

def get_channel():
    '''Returns a channel from the connection.'''
    if __CHANNEL_POOL__:
        return __CHANNEL_POOL__.acquire()
    else:
        raise daedalus.exceptions.NotConnected('Must be connected to create a channel')

def get_connected():
    '''Returns True if connected, False otherwise.'''
    return __CONNECTED__
