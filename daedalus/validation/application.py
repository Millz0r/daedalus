'''Runs the document validation service as a command line tool.'''

import sys

import daedalus.validation

DESCRIPTION = 'Validates Excel data with tape portfolio.'

def parse_args(args):
    '''Parses the command line arguments.'''
    import argparse
    argparser = argparse.ArgumentParser(description=DESCRIPTION)
    argparser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    argparser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    return argparser.parse_args(args)

def main():
    '''Entry point from the command line. Parses arguments and calls validate.'''
    args = parse_args(sys.argv[1:])
    input_data = args.infile.read()
    output_data = daedalus.validation.validate(input_data)
    args.outfile.write(output_data)
