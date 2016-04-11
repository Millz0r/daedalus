'''Runs the document translation service as a command line tool.'''

import sys

import daedalus.xlstransform

DESCRIPTION = 'Transforms xls and xlsx formats to json, or json to xlsx.'

def parse_args(args):
    '''Parses the command line arguments.'''
    import argparse

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    return parser.parse_args(args)

def main():
    '''Entry point from the command line. Parses arguments and calls main.'''
    args = parse_args(sys.argv[1:])
    input_data = args.infile.read()
    if daedalus.xlstransform.utils.is_json(input_data):
        target_format = 'excel'
    else:
        target_format = 'json'
    output_data = daedalus.xlstransform.transform(input_data, target_format=target_format, pretty=True)
    args.outfile.write(output_data)
