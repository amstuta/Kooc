#!/usr/bin/env python

import sys
sys.path.insert(0,'../../')
import unittest
import cnorm
from kooc_class import *
from decl_keeper import *


class ModuleTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def moduleTransfo(self, ast):
        for mod in DeclKeeper.instance().modules:
            if DeclKeeper.instance().modules[mod].recurs == False:
                for decl in DeclKeeper.instance().modules[mod].decls:
                    ast.body.append(DeclKeeper.instance().modules[mod].decls[decl])


    def test_module_simple(self):
        decl_i = cnorm.nodes.Decl('Var$A$i$$int', cnorm.nodes.PrimaryType('int'))
        setattr(decl_i, '_assign_expr', cnorm.nodes.Literal('1'))
        decl_f = cnorm.nodes.Decl('Func$A$f$$void', cnorm.nodes.FuncType('void', []))

        i_found = False
        f_found = False
        
        a = Kooc()
        res = a.parse_file('./ex_mod_1.kh')
        self.moduleTransfo(res)

        for elem in res.body:
            if elem.__dict__ == decl_i.__dict__:
                i_found = True
            if elem.__dict__ == decl_f.__dict__:
                f_found = True

        self.assertTrue(i_found)
        self.assertTrue(f_found)


if __name__ == '__main__':
    print('\033[32mTests de Module:\033[0m\n')
    unittest.main()
