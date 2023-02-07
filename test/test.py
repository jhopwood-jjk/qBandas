import qbandas as qb
import pandas as pd
import json, re

def str_format_payloads(x):
    text = json.dumps(x, indent=2)
    text = re.sub(r"\{\s*(\"value\": .*)\s*\}", r"{\1}", text)
    text = re.sub(r"\},\s*\{", r"}, {", text)
    return text

if __name__ == '__main__':
    
    # create a df for testing 
    df = pd.read_csv("data.csv")
    print("parsing the following data...")
    print(df)

    # test reading a schema from json
    schema = qb.read_schema('schema.json')
    print("schema read from file...")
    print(json.dumps(schema, indent=2))

    # transform the data
    out = qb.full_transform(df, schema=schema)
    print("formatted data as...")
    print(str_format_payloads(out))


