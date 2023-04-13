"""
CLI for qBandas.
"""

import argparse
from textwrap import fill

from .config import field_types
from .schema import pull_schema

argParser = argparse.ArgumentParser(
    prog = 'qbandas',
    description = 'CLI for qBandas.'
    )
argParser.add_argument("-t", "--col-types", 
    action='store_true',
    help='List the colmn types and their arguments.',
    )
argParser.add_argument("--head",
    action='store_true',
    help='Create an empty header file in the current working directory.'
    )   
argParser.add_argument("-s", "--schema",
    help='Pull a schema from QuickBase.',
    metavar="DBID",
    nargs=1,
    type=str,
    dest="DBID"
    )
argParser.add_argument("--test", 
    action='store_true',
    help='Run unit tests',
    )
args = argParser.parse_args()
    
if args.col_types:
    out = "data types:\n"
    for key in field_types:
        stub = f"  -{key}"
        gap = ' '*(16 - len(stub)) if len(stub) < 16 else '\n\t\t'
        out += stub + gap + fill(field_types[key]['desc'], 80, subsequent_indent="\t\t") + '\n'
    print(out, end='')
    exit()

if args.head:
    pass

if args.DBID:
    pull_schema(*args.DBID)

if args.test:
    import doctest
    from . import headers
    doctest.testmod(headers)