import os
import os.path as op
import shutil
import unittest

import qbandas

HERE = op.dirname(op.abspath(__file__))
TEMP_DIR = op.join(HERE, 'temp')
ORIG_DIR = qbandas.profiles.USER_PATH

class TestProfiles(unittest.TestCase):

    def setUpClass() -> None:
        shutil.copytree(ORIG_DIR, TEMP_DIR)
        qbandas.profiles.USER_PATH = TEMP_DIR
    
    def setUp(self) -> None:
        for profile in qbandas.list_profiles():
            qbandas._del_profile(profile)

    def test_list_empty(self):
        self.assertEqual(qbandas.list_profiles(), [])
        
    def test_list_add(self):
        qbandas.set_profile('p1')
        qbandas.set_profile('p2')
        qbandas.set_profile('p3')
        qbandas.set_profile('p4')
        self.assertEqual(qbandas.list_profiles(), ['p1', 'p2', 'p3', 'p4'])
        
    def test_list_add_del(self):
        qbandas.set_profile('p1')
        qbandas.set_profile('p2')
        qbandas.set_profile('p3')
        qbandas.set_profile('p4')
        qbandas._del_profile('p2')
        qbandas._del_profile('p4')
        self.assertEqual(qbandas.list_profiles(), ['p1', 'p3'])
        
    def test_valid_invalid1(self):
        qbandas.set_profile('p1', host='___***___')
        self.assertEqual(qbandas.is_valid_profile('p1'), False)
        
    def test_valid_invalid2(self):
        qbandas.set_profile('p1', auth='5555_8923570235_hjo213r8f')
        self.assertEqual(qbandas.is_valid_profile('p1'), False)

    def tearDown(self) -> None:
        pass

    def tearDownClass() -> None:
        shutil.rmtree(TEMP_DIR)
        qbandas.profiles.USER_PATH = ORIG_DIR