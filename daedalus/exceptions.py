'''Custom exceptions for the daedalus framework.'''

class DaedalusError(Exception):
    '''Base exception for the daedalus framework.'''

class HttpError(DaedalusError):
    '''Base exception for http errors in the daedalus framework.'''

class NotOk(HttpError):
    '''Thrown when the response is not a 200.'''

class BadConnectionString(DaedalusError):
    '''Thrown when trying to process a string that isn't formated as connection string.'''

class BadConnectionObject(DaedalusError):
    '''Thrown when the object given is not a connection object.'''

class MissingFields(DaedalusError):
    '''Thrown when fields are missing from something.'''

class MissingQueue(DaedalusError):
    '''Thrown when the given queue cannot be found.'''

class NotConnected(DaedalusError):
    '''Thrown when operation requires a queue connection to work.'''

class ConnectionExists(DaedalusError):
    '''Thrown when the queue connection is overwritten.'''

class InvalidRequestMessage(DaedalusError):
    '''Thrown when queue manipulations expect a RequestMessage.'''

class ImmutableObject(DaedalusError):
    '''Thrown when trying to change an immutable object.'''

class BadFileFormat(DaedalusError):
    '''Thrown when the given filetype is unexpected.'''

class InvalidAuthorizationHeader(DaedalusError):
    '''Thrown when the authorization is invalid.'''

class UnknownUsername(DaedalusError):
    '''Thrown when looking up the token of an unknown username.'''

class BadDataFrameKey(DaedalusError):
    '''Thrown when a key is missing from a dataframe.'''
