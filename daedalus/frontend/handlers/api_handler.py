#pylint: disable=line-too-long
'''Class for handling the /api route.'''

import cyclone.web
import importlib
import inflection
import re

class ApiHandler(cyclone.web.RequestHandler):
    '''Handles the '/api' route.'''

    @classmethod
    def route(cls):
        '''Route definition for the application.'''
        return ('/api', cls)

    def get(self):
        '''Returns a JSON object of each of the routes, the verbs they respond to, and some documentation on them.'''
        handlers_module = importlib.import_module('daedalus.frontend.handlers')
        non_important_handlers = [inflection.camelize(module_name) for module_name in getattr(handlers_module, '__non_important_handlers')]
        handler_names = [handler_name for handler_name in dir(handlers_module) if re.match(r'.*?Handler', handler_name) and handler_name not in non_important_handlers]

        data = {}
        for handler_name in handler_names:
            match = re.match(r'(.*?)Handler', handler_name)
            key = match.group(1).lower()

            handler = getattr(handlers_module, handler_name)
            route, _ = handler.route()

            verbs = []
            for verb in ('get', 'post', 'delete', 'put', 'options', 'head'):
                doc = getattr(handler, verb, None).__doc__
                if doc:
                    verbs.append({'verb': verb, 'doc': doc})

            data[key] = {
                'route': route,
                'verbs': verbs
            }

        self.write(data)
