'''Common security utilities for signing url callbacks.'''
import base64
import email.utils
import hashlib
import hmac

from daedalus.common import log_manager
from requests.auth import AuthBase
from urlparse import urlparse

class Signature(AuthBase): # pylint: disable=R0903
    '''Special authentication class that will sign urls.'''
    def __init__(self, token):
        self.token = token

    @staticmethod
    def sign_url(token, url, body, timestamp, job_id, job_status): # pylint: disable=too-many-arguments
        '''Given a url, body, timestamp, and token, this function will return a suitable signature.'''
        assert isinstance(token, basestring)
        assert isinstance(url, basestring)
        assert isinstance(body, basestring) or body is None
        assert isinstance(timestamp, basestring)
        assert isinstance(job_id, basestring)
        assert isinstance(job_status, basestring)

        assert len(token) > 0
        assert len(url) > 0
        assert len(timestamp) > 0
        assert len(job_id) > 0
        assert len(job_status) > 0

        assert bool(urlparse(url).netloc)

        if body is not None:
            b64_body = base64.b64encode(body)
        else:
            b64_body = ''

        total_url = url
        total_url += b64_body

        total_url += timestamp
        total_url += job_id
        total_url += job_status

        log_manager.debug('HASH: token -> %r' % token)
        log_manager.debug('HASH: url -> %r' % url)
        log_manager.debug('HASH: body -> %r' % b64_body)
        log_manager.debug('HASH: timestamp -> %r' % timestamp)
        log_manager.debug('HASH: job_id -> %r' % job_id)
        log_manager.debug('HASH: job_status -> %r' % job_status)
        log_manager.debug('HASH: total_url -> %r' % total_url)

        signature = hmac.new(token, total_url, hashlib.sha1)
        return base64.b64encode(signature.digest())

    def __call__(self, request):
        '''Adds a date and x-signature header to the request.'''
        url = request.url
        body = request.body
        timestamp = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
        job_id = request.headers['x-job-id']
        job_status = request.headers['x-job-status']
        request.headers['Date'] = timestamp
        request.headers['x-signature'] = self.sign_url(self.token, url, body, timestamp, job_id, job_status)
        return request
