"""
Functions for converting data from Python's representation to QuickBase's representation.
"""

from datetime import datetime

import pandas as pd

def _pack_default(x: object) -> dict:
    """
    Pack a value into the default QuickBase API format.

    Parameters
    ----------
    x
        The value to pack. It can be anything.

    Returns
    -------
    the packed value
    """
    if pd.isna(x):
        return None
    return {'value':x}


def _pack_duration(x: float|int|str, unit: str='seconds') -> dict:
    """
    Pack a number into duration format for the QuickBase API
    
    Parameters
    ----------
    x
        The value to pack. It should be a number.
    unit : str
        the duration unit 'seconds' or 'milliseconds'. Defaults to 'seconds'

    Returns
    -------
    the packed value
    """
    if pd.isna(x):
        return None

    x = int(x)

    if unit == 'seconds':
        x *= 1000
    elif unit == 'milliseconds':
        pass
    else:
        raise Exception(f"'{unit}' is not a valid duration unit for value {x} of type {type(x)}")

    return {'value':x}
    
def _pack_date(x: datetime|str, format: str = "%m.%d.%Y") -> dict:
    """
    Pack a date into the date format for the QuickBase API

    Parameters
    ----------
    x
        The value to pack. It should be a datetime object or a string
    format : str
        the format to decode str dates. Defaults to "%m.%d.%Y"

    Returns
    -------
    the packed value
    """
    if pd.isna(x):
        return None

    if not isinstance(x, (datetime, str)):
        raise Exception(f"value {x} of type {type(x)} cannot be coerced to date")
    elif isinstance(x, str):
        x = datetime.strptime(x, format)

    return {'value':x.strftime('%Y-%m-%d')}

def _pack_datetime(x: datetime|str, format: str = '%d%b%Y:%H:%M:%S.%f') -> dict:
    """
    Pack a datetime into the datetime format for the QuickBase API
    
    Parameters
    ----------
    x
        The value to pack. It should be a datetime object or a string
    format : str
        the format used to decode datetime strings, default '%d%b%Y:%H:%M:%S.%f'
    Returns
    -------
    the packed value
    """
    if pd.isna(x):
        return None

    if not isinstance(x, (datetime, str)):
        raise Exception(f"'{type(x)}' cannot be coerced to datetime")
    elif isinstance(x, str):
        x = datetime.strptime(x, format)
    
    return {'value':x.strftime('%Y-%m-%dT%H:%M:%SZ')}


def _pack_phonenum(x: None|str, format: str = "##########") -> dict:
    """
    Pack a phone string into the phone format for the QuickBase API
    
    Parameters
    ----------
    x
        The value to pack. It should be a string
    format : str
        the format string for reading the phone number. The phone number "(123) 456-7890 x123" would have the format string "(###) ###-#### x###". The extension must come last. It is optional for x to include it.

    Returns
    -------
    the packed value
    """
    
    if pd.isna(x):
        return None
    
    if not isinstance(x, str):
        raise Exception(f"type {type(x)} is invalid for value {x}, expected type str")

    # a str containing only the digits in order
    try:
        y = [x[i] for i in range(len(x)) if format[i] == '#']
        y = ''.join(y)
    except IndexError:
        raise Exception(f"could not parse '{x}' with format '{format}'") 

    if not y.isnumeric() or len(y) < 10:
        raise Exception(f"could not parse '{x}' with format '{format}'") 

    t = f'({y[0:3]}) {y[3:6]}-{y[6:10]}'
    if len(y) > 10:
        t = t + f' x{y[10:]}'

    #return "(123) 456-7890 x123"
    return {'value':t}