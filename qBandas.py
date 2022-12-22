""" Integrates the popular data handling library Pandas and the QuickBase API

"""

import pandas as pd
from datetime import datetime
import requests, re, json

def transform(
    df: pd.DataFrame, 
    col_types: dict, 
    date_format: str = '%Y-%m-%d', 
    datetime_format: str = '%d%b%Y:%H:%M:%S.%f',
    duration_units: str = "seconds"
    ) -> pd.DataFrame:
    """ Transforms the values in df into values that the QuickBase API can use
    
    After using this function, call `def payload(df, fids)` on the output to get
    your payload.
    
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
    date_format : str
        The format string to parse string-encoded dates in df. For help creating
        these strings visit 
        https://www.programiz.com/python-programming/datetime/strptime.
    datetime_format : str
        The format string to parse string-encoded datetimes in df
    duration_units : string 
        Specifies how durations should be interpereted. Accepted "seconds", "milliseconds"

    Returns
    -------
    pandas.DataFrame : a copy of df with its values encoded for the QuickBase 
        API
    """
    
    out = pd.DataFrame()
    
    for col in df.columns:

        if not col in col_types:
            print(f'col:{col} is missing in col_types')
            return None

        if col_types[col] == 'drop':
            print(f'col:{col} is dropped')
            continue
        
        t = df[col].copy()
        
        print(f'processing col:{col} as type:{col_types[col]}')
            
        # trivial impementations
        if col_types[col] in ['numeric', 'checkbox', 'text', 'email']:
            def f(x):
                if pd.isna(x):
                    return None
                return {'value':x}
                
        elif col_types[col] == 'duration':
        
            # convert units
            if duration_units == 'seconds':
                parse_dur = lambda x: x*1000
            elif duration_units == 'milliseconds':
                parse_dur = lambda x: x
            else:
                print(f'{duration_units} is an invalid duration unit')
                return None
               
            # parse duration col
            def f(x):
                if pd.isna(x):
                    return None
                return {'value':parse_dur(x)}
            
        elif col_types[col] == 'date':
            def f(x):
                if pd.isna(x):
                    return None
                elif not isinstance(x, (datetime, str)):
                    print(f"""removed col:{col} val:{x} type:{type(x)}\
                        expected type in: datetime, str""")
                    return None
                elif isinstance(x, str):
                    x = datetime.strptime(x, date_format)
                return {'value':x.strftime('%Y-%m-%d')}

        elif col_types[col] == 'datetime':
            def f(x):
                if pd.isna(x):
                    return None
                elif not isinstance(x, (datetime, str)):
                    print(f"""removed col:{col} val:{x} type:{type(x)}\
                        expected type in: datetime, str""")
                    return None
                elif isinstance(x, str):
                    x = datetime.strptime(x, datetime_format)
                return {'value':x.strftime('%Y-%m-%dT%H:%M:%SZ')}
            
        else: 
            print(f'col:{col} has an invalid type in col_types')
            return None
        
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
            print(f'col {col} not defined in fids')
            return None
        
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


# Tests         
if __name__ == '__main__':
    
    df = pd.DataFrame({
        'col1': [0, 1], 
        'col2': ['1OCT2022:0:45:13.000', '20NOV2022:17:45:13.000']
    })
    print(df)
    print(payloads(transform(df, {'col1':'numeric','col2':'datetime'}),{'col1':'6','col2':'7'}))


