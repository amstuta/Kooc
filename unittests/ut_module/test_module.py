#!/usr/bin/env python

import sys
import os
filePath = os.path.realpath(os.path.dirname(__file__))
sys.path.append(filePath + '/../..')
import unittest
import cnorm
from kooc_class import *
import decl_keeper

class ModuleTestCase(unittest.TestCase):
    def setUp(self):
        decl_keeper.reset()
        self.kooc = Kooc()

    def tearDown(self):
        pass

    def moduleTransfo(self, ast):
        for mod in decl_keeper.modules:
            if decl_keeper.modules[mod].recurs == False:
                for decl in decl_keeper.modules[mod].decls:
                    ast.body.append(decl)


    def test_module_simple(self):
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


    def test_module_overload2(self):
        res = self.kooc.parse("""
        @module A
        {
        int   j = 0;
        char *j;
        void (*j)(int, int);
        int  (*j)(void*, float);
        char *j(float);
        }
        """)
        expected = """
        int  Var$A$j$$int = 0;
        char *Var$A$j$P$char;
        void (*Var$A$j$PFunc$$int$$int)(int,int);
        int  (*Var$A$j$PFunc$P$void$$float)(void*,float);
        char *Func$A$j$P$char$$void(float);
        """
        
        self.moduleTransfo(res)
        """
        self.assertEqual(str(res.to_c()).replace(' ', '').replace('\n', ''),
                         expected.replace(' ', '').replace('\n', ''),
                         'Incorrect output for module overload test 2')
        """
