#!/usr/bin/env python

import sys
sys.path.insert(0,'../../')
import unittest
import cnorm
from kooc_class import *

class ModuleTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_module_simple(self):
        decl_i = cnorm.nodes.Decl('Var$A$i$$int', cnorm.nodes.PrimaryType('int'))
        setattr(decl_i, '_assign_expr', cnorm.nodes.Literal('1'))
        decl_f = cnorm.nodes.Decl('Func$A$f$$void', cnorm.nodes.FuncType('void', []))

        i_found = False
        f_found = False
        
        a = Kooc()
        res = a.parse_file('./ex_mod_1.kh')
        for elem in res.body:
            if elem == decl_i:
                i_found = True
            elif elem == decl_f:
                f_found = True

        self.assertTrue(i_found)
        self.assertTrue(f_found)


if __name__ == '__main__':
    print('\033[32mTests de Module:\033[0m\n')
    unittest.main()
