'''
Functions that deal with sending records or information to a Quickbase 
application.
'''

import asyncio
import datetime as dt
from functools import partial

import pandas as pd
import requests

from ._constants import FIELD_TYPES, MAX_BATCH_RECORDS, TIMEZONE_OFFSET
from .profiles import _get_headers, is_valid_profile
from .schemas import _read_schema


def upload_records(df: pd.DataFrame, table_name: str, profile: str,
                   drop: bool = False): 
    '''
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
    profile : str
        The profile to authorize this request
    drop : bool, optional
        Toggle dropping extra columns. If False, all columns must match, by deafult False
    '''

    if __debug__: 
        from pprint import pp
        print(df.head())
    
    # headers
    if not is_valid_profile(profile, talk =  True):
        raise ValueError(f'profile {profile} cannot be used')
    headers_ = _get_headers(profile)

    # schema
    dbid, schema = _read_schema(table_name)
    if not dbid:
        raise ValueError(f'schema for {table_name} cannot be found')

    if __debug__:
        pp(headers_)
        print(dbid)
        pp(schema)

    # Check that the columns in the df match the schema
    if not drop:
        unknown_columns = set(df.columns) - set(schema)
        unused_columns = set(schema) - set(df.columns)
        if unknown_columns:
            raise ValueError(f'the columns {unknown_columns} are not in'
                             f'the schema {table_name}. To drop these'
                             'columns, add drop=True. Unused columns: '
                             f'{unused_columns}.')
    
    # pack all the values into qb's crazy formats
    packed_df = pd.DataFrame()
    for col in df.columns:

        if col not in schema: continue
    
        col_type = schema[col]['type']
        col_kwargs = schema[col].get('args', {})

        try:
            # get the packing function and apply it
            packing_func = partial(FIELD_TYPES[col_type]['pack'], **col_kwargs)
            packed_df[col] = df[col].copy().apply(packing_func)
        except Exception as e:
            e.args = (f'Failed parsing column {col} with column type'
                      f'{col_type} and arguments {col_kwargs}', *e.args)
            raise

    if __debug__:
        print(packed_df.head())

    # grab the feild ids from schema, rename columns 
    fids = {k: v['id'] for k, v in schema.items()}
    renamed_df = packed_df.copy().rename(columns=fids) 

    def _row_to_dict(row):
        '''Convert a row into a dictonary and drop nulls'''
        row = dict(row)                                         
        return {k: v for k, v in row.items() if not pd.isna(v)} 
    records = list(renamed_df.apply(_row_to_dict, axis=1)) 

    if __debug__:
        pp(records[:5])

    # setup destination information
    body = {"to": dbid}
    
    async def _upload_batch(i: int):
        '''
        Upload a section of the records asynchronously 
        
        Parameters
        ----------
        i : int
            The index of the first record to upload
        '''
        body["data"] = records[i : i + MAX_BATCH_RECORDS]
        r = requests.post('https://api.quickbase.com/v1/records', 
            headers = headers_, json = body)
        if __debug__: 
            pp(r.json())
        r.raise_for_status()

    async def _upload_all():
        '''Uploads all the records in a series of batches'''
        jobs = []
        for i in range(0, len(records), MAX_BATCH_RECORDS):
            jobs.append(_upload_batch(i))
        await asyncio.gather(*jobs)
        
    asyncio.run(_upload_all())

def fetch_records(table_name: str, profile: str, *, columns: list[str] = None, 
                  where: str = None, order: list = None, 
                  group_by: list = None, skip: int = 0, 
                  limit: int = None) -> pd.DataFrame:
    '''
    Fetch a table of records from a QuickBase app

    Retrieves records from QuickBase

    Parameters
    ----------
    table_name : str
        The table to pull from
    profile : str
        The name of the profile to authorize this request
    columns : list[str], optional
        The columns to select, by default None
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
        
    Returns
    -------
    pd.DataFrame
        The records from QuickBase. 
    
    '''
    
    # headers
    if not is_valid_profile(profile, talk =  True):
        raise ValueError(f'profile {profile} cannot be used')
    headers_ = _get_headers(profile)
    
    if __debug__:
        from pprint import pp
        pp(headers_)

    # schema
    dbid, schema = _read_schema(table_name)
    if not dbid:
        raise ValueError(f'schema for {table_name} cannot be found')
    
    if __debug__:
        print(dbid)
        pp(schema)
        
    columns = columns if columns else set(schema)
        
    body = {
        'from': dbid,
        'select': [schema[c]['id'] for c in columns],
        "options": {
            "skip": skip if skip else 0,
            "top": limit if limit else -1,
            "compareWithAppLocalTime": True
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
    
    if __debug__:
        pp(body)
    
    # send request
    r = requests.post('https://api.quickbase.com/v1/records/query', 
        headers = headers_, json = body)
    if __debug__:
        pp(r.json())
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
    for id, type_ in type_map.items():
        if type_ in ['timestamp', 'date']:
            df[id] = pd.to_datetime(df[id]) - dt.timedelta(
                hours = TIMEZONE_OFFSET)
            
    df.rename(columns = name_map, inplace = True)
    return df