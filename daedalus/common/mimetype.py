'''Utilities for translating mimetypes to more easily digestable type strings.'''

import daedalus.exceptions

__MIMETYPE_MAPS__ = {
    'excel': {
        'default': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'other': ['application/vnd.ms-excel']
    },
    'json': {
        'default': 'application/json'
    }
}

def mimetype_to_simple(mimetype):
    '''Translates mimetype to simple type.'''
    mimetype = mimetype.lower().split(';')[0].strip()
    for key, value in __MIMETYPE_MAPS__.items():
        if mimetype == value['default'] or mimetype in value.get('other', list()):
            return key
    raise daedalus.exceptions.BadFileFormat('Unknown mimetype: %r' % mimetype)

def simple_to_mimetype(simpletype):
    '''Translates simple type to mimetype.'''
    simpletype = simpletype.lower()
    try:
        return __MIMETYPE_MAPS__[simpletype]['default']
    except KeyError:
        raise daedalus.exceptions.BadFileFormat('Unknown simple type: %r' % simpletype)
