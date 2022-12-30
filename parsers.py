import pandas as pd
from datetime import datetime
# import phonenumbers


def default(x: object) -> dict:
    """ Pack a value into the default QuickBase API format

    This function is designed to be applied to column from a pd.DataFrame.

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


def duration(x: float|int, col: str, units: str = 'milliseconds') -> dict:
    """ Pack a number into a duration format for the QuickBase API
    
    Parameters
    ----------
    x
        The value to pack. It should be a number.
    col
        The name of the column in the case of an exception
    units
        'seconds' or 'milliseconds'

    Returns
    -------
    the packed value
    """
    if pd.isna(x):
        return None

    if units == 'seconds':
        x *= 1000
    elif units == 'milliseconds':
        pass
    else:
        raise Exception(f"'{units}' is an invalid duration unit for "\
            f"column '{col}'")

    return {'value':int(x)}
    
def date(x: datetime|str, col: str, format: str = '%Y-%m-%d') -> dict:
    """ Pack a date into the date format for the QuickBase API
    
    Parameters
    ----------
    x
        The value to pack. It should be a datetime object or a string
    col
        The name of the column in the case of an exception
    format
        For help creating datetime format strings, vist 
        https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior.

    Returns
    -------
    the packed value
    """
    if pd.isna(x):
        return None

    if not isinstance(x, (datetime, str)):
        raise Exception(f"column '{col}' got invalid data type "\
            f"'{type(x)}', expected type datetime or str")
    elif isinstance(x, str):
        x = datetime.strptime(x, format)

    return {'value':x.strftime('%Y-%m-%d')}

def datetimes(x: datetime|str, col: str, format: str = '%d%b%Y:%H:%M:%S.%f') -> dict:
    """ Pack a datetime into the datetime format for the QuickBase API
    
    Parameters
    ----------
    x
        The value to pack. It should be a datetime object or a string
    col
        The name of the column in the case of an exception
    format
        For help creating datetime format strings, vist 
        https://www.programiz.com/python-programming/datetime/strptime.

    Returns
    -------
    the packed value
    """
    if pd.isna(x):
        return None

    if not isinstance(x, (datetime, str)):
        raise Exception(f"column '{col}' got invalid data type "\
            f"'{type(x)}', expected type datetime or str")
    elif isinstance(x, str):
        x = datetime.strptime(x, format)
    
    return {'value':x.strftime('%Y-%m-%dT%H:%M:%SZ')}


def phonenum(x: None|str, col: str, format: str= "##########") -> dict:
    """ Pack a phone string into the phone format for the QuickBase API
    
    Parameters
    ----------
    x
        The value to pack. It should be a string
    col
        The name of the column in the case of an exception
    format
        the format string for reading the phone number. The phone number 
        "(123) 456-7890 x123" would have the format string "(###) ###-#### x###"
        THe extension must come last. It is optional for x to include it.

    Returns
    -------
    the packed value
    """
    
    if pd.isna(x):
        return None
    
    if not isinstance(x, str):
        raise Exception(f"column '{col}' got invalid data type "\
            f"'{type(x)}', expected type str")

    # a str containing only the digits in order
    try:
        y = [x[i] for i in range(len(x)) if format[i] == '#']
        y = ''.join(y)
    except IndexError:
        raise Exception(f"column '{col}' got invalid data. "\
            f"could not parse '{x}' with format '{format}'") 

    if not y.isnumeric() or len(y) < 10:
        raise Exception(f"column '{col}' got invalid data. "\
            f"could not parse '{x}' with format '{format}'") 

    t = f'({y[0:3]}) {y[3:6]}-{y[6:10]}'
    if len(y) > 10:
        t = t + f' x{y[10:]}'

    #return "(123) 456-7890 x123"
    return {'value':t}