import mock
import unittest

from daedalus.frontend.handlers import RootHandler

class TestRootHandler(unittest.TestCase):
    def setUp(self):
        application = mock.MagicMock()
        request = mock.MagicMock()
        self.root_handler = RootHandler(application, request)

    def test_route(self):
        result = RootHandler.route()
        self.assertEqual('/', result[0])
        self.assertEqual(RootHandler, result[1])

    @mock.patch('subprocess.check_output', return_value='version_string')
    def test_get(self, check_output_mock):
        with mock.patch.object(self.root_handler, 'write') as write_mock:
            self.root_handler.get()
            check_output_mock.assert_called_with(['git', 'describe', '--always'])
            write_mock.assert_called_with('version_string')
