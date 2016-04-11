import mock
import unittest

import daedalus.validation.service

class TestValidationConsumer(unittest.TestCase):
    def setUp(self):
        self.validation_consumer = daedalus.validation.service.ValidationConsumer()

    def test_queue_name(self):
        self.assertEqual(self.validation_consumer.queue_name, 'validation')

    @mock.patch('daedalus.validation.validate', return_value='bazquux')
    def test_process_task(self, validate_mock):
        request_mock = mock.MagicMock()
        request_mock.body = 'foobar'

        response_mock = mock.MagicMock()

        self.validation_consumer.process_task(request_mock, response_mock)
        validate_mock.assert_called_with('foobar')
        self.assertEqual(response_mock.body, 'bazquux')

class TestMain(unittest.TestCase):
    @mock.patch.object(daedalus.validation.service.ValidationConsumer, 'run')
    @mock.patch('daedalus.common.service.preflight')
    def test_main(self, run_mock, preflight_mock):
        daedalus.validation.service.main()
        self.assertTrue(preflight_mock.called)
        self.assertTrue(run_mock.called)
