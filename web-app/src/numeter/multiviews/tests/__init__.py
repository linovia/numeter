from plugin import Plugin_Manager_TestCase, Plugin_TestCase
from data_source import Data_Source_TestCase

def suite():
    import unittest
    TEST_CASES = (
        'multiviews.tests.plugin',
        'multiviews.tests.data_source',
    )
    suite = unittest.TestSuite()
    for t in TEST_CASES:
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite

