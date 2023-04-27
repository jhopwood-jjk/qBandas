"""
Functions that deal with sending records or information to a Quickbase 
application.
"""

import json
import os
from datetime import datetime as dt
from functools import partial
from os.path import join
from pathlib import Path
from typing import NoReturn

import pandas as pd
import requests

from . import FIELD_TYPES, headers


def upload(df: pd.DataFrame, table_name: str, directory: Path|str = None,
            **kwargs) -> NoReturn: 
    """
    Send a table of records (rows) to a table on QuickBase.

    If no errors are thrown, the data was successfully uploaded to 
    QuickBase. If an error occurs when sending the data, it is possible 
    that only _some_ of your records will have been uploaded to 
    QuickBase. If that is an issue, please fix the data, and send it 
    all again.

    Parameters
    ----------
    df : pd.DataFrame
        The table of records
    table_name : str
        Identifies which table to send the data to. You should use 
        `pull_schema()` to create a valid `table_name`.
    directory : None | Path | str
        The directory to use for this operation. Default is current
    """

    # enable debugging print statements
    debug = kwargs.get('debug')
    if debug:
        from .util import str_dict, str_resp
        print(df.head())
    
    directory = directory if directory else os.getcwd()  
    if not os.path.isdir(directory):
        raise FileNotFoundError(f'{directory = } is not a valid directory')
    
    headers_ = headers.read(directory = directory)
    with open(join(directory, 'schemas', f'{table_name}.json'), 'r') as f:
        schema = json.load(f)

    if debug:
        print(str_dict(headers_))
        print(str_dict(schema))

    # Check that the columns in the df match the schema
    if not kwargs.get('drop'):
        unknown_columns = [] # columns in df that aren't in schema
        for column in df.columns:
            if column not in schema.keys():
                unknown_columns.append(column)
        if unknown_columns:
            raise Exception(f"The following columns from your dataframe have \
                            no matching column in the specified QuickBase \
                            table. If you want to drop these columns (not \
                            send their data), add `drop=True` to this function \
                            call. Columns: " + ', '.join(unknown_columns))
    
    # pack all the values into qb's crazy formats
    packed_df = pd.DataFrame()
    for col in df.columns:

        if col not in schema: # dropped columns
            continue

        col_info = schema[col]
        col_type = col_info['type']
        col_kwargs = col_info['args'] if 'args' in col_info else {}

        try:
            # get the packing function and apply it
            packing_func = partial(FIELD_TYPES[col_type]['pack'], **col_kwargs)
            packed_df[col] = df[col].copy().apply(packing_func)
        except Exception as e:
            e.args = (f"Failed parsing column '{col}' with column type \
                      '{col_type}' and arguments '{col_kwargs}'", *e.args)
            raise

    if debug:
        print(packed_df.head())

    # grab the feild ids from schema, rename columns 
    fids = {k: v['id'] for k, v in schema.items() if \
            k != '_DBID_' and k in packed_df.columns}
    renamed_df = packed_df.copy().rename(columns=fids) 

    def _row_to_dict(row):
        '''Convert a row into a dictonary and drop nulls'''
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
            headers = headers_, 
            json = body
        )
        if debug:
            print(str_resp(r))
        r.raise_for_status()
        

def fetch(table_name: str, *columns, where: str = None, order: list = None, 
            group_by: list = None, skip: int = 0, limit: int = None, 
            directory: Path|str = None, **kwargs) -> pd.DataFrame:
    '''
    Fetch a table of records from a QuickBase app

    Retrieves records from QuickBase. Authorized by `headers.json`.

    Parameters
    ----------
    table_name : str
        The table to pull from
    where : str, optional
        Should be written like an SQL statement, by default None
    order : list, optional
        The order in which to sort the returned records. Each entry 
        in this list is a tuple with the first element being the 
        column name, and the second is the word 'asc' or 'desc'. 
        by default None
    group_by : list, optional
        How to group records, by default None
    skip : int, optional
        Number of records to skip off the top off the returned 
        dataframe, by default 0
    limit : int, optional
        Maximum number of records that can be returned. None is no
        limit, by default None
    directory : Path | str, optional
        The directory for this operation, by default current
    *columns
        The columns to select
    **kwargs
        Unused

    Returns
    -------
    pd.DataFrame
        The records from QuickBase. 
    
    '''
    
    directory = directory if directory else os.getcwd()  
    if not os.path.isdir(directory):
        raise FileNotFoundError(f'{directory = } is not a valid directory')
    
    # read in headers and schema
    headers_ = headers.read(directory = directory)
    with open(join(directory, 'schemas', f'{table_name}.json'), 'r') as f:
        schema = json.load(f) # for resolving column names
        
    body = {
        'from': table_name,
        'select': [schema[c]['id'] for c in columns],
        "options": {
            "skip": skip if skip else 0,
            "top": limit if limit else -1,
            "compareWithAppLocalTime": False
        }
    }
    
    # are we sorting?
    if order:
        order = list(order)
        for i, item in enumerate(order.copy()):
            name, ord = item
            order[i] = {"fieldId": schema[name]['id'], 'order': ord.upper()}
        body['sortBy'] = order
        
    # are we grouping?
    if group_by:
        body["groupBy"] = [{"fieldId": 6, "grouping": "equal-values"}]
        raise NotImplementedError('No grouping just yet!')
    
    # are we filtering?
    if where:
        body['where'] = '{fid.op.\'value\'}'
        raise NotImplementedError('No filtering just yet!')
    
    # send request
    r = requests.post('https://api.quickbase.com/v1/records/query', 
        headers = headers_, json = body)
    r.raise_for_status()
    
    # unravel response
    data = r.json()['data']
    fields = r.json()['fields']
    name_map = {str(x['id']): x['label'] for x in fields}
    type_map = {str(x['id']): x['type'] for x in fields}
    
    # assemble dataframe
    for i, record in enumerate(data.copy()):
        data[i] = {k: v['value'] for k, v in record.items()}
    df = pd.DataFrame(data)
    # data typing... builtins didn't work for me
    for id, type_ in type_map.items():
        if type_ in ['timestamp', 'date']:
            df[id] = pd.to_datetime(df[id])
    df.rename(columns = name_map, inplace = True)
    
    return df