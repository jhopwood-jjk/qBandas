'''
Manage qbandas profiles

Profiles control the authorization of all qbandas requests. Each profile
contains some set of QuickBase API headers.
'''

from .profiles import (_del_profile, _get_headers, _get_profile_path,
                       is_valid_profile, list_profiles, set_profile)
