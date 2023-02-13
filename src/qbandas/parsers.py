import pandas as pd
from datetime import datetime

def parse_default(x: object, args: tuple) -> dict:
    """ Pack a value into the default QuickBase API format

    This function is designed to be applied to column from a pd.DataFrame.

    Parameters
    ----------
    x
        The value to pack. It can be anything.
    args
        UNUSED

    Returns
    -------
    the packed value
    """

    if len(args):
        raise Exception("Default columns take no arguments.")
    if pd.isna(x):
        return None
    return {'value':x}


def parse_duration(x: float|int, args: tuple) -> dict:
    """ Pack a number into a duration format for the QuickBase API
    
    Parameters
    ----------
    x
        The value to pack. It should be a number.
    args : tuple
        Arg zero is the duration unit 'seconds' or 'milliseconds'. Defaults to 'seconds'

    Returns
    -------
    the packed value
    """
    if pd.isna(x):
        return None

    units = args[0] if len(args) else 'seconds'

    if units == 'seconds':
        x *= 1000
    elif units == 'milliseconds':
        pass
    else:
        raise Exception(f"'{args[0]}' is not a valid duration unit")

    return {'value':int(x)}
    
def parse_date(x: datetime|str, args: tuple) -> dict:
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

    format = args[0] if len(args) else "%m.%d.%Y"

    if not isinstance(x, (datetime, str)):
        raise Exception(f"'{type(x)}' cannot be coerced to date")
    elif isinstance(x, str):
        x = datetime.strptime(x, format)

    return {'value':x.strftime('%Y-%m-%d')}

def parse_datetime(x: datetime|str, args: tuple) -> dict:
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

    format = args[0] if len(args) else '%d%b%Y:%H:%M:%S.%f'

    if not isinstance(x, (datetime, str)):
        raise Exception(f"'{type(x)}' cannot be coerced to datetime")
    elif isinstance(x, str):
        x = datetime.strptime(x, format)
    
    return {'value':x.strftime('%Y-%m-%dT%H:%M:%SZ')}


def parse_phonenum(x: None|str, args: tuple) -> dict:
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
    format = args[0] if len(args) else "##########"
    
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