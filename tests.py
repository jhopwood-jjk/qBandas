import qbandas as qb
import pandas as pd
import json

if __name__ == '__main__':
    
    # create a df for testing 
    data = {
        'nums' : [1, 2, 3, 4, 5, None, 7, 8, 9, 10],
        'names' : ["one", "two", "three", None, "five", "six", "seven", "eight", 
        "nine", "ten"],
        'dates' : ["1.14.2022", "2.27.2022", "3.29.2022", "4.29.2022", 
        "5.29.2022", "6.29.2022", "7.29.2022", "8.11.2022", pd.NA,
        "10.29.2022"],
        'drop_me' : ['kjdlf', 9, lambda x: x, None, int, str, 8.33, 'hello', 
        'world', 'josh'],
        'durr': [1, 2, 3, 4, 5, 6, 7, None, 8.3, 9.7],
        'dt' : [ '1 January 2022 10:16 PM', None, None, None, None, None, 
        None, None, None, None ],
        'phony':[ '555 687 5880x9237', '555.687.5880x9237', '555.687.5880', 
        None, None, None, None, None, None, None ]
    }
    df = pd.DataFrame(data)
    
    # test transforming the data
    col_types = {
        'nums' : 'numeric',
        'names' : 'text',
        'dates' : ('date', '%m.%d.%Y'),
        'drop_me' : 'drop',
        'durr' : ('duration', 'seconds'),
        'dt' : ('datetime', '%d %B %Y %H:%M %p'),
        'phony': ('phone', '###.###.####x####')
    }
    transformed = qb.transform(df, col_types=col_types)
    print(transformed)

    # test loading the data
    fids = {
        'nums' : '6',
        'names' : '7',
        'dates' : '8',
        'durr' : '9',
        'dt' : '10',
        'phony': '11'
    }
    out = qb.payloads(transformed, fids)
    print(json.dumps(out, indent=2))

    # test the full transform
    schema = {
        'nums' : (6, 'numeric'),
        'names' : (7, 'text'),
        'dates' : (8, 'date', '%m.%d.%Y'),
        'drop_me' : 'drop',
        'durr' : (9, 'duration', 'seconds'),
        'dt' : (10, 'datetime', '%d %B %Y %H:%M %p'),
        'phony': (11, 'phone', '###.###.####x####')
    }
    qb.full_transform(df, schema=schema)

