"""
Run all tests for this package
"""

import os
import os.path as op
from doctest import DocFileSuite
from unittest import TestLoader, TextTestRunner

this_dir = op.dirname(op.realpath(__file__))
pkg_dir = op.realpath(op.join(this_dir, ".."))

code_files = [f for f in os.listdir(this_dir) if '.py' in f]

loader = TestLoader()
runner = TextTestRunner()

suite = loader.discover(pkg_dir)
suite.addTests(DocFileSuite(*code_files))

runner.run(suite)
