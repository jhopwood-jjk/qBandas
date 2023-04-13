'''
TODO unit testing

Testing suite for qBandas
'''

import sys
from os.path import (
    abspath,
    exists,
    join,
    realpath,
    dirname,
    )

import pandas as pd

here = realpath(dirname(__file__))
sys.path.append(abspath(join(here, '..')))

import src.qbandas as qb

def test_pull_schema():
    qb.pull_schema('bs397hfuy', dir=here)
    assert exists(join(here, 'schemas', 'bs397hfuy.json'))

def test_upload_records():
    df = pd.read_csv(join(here, 'data.csv'))
    try:
        qb.upload_records(df, "Example Table", drop=True, dir=here)
        assert True
    except:
        assert False



# qb.set_args("Example Table", "names", "nums", argy="Arga")
# qb.add_args("Example Table",  more_args="replacement!")
# qb.upload_records(df, "Example Table", debug=True, drop=True)


# qb.execute('''
# /* this is a comment */
# SELECT nums, names 
# FROM bs397hfuy
# WHERE nums < 2;
# ''') 

# qb.execute('SELECT nums, names FROM bs397hfuy WHERE nums < 2;')  


