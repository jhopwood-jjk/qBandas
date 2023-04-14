import unittest
import os
from os.path import exists

from . import headers

class TestHeaders(unittest.TestCase):

    def setUp(self) -> None:
        '''Remove any leftover header files'''
        if exists(headers.HEADER_FILE_NAME):
            os.remove(headers.HEADER_FILE_NAME)

    def test_create(self):
        '''Test that it creates a headerfile'''
        headers.create()
        self.assertTrue(exists(headers.HEADER_FILE_NAME))

    def test_valid(self):
        '''Test that a valid headerfile is detected as such'''
        self.assertFalse(exists(headers.HEADER_FILE_NAME))
        headers.create(host='demo.quickbase.com', auth='QB-USER-TOKEN xxxxxx_xxx_x_xxxxxxxxxxxxxxxxxxxxxxxxxx')
        self.assertTrue(headers.valid(warn_=True))

    def test_invalid(self):
        '''Verify that this headerfile is invalid'''
        headers.create()
        self.assertFalse(headers.valid())

    def tearDown(self) -> None:
        '''Remove the header file we made'''
        os.remove(headers.HEADER_FILE_NAME)