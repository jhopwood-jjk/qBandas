"""
Methods that deal with resolving the structure of local and remote (QuickBase) tables.
"""

import json, requests, os

def pull_schema(DBID: str, name: str = None, **kwargs) -> None:
    """
    Download a local copy of a table's structure from a QuickBase application.

    This operation is authorized by `./headers.json`. The schema will be placed into `./schemas/` where other qBandas operations can use it. 

    Parameters
    ----------
    DBID : str
        The unique identifier of the table in QuickBase.
    Name : str
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
        "email": "email-address"
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
    file_name = (name if name else DBID) + '.json'
    with open(os.path.join(dir, 'schemas', file_name), 'w') as f:
        json.dump(schema, f, indent=4)
    
        
        
