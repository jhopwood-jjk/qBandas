import requests, json, re

def str_dict(x):
    """ Makes a readable string out of a dictionary
    """
    text = json.dumps(x, indent=2)
    text = re.sub(r"\{\s*(\"value\": .*)\s*\}", r"{\1}", text)
    text = re.sub(r"\},\s*\{", r"}, {", text)
    return text

def str_resp(r: requests.Response) -> str:
    """ Takes a resonse object and makes it into a string

    Parameters
    ----------
    r : requests.Response
        The response object with JSON

    Returns
    -------
    str : a string representation
    """

    text = str_dict(r.json())
    pattern = r"\[[\d,\s\n]+\]"
    matches = re.findall(pattern, text)
    for match in matches:
        n = match.count(',') 
        text = text.replace(match, f"[...{n+1} items...]")
    return text

