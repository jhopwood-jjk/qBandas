"""
TODO refactor this. PEP 8?
Configures the types of columns supported by qbandas.
"""

from json import (
    load
)

from os.path import (
    join,
    dirname,
    realpath
)

from .pack import (
    _pack_funcs
)

# field_types is the raw json to dict
here = dirname(realpath(__file__))
with open(join(here, 'data', 'field_types.json')) as f:
    field_types = load(f)

# resolve the packing functions
for t in field_types:
    if field_types[t]["pack"]:
        field_types[t]["pack"] = _pack_funcs[field_types[t]["pack"]]