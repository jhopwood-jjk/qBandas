field_types = [
    "text", 
    "rich-text", # supports html 
    "multi-line-text", # supports newline chars '\n'
    "multiple-choice-text", # string equal to one of qb's choices
    "multi-select", # a list of strings equal to choices on qb
    "address", # composite fields, requires multiple fids
    "email-address",
    "url",
    "numeric",
    "numeric-percent", # float 0 to 1
    "numeric-rating", # int 1 to 5
    "numeric-currency",
    "duration", # milliseconds
    "date", # eg. "2019-12-18"
    "datetime", # 'YYYY-MM-DDThh:mm:ssZ'
    "time-of-day", # military time hh:mm:ss.sss
    "checkbox", # bool
    "phone-number", # "(123) 456-7890 x123"
    "user", #   "value": { "id": "123456.ab1s" }
    "list-user", # list of user dicts
    "file-attachment",  # "value": {
                        #       "fileName": "report.pdf",
                        #       "data": "aHR0cHM6Ly9lbi53aWtpcGVkaWEub3JnL3dpa2kvQyUyQiUyQg=="
                        # }
                        # Base64 encoded file content
    "record-id", # int
    "lookup", # really unclear
    "summary" # really unclear
]