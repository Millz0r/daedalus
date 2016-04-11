import daedalus.queueing.messages
import json
import mock
import unittest

class TestMessage(unittest.TestCase):
    def test_set_headers(self):
        message = daedalus.queueing.messages.Message()
        new_headers = {'a-1': 1, 'b-2': 2}
        message.headers = new_headers
        self.assertIsNot(new_headers, message._headers)
        self.assertEqual({'a_1': 1, 'b_2': 2}, message._headers)

    def test_job_id(self):
        message = daedalus.queueing.messages.Message()
        job_id = 666
        message.job_id = job_id
        self.assertEqual(job_id, message._headers['job_id'])
        self.assertEqual(job_id, message.job_id)

    def test_callback_url(self):
        message = daedalus.queueing.messages.Message()
        callback_url = 'http://localhost'
        message.callback_url = callback_url
        self.assertEqual(callback_url, message._headers['callback_url'])
        self.assertEqual(callback_url, message.callback_url)

    def test_get_body_or_error_no_error(self):
        message = daedalus.queueing.messages.Message()
        body = 'my body'
        message.body = body
        self.assertEqual(body, message.get_body_or_error())

    def test_get_body_or_error_with_error(self):
        message = daedalus.queueing.messages.Message()
        error = 'bad error here'
        message.error = error
        self.assertEqual(error, message.get_body_or_error())

    def test_set_header(self):
        message = daedalus.queueing.messages.Message()
        message.set_header('foo', 'bar')
        self.assertEqual('bar', message._headers['foo'])

    def test_set_header_dashed(self):
        message = daedalus.queueing.messages.Message()
        message.set_header('foo-me', 'bar')
        self.assertEqual('bar', message._headers['foo_me'])

    def test_set_header_overwrite(self):
        message = daedalus.queueing.messages.Message()
        message.set_header('foo', 'bar')
        with self.assertRaisesRegexp(daedalus.exceptions.ImmutableObject, 'Cannot change header \'foo\', already set to \'bar\''):
            message.set_header('foo', 'baz')

    def test_get_header(self):
        message = daedalus.queueing.messages.Message()
        message.set_header('foo', 'bar')
        self.assertEqual('bar', message.get_header('foo'))

    def test_get_headers_no_format(self):
        message = daedalus.queueing.messages.Message()
        message.set_header('foo', 'bar')
        self.assertEqual({'foo': 'bar'}, message.get_headers())

    def test_get_headers_html_format(self):
        message = daedalus.queueing.messages.Message()
        message.set_header('content_type', 'application/json')
        message.set_header('foo', 'bar')
        self.assertEqual({'x-foo': 'bar', 'content-type': 'application/json'}, message.get_headers(key_format='html'))

    def test_yamlize(self):
        message = daedalus.queueing.messages.Message()
        self.assertIsInstance(message.yamlize(), basestring)        

    def test_body_overwrite(self):
        message = daedalus.queueing.messages.Message()
        message.body = 'foo'
        with self.assertRaisesRegexp(daedalus.exceptions.ImmutableObject, 'Cannot change body, already set to \'foo\''):
            message.body = 'bar'

    def test_error_overwrite(self):
        message = daedalus.queueing.messages.Message()
        message.error = 'foo'
        with self.assertRaisesRegexp(daedalus.exceptions.ImmutableObject, 'Cannot change error, already set to \'foo\''):
            message.error = 'bar'

    def test_error_jsoning(self):
        message = daedalus.queueing.messages.Message()
        message.error = {'error': 'foo'}
        self.assertIsInstance(message.error, basestring)
        self.assertEqual(json.loads(message.error), {'error': 'foo'})

class TestRequestMessage(unittest.TestCase):
    def test_load_good_object(self):
        message = '''!RequestMessage
        _headers:
          foo: bar
        body: boo
        '''
        message = daedalus.queueing.messages.RequestMessage.load(message)
        self.assertIsInstance(message, daedalus.queueing.messages.RequestMessage)

    def test_load_bad_object(self):
        message = '''!!python/dict
        _headers:
          foo: bar
        body: boo
        '''
        with self.assertRaises(AssertionError):
            daedalus.queueing.messages.RequestMessage.load(message)

class TestResponseMessage(unittest.TestCase):
    def test_load_good_object(self):
        message = '''!ResponseMessage
        _headers:
          foo: bar
        body: boo
        '''
        message = daedalus.queueing.messages.ResponseMessage.load(message)
        self.assertIsInstance(message, daedalus.queueing.messages.ResponseMessage)

    def test_load_bad_object(self):
        message = '''!!python/dict
        _headers:
          foo: bar
        body: boo
        '''
        with self.assertRaises(AssertionError):
            daedalus.queueing.messages.ResponseMessage.load(message)
