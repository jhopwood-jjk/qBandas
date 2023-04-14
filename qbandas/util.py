"""
Miscellaneous utility functions to make life a little easier
"""

import requests, json, re

def str_dict(x: dict, quotes: bool = False) -> str:
    """ 
    Makes a readable string out of a dictionary

    Parameters
    ----------
    x : dict
        the dictionary to stringify
    quotes : bool
        Flag to include quotes in the output. Defaults to False.

    Returns
    -------
    str : the stringified dictionary
    """
    text = json.dumps(x, indent=2)
    text = re.sub(r"\{\s*(\"value\": .*)\s*\}", r"{\1}", text)
    text = re.sub(r"\},\s*\{", r"}, {", text)
    if not quotes:
        text = re.sub("['\"]","", text)
    return text

def str_resp(r: requests.Response, quotes: bool = False) -> str:
    """ 
    Takes a resonse object and makes it into a string

    Parameters
    ----------
    r : requests.Response
        The response object with JSON
    quotes : bool
        Flag to include quotes in the output. Defaults to False.

    Returns
    -------
    str : a string representation
    """

    text = str_dict(r.json(), quotes)
    pattern = r"\[[\d,\s\n]+\]"
    matches = re.findall(pattern, text)
    for match in matches:
        n = match.count(',') 
        text = text.replace(match, f"[...{n+1} items...]")
    return text

