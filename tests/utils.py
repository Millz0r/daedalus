from cStringIO import StringIO
import json
import os.path

here = os.path.abspath(os.path.dirname(__file__))
data = os.path.join(here, '../data')
test_data = os.path.join(data, 'test')

def is_json(data):
    try:
        json.loads(data)
    except ValueError:
        return False
    return True

def to_json(data):
    return json.loads(data)

def xls_data(raw=False):
    with open(os.path.join(test_data, 'test.xls'), 'rb') as f:
        return f.read()

def xlsx_data(raw=False):
    with open(os.path.join(test_data, 'test.xlsx'), 'rb') as f:
        return f.read()

def json_xls_data(raw=False, minimized=False):
    file_name = 'test.xls.min.json' if minimized else 'test.xls.json'
    with open(os.path.join(test_data, file_name), 'rb') as f:
        if raw:
            return f.read()
        else:
            return to_json(f.read())

def json_xlsx_data(raw=False, minimized=False):
    file_name = 'test.xlsx.min.json' if minimized else 'test.xlsx.json'
    with open(os.path.join(test_data, file_name), 'rb') as f:
        if raw:
            return f.read()
        else:
            return to_json(f.read())

def json_corner_data(raw=False):
    with open(os.path.join(test_data, 'test_corner_cases.json'), 'rb') as f:
        if raw:
            return f.read()
        else:
            return to_json(f.read())

def json_object_notation(raw=False):
    with open(os.path.join(test_data, 'test_object_notation.json'), 'rb') as f:
        if raw:
            return f.read()
        else:
            return to_json(f.read())
            
def valuation_workbook():
    with open(os.path.join(test_data, 'real_properties_test.xlsx'), 'rb') as f:
        return f.read()

def valuation_workbook_path():
    return os.path.join(test_data, 'real_properties_test.xlsx')

def valuation_solution():
    with open(os.path.join(test_data, 'real_properties_test_result.json'), 'rb') as f:
        return f.read()

def valuation_workbook_two():
    with open(os.path.join(test_data, 'real_properties_test_params.xlsx'), 'rb') as f:
        return f.read()

def validation_valid_excel():
    with open(os.path.join(test_data, 'validation_mock_valid.xlsx'), 'rb') as f:
        return f.read()

def validation_invalid_type_excel():
    with open(os.path.join(test_data, 'validation_mock_invalid_type.xlsx'), 'rb') as f:
        return f.read()

def validation_invalid_required_excel():
    with open(os.path.join(test_data, 'validation_mock_invalid_required.xlsx'), 'rb') as f:
        return f.read()
