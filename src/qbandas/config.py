field_types = {
    "text": "string of text", 
    "rich-text": "html text", # supports html 
    "multi-line-text": "text with '\\n' support for newlines", # supports newline chars '\n'
    "multiple-choice-text": "string indicating selected option", # string equal to one of qb's choices
    "multi-select": "list of strings", # a list of strings equal to choices on qb
    "address": "composite field. there must be 4 columns in your datatframe for each address field on quickbase. street address, city, state, zip", # composite fields, requires multiple fids
    "email-address": "valid email adresses as strings",
    "url": "string of a url",
    "numeric": "int or float data",
    "numeric-percent": "supports floats from zero to one inclusive", # float 0 to 1
    "numeric-rating": "integer from one to five", # int 1 to 5
    "numeric-currency": "float indicating currency",
    "duration": "durration in milliseconds", # milliseconds
    "date": "date as a string or Datetime object. must specify date format as an argument eg. \"Y-D-M\" ", # eg. "2019-12-18"
    "datetime": "datetime as a string or a Datetime object. must specify datetime format as an argument eg. \"Y-D-M H:m:s\" ", # 'YYYY-MM-DDThh:mm:ssZ'
    "time-of-day": "military time as a string. must specify time-of-day format eg. \"hh:mm:ss.sss\"", # military time hh:mm:ss.sss
    "checkbox": "boolean as a int, string or bool. not case sensitve. false, 'no', 'n', 'f', 'false', 0 are all false, everything else is true except None", # bool
    "phone-number": "phone number as a string. must specify phone-number format eg. \"(###) ###-#### x####\" pound signs indicate digits. the first 10 digits are required, extension is optional.", # "(123) 456-7890 x123"
    "user": "dictionary containing the user data that must include the user's ID eg. { \"id\": \"123456.ab1s\" }", #   "value": 
    "list-user": "a list of user dicts", # list of user dicts
    "file-attachment": "Not supported",  # "value": {
                        #       "fileName": "report.pdf",
                        #       "data": "aHR0cHM6Ly9lbi53aWtpcGVkaWEub3JnL3dpa2kvQyUyQiUyQg=="
                        # }
                        # Base64 encoded file content
    "record-id": "int. default merge field", # int
    "lookup": "Not supported", # really unclear
    "summary": "Not supported" # really unclear
}