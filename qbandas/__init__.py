"""
Integrates the popular data handling library Pandas and the QuickBase API.
"""

__all__ = [ 
    'headers',
    'schema',
    ]

from . import headers
from . import schema

# scoped setup functions to avoid cluttering qbandas package 
def setup1():
    '''
    Create field types dict by reading in ./data/field_types.json and resolving the packing functions
    '''

    import json
    from os.path import dirname, join, realpath
    from .pack import PACKING_FUNCS

    # field_types is the raw json to dict
    here = dirname(realpath(__file__))
    with open(join(here, 'data', 'field_types.json')) as f:
        field_types = json.load(f)

    # resolve the packing functions
    for t in field_types:
        if field_types[t]["pack"]:
            field_types[t]["pack"] = PACKING_FUNCS[field_types[t]["pack"]]
    
    return field_types
FIELD_TYPES = setup1()


