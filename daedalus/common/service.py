'''Common service functions.'''

import daedalus.config
import os.path
import signal

from daedalus.common import log_manager
from daedalus.queueing import queue_manager

def preflight(file_path):
    '''Collection of common tasks that need to be run prior to starting a service.'''
    signal.signal(signal.SIGINT, queue_manager.close_connection)
    signal.signal(signal.SIGTERM, queue_manager.close_connection)
    queue_manager.set_connection(daedalus.config.RABBITMQ_PORT)
    log_manager.info('Starting %s service' % os.path.split(os.path.split(file_path)[0])[1])
