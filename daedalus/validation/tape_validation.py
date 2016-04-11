'''Tape validation for data in Excel format.'''

import sys
import re
import string
import json
import StringIO

from xlutils.copy import copy
from xlrd import open_workbook
from xlwt import easyxf

from daedalus.common import log_manager
from daedalus.xlstransform.transforms import excel_to_json
from daedalus.validation.validation import valid_date, valid_percentage, valid_dollar, valid_year, valid_address, valid_city, valid_county, valid_zip_code,\
                                           valid_us_state, valid_estimate_source, valid_leasing_status, valid_class_of_space, valid_integer, valid_float

class TapeValidation(object): # pylint: disable=too-few-public-methods
    '''Tape validation class. Initialize using Excel document and use run() to validate.'''

    # Supported types of cell borders.
    _BG_RED, _BG_GREEN, _BD_RED, _BD_RIGHT_RED = range(4)
    # Offset between Excel row numbering and JSON data. 1 for deleted 1st row in excel_to_json and 1 for 0-based numbering.
    _EXCEL_ROW_OFFSET = 2
    # Offset between Excel col numbering and JSON data. 1 for 0-based numbering.
    # TODO: keep this 0 for now, before breaking all other tests. Change to 1 before finishing write_to_excel. # pylint: disable=fixme
    _EXCEL_COL_OFFSET = 0
    # Mapping between Excel values and validator functions.
    _VALIDATOR_MAP = {
        u'ADDRESS': valid_address, # Address
        u'CITY': valid_city, # City
        u'CLASS_OF_SPACE': valid_class_of_space, # Class of Space
        u'COUNTY': valid_county, # County
        u'DATE': valid_date, # Renovation Date
        u'DOLLAR': valid_dollar, # Acquisition Price
        u'ESTIMATE_SOURCE': valid_estimate_source, # Owner Estimate Source
        u'FLOAT': valid_float, # Baths
        u'INTEGER': valid_integer, # #
        u'LEASING_STATUS': valid_leasing_status, # Lease Status
        u'PERCENTAGE': valid_percentage, # Management Fee
        u'US_STATE': valid_us_state, # State
        u'YEAR': valid_year, # Year Built
        u'ZIP_CODE': valid_zip_code # Zip Code
    }

    def __init__(self, input_doc):
        '''Add variables for document as Excel and dict.'''
        self.input_excel = input_doc
        self.input_dict = json.loads(excel_to_json(self.input_excel))['sheets'][0]['rows']
        self.metadata = {}
        self.validators = []
        self.mandatory_fields = []

    def _get_excel_tuple(self, excel_string): # pylint: disable=no-self-use
        '''Extract coordinate 0-based tuple from Excel numbering.'''
        pattern = '(\d+)([A-Z]+)' # pylint: disable=anomalous-backslash-in-string
        result = re.findall(pattern, excel_string)
        try:
            # Note - we add 1 to these results because we want to keep Excel 1-based system variables in hidden sheet.
            ret = (int(result[0][0]), string.ascii_uppercase.index(result[0][1]) + 1)
        except (ValueError, IndexError):
            log_manager.info('Invalid Excel metadata. Aborting.')
            sys.exit(0)
        return ret

    def _read_excel_metadata(self):
        '''Reads the metadata from the 'Map' sheet and saves it as dict. Also creates validators dict.'''
        # Reinitialise vars.
        self.metadata = {}
        self.validators = []
        self.mandatory_fields = []
        # Find the sheet called 'Map'
        input_json = json.loads(excel_to_json(self.input_excel))
        input_hidden_dict = []
        for sheet in input_json['sheets']:
            if sheet['name'] == u'Map':
                input_hidden_dict = sheet['rows']
                break
        try:
            # Row where the actual data start (eg. after data examples). 1st row is empty and is skipped in JSON.
            self.metadata['base_row'] = int(input_hidden_dict[0][2]) - self._EXCEL_ROW_OFFSET
            # Column where actual data start (eg. offset by 'Example Single Unit').
            self.metadata['base_column'] = string.ascii_uppercase.index(input_hidden_dict[0][3])
            # Column for validator error comments.
            self.metadata['comment_column'] = string.ascii_uppercase.index(input_hidden_dict[0][4])
            # Position of unit count column.
            self.metadata['unit_count_column'] = string.ascii_uppercase.index(input_hidden_dict[0][5])
            # Position of leased count column.
            self.metadata['leased_count_column'] = string.ascii_uppercase.index(input_hidden_dict[0][6])
            # Position of numbering column.
            self.metadata['identifier_column'] = string.ascii_uppercase.index(input_hidden_dict[0][7])
            # Coordinates of the total property count cell.
            self.metadata['property_count_field'] = self._get_excel_tuple(input_hidden_dict[0][8])
            # Coordinates of the total unit count cell.
            self.metadata['unit_count_field'] = self._get_excel_tuple(input_hidden_dict[0][9])
            # Coordinates of the total leased count cell.
            self.metadata['leased_count_field'] = self._get_excel_tuple(input_hidden_dict[0][10])
            # Coordinates of the total corporate debt cell.
            self.metadata['corporate_debt_field'] = self._get_excel_tuple(input_hidden_dict[0][11])
            # Coordinates of the status field.
            self.metadata['status_field'] = self._get_excel_tuple(input_hidden_dict[0][12])
            # Read data types for each column, set the validator function and whether it's mandatory.
            for i in range(0, len(input_hidden_dict)):
                validator_id = input_hidden_dict[i][0]
                self.validators.append(self._VALIDATOR_MAP[validator_id])
                if input_hidden_dict[i][1]:
                    self.mandatory_fields.append(True)
                else:
                    self.mandatory_fields.append(False)
        except (ValueError, IndexError):
            log_manager.info('Invalid Excel metadata. Aborting.')
            sys.exit(0)

    def _required_field(self, field, column):
        '''Check if a required field is not empty.'''
        if field == u'':
            if self.mandatory_fields[column]:
                return (False, 'Required cell is empty.')
            else:
                # Empty optional cells use this special output.
                return (False, None)
        return (True, None)

    def _calculate_unit_count(self):
        '''Get total number of property units.'''
        # Check that the unit count column exists, is not empty and is either floats or ints.
        unit_col = self.metadata['unit_count_column']
        try:
            if not all([row[unit_col] != u'' and (isinstance(row[unit_col], float) or isinstance(row[unit_col], int))
                        for row in self.input_dict[self.metadata['base_row']:]]):
                raise ValueError
        except (IndexError, ValueError):
            return 'Error in unit fields.'
        # Sum all unit cell values.
        total = sum([int(row[unit_col]) for row in self.input_dict[self.metadata['base_row']:]])
        return total

    def _calculate_property_count(self):
        '''Get total number of properties.'''
        return len(self.input_dict) - self.metadata['base_row']

    def _calculate_leased_count(self):
        '''Get total number of leased properties.'''
        leased_col = self.metadata['leased_count_column']
        # Check that the leased status column exists and is not empty.
        try:
            if not all([row[leased_col] != u'' for row in self.input_dict[self.metadata['base_row']:]]):
                raise ValueError
        except (IndexError, ValueError):
            return 'Error in leased fields.'
        # Sum all leased cells with LEASED or LEASED - M2M status.
        total = sum([row[leased_col].upper() == 'LEASED' or row[leased_col].upper() == 'LEASED - M2M'
                     for row in self.input_dict[self.metadata['base_row']:]])
        return total

    def _check_type(self):
        '''Perform type validation for relevant cells of the input Excel document. Return list of problems.'''
        # Extract field metadata from Excel document first.
        self._read_excel_metadata()
        problems = []
        # Check all cell fields for validity. Iterate from start of actual data.
        for row in range(self.metadata['base_row'], len(self.input_dict)):
            # Check for proper numbering in # field. Excel uses 1-based system.
            try:
                if int(self.input_dict[row][self.metadata['identifier_column']]) != row - self.metadata['base_row'] + 1:
                    problems.append(((row + self._EXCEL_ROW_OFFSET, self.metadata['identifier_column']), 'Invalid numbering.'))
            except ValueError:
                pass
            for col in range(0, len(self.validators)):
                data_cell = self.input_dict[row][self.metadata['base_column'] + col]
                result, error = self._required_field(data_cell, col)
                if not result:
                    if error:
                        problems.append(((row + self._EXCEL_ROW_OFFSET, self.metadata['base_column'] + col + self._EXCEL_COL_OFFSET), error))
                    # Skip validation of empty cells.
                    continue
                # Check if all records are of valid type.
                validate_func = self.validators[col]
                result, error = validate_func(data_cell)
                if not result:
                    problems.append(((row + self._EXCEL_ROW_OFFSET, self.metadata['base_column'] + col + self._EXCEL_COL_OFFSET), error))
        return problems

    def _alter_document(self, problems):
        '''Transform the Excel document relative to type validation errors. Return the modified Excel document.'''
        cell_updates = []
        error_rows = []
        if problems:
            for (row, col), error in problems:
                # First item in row gets right border.
                cell_updates.append(((row, 0), None, self._BD_RIGHT_RED))
                # Invalidated field gets full border.
                cell_updates.append(((row, col), None, self._BD_RED))
            # Iterate over unique rows from problems list.
            for cur_row in list(set([row for (row, col), error in problems])):
                row_problems = ['%d: %s' % (col, error) for ((row, col), error) in problems if row == cur_row]
                if row_problems:
                    # Add col and the error message to the comment field.
                    cell_updates.append(((cur_row, self.metadata['comment_column']), '; '.join(row_problems), None))
                    error_rows.append(cur_row)
            # Add row numbers of invalid cells to the status field and updated status field to red.
            cell_updates.append((self.metadata['status_field'], ', '.join([str(x) for x in error_rows]), self._BG_RED))
        else:
            # Return the same document, only alter status field.
            cell_updates = [(self.metadata['status_field'], 'Valid', self._BG_GREEN)]
        # Add total counts.
        cell_updates.append((self.metadata['property_count_field'], self._calculate_property_count(), None))
        cells.append((self.metadata['unit_count_field'], self._calculate_unit_count(), None))
        cells.append((self.metadata['leased_count_field'], self._calculate_leased_count(), None))
        # Transform the input document.
        output_data = self._write_to_excel(cell_updates)
        return output_data

    def _write_to_excel(self, alter_cells):
        '''Given input Excel document, the cells and their styles to be altered, produce a new Excel document.'''
        # Read-only copy to duplicate and get old values from.
        rb = open_workbook(file_contents=self.input_excel, formatting_info=True)
        r_sheet = rb.sheet_by_index(0)
        # Writable copy (can't read values from this one).
        wb = copy(rb)
        w_sheet = wb.get_sheet(0)
        # Save new cell styles.
        for ((row, col), value, style) in alter_cells:
            xfstyle = None
            if style == _BG_RED:
                xfstyle = xlwt.easyxf("background: pattern solid, color red; font: color white;")
            elif style == _BG_GREEN:
                xfstyle = xlwt.easyxf("background: pattern solid, color green; font: color white;")
            elif style == _BD_RED:
                xfstyle = xlwt.easyxf("border: pattern solid, color green, size 1px;")
            elif style == _BD_RIGHT_RED:
                xfstyle = xlwt.easyxf("border-right: pattern solid, color green, size 5px;")
            # See if we need to set a value.
            if value == None:
                value = r_sheet.cell(row, col).value
            w_sheet.write(row, col, value, xfstyle)
        # Save the workbook to a stream object.
        output_stream = StringIO.StringIO()
        wb.save(output_stream)
        return output_stream.getvalue()

    def run(self):
        '''Run the tape validation process.'''
        # Perform type validation.
        log_manager.info('Tape validating document.')
        errors = self._check_type()
        if errors:
            log_manager.info('Document failed tape validation. List of errors:\n%s.' % str(errors))
        else:
            log_manager.info('Document successfully tape validated.')
        # Transform the Excel document to reflect on its validity.
        output_data = self._alter_document(errors)
        return output_data


def validate(input_excel):
    '''Main entrypoint of the validator.'''
    validator = TapeValidation(input_excel)
    output_data = validator.run()
    return output_data
