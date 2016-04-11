import daedalus.common.mimetype
import daedalus.exceptions
import mock
import unittest

class TestMimetype(unittest.TestCase):
    def test_mimetype_to_simple_good_mimetype(self):
        self.assertEqual(daedalus.common.mimetype.mimetype_to_simple('application/json'), 'json')

    def test_mimetype_to_simple_upper_mimetype(self):
        self.assertEqual(daedalus.common.mimetype.mimetype_to_simple('application/JSON'), 'json')

    def test_mimetype_to_simple_with_charset(self):
        self.assertEqual(daedalus.common.mimetype.mimetype_to_simple('application/json; charset=UTF-8'), 'json')

    def test_mimetype_to_simple_bad_mimetype(self):
        with self.assertRaisesRegexp(daedalus.exceptions.BadFileFormat, 'Unknown mimetype: \'application/bad_format\''):
            daedalus.common.mimetype.mimetype_to_simple('application/bad_format')

    def test_mimetype_to_simple_alternate_mimetype(self):
        self.assertEqual(daedalus.common.mimetype.mimetype_to_simple('application/vnd.ms-excel'), 'excel')

    def test_simple_to_mimetype_good_simple(self):
        self.assertEqual(daedalus.common.mimetype.simple_to_mimetype('json'), 'application/json')

    def test_simple_to_mimetype_upper_simple(self):
        self.assertEqual(daedalus.common.mimetype.simple_to_mimetype('JSON'), 'application/json')

    def test_simple_to_mimetype_bad_simple(self):
        with self.assertRaisesRegexp(daedalus.exceptions.BadFileFormat, 'Unknown simple type: \'bad_format\''):
            daedalus.common.mimetype.simple_to_mimetype('bad_format')
