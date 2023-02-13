import sys, os; sys.path.append(os.path.abspath(".."));
import src.qbandas as qb;
import pandas as pd

import src.qbandas.util as util

if __name__ == '__main__':
    
    # create a df for testing 
    df = pd.read_csv("data.csv")
    print("DATA: ", df)

    # test reading a schema from json
    schema = qb.read_schema('schema.json')
    print("SCHEMA: ")
    print("COL_TYPES: ", util.str_dict(schema[0]))
    print("FIDS: ", util.str_dict(schema[1]))

    # transform the data
    out = qb.format_values(df, schema[0])
    print("FORMATTED: ", out)

    out = qb.list_records(out, schema[1])
    print("RECORDS: ", util.str_dict(out))


