"""
CLI for qBandas.
"""

import argparse
from textwrap import fill

from .config import field_types

argParser = argparse.ArgumentParser(
    prog = 'qbandas',
    description = 'CLI for qBandas.'
)

argParser.add_argument("-t", "--col-types", 
    action='store_true',
    help='List the colmn types and their arguments.',
)

argParser.add_argument("-h", "--head",
    action='store_true',
    help='Create an empty header file in the current working directory.'
)

# TODO implement
argParser.add_argument("-s", "--schema",
    help='Pull a schema from QuickBase. (Not implemented)'
)

args = argParser.parse_args()
    
if args.col_types:
    out = "data types:\n"
    for key in field_types:
        stub = f"  -{key}"
        gap = ' '*(16 - len(stub)) if len(stub) < 16 else '\n\t\t'
        out += stub + gap + fill(field_types[key], 80, subsequent_indent="\t\t") + '\n'
    print(out, end='')
    exit()

if args.head:
    with open('headers.json', 'w') as f:
        f.write('{\n\t"QB-Realm-Hostname": "{QB-Realm-Hostname}",\n\t"User-Agent": "{User-Agent}",\n\t"Authorization": "{Authorization}\n"}')