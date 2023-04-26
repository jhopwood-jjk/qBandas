import json
import os
import re
from os.path import exists as p_exists
from os.path import join
from pathlib import Path
from typing import NoReturn
from warnings import warn

HEADER_FILE_NAME = 'headers.json'

DEFAULT_HOST = '<demo.quickbase.com>'
DEFAULT_USER = 'user'
DEFAULT_AUTH = '<QB-USER-TOKEN xxxxxx_xxx_x_xxxxxxxxxxxxxxxxxxxxxxxxxx>'

def create(interactive: bool = False, repair: bool = False, *, 
           host: str = DEFAULT_HOST, user: str = DEFAULT_USER, 
           auth: str = DEFAULT_AUTH, directory: Path|str = None,
           **kwargs) -> None:
    '''
    Create a header file if there isn't one

    If this function does not create or repair a header file, it does 
    nothing.

    Parameters
    ----------
    interactive : bool
        True means execution will pause and prompt you to give the 
        content of the header file if it doesn't exist or needs 
        repairs. False will dump a skeleton file. Default is False.
    repair : bool
        If the header file is invalid, it will be overwritten with 
        either interactive input, or a template file. Default is False.
    host : str
        The QuickBase realm hostname
    user : str
        The name of the user agent
    auth : str
        The authorization or API token
    directory : None | Path | str
        The directory to use for this operation. Default is current
        
    **kwargs 
        key word arguments

    Exmaples
    --------
    >>> import qbandas
    >>> qbandas.headers.create()
    >>> print(open('headers.json').read())
    {
        "QB-Realm-Hostname": "<demo.quickbase.com>",
        "User-Agent": "user",
        "Authorization": "<QB-USER-TOKEN xxxxxx_xxx_x_xxxxxxxxxxxxxxxxxxxxxxxxxx>"
    }

    '''

    directory = directory if directory else os.getcwd()  
    if not os.path.isdir(directory):
        raise FileNotFoundError(f'{directory = } is not a valid directory')

    # figure out what to do with existing file
    if exists(directory = directory):
        if valid(directory = directory):
            return
        elif not repair:
            return

    out_path = join(directory, HEADER_FILE_NAME)

    if interactive:
        print(f'creating {out_path}')
        print(f'Enter realm hostname: (RETURN for {host})')
        if (input_ := input()):
            host = input_
        print(f'Enter user agent: (RETURN for {user})')
        if (input_ := input()):
            user = input_
        print(f'Enter authorization: (RETURN for {auth})')
        if (input_ := input()):
            auth = input_

    with open(out_path, 'w') as f:
        json.dump({
            'QB-Realm-Hostname': host,
            'User-Agent': user,
            'Authorization': auth
        }, f, indent=4)
    

def exists(directory: Path|str = None, **kwargs) -> bool:
    '''
    Check if any header file exists

    Parameters
    ---------
    **kwargs 
        key word arguments
    directory : None | Path | str
        The directory to use for this operation. Default is current

    Examples
    --------
    >>> import qbandas
    >>> qbandas.headers.create()
    >>> qbandas.headers.exists()
    True

    '''
    directory = directory if directory else os.getcwd()  
    if not os.path.isdir(directory):
        raise FileNotFoundError(f'{directory = } is not a valid directory')
    
    return p_exists(join(directory, HEADER_FILE_NAME))
    

def valid(*, directory: Path|str = None, warn_: bool = False, **kwargs) -> bool:
    '''
    Check if the header file in the current working directory is valid

    If a header file is valid, you will be able to make requests to the 
    QuickBase API; however, these requests are not guaranteed to be 
    authorized. If a header file doesn't exist, it is automaically 
    invalid. 

    Parameters
    ----------
    warn_ : bool
        Warn you about what makes the headers file invalid
    **kwargs 
        key word arguments
    directory : None | Path | str
        The directory to use for this operation. Default is current

    Returns
    -------
    bool : the validity of the headers file

    Examples
    --------
    >>> import qbandas
    >>> qbandas.headers.create(repair=True)
    >>> qbandas.headers.valid()
    False

    '''

    directory = directory if directory else os.getcwd()  
    if not os.path.isdir(directory):
        raise FileNotFoundError(f'{directory = } is not a valid directory')

    # load in 
    header_path = join(directory, HEADER_FILE_NAME)
    with open(header_path) as f:
        contents = json.load(f)

    # check the keys are correct
    if not {"QB-Realm-Hostname","User-Agent","Authorization"} == set(contents):
        if warn_: warn(f'header file: {header_path} has invalid keys')
        return False

    # check hostname
    if not re.match(r'^[\w\-]+\.quickbase\.com$',contents["QB-Realm-Hostname"]):
        if warn_: warn(f'header file: {header_path} has invalid hostname')
        return False
    
    # check authorization
    if not re.match(r'^QB-(USER|TEMP)-TOKEN \w{6}_\w{2,5}_\w_\w{20,30}$', contents["Authorization"]):
        if warn_: warn(f'header file: {header_path} has invalid authorization')
        return False

    return True


def read(directory: Path|str = None, **kwargs) -> dict[str, str]:
    '''
    Return the headers specified in the header file

    Parameters
    ----------
    **kwargs
        key word arguments
    directory : None | Path | str
        The directory to use for this operation. Default is current

    Returns
    -------
    dict[str, str] : the headers in headers.json
    '''

    directory = directory if directory else os.getcwd()  
    if not os.path.isdir(directory):
        raise FileNotFoundError(f'{directory = } is not a valid directory')

    if not exists(directory = directory):
        raise FileNotFoundError(f'No header file found in {directory}')
    
    if not valid(directory = directory, warn_=True):
        raise ValueError(f'header file in {directory} is invalid')
    
    with open(join(directory, HEADER_FILE_NAME)) as f:
        return json.load(f)
