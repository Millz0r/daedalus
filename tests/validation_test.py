import unittest
import re

import daedalus.validation

class CheckRegexFieldTest(unittest.TestCase):
    def setUp(self):
        self.regex = '\d{2}-\d{1}'
        self.regex_obj = re.compile(self.regex)

    def test_true(self):
        field = '22-1'
        correct_result = False
        result = re.match(self.regex_obj, field)
        test_result, errors = daedalus.validation.validation._check_regex_field(self.regex, field)
        if result:
           correct_result = True
        self.assertEqual(correct_result, test_result)

    def test_false(self):
        field = 'foobar'
        correct_result = False
        result = re.match(self.regex_obj, field)
        test_result, errors = daedalus.validation.validation._check_regex_field(self.regex, field)
        if result:
           correct_result = True
        self.assertEqual(correct_result, test_result)

class ValidDateTest(unittest.TestCase):
    def test_true_excel(self):
        field = 42278.0
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (True, None))

    def test_true_first(self):
        field = '01/02/2015'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (True, None))

    def test_true_second(self):
        field = '01/Feb/2015'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (True, None))

    def test_true_third(self):
        field = '2015/02/01'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (True, None))

    def test_true_forth(self):
        field = '2015/Feb/01'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (True, None))

    def test_true_first_dash(self):
        field = '01-02-2015'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (True, None))

    def test_true_second_dash(self):
        field = '01-Feb-2015'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (True, None))

    def test_true_third_dash(self):
        field = '2015-02-01'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (True, None))

    def test_true_forth_dash(self):
        field = '2015-Feb-01'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (True, None))

    def test_true_uppercase(self):
        field = '12-JAN-2010'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (True, None))

    def test_true_lowercase(self):
        field = '12-jan-2010'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (True, None))

    def test_true_leap_year(self):
        field = '2016-02-29'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (True, None))

    def test_false_full(self):
        field = '12-January-10'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (False, 'Invalid date.'))

    def test_false_format(self):
        field = '01 01 12'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (False, 'Invalid date.'))

    def test_false_format_us(self):
        field = '2012-31-12'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (False, 'Invalid date.'))

    def test_false_format_us_full(self):
        field = 'December-31-12'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (False, 'Invalid date.'))

    def test_false_chars(self):
        field = '1st July 2012'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (False, 'Invalid date.'))

    def test_false_boundary_high_day(self):
        field = '32-Aug-03'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (False, 'Invalid date.'))

    def test_false_boundary_low_day(self):
        field = '0-Aug-03'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (False, 'Invalid date.'))

    def test_false_leap_year(self):
        field = '2015-02-29'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (False, 'Invalid date.'))

    def test_false_boundary_high_month(self):
        field = '2013-13-03'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (False, 'Invalid date.'))

    def test_false_boundary_low_month(self):
        field = '2013-00-03'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (False, 'Invalid date.'))

    def test_false_boundary_month(self):
        field = '1-Foo-03'
        result = daedalus.validation.validation.valid_date(field)
        self.assertEqual(result, (False, 'Invalid date.'))

class ValidPercentageTest(unittest.TestCase):
    def test_true_excel(self):
        field = 0.05
        result = daedalus.validation.validation.valid_percentage(field)
        self.assertEqual(result, (True, None))

    def test_true(self):
        field = '5%'
        result = daedalus.validation.validation.valid_percentage(field)
        self.assertEqual(result, (True, None))

    def test_true_fraction(self):
        field = '14.43%'
        result = daedalus.validation.validation.valid_percentage(field)
        self.assertEqual(result, (True, None))

    def test_true_precision(self):
        field = '14.43%'
        result = daedalus.validation.validation.valid_percentage(field, precision=2)
        self.assertEqual(result, (True, None))

    def test_true_precision_zero(self):
        field = '14%'
        result = daedalus.validation.validation.valid_percentage(field, precision=0)
        self.assertEqual(result, (True, None))

    def test_false_precision(self):
        field = '14.436%'
        result = daedalus.validation.validation.valid_percentage(field, precision=2)
        self.assertEqual(result, (False, 'Invalid character or format.'))

    def test_false_boundary_high(self):
        field = '101%'
        result = daedalus.validation.validation.valid_percentage(field)
        self.assertEqual(result, (False, 'Percentage outside 0-100 bounds.'))

    def test_false_boundary_low(self):
        field = '-1%'
        result = daedalus.validation.validation.valid_percentage(field)
        self.assertEqual(result, (False, 'Invalid character or format.'))

class ValidDollarTest(unittest.TestCase):
    def test_true_excel(self):
        field = 1000000.0
        result = daedalus.validation.validation.valid_dollar(field)
        self.assertEqual(result, (True, None))

    def test_true_dollarsign(self):
        field = '$1,000,000'
        result = daedalus.validation.validation.valid_dollar(field)
        self.assertEqual(result, (True, None))

    def test_true_usd(self):
        field = '1,000,000USD'
        result = daedalus.validation.validation.valid_dollar(field)
        self.assertEqual(result, (True, None))

    def test_true_no_currency(self):
        field = '1,000,000'
        result = daedalus.validation.validation.valid_dollar(field)
        self.assertEqual(result, (True, None))

    def test_true_fraction(self):
        field = '$1,000,000.00'
        result = daedalus.validation.validation.valid_dollar(field)
        self.assertEqual(result, (True, None))

    def test_true_precision(self):
        field = '$1,000,000.00'
        result = daedalus.validation.validation.valid_dollar(field, precision=2)
        self.assertEqual(result, (True, None))

    def test_true_no_commas(self):
        field = '1000000'
        result = daedalus.validation.validation.valid_dollar(field)
        self.assertEqual(result, (True, None))

    def test_true_no_commas_fraction(self):
        field = '1000000.245USD'
        result = daedalus.validation.validation.valid_dollar(field)
        self.assertEqual(result, (True, None))

    def test_false_precision(self):
        field = '$1,000,000.001'
        result = daedalus.validation.validation.valid_dollar(field, precision=2)
        self.assertEqual(result, (False, 'Invalid precision.'))

    def test_false_gbp(self):
        field = '1,000,000GBP'
        result = daedalus.validation.validation.valid_dollar(field)
        self.assertEqual(result, (False, 'Invalid dollar value.'))

class ValidYearTest(unittest.TestCase):
    def test_true_excel(self):
        field = 1994.0
        result = daedalus.validation.validation.valid_year(field)
        self.assertEqual(result, (True, None))

    def test_true(self):
        field = '1994'
        result = daedalus.validation.validation.valid_year(field)
        self.assertEqual(result, (True, None))

    def test_false(self):
        field = '97854'
        result = daedalus.validation.validation.valid_year(field)
        self.assertEqual(result, (False, 'Invalid character or format.'))

class ValidAddressTest(unittest.TestCase):
    def test_true(self):
        field = '45639 Gibbon Street - Unit G'
        result = daedalus.validation.validation.valid_address(field)
        self.assertEqual(result, (True, None))

    def test_true_postal(self):
        field = '45639 Gibbon Street Unit G'
        result = daedalus.validation.validation.valid_address(field)
        self.assertEqual(result, (True, None))

    def test_true_alternative(self):
        field = '45639 Gibbon Street, Unit G'
        result = daedalus.validation.validation.valid_address(field)
        self.assertEqual(result, (True, None))

    def test_true_numerals(self):
        field = '639 1st Rd'
        result = daedalus.validation.validation.valid_address(field)
        self.assertEqual(result, (True, None))

    def test_false(self):
        field = 'address with invalid chars;'
        result = daedalus.validation.validation.valid_address(field)
        self.assertEqual(result, (False, 'Invalid character or format.'))

class ValidCityTest(unittest.TestCase):
    def test_true(self):
        field = 'San Jose'
        result = daedalus.validation.validation.valid_city(field)
        self.assertEqual(result, (True, None))

    def test_false(self):
        field = '2323; semicolon in city'
        result = daedalus.validation.validation.valid_city(field)
        self.assertEqual(result, (False, 'Invalid character or format.'))

class ValidCounty(unittest.TestCase):
    def test_true(self):
        field = 'McPherson County'
        result = daedalus.validation.validation.valid_county(field)
        self.assertEqual(result, (True, None))

    def test_false(self):
        field = '2323; semicolon in county'
        result = daedalus.validation.validation.valid_county(field)
        self.assertEqual(result, (False, 'Invalid character or format.'))

class ValidZipCodeTest(unittest.TestCase):
    def test_true_excel(self):
        field = 56341.0
        result = daedalus.validation.validation.valid_zip_code(field)
        self.assertEqual(result, (True, None))

    def test_true(self):
        field = '56341'
        result = daedalus.validation.validation.valid_zip_code(field)
        self.assertEqual(result, (True, None))

    def test_true_long(self):
        field = '06341-2534'
        result = daedalus.validation.validation.valid_zip_code(field)
        self.assertEqual(result, (True, None))

    def test_false(self):
        field = '232333'
        result = daedalus.validation.validation.valid_zip_code(field)
        self.assertEqual(result, (False, 'Invalid character or format.'))

class ValidUSStateTest(unittest.TestCase):
    def test_true(self):
        field = 'Illinois'
        result = daedalus.validation.validation.valid_us_state(field)
        self.assertEqual(result, (True, None))

    def test_true_uppercase(self):
        field = 'ILLINOIS'
        result = daedalus.validation.validation.valid_us_state(field)
        self.assertEqual(result, (True, None))

    def test_true_lowercase(self):
        field = 'illinois'
        result = daedalus.validation.validation.valid_us_state(field)
        self.assertEqual(result, (True, None))

    def test_true_abbr(self):
        field = 'IL'
        result = daedalus.validation.validation.valid_us_state(field)
        self.assertEqual(result, (True, None))

    def test_false(self):
        field = 'foobar'
        result = daedalus.validation.validation.valid_us_state(field)
        self.assertEqual(result, (False, 'No such US state: foobar.'))

class ValidEstimateSourceTest(unittest.TestCase):
    def test_true(self):
        field = 'External BPO'
        result = daedalus.validation.validation.valid_estimate_source(field)
        self.assertEqual(result, (True, None))

    def test_true_uppercase(self):
        field = 'EXTERNAL BPO'
        result = daedalus.validation.validation.valid_estimate_source(field)
        self.assertEqual(result, (True, None))

    def test_true_lowercase(self):
        field = 'external bpo'
        result = daedalus.validation.validation.valid_estimate_source(field)
        self.assertEqual(result, (True, None))

    def test_false(self):
        field = 'foobar'
        result = daedalus.validation.validation.valid_estimate_source(field)
        self.assertEqual(result, (False, 'No such owner estimate source: foobar.'))

class ValidLeasingStatusTest(unittest.TestCase):
    def test_true(self):
        field = 'Leased - M2M'
        result = daedalus.validation.validation.valid_leasing_status(field)
        self.assertEqual(result, (True, None))

    def test_true_uppercase(self):
        field = 'LEASED - M2M'
        result = daedalus.validation.validation.valid_leasing_status(field)
        self.assertEqual(result, (True, None))

    def test_true_lowercase(self):
        field = 'leased - m2m'
        result = daedalus.validation.validation.valid_leasing_status(field)
        self.assertEqual(result, (True, None))

    def test_false(self):
        field = 'foobar'
        result = daedalus.validation.validation.valid_leasing_status(field)
        self.assertEqual(result, (False, 'No such leasing status: foobar.'))

class ValidClassOfSpaceTest(unittest.TestCase):
    def test_true(self):
        result = daedalus.validation.validation.valid_class_of_space('A')
        self.assertEqual(result, (True, None))

    def test_false(self):
        result = daedalus.validation.validation.valid_class_of_space('E')
        self.assertEqual(result, (False, 'No such class of space E.'))

    def test_false_foo(self):
        result = daedalus.validation.validation.valid_class_of_space('foo')
        self.assertEqual(result, (False, 'No such class of space foo.'))

class ValidIntegerTest(unittest.TestCase):
    def test_true_excel(self):
        result = daedalus.validation.validation.valid_integer(2.0)
        self.assertEqual(result, (True, None))

    def test_true(self):
        result = daedalus.validation.validation.valid_integer('2')
        self.assertEqual(result, (True, None))

    def test_max_value(self):
        result = daedalus.validation.validation.valid_integer('2', max_value=1)
        self.assertEqual(result, (False, 'Integer outside of max bounds: 2.'))

    def test_min_value(self):
        result = daedalus.validation.validation.valid_integer('2', min_value=3)
        self.assertEqual(result, (False, 'Integer outside of min bounds: 2.'))

    def test_false(self):
        result = daedalus.validation.validation.valid_integer('2.0')
        self.assertEqual(result, (False, 'Not an integer: 2.0.'))

class ValidFloatTest(unittest.TestCase):
    def test_true_excel(self):
        result = daedalus.validation.validation.valid_float(6.5)
        self.assertEqual(result, (True, None))

    def test_true(self):
        result = daedalus.validation.validation.valid_float('6.5')
        self.assertEqual(result, (True, None))

    def test_true_int(self):
        result = daedalus.validation.validation.valid_float('6')
        self.assertEqual(result, (True, None))

    def test_true_precision(self):
        result = daedalus.validation.validation.valid_float('6.5', precision=1)
        self.assertEqual(result, (True, None))

    def test_true_precision_zero(self):
        result = daedalus.validation.validation.valid_float('6', precision=0)
        self.assertEqual(result, (True, None))

    def test_max_value(self):
        result = daedalus.validation.validation.valid_float('4284.2', max_value=5.4)
        self.assertEqual(result, (False, 'Float outside of max bounds: 4284.200000.'))

    def test_min_value(self):
        result = daedalus.validation.validation.valid_float('3.4463', min_value=7.2)
        self.assertEqual(result, (False, 'Float outside of min bounds: 3.446300.'))

    def test_false(self):
        result = daedalus.validation.validation.valid_float('foobar')
        self.assertEqual(result, (False, 'Not a float: foobar.'))

    def test_false_precision(self):
        result = daedalus.validation.validation.valid_float('6.523', precision=1)
        self.assertEqual(result, (False, 'Precision does not match.'))
