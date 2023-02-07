import argparse, os, pathlib
import pandas as pd
from __init__ import write_schema

argParser = argparse.ArgumentParser(
    prog = 'qbandas',
    description = 'Utility functions to setup qBandas calls'
)

argParser.add_argument("-c", "--create-schema", 
    action='store_true',
    help='Create a schema file from the specified data file. See -d and -s.',
)

argParser.add_argument("-d", "--data-file", 
    type=pathlib.Path, 
    help="""Path to the data file. Defaults to 'data.csv' in current working directory. Only supports general delimited files (.csv, .tsv, etc.).""",
    metavar="file"
)

argParser.add_argument('-s', '--schema-file', 
    type=pathlib.Path, 
    help="Path to create schema file. Defaults to 'schema.json' in current working directory.",
    metavar="file"
)

argParser.add_argument('--delim',  
    help="The delimiter of the data file. Defaults to ','.",
    choices=[',', '\t', ' ', ';', '|'],
    default=',',
    metavar="delimiter"
)

argParser.add_argument("-t", "--col-types", 
    action='store_true',
    help='Create a schema file from the specified data file. See -d and -s.',
)

args = argParser.parse_args()
if args.create_schema:

    data_path = args.data_file
    if not data_path:
        data_path = os.path.join(os.getcwd(), 'data.csv')
    with open(data_path, 'r') as f:
        df = pd.read_table(data_path, delimiter=args.delim)

    schema_path = args.schema_file
    if not schema_path:
        schema_path = open(os.path.join(os.getcwd(), 'schema.json'), 'a')
    with open(schema_path, 'a') as f:
        write_schema(df, f)
    exit()
    
if args.col_types:
    import config
    from textwrap import fill
    out = "data-type: desc\n" + ('-'*80) + '\n'
    for key in config.field_types:
        out += fill(f"-{key}: " + config.field_types[key], 80, subsequent_indent="\t") + '\n'
    print(out, end='')
    exit()
