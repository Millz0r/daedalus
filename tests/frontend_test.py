import mock
import sys
import unittest

from daedalus.frontend import service

class FrontendTestCase(unittest.TestCase):

    @mock.patch.dict('os.environ', {'PORT': '5001', 'DEBUG': 'True'})
    @mock.patch('twisted.internet.reactor', autospec=True)
    @mock.patch('twisted.python.log', autospec=True)
    @mock.patch('daedalus.frontend.SecureApplication', autospec=True)
    def test_frontend_main(self, application_mock, log_mock, reactor_mock):
        service.main()
        self.assertTrue(application_mock.called)
        self.assertTrue(log_mock.startLogging.called)
        reactor_mock.listenTCP.assert_called_with(5001, application_mock(), interface='0.0.0.0')
        self.assertTrue(reactor_mock.run.called)
