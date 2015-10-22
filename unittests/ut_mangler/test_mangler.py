#!/usr/bin/env python

import sys
import os
cur_path = os.getcwd()
while not cur_path.endswith('Kooc'):
    cur_path = cur_path[:cur_path.rfind('/')]
sys.path.append(cur_path)
import unittest
import cnorm
import mangler

class ManglerTestCase(unittest.TestCase):
        def setUp(self):
                pass

        def tearDown(self):
                pass

        def test_complete_mangle(self):
                print('\033[35mTest Mangling complet')
                ex_decl = cnorm.nodes.Decl('i', cnorm.nodes.PrimaryType('int'))
                self.assertEqual(mangler.muckFangle(ex_decl, 'A'), 'Var$A$i$$int', 'incorrect complete mangling')

        def test_simple_mangle(self):
                print('Test Mangling simple\033[0m')

                # void clean(Object*);
                decl_clean = cnorm.nodes.Decl('clean', cnorm.nodes.PrimaryType(''))
                setattr(decl_clean._ctype, '_decltype', cnorm.nodes.PointerType())
                setattr(decl_clean._ctype._decltype, '_decltype', cnorm.nodes.ParenType([cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('Object'))]))
                setattr(decl_clean._ctype._decltype._decltype._params[0]._ctype, '_decltype', cnorm.nodes.PointerType())
                self.assertEqual(mangler.mimpleSangle(decl_clean), 'clean$P$', 'incorrect simple mangling')




if __name__ == '__main__':
        print('\033[32mTests du Mangler:\033[0m\n')
        unittest.main()
