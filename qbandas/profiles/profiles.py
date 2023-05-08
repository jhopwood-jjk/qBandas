import json
import os
import os.path as op
import re

from .. import USER_PATH


def set_profile(profile: str, *, host: str = None, user: str = None, 
                auth: str = None, temp_token: bool = False, 
                auto_user: bool = True) -> None:
    '''
    Configure a profile

    If no profile exists with the name `profile`, a new profile will be created. Unspecified arguments will not override existing profile 
    information.

    Parameters
    ----------
    name : str
        The name of the profile to configure
    host : str, optional
        The QuickBase realm hostname, by default None
    user : str, optional
        The name of the user agent, by default None
    auth : str, optional
        The QuickBase API token, by default None
    temp_token : bool, optional
        Specify if the API token is temporary, by default False
    auto_user : bool, optional
        Specify if this profile should automatically populate the user 
        argument with `profile`, by default True
        
    Exmaples
    --------
    >>> import qbandas as qq
    >>> qq.set_profile('example', host='sample', auth='12345')
    >>> qq._get_headers('example')
    {
        'QB-Realm-Hostname': 'sample.quickbase.com'
        'User-Agent': 'example'
        'Authorization': 'QB-USER-TOKEN 12345'
    }

    '''

    token_prefix = 'QB-TEMP-TOKEN ' if temp_token else 'QB-USER-TOKEN '
    generated = {
        'QB-Realm-Hostname': (host + '.quickbase.com') if host else None,
        'User-Agent': profile if auto_user and not user else user,
        'Authorization': (token_prefix + auth) if auth else None
    }
    
    # remove the Nones from both dictonaries
    current = {k: v for k, v in _get_headers(profile).items() if v}
    generated = {k: v for k, v in generated.items() if v}
    
    profile_path = _get_profile_path(profile)
    mode = 'w' if op.exists(profile_path) else 'x'
    with open(profile_path, mode) as f:
        json.dump(current | generated, f, indent = 4)
        
def list_profiles() -> list[str]:
    '''
    List all the usable profiles

    Profiles in this list are not guaranteed to authorize your requests.

    Returns
    -------
    list[str]
        The names of all the profiles
    '''
    
    files = os.listdir(op.join(USER_PATH, 'profiles'))    
    return [re.sub(r'\.json', '', x) for x in files]
    
def is_valid_profile(profile: str, talk: bool = False) -> bool:
    '''
    Check if a profile is usable

    If a profile is valid, you will be able to make requests to the 
    QuickBase API; however, these requests are not guaranteed to be 
    authorized. If a profile doesn't exist, it is automaically 
    invalid. 

    Parameters
    ----------
    profile : str
        The name of the profile to check
    talk : bool, optional
        Whether to tell you what is wrong with the profile's headers, by 
        default False
    
    Returns
    -------
    bool
        the validity of the profile

    Examples
    --------
    >>> import qbandas as qq
    >>> qq.create_profile()
    >>> qq.headers.valid()
    False

    '''
    
    headers = _get_headers(profile)
    
    def error(text):
        '''convenience function for returning an error'''
        import sys
        
        if talk:
            sys.stderr.write(text)
            sys.stderr.flush()
        return False

    if not headers:
        return error(f'profile {profile} does not exist\n')

    # check the keys are correct
    if not {"QB-Realm-Hostname", "User-Agent", "Authorization"} == set(headers):
        return error(f'profile {profile} has wrong keys\n')

    # check hostname
    if not (host := headers.get("QB-Realm-Hostname")):
        return error(f'profile {profile} has no hostname\n')
    if not re.match(r'^[\w\-]+\.quickbase\.com$', host):
        return error(f'profile {profile} has an invalid hostname\n')
    
    # check authorization
    if not (auth := headers.get("Authorization")):
        return error(f'profile {profile} has no api token\n')
    if not re.match(r'^QB-(USER|TEMP)-TOKEN \w{6}_\w{2,5}_\w_\w{20,30}$', auth):
        return error(f'profile {profile} has an invalid api token\n')

    return True

def _get_headers(profile: str) -> dict[str, str]:
    '''
    Read the API headers for a given profile
    
    If the profile doesn't exist, returns an empty dictionary

    Parameters
    ----------
    profile : str
        Check this profile for headers

    Returns
    -------
    dict[str, str] | None
        The API headers if the profile exists or None
    '''
    
    profile_path = _get_profile_path(profile)
    
    if op.exists(profile_path):
        with open(profile_path) as f:
            return json.load(f)
    return dict()

def _get_profile_path(profile: str) -> str:
    '''
    Get the file path to a profile json file

    Parameters
    ----------
    profile : str
        The name of the profile

    Returns
    -------
    str
        The path to the profile whether it exists or not
    '''
    
    return op.join(USER_PATH, 'profiles', profile + '.json')

def _del_profile(profile: str):
    '''
    Remove a profile from your saved list

    If the profile doesn't exist, do nothing

    Parameters
    ----------
    profile : str
        The name of the profile to remove
    '''
    
    profile_path = _get_profile_path(profile)
    if op.exists(profile_path): 
        os.remove(profile_path)
