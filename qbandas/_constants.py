'''
Constants for qBandas

Some of these can be modified, but modifying them is considered 
undefined behavior
'''

import configparser
import json
import os.path as op

from . import _pack

QB_PATH: str = op.dirname(op.realpath(__file__))

config = configparser.ConfigParser()
config.read(op.join(QB_PATH, 'data', 'config.ini'))
    
USER_PATH: str = op.expanduser(op.join(config['general']['base_dir'], 
                                config['general']['qbandas_dir']))
MAX_BATCH_RECORDS: int = int(config['records']['max_batch'])
TIMEZONE_OFFSET: int = int(config['timezone']['offset'])

with open(op.join(QB_PATH, 'data', 'field_types.json')) as f:
    FIELD_TYPES = json.load(f)
    
# resolve the packing functions
for _, cnfg in FIELD_TYPES.items():
    if cnfg["packing-function"]:
        cnfg["packing-function"] = getattr(_pack, cnfg["packing-function"])

