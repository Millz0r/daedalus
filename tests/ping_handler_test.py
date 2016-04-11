import mock
import unittest

from daedalus.frontend.handlers import PingHandler

class TestPingHandler(unittest.TestCase):
    def setUp(self):
        application = mock.MagicMock()
        request = mock.MagicMock()
        self.ping_handler = PingHandler(application, request)

    def test_route(self):
        result = PingHandler.route()
        self.assertEqual('/ping', result[0])
        self.assertEqual(PingHandler, result[1])

    def test_get(self):
        with mock.patch.object(self.ping_handler, 'write') as write_mock:
            self.ping_handler.get()
            write_mock.assert_called_with('pong')
