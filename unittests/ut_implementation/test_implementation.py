#!/usr/bin/env python

import sys
import os
filePath = os.path.realpath(os.path.dirname(__file__))
sys.path.append(filePath + '/../..')
import unittest
import cnorm
from kooc_class import *
import decl_keeper


class ImplementationTestCase(unittest.TestCase):
    def setUp(self):
        self.kooc = Kooc()
        decl_keeper.reset()

    def tearDown(self):
        pass

    def moduleTransfo(self, ast):
        for imp in decl_keeper.implementations:
            for i in imp.imps:
                ast.body.append(i)
            ast.body.extend(imp.virtuals)
        decl_keeper.clean_implementations()


    def test_implementation_simple(self):
        res = self.kooc.parse("""
        @implementation Test
        {
        int toto()
        {
        printf("je suis la fonction toto qui retourne un int\n");
        return (42);
        }
        void toto()
        {
        printf("je suis la fonction toto de base\n");
        }
        void toto(int n)
        {
        printf("je suis la fonction toto qui prend 1 parametre=%d\n", n);
        }
        }
        """)

        expected = """
        int Func$Test$toto$$int()
        {
        printf("je suis la fonction toto qui retourne un int\n");
        return (42);
        }
        void Func$Test$toto$$void()
        {
        printf("je suis la fonction toto de base\n");
        }
        void Func$Test$toto$$void$$int(int n)
        {
        printf("je suis la fonction toto qui prend 1 parametre=%d\n", n);
        }
        """
        self.moduleTransfo(res)
        self.assertEqual(str(res.to_c()).replace(' ', '').replace('\n', ''),
                         expected.replace(' ', '').replace('\n', ''),
                         'Incorrect output for simple implementation test')


    def test_implementation_second(self):
        res = self.kooc.parse("""
        @implementation A {
        void f() {}
        void f(int a, float b) {}
        char *f() {}
        }
        @implementation B {
        void f() {}
        void f(int a, float b) {}
        char *f() {}
        }
        """)
        expected = """
        void Func$A$f$$void() {}
        void Func$A$f$$void$$int$$float(int a, float b) {}
        char *Func$A$f$P$char() {}
        void Func$B$f$$void() {}
        void Func$B$f$$void$$int$$float(int a, float b) {}
        char *Func$B$f$P$char() {}
        """
        self.moduleTransfo(res)
        self.assertEqual(str(res.to_c()).replace(' ','').replace('\n',''),
                         expected.replace(' ','').replace('\n',''),
                         'Incorrect output for second implementation test')
