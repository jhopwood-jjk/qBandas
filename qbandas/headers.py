import os
import re
import json
from os.path import join, exists as p_exists
from warnings import warn

HEADER_FILE_NAME = 'headers.json'

DEFAULT_HOST = '<demo.quickbase.com>'
DEFAULT_USER = 'user'
DEFAULT_AUTH = '<QB-USER-TOKEN xxxxxx_xxx_x_xxxxxxxxxxxxxxxxxxxxxxxxxx>'

def create(interactive: bool = False, repair: bool = False, *, host: str = DEFAULT_HOST, user: str = DEFAULT_USER, auth: str = DEFAULT_AUTH, **kwargs) -> None:
    '''
    TODO investigate unit test failures 

    Create a header file if there isn't one

    Parameters
    ----------
    interactive : bool
        True means execution will pause and prompt you to give the content of the header file if it doesn't exist or needs repairs. False will dump a skeleton file. Default is False.
    repair : bool
        If the header file is invalid, it will be overwritten with either interactive input, or a template file. Default is False.
    host : str
        The QuickBase realm hostname
    user : str
        The name of the user agent
    auth : str
        The authorization or API token
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
        json.dump({
            'QB-Realm-Hostname': host,
            'User-Agent': user,
            'Authorization': auth
        }, f, indent=4)
    

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
    

def valid(*, warn_: bool = False, **kwargs) -> bool:
    '''
    TODO test this 

    Check if the header file in the current working directory is valid

    If a header file is valid, you will be able to make requests to the QuickBase API; however, these requests are not guaranteed to be authorized. If a header file doesn't exist, it is automaically invalid. 

    Parameters
    ----------
    warn_ : bool
        Warn you about what makes the headers file invalid
    **kwargs 
        key word arguments

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

    cwd = os.getcwd() if not kwargs.get('dir') else kwargs['dir']

    # load in 
    header_path = join(cwd, HEADER_FILE_NAME)
    with open(header_path) as f:
        contents = json.load(f)

    # check the keys are correct
    if not {"QB-Realm-Hostname","User-Agent","Authorization"} == set(contents):
        if warn_: warn(f'header file: {header_path} has invalid keys')
        return False

    # check hostname
    if not re.match(r'^[a-zA-Z]+\.quickbase\.com$', contents["QB-Realm-Hostname"]):
        if warn_: warn(f'header file: {header_path} has invalid hostname')
        return False
    
    # check authorization
    if not re.match(r'^QB-(USER|TEMP)-TOKEN \w{6}_\w{3}_\w_\w{26}$', contents["Authorization"]):
        if warn_: warn(f'header file: {header_path} has invalid authorization')
        return False

    return True