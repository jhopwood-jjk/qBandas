""" Integrates the popular data handling library Pandas and the QuickBase API
"""
import requests
from functools import partial
from typing import Iterator

import pandas as pd

from .config import field_types
from .schema import *

def format_values(df: pd.DataFrame, col_types: dict) -> pd.DataFrame:
    """ Reformats the values in a dataframe into values that the QuickBase API can use

    WARNING: Function not intended for enduser. See `qb.upload()`.
    
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the records that you want to send to QuickBase. 
    col_types : dict
        Controlls how the columns of the DataFrame are formatted. See `qb.read_schema()` for instructions on how to create and read in this dictonary. 

    Returns
    -------
    DataFrame : A copy of the original dataframe with it's values reformatted. 
    """

    # Figure out what columns are going where, set operations!
    requested_cols = set(col_types.keys())  # from col_types, user specced
    actual_cols = set(df.columns)           # from df

    # check for typos in the schema
    invalid_cols = requested_cols.difference(actual_cols)
    if len(invalid_cols):
        raise Exception(f"columns '{invalid_cols}' are invalid")

    # tell enduser about drops
    for col in actual_cols.difference(requested_cols):
        print(f'column \'{col}\' is being dropped')

    out = pd.DataFrame()

    # look at only the columns in schema and df
    for col in requested_cols.intersection(actual_cols):

        
        # parse the spec
        col_type, args = col_types[col][0], col_types[col][1:]
        print(f"processing column '{col}' as '{col_type}'")

        try:
            # Magic lines! Get the related parsing function from config, create
            # a partial of it with the given arguments, apply it to a copy of the
            # current column, and save it in the output
            parsing_func = field_types[col_type].parsing_func
            out[col] = df[col].copy().apply(partial(parsing_func, args=args))
        except Exception as e:
            raise Exception(f"Failed parsing column '{col}' with column type '{col_type}' and arguments '{args}'") from e

    return out 

def list_records(df: pd.DataFrame, fids: dict) -> list:
    """ Get a list of all the records in your dataframe.

    WARNING: Function not intended for enduser. See `qb.upload()`.
    
    Parameters
    ----------
    df : pandas.Dataframe
        The DataFrame containing the records that you want to send to QuickBase. The values in this DataFrame shoul be formatted for QuickBase. You can do this by calling `qb.format_values()` or write your own proceedure.
    fids : dict
        A mapping from columns in df to QuickBase field IDs as strings.  See `qb.read_schema()` for instructions on how to create and read in this dictonary. 
        
    Returns
    -------
    list : all the records in your table now ready to be sent to the QuickBase API.
    """
    
    # validate the fids
    for col in df.columns:
        if not col in fids.keys():
            raise Exception(f"column '{col}' not defined in fids")
        
    # output dataframe, remap cols to fids
    out = df.copy().rename(columns=fids)

    # Convert each row to a dictonary, drop keys with null values
    def _row_to_dict(row):
        "Convert a row into a dictonary"
        row = dict(row)                                         # makes dict
        return {k: v for k, v in row.items() if not pd.isna(v)} # drops null
    out = list(out.apply(_row_to_dict, axis=1)) 

    return out

def send_records(records: list, info: dict) -> Iterator[dict]:
    """ Send a list of records to a table in a QuickBase app. 

    WARNING: not intended for enduser. see `qb.upload()`.

    Parameters
    ----------
    records : list
        A list of dictonaries. Each dictonary is one record with field IDs for keys.
    info : dict
        Determines the which table in which QuickBase app to send to. See `qb.upload()` for more details. 

    Throws
    ------
    requests.HTTPError : on bad response from endpoint. 

    Returns
    -------
    Iterator[dict] : The json responses from QuickBase. This is mostly for advanced users who want to see stats and such. Visit [this link](https://developer.quickbase.com/operation/upsert) to see the formatting.
    """

    # setup destination information
    headers = {
        'QB-Realm-Hostname': info['QB-Realm-Hostname'],
        'User-Agent': info['User-Agent'] if 'User-Agent' in info else 'qBandas User',
        'Authorization': info['Authorization']
    }
    body = {"to": info['DBID']}

    # look for optinal arguments to include
    for option in ["fieldsToReturn", 'mergeFieldId']:
        if option in info:
            body[option] = info[option]

    # send the data one batch a time
    batch_size = info["Payload-Size"] if "Payload-Size" in info else 20_000
    for i in range(0, len(records), batch_size):

        body["data"] = records[i:i+batch_size]

        r = requests.post(
            'https://api.quickbase.com/v1/records', 
            headers = headers, 
            json = body
        )
        
        r.raise_for_status()
        

        yield r.json()
        
    



def upload(df: pd.DataFrame, schema: tuple|str, info: dict) -> Iterator[dict]:
    """
    Send tabular data to QuickBase.

    Parameters
    ----------
    df : pd.DataFrame
        The tabular data to send. 
    schema : tuple|str
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
    list[dict] : a list of responses from the endpoint about each payload you sent. Your df will be divided into payloads to accomodate the size limitations of the endpoint. 
    """
    col_types, fids = schema
    formatted = format_values(df, col_types)
    records = list_records(formatted, fids)
    send_records(records, info)


    