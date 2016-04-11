'''Classes for handling / route'''

import cyclone.web
import subprocess

class RootHandler(cyclone.web.RequestHandler):
    '''Handles the '/' route.'''

    @classmethod
    def route(cls):
        '''Route definition for the application.'''
        return ('/', cls)

    def get(self):
        '''Responds with the version of the code being run.'''
        self.write(subprocess.check_output(['git', 'describe', '--always']).strip())
