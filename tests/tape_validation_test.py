import StringIO
import unittest
from mock import patch

import daedalus.validation
from utils import validation_valid_excel, validation_invalid_type_excel, validation_invalid_required_excel

class TapeValidationTest(unittest.TestCase):
    def setUp(self):
        self.valid = daedalus.validation.tape_validation.TapeValidation(validation_valid_excel())
        self.invalid_type = daedalus.validation.tape_validation.TapeValidation(validation_invalid_type_excel())
        self.invalid_required = daedalus.validation.tape_validation.TapeValidation(validation_invalid_required_excel())
        self.valid._read_excel_metadata()
        self.invalid_type._read_excel_metadata()
        self.invalid_required._read_excel_metadata()

    def test_calculate_unit_count_valid(self):
        result = self.valid._calculate_unit_count()
        self.assertEqual(result, 25)

    def test_calculate_unit_count_invalid(self):
        result = self.invalid_required._calculate_unit_count()
        self.assertEqual(result, 'Error in unit fields.')

    def test_calculate_property_count_valid(self):
        result = self.valid._calculate_property_count()
        self.assertEqual(result, 4)

    def test_calculate_leased_count_valid(self):
        result = self.valid._calculate_leased_count()
        self.assertEqual(result, 3)

    def test_calculate_leased_count_invalid(self):
        result = self.invalid_required._calculate_leased_count()
        self.assertEqual(result, 'Error in leased fields.')

    def test_check_type_valid(self):
        result = self.valid._check_type()
        expected_result = []
        self.assertEqual(result, expected_result)

    def test_check_type_invalid_type(self):
        result = self.invalid_type._check_type()
        expected_result = [
            ((24, 1), 'Not an integer: FOO.'), ((24, 7), 'Invalid character or format.'), ((24, 8), 'Invalid character or format.'),
            ((24, 9), 'Invalid date.'), ((24, 18), 'Invalid date.'), ((24, 19), 'Invalid date.'), ((25, 3), 'Invalid character or format.'),
            ((25, 4), 'Invalid character or format.'), ((25, 5), 'Invalid character or format.'), ((25, 6), 'No such US state: NUL.'),
            ((26, 10), 'Invalid dollar value.'), ((26, 11), 'Invalid dollar value.'), ((26, 20), 'Invalid dollar value.'),
            ((26, 21), 'Invalid dollar value.'), ((26, 22), 'Invalid dollar value.'), ((26, 23), 'Invalid character or format.'),
            ((26, 24), 'Invalid dollar value.'), ((26, 25), 'Invalid dollar value.'), ((26, 26), 'Invalid dollar value.'),
            ((26, 27), 'Invalid dollar value.'), ((26, 28), 'Invalid dollar value.'), ((26, 29), 'Invalid dollar value.'),
            ((26, 31), 'Invalid dollar value.'), ((26, 32), 'Invalid dollar value.'), ((27, 1), 'Invalid numbering.'),
            ((27, 8), 'Invalid character or format.'), ((27, 23), 'Percentage outside 0-100 bounds.')]
        self.assertEqual(result, expected_result)

    def test_check_type_invalid_required(self):
        result = self.invalid_required._check_type()
        expected_result = [
            ((24, 3), 'Required cell is empty.'), ((24, 4), 'Required cell is empty.'), ((24, 5), 'Required cell is empty.'),
            ((24, 6), 'Required cell is empty.'), ((24, 7), 'Required cell is empty.'), ((25, 10), 'Required cell is empty.'),
            ((25, 21), 'Required cell is empty.'), ((25, 25), 'Required cell is empty.'), ((25, 26), 'Required cell is empty.'),
            ((26, 1), 'Invalid numbering.'), ((26, 2), 'Required cell is empty.'), ((26, 9), 'Required cell is empty.'),
            ((27, 16), 'Required cell is empty.'), ((27, 23), 'Required cell is empty.'), ((27, 29), 'Required cell is empty.'),
            ((27, 30), 'Required cell is empty.')]
        self.assertEqual(result, expected_result)

    def test_alter_document_valid(self):
        doc_problems = []
        expected_result = {'cell_styles': [((1, 1), 1)], 'cells': [((7, 4), 4), ((8, 4), 25), ((9, 4), 3)]}
        result = self.valid._alter_document(doc_problems)
        self.assertEqual(result, expected_result)

    def test_alter_document_invalid_type(self):
        doc_problems = [
            ((24, 1), 'Not an integer: FOO.'), ((24, 7), 'Invalid character or format.'), ((24, 8), 'Invalid character or format.'),
            ((24, 9), 'Invalid date.'), ((24, 18), 'Invalid date.'), ((24, 19), 'Invalid date.'), ((25, 3), 'Invalid character or format.'),
            ((25, 4), 'Invalid character or format.'), ((25, 5), 'Invalid character or format.'), ((25, 6), 'No such US state: NUL.'),
            ((26, 10), 'Invalid dollar value.'), ((26, 11), 'Invalid dollar value.'), ((26, 20), 'Invalid dollar value.'),
            ((26, 21), 'Invalid dollar value.'), ((26, 22), 'Invalid dollar value.'), ((26, 23), 'Invalid character or format.'),
            ((26, 24), 'Invalid dollar value.'), ((26, 25), 'Invalid dollar value.'), ((26, 26), 'Invalid dollar value.'),
            ((26, 27), 'Invalid dollar value.'), ((26, 28), 'Invalid dollar value.'), ((26, 29), 'Invalid dollar value.'),
            ((26, 31), 'Invalid dollar value.'), ((26, 32), 'Invalid dollar value.'), ((27, 1), 'Invalid numbering.'),
            ((27, 8), 'Invalid character or format.'), ((27, 23), 'Percentage outside 0-100 bounds.')]
        expected_result = {'cell_styles': [((1, 1), 0), ((24, 0), 3), ((24, 1), 2), ((24, 0), 3), ((24, 7), 2), ((24, 0), 3), ((24, 8), 2), ((24, 0), 3), ((24, 9), 2), ((24, 0), 3), ((24, 18), 2), ((24, 0), 3), ((24, 19), 2), ((25, 0), 3), ((25, 3), 2), ((25, 0), 3), ((25, 4), 2), ((25, 0), 3), ((25, 5), 2), ((25, 0), 3), ((25, 6), 2), ((26, 0), 3), ((26, 10), 2), ((26, 0), 3), ((26, 11), 2), ((26, 0), 3), ((26, 20), 2), ((26, 0), 3), ((26, 21), 2), ((26, 0), 3), ((26, 22), 2), ((26, 0), 3), ((26, 23), 2), ((26, 0), 3), ((26, 24), 2), ((26, 0), 3), ((26, 25), 2), ((26, 0), 3), ((26, 26), 2), ((26, 0), 3), ((26, 27), 2), ((26, 0), 3), ((26, 28), 2), ((26, 0), 3), ((26, 29), 2), ((26, 0), 3), ((26, 31), 2), ((26, 0), 3), ((26, 32), 2), ((27, 0), 3), ((27, 1), 2), ((27, 0), 3), ((27, 8), 2), ((27, 0), 3), ((27, 23), 2)], 'cells': [((24, 0), '1: Not an integer: FOO.; 7: Invalid character or format.; 8: Invalid character or format.; 9: Invalid date.; 18: Invalid date.; 19: Invalid date.'), ((25, 0), '3: Invalid character or format.; 4: Invalid character or format.; 5: Invalid character or format.; 6: No such US state: NUL.'), ((26, 0), '10: Invalid dollar value.; 11: Invalid dollar value.; 20: Invalid dollar value.; 21: Invalid dollar value.; 22: Invalid dollar value.; 23: Invalid character or format.; 24: Invalid dollar value.; 25: Invalid dollar value.; 26: Invalid dollar value.; 27: Invalid dollar value.; 28: Invalid dollar value.; 29: Invalid dollar value.; 31: Invalid dollar value.; 32: Invalid dollar value.'), ((27, 0), '1: Invalid numbering.; 8: Invalid character or format.; 23: Percentage outside 0-100 bounds.'), ((1, 1), '24, 25, 26, 27'), ((7, 4), 4), ((8, 4), 24), ((9, 4), 3)]}
        result = self.invalid_type._alter_document(doc_problems)
        self.assertEqual(result, expected_result)

    def test_alter_document_invalid_required(self):
        doc_problems = [
            ((24, 3), 'Required cell is empty.'), ((24, 4), 'Required cell is empty.'), ((24, 5), 'Required cell is empty.'),
            ((24, 6), 'Required cell is empty.'), ((24, 7), 'Required cell is empty.'), ((25, 10), 'Required cell is empty.'),
            ((25, 21), 'Required cell is empty.'), ((25, 25), 'Required cell is empty.'), ((25, 26), 'Required cell is empty.'),
            ((26, 1), 'Invalid numbering.'), ((26, 2), 'Required cell is empty.'), ((26, 9), 'Required cell is empty.'),
            ((27, 16), 'Required cell is empty.'), ((27, 23), 'Required cell is empty.'), ((27, 29), 'Required cell is empty.'),
            ((27, 30), 'Required cell is empty.')]
        expected_result = {'cell_styles': [((1, 1), 0), ((24, 0), 3), ((24, 3), 2), ((24, 0), 3), ((24, 4), 2), ((24, 0), 3), ((24, 5), 2), ((24, 0), 3), ((24, 6), 2), ((24, 0), 3), ((24, 7), 2), ((25, 0), 3), ((25, 10), 2), ((25, 0), 3), ((25, 21), 2), ((25, 0), 3), ((25, 25), 2), ((25, 0), 3), ((25, 26), 2), ((26, 0), 3), ((26, 1), 2), ((26, 0), 3), ((26, 2), 2), ((26, 0), 3), ((26, 9), 2), ((27, 0), 3), ((27, 16), 2), ((27, 0), 3), ((27, 23), 2), ((27, 0), 3), ((27, 29), 2), ((27, 0), 3), ((27, 30), 2)], 'cells': [((24, 0), '3: Required cell is empty.; 4: Required cell is empty.; 5: Required cell is empty.; 6: Required cell is empty.; 7: Required cell is empty.'), ((25, 0), '10: Required cell is empty.; 21: Required cell is empty.; 25: Required cell is empty.; 26: Required cell is empty.'), ((26, 0), '1: Invalid numbering.; 2: Required cell is empty.; 9: Required cell is empty.'), ((27, 0), '16: Required cell is empty.; 23: Required cell is empty.; 29: Required cell is empty.; 30: Required cell is empty.'), ((1, 1), '24, 25, 26, 27'), ((7, 4), 4), ((8, 4), 'Error in unit fields.'), ((9, 4), 'Error in leased fields.')]}
        result = self.invalid_required._alter_document(doc_problems)
        self.assertEqual(result, expected_result)

class ValidationTest(unittest.TestCase):
    def test_parse_args(self):
        args = daedalus.validation.application.parse_args([])
        self.assertTrue(isinstance(args.infile, file))
        self.assertEqual(args.infile.mode, 'r')
        self.assertTrue(isinstance(args.outfile, StringIO.StringIO))

    def test_validate_valid(self):
        doc_excel = validation_valid_excel()
        expected_result = "{'cell_styles': [((1, 1), 1)], 'cells': [((7, 4), 4), ((8, 4), 25), ((9, 4), 3)]}"

        result = daedalus.validation.validate(doc_excel)
        self.assertEqual(result, expected_result)

    def test_validate_invalid_type(self):
        doc_excel = validation_invalid_type_excel()
        expected_result = "{'cell_styles': [((1, 1), 0), ((24, 0), 3), ((24, 1), 2), ((24, 0), 3), ((24, 7), 2), ((24, 0), 3), ((24, 8), 2), ((24, 0), 3), ((24, 9), 2), ((24, 0), 3), ((24, 18), 2), ((24, 0), 3), ((24, 19), 2), ((25, 0), 3), ((25, 3), 2), ((25, 0), 3), ((25, 4), 2), ((25, 0), 3), ((25, 5), 2), ((25, 0), 3), ((25, 6), 2), ((26, 0), 3), ((26, 10), 2), ((26, 0), 3), ((26, 11), 2), ((26, 0), 3), ((26, 20), 2), ((26, 0), 3), ((26, 21), 2), ((26, 0), 3), ((26, 22), 2), ((26, 0), 3), ((26, 23), 2), ((26, 0), 3), ((26, 24), 2), ((26, 0), 3), ((26, 25), 2), ((26, 0), 3), ((26, 26), 2), ((26, 0), 3), ((26, 27), 2), ((26, 0), 3), ((26, 28), 2), ((26, 0), 3), ((26, 29), 2), ((26, 0), 3), ((26, 31), 2), ((26, 0), 3), ((26, 32), 2), ((27, 0), 3), ((27, 1), 2), ((27, 0), 3), ((27, 8), 2), ((27, 0), 3), ((27, 23), 2)], 'cells': [((24, 0), u'1: Not an integer: FOO.; 7: Invalid character or format.; 8: Invalid character or format.; 9: Invalid date.; 18: Invalid date.; 19: Invalid date.'), ((25, 0), u'3: Invalid character or format.; 4: Invalid character or format.; 5: Invalid character or format.; 6: No such US state: NUL.'), ((26, 0), '10: Invalid dollar value.; 11: Invalid dollar value.; 20: Invalid dollar value.; 21: Invalid dollar value.; 22: Invalid dollar value.; 23: Invalid character or format.; 24: Invalid dollar value.; 25: Invalid dollar value.; 26: Invalid dollar value.; 27: Invalid dollar value.; 28: Invalid dollar value.; 29: Invalid dollar value.; 31: Invalid dollar value.; 32: Invalid dollar value.'), ((27, 0), '1: Invalid numbering.; 8: Invalid character or format.; 23: Percentage outside 0-100 bounds.'), ((1, 1), '24, 25, 26, 27'), ((7, 4), 4), ((8, 4), 24), ((9, 4), 3)]}"

        result = daedalus.validation.validate(doc_excel)
        self.assertEqual(result, expected_result)

    def test_validate_invalid_required(self):
        doc_excel = validation_invalid_required_excel()
        expected_result = "{'cell_styles': [((1, 1), 0), ((24, 0), 3), ((24, 3), 2), ((24, 0), 3), ((24, 4), 2), ((24, 0), 3), ((24, 5), 2), ((24, 0), 3), ((24, 6), 2), ((24, 0), 3), ((24, 7), 2), ((25, 0), 3), ((25, 10), 2), ((25, 0), 3), ((25, 21), 2), ((25, 0), 3), ((25, 25), 2), ((25, 0), 3), ((25, 26), 2), ((26, 0), 3), ((26, 1), 2), ((26, 0), 3), ((26, 2), 2), ((26, 0), 3), ((26, 9), 2), ((27, 0), 3), ((27, 16), 2), ((27, 0), 3), ((27, 23), 2), ((27, 0), 3), ((27, 29), 2), ((27, 0), 3), ((27, 30), 2)], 'cells': [((24, 0), '3: Required cell is empty.; 4: Required cell is empty.; 5: Required cell is empty.; 6: Required cell is empty.; 7: Required cell is empty.'), ((25, 0), '10: Required cell is empty.; 21: Required cell is empty.; 25: Required cell is empty.; 26: Required cell is empty.'), ((26, 0), '1: Invalid numbering.; 2: Required cell is empty.; 9: Required cell is empty.'), ((27, 0), '16: Required cell is empty.; 23: Required cell is empty.; 29: Required cell is empty.; 30: Required cell is empty.'), ((1, 1), '24, 25, 26, 27'), ((7, 4), 4), ((8, 4), 'Error in unit fields.'), ((9, 4), 'Error in leased fields.')]}"

        result = daedalus.validation.validate(doc_excel)
        self.assertEqual(result, expected_result)

    def test_main(self):
        with patch('daedalus.validation.validate') as validate_mock:
            with patch('daedalus.validation.application.parse_args') as parse_mock:
                daedalus.validation.application.main()
                parse_mock.assert_called()
                validate_mock.assert_called()
