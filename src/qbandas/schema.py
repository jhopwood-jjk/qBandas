import shlex, json
import pandas as pd

def read_schema(path: str) -> tuple[dict, dict]:
    """ Read a schema from a JSON file and get a column types and field IDs dictionary

    Entries should have the format `"<column_name>": "<field_ID> <column_type> <*args>"`. This means each key is a column name, and each value is a field ID and column type plus additional formatting arguments. If you do not specify a column, it will be automatically dropped.
    
    Here is an example `schema.json`
    ```json
    {
        "PhoneNum": "7 phone ###.###.####",
        "FirstName": "8 text"
    }
    ```
    
    Parameters
    ----------
    path : str
        The location of the JSON file

    Returns
    -------
    tuple[dict, dict] : the first dictonary is the column types (plus any arguments) and the second is the field IDs
    """
    from .config import field_types
    col_types = {}
    fids = {}

    raw = json.load(open(path))
    
    for col in raw:
        value = shlex.split(raw[col])

        # check that everything is valid
        if len(value) < 2:
            raise Exception(f"column {col} has an invalid format {raw[col]}")
        if not str(value[0]).isdigit() or int(value[0]) < 1:
            raise Exception(f"column {col} has an invalid field ID {value[0]}")
        if not value[1] in field_types:
            raise Exception(f"column {col} has an invalid type {value[1]}")

        # save the arguments
        fids[col] = value[0]
        col_types[col] = value[1:]

    return col_types, fids

def write_schema(df: pd.DataFrame, path: str, space: int=32) -> None:
    """ Define a generic schema from a dataframe and write it to disk

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to create a schema from
    path : str
        The path to the file to write the schema to
    space : int
        number of chars after the tab but before the type string
    """
    mapping = {
        'int64': 'numeric',
        'float64': 'numeric',
        'object': 'text',
        'str': 'text',
        'bool': 'checkbox',
        'datetime': 'datetime'
    }
    with open(path, 'a') as f:
    
        # check python's column types and get a list of the schema counterparts
        types = map(str, df.dtypes)
        types = map(lambda x: mapping[x] if x in mapping else None, types)
        
        # magic
        out = '{\n'
        for col, typ in zip(df.columns, types):
            b = ' '*(space-len(col)) if len(col) < 16 else ' '
            out += f'\t"{col}":' + b + f'"000 {typ}",\n'
        out = out[:-2] + '\n}'

        f.write(out)