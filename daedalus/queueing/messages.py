'''Request and Response message classes used for internal message passing paradigms.'''

import daedalus.exceptions
import json
import yaml

from inflection import dasherize, underscore

class Message(object):
    '''Base class for messages in Daedalus.'''
    _http_headers = ['content_type', 'date']

    def __init__(self):
        self._headers = {}
        self._body = None
        self._error = None

    @property
    def headers(self):
        '''Returns the headers of the message.'''
        return self._headers

    @headers.setter
    def headers(self, new_headers):
        '''Sets the headers of the message.'''
        # you can't change the reference to my _headers!
        for key, value in new_headers.items():
            self._headers[underscore(key)] = value

    @property
    def job_id(self):
        '''Gets the job id of the message.'''
        return self._headers.get('job_id')

    @job_id.setter
    def job_id(self, value):
        '''Sets the job id of the message.'''
        self.set_header('job_id', value)

    @property
    def username(self):
        '''Gets the username of the message.'''
        return self._headers.get('username')

    @username.setter
    def username(self, value):
        '''Sets the username of the message.'''
        self.set_header('username', value)

    @property
    def callback_url(self):
        '''Gets the callback url of the message.'''
        return self._headers.get('callback_url')

    @callback_url.setter
    def callback_url(self, value):
        '''Sets the callback url of the message.'''
        self.set_header('callback_url', value)

    @property
    def body(self):
        '''Gets the body of the message.'''
        return self._body

    @body.setter
    def body(self, value):
        '''Sets the body of the message.'''
        if self._body is not None:
            raise daedalus.exceptions.ImmutableObject('Cannot change body, already set to %r' % (self._body))
        self._body = value

    @property
    def error(self):
        '''Gets the error of the message.'''
        return self._error

    @error.setter
    def error(self, value):
        '''Sets the error of the message. If the error is a dictionary then it automatically gets transformed to json.'''
        if self._error is not None:
            raise daedalus.exceptions.ImmutableObject('Cannot change error, already set to %r' % (self._error))
        if isinstance(value, dict):
            self._error = json.dumps(value, separators=(',', ':'))
            self._headers['content_type'] = 'application/json'
        else:
            self._error = value

    def get_body_or_error(self):
        '''If there is an error, returns that, otherwise returns the body.'''
        if self._error is not None:
            return self._error
        else:
            return self._body

    def set_header(self, key, value):
        '''Sets a header value to the provided value.'''
        key = underscore(key)
        if self._headers.get(key) is not None:
            raise daedalus.exceptions.ImmutableObject('Cannot change header %r, already set to %r' % (key, self._headers.get(key)))
        self._headers[key] = value

    def get_header(self, key):
        '''Gets a header value.'''
        return self._headers.get(underscore(key))

    def get_headers(self, key_format=None):
        '''Gets all the headers, optionally formatted.'''
        if not key_format:
            return self._headers

        if key_format.lower() == 'html':
            dasherize_header = lambda x: dasherize('x_' + str(x).lower()) if x not in self._http_headers else dasherize(str(x).lower())
            return {dasherize_header(key): value for key, value in self._headers.items()}

    def yamlize(self):
        '''Turns the message to yaml.'''
        return yaml.dump(self)

class RequestMessage(yaml.YAMLObject, Message):
    '''Class for request messages.'''
    yaml_tag = r'!RequestMessage'

    @staticmethod
    def load(message_yaml):
        '''Loads the request message from yaml asserting it deserialized properly.'''
        message = yaml.load(message_yaml)
        assert isinstance(message, RequestMessage)
        return message

class ResponseMessage(yaml.YAMLObject, Message):
    '''Class for response messages.'''
    yaml_tag = u'!ResponseMessage'

    @staticmethod
    def from_request_message(request_message):
        '''Builds a response object from a request object.'''
        response_message = ResponseMessage()

        response_message.callback_url = request_message.callback_url
        response_message.job_id = request_message.job_id
        response_message.username = request_message.username

        return response_message

    @staticmethod
    def load(message_yaml):
        '''Loads the response message from yaml asserting it deserialized properly.'''
        message = yaml.load(message_yaml)
        assert isinstance(message, ResponseMessage)
        return message
