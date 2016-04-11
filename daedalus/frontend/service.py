'''Runs the web frontend for daedalus.'''

import daedalus.config
import daedalus.frontend
import daedalus.frontend.handlers
import os
import sys
import twisted.internet
import twisted.python

from daedalus.queueing import queue_manager

def main():
    '''Entry point for the frontend server. Starts a server (with optional debug logging).'''
    port = int(os.environ.get('PORT', 5000))
    debug = bool(os.environ.get('DEBUG', False))
    queue_manager.set_connection(daedalus.config.RABBITMQ_PORT)

    application = daedalus.frontend.SecureApplication([
        daedalus.frontend.handlers.RootHandler.route(), #pylint: disable=E1101
        daedalus.frontend.handlers.PingHandler.route(), #pylint: disable=E1101
        daedalus.frontend.handlers.TransformHandler.route(), #pylint: disable=E1101
        daedalus.frontend.handlers.ApiHandler.route(), #pylint: disable=E1101
        daedalus.frontend.handlers.ValidateHandler.route(), #pylint: disable=E1101
    ], debug=debug)

    twisted.python.log.startLogging(sys.stdout)
    twisted.internet.reactor.listenTCP(port, application, interface='0.0.0.0') #pylint: disable=E1101

    twisted.internet.reactor.addSystemEventTrigger('before', 'shutdown', queue_manager.close_connection) #pylint: disable=E1101
    twisted.internet.reactor.run() #pylint: disable=E1101
