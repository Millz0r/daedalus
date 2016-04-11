'''Stores all of the transforms for the different document formats.'''

import daedalus.exceptions
import json
import StringIO
import openpyxl
import xlrd

from daedalus.common import log_manager

def excel_to_json(data, pretty=False):
    '''Given an Excel representation of the data, it returns a JSON transformation of the data.'''
    excel_dict = {'sheets': []}
    workbook = xlrd.open_workbook(file_contents=data)
    for sheet in workbook.sheets():
        if sheet.nrows == 0:
            continue
        sheet_data = {'name': sheet.name, 'columns': sheet.row_values(0), 'rows': []}
        for row_index in range(1, sheet.nrows):
            sheet_data['rows'].append(sheet.row_values(row_index))
        excel_dict['sheets'].append(sheet_data)
    if pretty:
        return json.dumps(excel_dict, indent=2, separators=(',', ': '), sort_keys=True)
    else:
        return json.dumps(excel_dict, separators=(',', ':'))

def json_to_excel(data):
    '''Given a JSON representation of the data, it returns an Excel workbook.'''
    workbook = openpyxl.Workbook()
    jsondata = json.loads(data)
    current_sheet = workbook.active
    for sheet in jsondata['sheets']:
        current_sheet.title = sheet['name']

        current_sheet.append(sheet['columns']) # pylint: disable=E1101
        for row in sheet['rows']:
            if row is None:
                current_sheet.append([]) # pylint: disable=E1101
            elif isinstance(row, dict):
                current_sheet.append(process_json_row(sheet['columns'], row)) # pylint: disable=E1101
            else:
                current_sheet.append(row) # pylint: disable=E1101
        current_sheet = workbook.create_sheet()
    workbook.remove_sheet(current_sheet) # Kill the last sheet (it's always empty)
    data = StringIO.StringIO()
    workbook.save(data)
    return data.getvalue()

def process_json_row(columns, row):
    '''Helper function to process a row formatted as a JSON object.'''
    row_data = []
    for key, value in row.items():
        try:
            index = columns.index(key)
            row_data.append((index, value)) # Extra parens denote tuple.
        except ValueError:
            pass
    row_data.sort(key=lambda x: x[0])
    final_row_data = []
    current_index = 0
    item = row_data.pop(0)
    while True:
        if current_index == item[0]:
            final_row_data.append(item[1])
            try:
                item = row_data.pop(0)
            except IndexError:
                break
        elif current_index < item[0]:
            final_row_data.append(None)
        current_index += 1
    return final_row_data

def transform(data, source_format='excel', target_format='json', pretty=False):
    '''Main entrypoint of the transformer.'''
    log_manager.info('Transforming document into %s' % target_format)

    if  target_format == 'json':
        if source_format != 'excel':
            raise daedalus.exceptions.BadFileFormat('Need excel document to translate to JSON')
        return excel_to_json(data, pretty)
    elif target_format == 'excel':
        if source_format != 'json':
            raise daedalus.exceptions.BadFileFormat('Need JSON document to translate to excel')
        return json_to_excel(data)
