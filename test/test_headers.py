import os
import os.path as op
import unittest

import qbandas


class TestHeaders(unittest.TestCase):

    def setUp(self) -> None:
        '''Remove any leftover header files'''
        pass

    def test_create(self):
        '''Test that it creates a headerfile'''
        pass

    def test_valid(self):
        '''Test that a valid headerfile is detected as such'''
        pass

    def test_invalid(self):
        '''Verify that this headerfile is invalid'''
        pass

    def tearDown(self) -> None:
        '''Remove the header file we made'''
        pass