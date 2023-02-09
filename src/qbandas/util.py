import requests, json, re

def pretty_str(r: requests.Response) -> str:
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
    pattern = r"\[[\d,\s]+\]"
    matches = re.findall(pattern, text)
    for match in matches:
        n = match.count(',') 
        text = text.replace(match, f"[...{n+1} items...]")
    return text