#!/usr/bin/env python

import sys
sys.path.insert(0,'../../')
import unittest
import cnorm
from mangler import *

class ManglerTestCase(unittest.TestCase):
        def setUp(self):
            self.mangler = Mangler.instance()

        def tearDown(self):
            self.mangler = None

        def test_complete_mangle(self):
            ex_decl = cnorm.nodes.Decl('i', cnorm.nodes.PrimaryType('int'))
            print(self.mangler.muckFangle(ex_decl, 'A'))
            self.assertEqual(self.mangler.muckFangle(ex_decl, 'A'), 'Var$B$i$int', 'incorrect complete mangling')


# Renvoit la fct de test
test = ManglerTestCase('test_complete_mangle')
testSuite = unittest.TestSuite()
testSuite.addTest(test)
