""" Integrates the popular data handling library Pandas and the QuickBase API

"""

import pandas as pd
import requests, re, json
from functools import partial

from .parsers import parse_default, parse_duration, parse_date
from .parsers import parse_datetime, parse_phonenum

print("Using qBandas version 0.0.1")
print("Read the docs https://github.com/jhopwood-jjk/qBandas")

def transform(
    df: pd.DataFrame, 
    col_types: dict 
    ) -> pd.DataFrame:
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


def send_records(
    payload: list,
    table: str,
    QB_Realm_Hostname: str,
    Authorization: str,
    User_Agent: str = 'qBandasUser',
    fieldsToReturn: list = None
    ) -> requests.Response:
    """ Send a list of records to a table in a QuickBase app

    Please see `transform(df, col_types)` and `payload(df, fids)` to set up your
    payload.

    Parameters
    ----------
    payload : list
        The QuickBase API encoded data you would like to send.
    table : str
        The destination table identifier on QuickBase. Can be found in the URL
        when viewing the table. Example: "brqfpn6ur"
    QB_Realm_Hostname : str
        Your Quickbase domain, for example "demo.quickbase.com"
    User_Agent : str
        This is entered by the person or utility invoking the API. You might 
        custom create this or use the default one of your toolkit. Being 
        descriptive here may offer more identification and troubleshooting 
        capabilities.
    Authorization : str
        The Quickbase authentication scheme you are using to authenticate the 
        request, as described on the [authorization page](https://developer.quickbase.com/auth).
    fieldsToReturn : list
        A list of field IDs from the destination table that you would like 
        returned. Example: `fieldsToReturn = [6,7]`

    Returns
    -------
    requests.Response : the response from the destination. Call `.json()` on the 
        response to see the text.
    """
        
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

    r = requests.post(
        'https://api.quickbase.com/v1/records', 
        headers = headers, 
        json = body
    )

    return r
    
def pretty_print(r: requests.Response) -> str:
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
    pattern = r"\[[\d,\s]*\]"
    matches = re.findall(pattern, text)
    for match in matches:
        n = match.count(',') 
        text = text.replace(match, f"[...{n+1} items...]")
    return text

def fastSchema(x: str = "COL1 COL2 COL3", delim:str=None):
    """ Print out the python code for making the schema dict

    Parameters
    ----------
    x
        The string contatining all column names seperated by a delimeter
    delim
        the deliminating string. None means split on whitespace

    Returns
    -------
    Python code as a string
    """
    if delim:
        t = x.split(delim)
    else:
        t = x.split()
    print("col_types = {")
    for item in t:
        print(f'\t"{item.strip()}": (000, None),')
    print('}')

def full_transform(df: pd.DataFrame, schema: dict[tuple[int, str]],
    size: int = 20_000) -> list[list[dict]]:
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
            if not isinstance(t, int):
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