"""
Configures the types of columns supported by qbandas.

TODO convert this into a JSON file.
"""

from collections import namedtuple

from .pack import _pack_default, _pack_duration, _pack_date, _pack_datetime, _pack_phonenum

Info = namedtuple('Info', ['info', 'packing_func'])

field_types = {
    "text": Info(
        """string of text""",
        _pack_default),

    "rich-text": Info(
        """html text""",
        _pack_default),

    "multi-line-text": Info(
        """text with '\\n' support for newlines""",
        _pack_default),  

    "multiple-choice-text": Info(
        "string indicating selected option", 
        _pack_default),

    "multi-select": Info(
        "list of strings", 
        None),

    "address": Info(
        "composite field. there must be 4 columns in your datatframe for each address field on quickbase. street address, city, state, zip",
        _pack_default), 

    "email-address": Info(
        "valid email adresses as strings", 
        _pack_default),

    "url": Info(
        "string of a url", 
        _pack_default),

    "numeric": Info(
        "int or float data", 
        _pack_default),

    "numeric-percent": Info(
        "supports floats from zero to one inclusive",
        _pack_default), 

    "numeric-rating": Info(
        "integer from one to five", 
        _pack_default), 

    "numeric-currency": Info(
        "float indicating currency", 
        _pack_default),

    "duration": Info(
        "durration in milliseconds", 
        _pack_duration), 

    # eg. "2019-12-18"
    "date": Info(
        "date as a string or Datetime object. must specify date format as an argument eg. \"Y-D-M\" ", 
        _pack_date),

    # 'YYYY-MM-DDThh:mm:ssZ'
    "datetime": Info(
        "datetime as a string or a Datetime object. must specify datetime format as an argument eg. \"Y-D-M H:m:s\" ", 
        _pack_datetime),

    # military time hh:mm:ss.sss
    "time-of-day": Info(
        "military time as a string. must specify time-of-day format eg. \"hh:mm:ss.sss\"", 
        None),

    "checkbox": Info(
        "boolean as a int, string or bool. not case sensitve. false, 'no', 'n', 'f', 'false', 0 are all false, everything else is true except None", 
        _pack_default), 

    # "(123) 456-7890 x123"
    "phone-number": Info(
        "phone number as a string. must specify phone-number format eg. \"(###) ###-#### x####\" pound signs indicate digits. the first 10 digits are required, extension is optional.", 
        _pack_phonenum),

    # "value":
    "user": Info(
        "dictionary containing the user data that must include the user's ID eg. { \"id\": \"123456.ab1s\" }", 
        None),

    "list-user": Info(
        "a list of user dicts", 
        None),  # list of user dicts

    "file-attachment": Info(
        "Not supported", 
        None),

    "record-id": Info(
        "int. default merge field", 
        _pack_default),

    "lookup": Info(
        "Not supported", 
        None),

    "summary": Info(
        "Not supported", 
        None) 

}
