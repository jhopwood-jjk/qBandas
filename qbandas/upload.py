"""
Functions that deal with sending records or information to a Quickbase application.
"""

import requests, json, os
from functools import partial

import pandas as pd

from .config import field_types

def upload_records(df: pd.DataFrame, table_name: str, **kwargs): 
    """
    Send a table of records (rows) to a table on QuickBase.

    If no errors are thrown, the data was successfully uploaded to QuickBase. If an error occurs when sending the data, it is possible that only _some_ of your records will have been uploaded to QuickBase. If that is an issue, please fix the data, and send it all again.

    Parameters
    ----------
    df : pd.DataFrame
        The table of records
    table_name : str
        Identifies which table to send the data to. You should use `pull_schema()` to create a valid `table_name`.
    """

    debug = 'debug' in kwargs and kwargs['debug']
    if debug:
        from .util import str_dict, str_resp
        print(df.head())
    

    # setup: read in the headers and the schema
    # Can set the directory with dir=<dir>, defaults to .
    dir = kwargs['dir'] if 'dir' in kwargs else os.getcwd()
    with open(os.path.join(dir, 'headers.json'), 'r') as f:
            headers = json.load(f)
    with open(os.path.join(dir, 'schemas', table_name+'.json'), 'r') as f:
            schema = json.load(f)

    if debug:
        print(str_dict(headers))
        print(str_dict(schema))

    # Check that the columns in the df match the schema
    if 'drop' not in kwargs or not kwargs['drop']:
        unknown_columns = [] # columns in df that aren't in schema
        for column in df.columns:
            if column not in schema.keys():
                unknown_columns.append(column)
        if unknown_columns:
            raise Exception(f"The following columns from your dataframe have no matching column in the specified QuickBase table. If you want to drop these columns (not send their data), add `drop=True` to this function call. Columns: " + ', '.join(unknown_columns))
    
    # pack all the values into qb's crazy formats
    packed_df = pd.DataFrame()
    for col in df.columns:

        if col not in schema: # dropped columns
            continue

        col_info = schema[col]
        col_type = col_info['type']
        col_kwargs = col_info['args'] if 'args' in col_info else {}

        # Magic lines! Get the related parsing function from config, create a partial of it with the given column arguments, apply it to a copy of the current column, and save it in the output
        try:
            packing_func = field_types[col_type]['pack']
            packed_df[col] = df[col].copy().apply(partial(packing_func, **col_kwargs))
        except Exception as e:
            e.args = (f"Failed parsing column '{col}' with column type '{col_type}' and arguments '{col_kwargs}'", *e.args)
            raise

    if debug:
        print(packed_df.head())

    # grab the feild ids from schema, rename columns 
    fids = {k:v['id'] for k,v in schema.items() if k != '_DBID_' and k in packed_df.columns}
    renamed_df = packed_df.copy().rename(columns=fids) 

    # Convert each row to a dictonary, drop keys with null values, create the list of records
    def _row_to_dict(row):
        "Convert a row into a dictonary"
        row = dict(row)                                         
        return {k: v for k, v in row.items() if not pd.isna(v)} 
    records = list(renamed_df.apply(_row_to_dict, axis=1)) 

    if debug:
        print(str_dict(records[:5]))

     # setup destination information
    body = {"to": schema['_DBID_']}

    # look for optinal arguments to include from kwargs
    for option in ["fieldsToReturn", 'mergeFieldId']:
        if option in kwargs:
            body[option] = kwargs[option]

    # send the data one batch a time
    batch_size = kwargs["Payload-Size"] if "Payload-Size" in kwargs else 20_000
    for i in range(0, len(records), batch_size):
        body["data"] = records[i:i+batch_size]
        r = requests.post(
            'https://api.quickbase.com/v1/records', 
            headers = headers, 
            json = body
        )
        if debug:
            print(str_resp(r))
        r.raise_for_status()
    