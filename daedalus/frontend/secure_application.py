'''Classes for ensuring basic auth connections.'''

import cyclone.web

from daedalus.common import auth

class JsonErrorHandler(cyclone.web.ErrorHandler):
    '''Error handler class that writes JSON errors.'''
    error_messages = {
        401: 'Unauthorized',
        404: 'Not found',
    }

    @classmethod
    def get_error_message(cls, status_code):
        '''Looks up the status code to find the error message.'''
        try:
            return cls.error_messages[status_code]
        except KeyError:
            return 'Unknown error'

    def write_error(self, status_code, **kwargs):
        '''Writes the error.'''
        self.write({'error': self.get_error_message(status_code)})

class SecureApplication(cyclone.web.Application):
    '''Application that checks for HTTP Basic Auth prior to executing any commands.'''
    def __call__(self, request):
        '''Called by HTTPServer to execute the request, authorization required.'''
        # Code adapted from https://github.com/fiorix/cyclone/blob/master/demos/httpauth/httpauthdemo.py
        if auth.check_auth(request.headers.get('Authorization'), request.headers.get('x-callback-url')):
            # cyclone.web.Application is an old school class so we can't use super.
            request.headers.add('username', auth.get_username(request.headers.get('Authorization')))
            return cyclone.web.Application.__call__(self, request)
        else:
            # This is a hack to get cyclone to respond with an error.
            # At this point in time I cannot raise any HTTPErrors.
            # Instead I instantiate an ErrorHandler populate it, and execute it manually.
            error_handler = JsonErrorHandler(self, request, status_code=401)
            error_handler._execute([]) # pylint: disable=W0212
            return error_handler
