import argparse, os, pathlib
import pandas as pd

from .schema import write_schema
from .config import field_types
from textwrap import fill

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
    help='List the colmn types and their arguments.',
)

args = argParser.parse_args()
if args.create_schema:

    data_path = args.data_file
    if not data_path:
        data_path = os.path.join(os.getcwd(), 'data.csv')
    df = pd.read_table(data_path, delimiter=args.delim)

    schema_path = args.schema_file
    if not schema_path:
        schema_path = os.path.join(os.getcwd(), 'schema.json')
    write_schema(df, schema_path)
    
    exit()
    
if args.col_types:
    out = "data types:\n"
    for key in field_types:
        stub = f"  -{key}"
        gap = ' '*(16 - len(stub)) if len(stub) < 16 else '\n\t\t'
        out += stub + gap + fill(field_types[key], 80, subsequent_indent="\t\t") + '\n'
    print(out, end='')
    exit()
