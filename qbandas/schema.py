"""
Methods that deal with resolving the structure of local and remote (QuickBase) tables.
"""
import json
import requests
import os
from os.path import join, exists
from typing import NoReturn

from . import headers

def pull(DBID: str, **kwargs) -> NoReturn:
    """
    Download a local copy of a table's structure from a QuickBase application.

    This operation is authorized by `./headers.json`. The schema will be placed into `./schemas/` where other qBandas operations can use it. 

    Parameters
    ----------
    DBID : str
        The unique identifier of the table in QuickBase.

    Examples
    --------
    >>> import qbandas
    >>> # qbandas.schema.pull('bb7f543') # unauthorized

    """
    # Can set the directory with dir=<dir>
    cwd = kwargs['dir'] if kwargs.get('dir') else os.getcwd()

    headers_ = headers.read(dir=cwd)

    # send the request to quickbase
    params = {'tableId': DBID, 'includeFieldPerms': "false"}
    r = requests.get('https://api.quickbase.com/v1/fields', params = params, headers = headers_)
    r.raise_for_status()

    # convert the language in the api to user language
    type_conversion = {
        "timestamp": "datetime",
        "recordid": "numeric",
        "email": "email-address",
        "phone": "phone-number",
        }

    address_subfields = {
        ": Street 1": 1,
        ": Street 2": 2,
        ": City": 3,
        ": State": 4,
        ": Zip": 5,
        ": Country": 6,
        }

    # parse the schema from the response
    schema = dict()
    schema['_DBID_'] = DBID
    for field in r.json():

        # address fields send extra unlabeled info that we cannot use. remove it
        if field['label'] in ['Street 1', 'Street 2', 'City', 'State/Region', 'Postal Code', 'Country']:
            continue

        type_ = field['fieldType']
        if type_ in type_conversion:
            type_ = type_conversion[type_]
        
        schema[field['label']] = {'id': field['id'], 'type': type_}

        # recreate subfields for adresses with propper names
        if type_ == 'address':
            for sufix, fid_offset in address_subfields.items():
                schema[field['label'] + sufix] = {
                    'id': field['id'] + fid_offset,
                    'type': "text"
                }

    # dump the schema to disk
    schemas_dir = join(cwd, 'schemas')
    if not exists(schemas_dir):
        os.makedirs(schemas_dir)
    with open(join(schemas_dir, DBID + '.json'), 'w') as f:
        json.dump(schema, f, indent=4)
    
        
def add_args(schema_name: str, *args, **kwargs):
    """
    Append new config options (args) for fields in a schema.

    Parameters
    ----------
    schema_name : str
        The schema to modify.
    *args
        These fields will be configured.
    **kwargs
        The arguments to add.
    """

    # Can set the directory with dir=<dir>
    dir = os.getcwd()
    if 'dir' in kwargs:
        dir = kwargs['dir']
        del kwargs['dir']

    # read in the schema
    file_name = schema_name + '.json'
    with open(os.path.join(dir, 'schemas', file_name), 'r') as f:
        schema = json.load(f)

    # append the new arguments
    for field in args:
        if field not in schema:
            raise Exception(f"The field {field} is not in the schema {schema_name}")
        if 'args' not in schema[field]:
            schema[field]['args'] = kwargs
        else:
            schema[field]['args'] = schema[field]['args'] | kwargs

    # put the schema pack into the file
    with open(join(dir, 'schemas', file_name), 'w') as f:
        json.dump(schema, f, indent=4)

def set_args(schema_name: str, *args, **kwargs):
    """
    Set the config options (args) for fields in a schema.

    Parameters
    ----------
    schema_name : str
        The schema to modify.
    *args
        These fields will be configured.
    **kwargs
        The arguments to add.
    """

    # Can set the directory with dir=<dir>
    dir = os.getcwd()
    if 'dir' in kwargs:
        dir = kwargs['dir']
        del kwargs['dir']

    # read in the schema
    file_name = schema_name + '.json'
    with open(os.path.join(dir, 'schemas', file_name), 'r') as f:
        schema = json.load(f)

    # set the arguments
    for field in args:
        if field not in schema:
            raise Exception(f"The field {field} is not in the schema {schema_name}")
        schema[field]['args'] = kwargs

    # put the schema pack into the file
    with open(os.path.join(dir, 'schemas', file_name), 'w') as f:
        json.dump(schema, f, indent=4)