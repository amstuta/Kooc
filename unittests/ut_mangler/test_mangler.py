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
                print('\033[35mTest Mangling complet')
                ex_decl = cnorm.nodes.Decl('i', cnorm.nodes.PrimaryType('int'))
                self.assertEqual(self.mangler.muckFangle(ex_decl, 'A'), 'Var$A$i$$int', 'incorrect complete mangling')

        def test_simple_mangle(self):
                print('Test Mangling simple\033[0m')

                # void clean(Object*);
                decl_clean = cnorm.nodes.Decl('clean', cnorm.nodes.PrimaryType(''))
                setattr(decl_clean._ctype, '_decltype', cnorm.nodes.PointerType())
                setattr(decl_clean._ctype._decltype, '_decltype', cnorm.nodes.ParenType([cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('Object'))]))
                setattr(decl_clean._ctype._decltype._decltype._params[0]._ctype, '_decltype', cnorm.nodes.PointerType())
                self.assertEqual(self.mangler.mimpleSangle(decl_clean), 'clean$P$', 'incorrect simple mangling')




if __name__ == '__main__':
        print('\033[32mTests du Mangler:\033[0m\n')
        unittest.main()
