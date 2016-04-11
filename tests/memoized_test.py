import mock
import unittest

from daedalus.common.memoized import memoized

# This is the basic number of calls to test_function_mock made by setUp(). If you change the data there, change this one too.
BASE_CALL_COUNT = 2

class MemoizedTest(unittest.TestCase):
    # Note - this function is chosen arbitrarily, any other would do as well.
    @mock.patch('daedalus.common.auth.get_token', return_value='foobar')
    def setUp(self, test_function_mock):
        test_function_mock.__name__ = 'test_function'
        self.mock = test_function_mock
        self.func = memoized(self.mock)
        self.func(0)
        self.func(1.0)

    def test_call_hashed(self):
        self.func(0)
        self.func(1.0)
        self.assertEqual(self.mock.call_count, BASE_CALL_COUNT)

    def test_call_miss(self):
        self.func(999)
        self.assertEqual(self.mock.call_count, BASE_CALL_COUNT + 1)

    # None and null argument still checks the cache, but it fails to locate the key in the dict.
    def test_call_no_argument(self):
        self.func()
        self.assertEqual(self.mock.call_count, BASE_CALL_COUNT + 1)

    def test_call_none_argument(self):
        self.func(None)
        self.assertEqual(self.mock.call_count, BASE_CALL_COUNT + 1)

    def test_get_list(self):
        func_list = self.func.get_list('test_function')
        self.assertEqual(func_list, ['foobar', 'foobar'])

    def test_get_list_invalid(self):
        with self.assertRaisesRegexp(KeyError, 'foobar'):
            func_list = self.func.get_list('foobar')

    def test_clear_cache(self):
        self.func.clear_cache()
        self.func('foobar')
        self.assertEqual(self.mock.call_count, BASE_CALL_COUNT + 1)
