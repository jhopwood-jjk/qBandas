""" Integrates the popular data handling library Pandas and the QuickBase API
"""
import requests, re, json, typing
import pandas as pd
from functools import partial

from .parsers import parse_default, parse_duration, parse_date, parse_datetime, parse_phonenum

def transform(df: pd.DataFrame, col_types: dict) -> pd.DataFrame:
    """ Transforms the values in df into values that the QuickBase API can use
    
    After using this function, call `def payload(df, fids)` on the output to get
    your payload.

    For help creating datetime format strings, vist 
    https://www.programiz.com/python-programming/datetime/strptime.
    
    Parameters
    ----------
    df : pandas.Dataframe
        The dataframe containing the raw data
    col_types : dict
        A mapping of the column names of df to QuickBase data types. The 
        supported data types are:
        "drop" : drops the column in the output
        "numeric" : takes a column of numeric values
        "checkbox" : takes a column of boolean values
        "text" : takes a column of string values
        "email" : takes a column of string values
        "date" : takes a column of datatime objects or strings. You can 
            configure the parsing of strings using date_format.
        "datetime" : takes a column of datatime objects or strings. You can 
            configure the parsing of strings using datetime_format.
        Example: `col_types = {"column one": "drop", "column two": "checkbox"}`

    Returns
    -------
    pandas.DataFrame : a copy of df with its values encoded for the QuickBase 
        API
    """
    
    out = pd.DataFrame()
    
    for col in df.columns:

        # Column not specified in col_types
        if not col in col_types:
            raise Exception(f'column \'{col}\' is missing in col_types')

        # Get the type of column and unpack any column args
        column_type = col_types[col]
        args = []
        if isinstance(column_type, tuple):
            column_type, *args = col_types[col]

        if col_types[col] == 'drop':
            print(f'column \'{col}\' is dropped')
            continue
        
        # temp copy of column to modify
        t = df[col].copy()

        # parsing function
        f = None
        
        print(f"processing column '{col}' as '{column_type}'")
            
        if column_type in ['numeric', 'checkbox', 'text', 'email']:
            f = parse_default
                
        elif column_type == 'duration':
            if not args:
                raise Exception(f"specify a duration unit for "\
                    f"column '{col}'")
            f = partial(
                parse_duration, col=col, units=args[0]
            )
            
        elif column_type == 'date':
            if not args:
                raise Exception(f"specify a date format for "\
                    f"column '{col}'")
            f = partial(
                parse_date, col=col, format=args[0]
            )

        elif column_type == 'datetime':
            if not args:
                raise Exception(f"specify a datetime format for "\
                    f"column '{col}'")
            f = partial(
                parse_datetime, col=col, format=args[0]
            )
        
        elif column_type == 'phone':
            if not args:
                raise Exception(f"specify a phone number format for "\
                    f"column '{col}'")
            f = partial(
                parse_phonenum, col=col, format=args[0]
            )
            
        else: 
            raise Exception(f"column '{col}' has an invalid type")
        
        t = t.apply(f)
        out[col] = t
            
    return out 

def payloads(df: pd.DataFrame, fids: dict, size: int = 20_000) -> list:
    """ Create a list of payloads to be sent
    
    Before calling this function, call `transform(df, col_types)` on your table.
    
    Parameters
    ----------
    df : pandas.Dataframe
        The dataframe containing the transformed data
    fids : dict
        A mapping from columns in df to QuickBase field IDs as strings.
        Example: `fids = { "column one": "6", "column two": "7" }`
    size : int
        The size of the payloads
        
    Returns
    -------
    list : the table encoded as a list of JSON payloads for the `send_records` 
        function
    """
    
     # validate the fids
    for col in df.columns:
        if not col in fids.keys():
            raise Exception(f"column '{col}' not defined in fids")
        
    t = df.copy().rename(columns=fids)

    # remove all null value entries before packaging
    def f(x):
        x = dict(x)
        return {k: v for k, v in x.items() if not pd.isna(v)}

    t = list(t.apply(f, axis=1))

    out = list()
    for i in range(0, len(t), size):
        out.append(t[i:i+size])
        
    return out


def send_records(payload: list, info: dict) -> requests.Response:
    """ Send a list of records to a table in a QuickBase app

    Parameters
    ----------
    payload : list
        The QuickBase API encoded data you would like to send.
    info : dict
        See docs for qBandas.upload() for spec. 

    Returns
    -------
    requests.Response : the response from the destination. Call `.json()` on the response to see the text.
    """

    # parse the info dict, required arguments
    QB_Realm_Hostname = info['QB-Realm-Hostname']
    Authorization = info['Authorization']
    table = info['DBID']

    # optional arguments r/badcode
    if 'User-Agent' in info:
        User_Agent = info['User-Agent']
    else:
        User_Agent = 'qBandas User'

    if "fieldsToReturn" in info:
        fieldsToReturn = info['fieldsToReturn']
    else:
        fieldsToReturn = None

    if 'mergeFieldId' in info:
        mergeFieldId = info['mergeFieldId']
    else:
        mergeFieldId = None

    headers = {
        'QB-Realm-Hostname': QB_Realm_Hostname,
        'User-Agent': User_Agent,
        'Authorization': Authorization
    }

    body = {
        "to": table,
        "data": payload
    }

    if fieldsToReturn:
        body["fieldsToReturn"] = fieldsToReturn

    if mergeFieldId:
        body['mergeFieldId'] = mergeFieldId

    r = requests.post(
        'https://api.quickbase.com/v1/records', 
        headers = headers, 
        json = body
    )

    return r
    
def pretty_str(r: requests.Response) -> str:
    """ Takes a resonse object from `send_records()` and makes it pretty

    Parameters
    ----------
    r : requests.Response
        The response from calling `send_records()`

    Returns
    -------
    str : a pretty string representation
    """

    text = json.dumps(r.json(),indent=4)
    pattern = r"\[[\d,\s]+\]"
    matches = re.findall(pattern, text)
    for match in matches:
        n = match.count(',') 
        text = text.replace(match, f"[...{n+1} items...]")
    return text

def full_transform(df: pd.DataFrame, schema: dict[tuple[int, str]], size: int = 20_000) -> list[list[dict]]:
    """
    Turn a dataframe into payloads for the quickbase API

    Parameters
    ----------
    df : pandas.DataFrame
        The data to transform
    schema : dict
        Specifies the field in the destination table on quickbase
        and the data type (with additional formatting requirements)
        Example:
        `schema = { "my_col" = (7, "phone", "###-###-####") }`
        The column called "my_col" will be parsed a phone number in the format
        "###-###-####", it will be sent to FID 7 in the destination table.
    size : int
        The size of the payloads to send

    Returns
    -------
    list[list[dict]] : The outermost list species which payload. Each element of
    the outer list is a stand-alone payload to be sent. 
    """
    fids = dict()
    col_types = dict()

    # unpack the schema
    for key in schema.keys():

        # dropped columns don't have fid or args
        if schema[key] == 'drop':
            col_types[key] = schema[key]
        
        # non-dropped cols
        else:
            #these must ALL be tuples of args
            if not isinstance(schema[key], tuple):
                raise Exception(f"column '{key}' has invalid schema "\
                    f"'{schema[key]}', expected a tuple")

            t, *col_types[key] = schema[key]

            # validate fids
            if not (isinstance(t, int) or t.isnumeric()):
                raise Exception(f"column '{key}' has invalid fid '{t}'")
            fids[key] = str(t)

            # validate column parsing args
            if not len(col_types[key]):
                raise Exception(f"column '{key}' has no data type.")
            if len(col_types[key]) == 1:
                col_types[key] = col_types[key][0] # no formatting
            else:
                col_types[key] = tuple(col_types[key])

    inter = transform(df, col_types=col_types)
    out = payloads(inter, fids=fids, size=size)

    return out

def read_schema(path: str) -> dict:
    """ Read a schema from a JSON file

    Almost all entries should have the form `"col": "<fid> <col_type> <*args>"`. 
    Dropped columns do not need an fid. Below is an example `schema.json`
    ```json
    {
        "PhoneNum": "7 phone ###.###.####",
        "BadInfo": "drop",
        "FirstName": "8 text"
    }
    ```
    
    Parameters
    ----------
    path : str
        The location of the JSON file

    Returns
    -------
    The schema as a python object
    """
    import shlex
    out = json.load(open(path))
    for key in out:
        t = shlex.split(out[key])
        s = t[0] if len(t) == 1 else tuple(t)
        out[key] = s
    return out

def write_schema(df: pd.DataFrame, f: typing.IO, space: int=32) -> None:
    """ Define a generic schema from a dataframe and write it to disk

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to create a schema from
    f : file 
        The file to write the schema to
    space : int
        number of chars after the tab but before the type string
    """

    mapping = {
        'int64': 'numeric',
        'float64': 'numeric',
        'object': 'text',
        'str': 'text',
        'bool': 'checkbox',
        'datetime': 'datetime'
    }
    t = map(str, df.dtypes)
    types = map(lambda x: mapping[x] if x in mapping else None, t)
    
    out = '{\n'
    for col, typ in zip(df.columns, types):
        b = ' '*(space-len(col)) if len(col) < 16 else ' '
        out += f'\t"{col}":' + b + f'"000 {typ}",\n'
    out = out[:-2] + '\n}'

    f.write(out)

def upload(df: pd.DataFrame, schema: dict, info: dict) -> list[requests.Response]:
    """
    Send tabular data to QuickBase.

    Parameters
    ----------
    df : pd.DataFrame
        The tabular data to send. 
    schema : dict
        Specifies the field IDs and the data type (with additional formatting requirements) for each column in the dataframe. Use read_schema() to get this Python object. 
    info : dict
        Specify who is sending the data and where it is going. This info dict has three required keys. Here is an example `info` dict.
        
        ``` python
        info = {
            "QB-Realm-Hostname": 'demo.quickbase.com',
            "Authorization": 'QB-USER-TOKEN {TOKEN}',
            "DBID": "abcdef123"
        }
        ```

        Required arguments are "QB-Realm-Hostname", "Authorization", and "DBID". "DBID" is the destination table identifier on QuickBase. Can be found in the URL when viewing the table. You can also find it in the app protperties if you are an admin. "QB-Realm-Hostname" is your Quickbase subdomain. "Authorization" is the Quickbase authentication scheme you are using to authenticate the request, as described on the [authorization page](https://developer.quickbase.com/auth).

        Optional keys are "mergeFieldId", "User-Agent", and "fieldsToReturn". "mergeFieldId" gets a integer value to specify how to merge these new records into the exsiting records. The default is 3 or Record ID#. "fieldsToReturn" gets a list of integers specifying fields to get back after the upload. If you request any fields, you will automatically get the field's Records ID#s. "User-Agent" lets you name yourself for the API. Defaults to 'qBandas User'.

        A final optional key is "Payload-Size". This key takes and integer value that specifies the number of records to send per API request. The endpoint only supports payloads up to 10MB. Be careful with this setting, if it is too small performance will be significatly decreased; too large and you will have your requests rejected. Defaults to 20,000. 

        More information about all of these keys can be found on the QuickBase API [docs](https://developer.quickbase.com/operation/upsert). 

    Returns
    -------
    list[requests.Response] : a list of responses from the endpoint about each payload you sent. Your df will be divided into payloads to accomodate the size limitations of the endpoint. 
    """

    if "Payload-Size" in info:
        payloads = full_transform(df, schema, size=info["Payload-Size"])
        del info["Payload-Size"] # we don't want this key for send_records
    else:
        payloads = full_transform(df, schema)

    out = [None] * len(payloads)
    for i, payload in enumerate(payloads):
        try:
            r = send_records(payload, info)
            out[i] = r
            r.raise_for_status()
        except Exception as e:
            import warnings
            warnings.warn(f"Payload {i} bad response")
            warnings.warn(pretty_str(r))
    
    return out



    