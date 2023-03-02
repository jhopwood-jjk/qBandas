"""
Methods that deal with resolving the structure of local and remote (QuickBase) tables.
"""

import json, requests, os

def pull_schema(DBID: str, schema_name: str = None, **kwargs) -> None:
    """
    Download a local copy of a table's structure from a QuickBase application.

    This operation is authorized by `./headers.json`. The schema will be placed into `./schemas/` where other qBandas operations can use it. 

    Parameters
    ----------
    DBID : str
        The unique identifier of the table in QuickBase.
    schema_name : str
        The identifier that qBanads should use to refer to this table. Defaults to `DBID`.
    """
    # Can set the directory with dir=<dir>
    dir = kwargs['dir'] if 'dir' in kwargs else os.getcwd()

    # resolve the headers
    with open(os.path.join(dir, 'headers.json'), 'r') as f:
            headers = json.load(f)

    # send the request to quickbase
    params = {
        'tableId': DBID,
        'includeFieldPerms': "false"
    }
    r = requests.get(
        'https://api.quickbase.com/v1/fields', 
        params = params, 
        headers = headers
    )
    r.raise_for_status()

    # convert the language in the api to user language
    type_conversion = {
        "timestamp": "datetime",
        "recordid": "numeric",
        "email": "email-address",
        "phone": "phone-number"
    }

    # parse the schema from the response
    schema = dict()
    schema['_DBID_'] = DBID
    for field in r.json():
        _type = field['fieldType']
        if _type in type_conversion:
            _type = type_conversion[_type]
        schema[field['label']] = {
            'id': field['id'],
            'type': _type
        }

    # dump the schmea to disk
    file_name = (schema_name if schema_name else DBID) + '.json'
    with open(os.path.join(dir, 'schemas', file_name), 'w') as f:
        json.dump(schema, f, indent=4)
    
        
def add_args(schema_name: str, field: str, **kwargs):
    """
    Append new config options (args) for a field in a schema.

    Parameters
    ----------
    schema_name : str
        The schema to modify.
    field : str
        This field will be configured.
    **kwargs
        The arguments to add.

    Examples
    --------
    ``` 
    >>> import qbandas as qb
    TODO
    ```
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
    if field not in schema:
        raise Exception(f"The field {field} is not in the schema {schema_name}")
    if 'args' not in schema[field]:
        schema[field]['args'] = kwargs
    else:
        schema[field]['args'] = schema[field]['args'] | kwargs

    # put the schema pack into the file
    with open(os.path.join(dir, 'schemas', file_name), 'w') as f:
        json.dump(schema, f, indent=4)

def set_args(schema_name: str, field: str, **kwargs):
    """
    Set the config options (args) for a field in a schema.

    Parameters
    ----------
    schema_name : str
        The schema to modify.
    field : str
        This field will be configured.
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
    if field not in schema:
        raise Exception(f"The field {field} is not in the schema {schema_name}")
    schema[field]['args'] = kwargs

    # put the schema pack into the file
    with open(os.path.join(dir, 'schemas', file_name), 'w') as f:
        json.dump(schema, f, indent=4)