import argparse, os

argParser = argparse.ArgumentParser(
    prog = 'qbandas',
    description = 'Utility functions to setup qBandas calls'
)

argParser.add_argument("-c", "--create-schema", 
    action='store_true',
    help='Create a schema file from the specified data file. See -d and -s.',
)

argParser.add_argument("-d", "--data-file", 
    type=argparse.FileType('r'), 
    help="Path to the data file. Defaults to 'data.csv' in current working directory.",
    metavar="file"
)

argParser.add_argument('-s', '--schema-file', 
    type=argparse.FileType('w'), 
    help="Path to create schema file. Defaults to 'schema.json' in current working directory.",
    metavar="file"
)

args = argParser.parse_args()
if args.create_schema:
    print(args)
    data = args.data_file
    if not data:
        data = open(os.path.join(os.getcwd(), 'data.csv'), 'r')

    schema = args.schema_file
    if not schema:
        data = open(os.path.join(os.getcwd(), 'schema.json'), 'w')

