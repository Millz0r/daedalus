import mock
import unittest

import daedalus.valuation.service

class TestValuationConsumer(unittest.TestCase):
    def setUp(self):
        self.valuation_consumer = daedalus.valuation.service.ValuationConsumer()

    def test_queue_name(self):
        self.assertEqual(self.valuation_consumer.queue_name, 'valuation')

    @mock.patch('daedalus.valuation.valuate', return_value='bazquux') 
    def test_process_task(self, valuate_mock):
        request_mock = mock.MagicMock()
        request_mock.body = 'foobar'

        response_mock = mock.MagicMock()

        self.valuation_consumer.process_task(request_mock, response_mock)
        response_mock.set_header.assert_called_with('content_type', 'application/json')
        valuate_mock.assert_called_with('foobar')
        self.assertEqual(response_mock.body, 'bazquux')

class TestMain(unittest.TestCase):
    @mock.patch.object(daedalus.valuation.service.ValuationConsumer, 'run')
    @mock.patch('daedalus.common.service.preflight')
    def test_main(self, preflight_mock, run_mock):
        daedalus.valuation.service.main()
        self.assertTrue(preflight_mock.called)
        self.assertTrue(run_mock.called)
