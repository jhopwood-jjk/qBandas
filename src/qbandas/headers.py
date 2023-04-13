import os
import re
import json
from os.path import join, exists as p_exists
from textwrap import dedent
from warnings import warn

HEADER_FILE_NAME = 'headers.json'

def create(interactive: bool = False, repair: bool = False, **kwargs) -> None:
    '''
    TODO investigate unit test failures 

    Create a header file if there isn't one

    Parameters
    ----------
    interactive : bool
        True means execution will pause and prompt you to give the content of the header file if it doesn't exist or needs repairs. False will dump a skeleton file. Default is False.
    repair : bool
        If the header file is invalid, it will be overwritten with either interactive input, or a template file. Default is False.
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

    cwd = os.getcwd() if not kwargs.get('dir') else kwargs['dir']

    # figure out what to do with existing file
    if exists(dir=cwd):
        if valid(dir=cwd):
            return
        elif not repair:
            return
        
    host = r'<demo.quickbase.com>'
    user = r'user'
    auth = r'<QB-USER-TOKEN xxxxxx_xxx_x_xxxxxxxxxxxxxxxxxxxxxxxxxx>'

    out_path = join(cwd, HEADER_FILE_NAME)

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
        f.write(dedent(f'''\
        {'{'}
            "QB-Realm-Hostname": "{host}",
            "User-Agent": "{user}",
            "Authorization": "{auth}"
        {'}'}\
        '''))

def exists(**kwargs) -> bool:
    '''
    Check if any header file exists

    Parameters
    ---------
    **kwargs 
        key word arguments

    Examples
    --------
    >>> import qbandas
    >>> qbandas.headers.create()
    >>> qbandas.headers.exists()
    True

    '''
    cwd = os.getcwd() if not kwargs.get('dir') else kwargs['dir']
    return p_exists(join(cwd, HEADER_FILE_NAME))
    

def valid(**kwargs) -> bool:
    '''
    TODO test this 

    Check if the header file in the current working directory is valid

    If a header file is valid, you will be able to make requests to the QuickBase API; however, these requests are not guaranteed to be authorized. If a header file doesn't exist, it is automaically invalid. 

    Parameters
    ----------
    **kwargs 
        key word arguments

    Returns
    -------
    bool : the validity of the header file

    Examples
    --------
    >>> import qbandas
    >>> qbandas.headers.create(repair=True)
    >>> qbandas.headers.valid()
    False

    '''

    cwd = os.getcwd() if not kwargs.get('dir') else kwargs['dir']

    # load in 
    header_path = join(cwd, HEADER_FILE_NAME)
    with open(header_path) as f:
        contents = json.load(f)

    # check the keys are correct
    if not {"QB-Realm-Hostname","User-Agent","Authorization"} == set(contents):
        warn(f'header file: {header_path} has invalid keys')
        return False

    # check hostname
    if not re.match(r'$[a-zA-Z]+\.quickbase\.com^', contents["QB-Realm-Hostname"]):
        warn(f'header file: {header_path} has invalid hostname')
        return False
    
    # check authorization
    if not re.match(r'$QB-(USER|TEMP)-TOKEN \w{6}-\w{3}-\w-\w{26}^', contents["Authorization"]):
        warn(f'header file: {header_path} has invalid authorization')
        return False

    return True