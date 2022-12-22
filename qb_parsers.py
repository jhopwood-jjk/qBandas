import pandas as pd

def default(x):
    if pd.isna(x):
        return None
    return {'value':x}

