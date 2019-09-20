import unittest
import os
import coverage
from mvm import db
from application import application




def test():
    """Runs the unit tests without coverage."""
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


"""Runs the unit tests with coverage."""
cov = coverage.coverage(
    branch=True,
    include='mvm/*'
)
cov.start()
tests = unittest.TestLoader().discover('tests')
unittest.TextTestRunner(verbosity=2).run(tests)
cov.stop()
cov.save()
cov.report()
basedir = os.path.abspath(os.path.dirname(__file__))
covdir = os.path.join(basedir, 'coverage')
cov.html_report(directory=covdir)
cov.erase()