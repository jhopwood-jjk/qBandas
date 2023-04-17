"""
Functions for converting data from Python's representation to QuickBase's representation.
"""

from datetime import datetime
from typing import Callable, Any

import pandas as pd


def _pack_default(x: Any) -> dict|None:
    """
    Pack a value into the default QuickBase API format.

    Parameters
    ----------
    x : Any
        The value to pack

    Returns
    -------
    dict | None : the packed value

    Examples
    --------
    >>> import qbandas
    >>> qbandas.pack._pack_default('Object')
    {'value': 'Object'}
    >>> qbandas.pack._pack_default(None) == None
    True

    """

    if pd.isna(x):
        return None
    return {'value':x}

def _pack_duration(x: float|int|str|None, unit: str = 'seconds') -> dict|None:
    """
    Pack a number into duration format for the QuickBase API
    
    Parameters
    ----------
    x : float | int | str | None
        The value to pack.
    unit : str
        the duration unit 'seconds' or 'milliseconds'. Defaults to 'seconds'

    Returns
    -------
    dict | None : the packed value

    Examples
    --------
    >>> import qbandas
    >>> qbandas.pack._pack_duration(15)
    {'value': 15000}
    >>> qbandas.pack._pack_duration(15, unit = 'milliseconds')
    {'value': 15}
    >>> qbandas.pack._pack_duration(None) == None
    True

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


    
def _pack_date(x: datetime|str|None, format: str = "%m.%d.%Y") -> dict|None:
    """
    Pack a date into the date format for the QuickBase API

    Parameters
    ----------
    x :  datetime | str | None
        The value to pack
    format : str
        the format to decode str dates. Defaults to "%m.%d.%Y"

    Returns
    -------
    dict | None : the packed value

    Examples
    --------
    >>> import qbandas
    >>> from datetime import datetime as dt
    >>> qbandas.pack._pack_date('11.22.1972')
    {'value': '1972-11-22'}
    >>> qbandas.pack._pack_date(dt(day=10, month=5, year=1754))
    {'value': '1754-05-10'}
    >>> qbandas.pack._pack_date('Friday, Nov 11, 2022', format='%A, %b %d, %Y')
    {'value': '2022-11-11'}
    >>> qbandas.pack._pack_date(None) == None
    True

    """
    if pd.isna(x):
        return None

    if not isinstance(x, (datetime, str)):
        raise Exception(f"value {x} of type {type(x)} cannot be coerced to date")
    elif isinstance(x, str):
        x = datetime.strptime(x, format)

    return {'value':x.strftime('%Y-%m-%d')}

    

def _pack_datetime(x: datetime|str|None, format: str = '%d%b%Y:%H:%M:%S.%f') -> dict|None:
    """
    Pack a datetime into the datetime format for the QuickBase API
    
    Parameters
    ----------
    x : datetime | str | None
        The value to pack
    format : str
        the format used to decode datetime strings, default '%d%b%Y:%H:%M:%S.%f'

    Returns
    -------
    dict | None : the packed value

    Examples
    --------
    >>> import qbandas
    >>> from datetime import datetime as dt
    >>> qbandas.pack._pack_datetime('30Nov1974:14:56:08.967')
    {'value': '1974-11-30T14:56:08Z'}
    >>> qbandas.pack._pack_datetime(dt(day=10, month=5, year=1754, minute=24))
    {'value': '1754-05-10T00:24:00Z'}
    >>> qbandas.pack._pack_datetime('Friday, Nov 11, 2022 at 9:30 AM', format='%A, %b %d, %Y at %H:%M %p')
    {'value': '2022-11-11T09:30:00Z'}
    >>> qbandas.pack._pack_datetime(None) == None
    True

    """
    
    if pd.isna(x):
        return None

    if not isinstance(x, (datetime, str)):
        raise Exception(f"'{type(x)}' cannot be coerced to datetime")
    elif isinstance(x, str):
        x = datetime.strptime(x, format)
    
    return {'value':x.strftime('%Y-%m-%dT%H:%M:%SZ')}

   

def _pack_phonenum(x: None|str, format: str = "##########") -> dict|None:
    """
    Pack a phone string into the phone format for the QuickBase API
    
    Parameters
    ----------
    x : None | str
        The value to pack. It should be a string
    format : str
        the format string for reading the phone number. The phone number "(123) 456-7890 x123" would have the format string "(###) ###-#### x###". The extension must come last. It is optional for x to include it.

    Returns
    -------
    dict | None : the packed value

    Examples
    --------
    >>> import qbandas
    >>> qbandas.pack._pack_phonenum('9205551234')
    {'value': '(920) 555-1234'}
    >>> qbandas.pack._pack_phonenum('<920>888.1234x553', format = '<###>###.####x###')
    {'value': '(920) 888-1234 x553'}
    >>> qbandas.pack._pack_phonenum(None) == None
    True

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

# a string to func mapping allowing the packing funcs to be assigned in data/field_types.json
PACKING_FUNCS: dict[str, Callable[..., dict|None]] = {
    'default': _pack_default,
    'duration': _pack_duration,
    'date': _pack_date,
    'datetime': _pack_datetime,
    'phonenum': _pack_phonenum,
    }