'''
Methods that deal with handling local copies of QuickBase tables' 
schemas.

Everytime you want to upload or fetch records on QuickBase, you must
have a valid schema for the table. 

Arguments
---------
Field arguments for the schema are used to tell qbandas how to parse
the incoming/outgoing data. You can set field arguments using 
`add_schema_args()` and `set_schema_args()`.

For help creating datetime format strings, see 
[here](https://www.programiz.com/python-programming/datetime/strftime) 
and [here](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior).

| Field Type | Supported arguments                                     |
| ---------- | ------------------------------------------------------- |
| duration   | unit : str, either 'seconds' or 'milliseconds'          |
| date       | format : str, datetime format string                    |
| datetime   | format : str, datetime format string                    |


'''

import json
import os
import os.path as op
import re

import requests

from ._constants import QB_PATH, USER_PATH
from .profiles import _get_headers, is_valid_profile

try: os.makedirs(op.join(USER_PATH, 'schemas'))
except FileExistsError: pass
        

def fetch_schema(dbid: str, profile: str, table_name: str = None):
    '''
    Download a local copy of a table's structure from a QuickBase 
    application.

    Parameters
    ----------
    dbid : str
        The unique identifier of the table in QuickBase.
    profile : str
        The profile to authorize this request
    table_name : str, optional
        The name of the table. None uses the dbid, by default None

    '''

    headers = _get_headers(profile)
    if not is_valid_profile(profile, talk = True):
        raise ValueError(f'unusable profile {profile}')

    # send the request to quickbase
    r = requests.get('https://api.quickbase.com/v1/fields', 
                    params = {
                        'tableId': dbid, 
                        'includeFieldPerms': "false"
                    }, 
                    headers = headers)
    r.raise_for_status()

    # get the address subfields
    with open(op.join(QB_PATH, 'data', 'address-fields.json')) as f:        
        address_fields = json.load(f)

    # parse the schema from the response
    fields = dict()
    for item in r.json():
        
        type_ = item['fieldType']
        id_ = item['id']
        label_ = item['label']
        
        # address fields send extra unlabeled info that we cannot use. 
        # remove it.
        if label_ in address_fields['junk-names']:
            continue
        
        fields[label_] = {'id': id_, 'type': type_}

        # recreate subfields for adresses with propper names
        if type_ == 'address':
            for sufix, fid_offset in address_fields["suffixes"].items():
                fields[label_ + sufix] = {
                    'id': id_ + fid_offset,
                    'type': "text"
                }

    _write_schema(table_name, dbid, fields)
    
def list_schemas() -> list[str]:
    '''
    List the names of all the usable schemas.

    The names are 'table_names'

    Returns
    -------
    list[str]
        The names of all the usable schemas
    '''
    schema_path = op.join(USER_PATH, 'schemas')
    names = [re.sub(r'\.json', '', x) for x in os.listdir(schema_path)]
    return names

def _read_schema(table_name: str) -> tuple[str, dict]:
    '''
    Read in a schema

    Returns the information if the schema exists
    
    Parameters
    ----------
    table_name : str
        The name of the table to get the schema for

    Returns
    -------
    tuple[str, dict]
        The dbid of the table followed by the field information if the 
        schem exists. If it doesn't exist, you get (None, dict())
    '''
    
    schema_path = op.join(USER_PATH, 'schemas', table_name + '.json')
    if not op.exists(schema_path):
        return None, {}
    with open(schema_path) as f:
        data = json.load(f)
        return data['dbid'], data['fields']
        
def _write_schema(table_name: str, dbid: str, fields: dict):
    '''
    Write a schema to disk

    For internal use

    Parameters
    ----------
    table_name : str
        The name of the schema to write
    dbid : str
        The database ID of the QuickBase table
    fields : dict
        A dictonary of fields and their metadata
    '''
    schema_path = op.join(USER_PATH, 'schemas', table_name + '.json')
    with open(schema_path, 'w') as f:
        data = {'dbid': dbid, 'fields': fields}
        json.dump(data, f)
    
def add_schema_args(table_name: str, fields: list = None, 
                    arguments: dict = None, *fields_, **arguments_):
    '''
    Add arguments to a table's schema

    Will append to the schema and override any existing arguments with 
    the same name

    Parameters
    ----------
    table_name : str
        The table to update
    fields : list
        The field names to update, by default None
    arguments : dict
        The arguments to add, by default None
    '''

    # read in the schema
    dbid, schema = _read_schema(table_name)
    if not dbid: raise ValueError(f'table {table_name} does not exist')

    fields = (fields if fields else []) + fields_
    arguments = (arguments if arguments else {}) | arguments_
    
    # append the new arguments
    for field in fields:
        if field not in schema:
            raise ValueError(f"The field {field} is not in the schema"
                             f"{table_name}.")
        current = schema[field].get('args', {})
        schema[field]['args'] = current | arguments

    # put the schema pack into the file
    _write_schema(table_name, dbid, fields)

def set_schema_args(table_name: str, fields: list = None, 
                    arguments: dict = None, *fields_, **arguments_):
    '''
    Set the arguments for some fields in a given schema

    Parameters
    ----------
    table_name : str
        The nameof the table to configure
    fields : list, optional
        The fields to configure, by default None
    arguments : dict, optional
        The arguments to add, by default None
    '''

    # read in the schema
    dbid, schema = _read_schema(table_name)
    if not dbid: raise ValueError(f'table {table_name} does not exist')

    fields = (fields if fields else []) + fields_
    arguments = (arguments if arguments else {}) | arguments_
    
    # append the new arguments
    for field in fields:
        if field not in schema:
            raise ValueError(f"The field {field} is not in the schema"
                             f"{table_name}.")
        schema[field]['args'] = arguments

    # put the schema pack into the file
    _write_schema(table_name, dbid, fields)