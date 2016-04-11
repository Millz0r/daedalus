'''Classes for handling /ping route'''

import cyclone.web

class PingHandler(cyclone.web.RequestHandler):
    '''Handles the '/ping' route.'''

    @classmethod
    def route(cls):
        '''Route definition for the application.'''
        return ('/ping', cls)

    def get(self):
        '''Pongs the caller.'''
        self.write('pong')
