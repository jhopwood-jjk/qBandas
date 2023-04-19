"""
Run all tests for this package
"""

import os
from doctest import DocFileSuite
from os.path import dirname, exists, join, realpath
from unittest import TestLoader, TextTestRunner

this_dir = dirname(realpath(__file__))
pkg_dir = realpath(join(this_dir, ".."))

code_files = [f for f in os.listdir(this_dir) if '.py' in f]

loader = TestLoader()
runner = TextTestRunner()

suite = loader.discover(pkg_dir)
suite.addTests(DocFileSuite(*code_files))

runner.run(suite)

# clean up any leftover files from doc tests
from .headers import HEADER_FILE_NAME

if exists(HEADER_FILE_NAME):
    os.remove(HEADER_FILE_NAME)