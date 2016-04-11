import base64
import daedalus.common.security
import daedalus.common.service
import hashlib
import mock
import signal
import unittest

from daedalus.queueing import queue_manager

# This example is taken straight from the twillio security site.
# https://www.twilio.com/docs/security
class SignatureTest(unittest.TestCase):
    def setUp(self):
        self.params = {
            'Digits': 1234,
            'To': '+18005551212',
            'From': '+14158675309',
            'Caller': '+14158675309',
            'CallSid': 'CA1234567890ABCDE'
        }
        self.token = '12345'
        self.url = 'https://mycompany.com/myapp.php?foo=1&bar=2'
        self.timestamp = 'foobar'
        self.job_id = '45'
        self.job_status = 'success'
        self.total_url = 'https://mycompany.com/myapp.php?foo=1&bar=2CallSidCA1234567890ABCDECaller+14158675309Digits1234From+14158675309To+18005551212foobar45success'
        self.signature_obj = daedalus.common.security.Signature(self.token)

    def test_sign_url_with_string_params(self):
        sig_mock = mock.MagicMock()
        sig_mock.digest.return_value = 'foo'
        with mock.patch('hmac.new', return_value=sig_mock) as hmac_new_mock:
            self.signature_obj.sign_url(self.token, 'http://localhost', 'foo', self.timestamp, self.job_id, self.job_status)
            hmac_new_mock.assert_called_with(self.token, 'http://localhost%sfoobar45success' % base64.b64encode('foo'), hashlib.sha1)

    def test_sign_url_without_params(self):
        sig_mock = mock.MagicMock()
        sig_mock.digest.return_value = 'foo'
        with mock.patch('hmac.new', return_value=sig_mock) as hmac_new_mock:
            self.signature_obj.sign_url('foo', 'https://example.com', None, self.timestamp, self.job_id, self.job_status)
            hmac_new_mock.assert_called_with('foo', 'https://example.comfoobar45success', hashlib.sha1)

    def test_sign_url_without_token(self):
        with self.assertRaises(AssertionError):
            self.signature_obj.sign_url(None, 'http://localhost', None, self.timestamp, self.job_id, self.job_status)

    def test_sign_url_with_empty_token(self):
        with self.assertRaises(AssertionError):
            self.signature_obj.sign_url('', 'http://localhost', None, self.timestamp, self.job_id, self.job_status)

    def test_sign_url_without_url(self):
        with self.assertRaises(AssertionError):
            self.signature_obj.sign_url('foo', None, None, self.timestamp, self.job_id, self.job_status)

    def test_sign_url_with_empty_url(self):
        with self.assertRaises(AssertionError):
            self.signature_obj.sign_url('foo', '', None, self.timestamp, self.job_id, self.job_status)

    def test_sign_url_with_bad_url(self):
        with self.assertRaises(AssertionError):
            self.signature_obj.sign_url('foo', 'asdfasdfbafnotaurl', None, self.timestamp, self.job_id, self.job_status)

    def test_sign_url_without_timestamp(self):
        with self.assertRaises(AssertionError):
            self.signature_obj.sign_url('foo', 'http://localhost', None, None, self.job_id, self.job_status)

    def test_sign_url_empty_timestamp(self):
        with self.assertRaises(AssertionError):
            self.signature_obj.sign_url('foo', 'http://localhost', None, '', self.job_id, self.job_status)

    def test_sign_url_without_job_id(self):
        with self.assertRaises(AssertionError):
            self.signature_obj.sign_url('foo', 'http://localhost', None, self.timestamp, None, self.job_status)

    def test_sign_url_empty_job_id(self):
        with self.assertRaises(AssertionError):
            self.signature_obj.sign_url('foo', 'http://localhost', None, self.timestamp, '', self.job_status)

    def test_sign_url_without_job_status(self):
        with self.assertRaises(AssertionError):
            self.signature_obj.sign_url('foo', 'http://localhost', None, self.timestamp, self.job_id, None)

    def test_sign_url_empty_job_status(self):
        with self.assertRaises(AssertionError):
            self.signature_obj.sign_url('foo', 'http://localhost', None, self.timestamp, self.job_id, '')

    @mock.patch('requests.Request', auto_spec=True)
    @mock.patch('email.utils.formatdate', return_value='1/1/11')
    def test_call(self, formatdate_mock, request_mock):
        with mock.patch.object(self.signature_obj, 'sign_url', return_value='my_signature') as sign_url_mock:
            request_mock.headers = {}
            request_mock.headers['x-job-id'] = '4'
            request_mock.headers['x-job-status'] = 'success'
            request_mock.body = 'foo'
            self.signature_obj(request_mock)
            formatdate_mock.assert_called_with(timeval=None, localtime=False, usegmt=True)
            self.assertEqual(request_mock.headers['Date'], '1/1/11')
            self.assertEqual(request_mock.headers['x-signature'], 'my_signature')

class PreflightTest(unittest.TestCase):
    @mock.patch('daedalus.common.log_manager.info')
    @mock.patch('daedalus.queueing.queue_manager.set_connection')
    @mock.patch('signal.signal')
    def test_preflight(self, signal_mock, set_connection_mock, info_mock):
        expected_signal_calls = [mock.call(signal.SIGINT, queue_manager.close_connection), mock.call(signal.SIGTERM, queue_manager.close_connection)]
        daedalus.common.service.preflight('/my/fake/service.py')
        self.assertEqual(expected_signal_calls, signal_mock.call_args_list)
        set_connection_mock.assert_called_with(daedalus.config.RABBITMQ_PORT)
        info_mock.assert_called_with('Starting fake service')
