'''
Integrates the popular data handling library Pandas and the QuickBase 
API.
'''

def _setup():
    '''
    Onetime setup function for qBandas on import

    Do not run this. For interal use only
    '''
    
    import configparser
    import os
    import os.path as op
    
    global QB_PATH, USER_PATH, MAX_BATCH_RECORDS, TIMEZONE_OFFSET
    
    # field_types is the raw json to dict
    QB_PATH = op.dirname(op.realpath(__file__))
    
    config = configparser.ConfigParser()
    config.read(op.join(QB_PATH, 'data', 'config.ini'))
        
    USER_PATH = op.expanduser(op.join(config['general']['base_dir'], 
                                    config['general']['qbandas_dir']))
    
    MAX_BATCH_RECORDS = config['records']['max_batch']
    TIMEZONE_OFFSET = int(config['timezone']['offset'])
    
    try: os.makedirs(op.join(USER_PATH, 'profiles'))
    except FileExistsError: pass
        
    try: os.makedirs(op.join(USER_PATH, 'schemas'))
    except FileExistsError: pass
        
_setup()
del _setup

from .profiles import (_del_profile, _get_headers, _get_profile_path,
                       is_valid_profile, list_profiles, set_profile)
from .records import fetch_records, upload_records
from .schemas import (_read_schema, _write_schema, add_schema_args,
                      fetch_schema, list_schemas, set_schema_args)
