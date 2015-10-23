#!/usr/bin/env python

import sys
import os
cur_path = os.getcwd()
exe_path = os.path.dirname(os.path.abspath(__file__))
while not cur_path.endswith('Kooc'):
    cur_path = cur_path[:cur_path.rfind('/')]
sys.path.append(cur_path)
import unittest
import cnorm
from kooc_class import *
import decl_keeper


class ModuleTestCase(unittest.TestCase):
    def setUp(self):
        self.kooc = Kooc()
        pass

    def tearDown(self):
        pass

    def moduleTransfo(self, ast):
        for mod in decl_keeper.modules:
            if decl_keeper.modules[mod].recurs == False:
                for decl in decl_keeper.modules[mod].decls:
                    ast.body.append(decl)


    def test_module_simple(self):
        print('\033[35mTest Module simple\033[0m')
        
        res = self.kooc.parse("""
        @module A
        {
        int i = 0;
        void f();
        }
        """)
        
        expected = """
        int Var$A$i$$int = 0;
        void Func$A$f$$void();
        """
        self.moduleTransfo(res)
        self.assertEqual(str(res.to_c()).replace(' ', '').replace('\n', ''),
                         expected.replace(' ', '').replace('\n', ''),
                         'Incorrect output for simple module test')


    def test_module_overload1(self):
        res = self.kooc.parse("""
        @module A
        {
        int i = 0;
        float i = 1;
        void *i = NULL;
        void i(const char*);
        int  i(float, int, char);
        int  i(float, int);
        }
        """)

        expected = """
        int   Var$A$i$$int = 0;
        float Var$A$i$$float = 1;
        void  *Var$A$i$P$void = NULL;
        void  Func$A$i$$void$P$char(const char *);
        int   Func$A$i$$int$$float$$int$$char(float,int,char);
        int   Func$A$i$$int$$float$$int(float,int);
        """

        self.moduleTransfo(res)
        self.assertEqual(str(res.to_c()).replace(' ', '').replace('\n', ''),
                         expected.replace(' ', '').replace('\n', ''),
                         'Incorrect output for module overload test 1')



if __name__ == '__main__':
    print('\033[32mTests de Module:\033[0m\n')
    unittest.main()
