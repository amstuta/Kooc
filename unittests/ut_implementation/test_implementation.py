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
        create_header()
        self.kooc = Kooc()
        decl_keeper.reset()

    def tearDown(self):
        pass


    def rmNull(self, str):
        return str.replace(' ', '').replace('\n', '')

    def test_implementation_simple(self):
        res = self.kooc.parse("""
        @module Test
        {
        }
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
        self.assertEqual(self.rmNull(str(res.to_c())),
                         self.rmNull(expected),
                         'Incorrect output for simple implementation test')


    def test_implementation_second(self):
        res = self.kooc.parse("""
        @module A
        {}
        @module B
        {}
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
        self.assertEqual(self.rmNull(str(res.to_c())),
                         self.rmNull(expected),
                         'Incorrect output for second implementation test')

    def test_implementation_new_simple(self):
        res = self.kooc.parse("""
        @class A {
        @member void init(int);
        }
        @implementation A {
        void init(int a) {
        }
        }
        """)
        expected = """
        A *Func$A$new$P$A$$int(int a)
        {
        A *self;
        self = Func$A$alloc$P$A();
        Func$A$init$$void$P$A$$int(self, a);
        ((Object *) self)->name = "A";
        ((Object *) self)->vt = vtable_A;
        ((Object *) self)->inheritance = malloc((1 + 1) * sizeof (char *));
        ((Object *) self)->inheritance[0] = "Object";
        ((Object *) self)->inheritance[1] = NULL;
        return (self);
        }
        """
        for decl in res.body:
            if hasattr(decl, '_name') and decl._name == 'Func$A$new$P$A$$int' and hasattr(decl, 'body'):
                self.assertEqual(self.rmNull(str(decl.to_c())),
                                 self.rmNull(expected),
                                 'Fail test implementation new simple')
                return
        self.assertTrue(False, 'Fail test implementation new simple : (Decl not found)')


    def test_implementation_new_with_inheritance(self):
        res = self.kooc.parse("""
        @class A {
        @member void init(int);
        }

        @implementation A {
        void init(int a) {
        }

        }

        @class B : A {
        @member void init(int);
        }

        @implementation B {
        void init(int b);
        }

        """)
        expected = """
        B *Func$B$new$P$B$$int(int b)
        {
        B *self;
        self = Func$B$alloc$P$B();
        Func$B$init$$void$P$B$$int(self, b);
        ((Object *) self)->name = "B";
        ((Object *) self)->vt = vtable_B;
        ((Object *) self)->inheritance = malloc((2 + 1) * sizeof (char *));
        ((Object *) self)->inheritance[0] = "A";
        ((Object *) self)->inheritance[1] = "Object";
        ((Object *) self)->inheritance[2] = NULL;
        return (self);
        }
        """
        for decl in res.body:
            if hasattr(decl, '_name') and decl._name == 'Func$B$new$P$B$$int' and hasattr(decl, 'body'):
                self.assertEqual(self.rmNull(str(decl.to_c())),
                                 self.rmNull(expected),
                                 'Fail test implementation new simple with inheritance')
                return
        self.assertTrue(False, 'Fail test implementation new simple with inheritance : (Decl not found)')

    def test_implementation_double_new_simple(self):
        res = self.kooc.parse("""
        @class A {
        @member void init(int);
        @member void init(float);
        }

        @implementation A {
        void init(int a) {
        }
        void init(float a) {
        }
        }
        """)
        expected = """
        A *Func$A$new$P$A$$int(int a)
        {
        A *self;
        self = Func$A$alloc$P$A();
        Func$A$init$$void$P$A$$int(self, a);
        ((Object *) self)->name = "A";
        ((Object *) self)->vt = vtable_A;
        ((Object *) self)->inheritance = malloc((1 + 1) * sizeof (char *));
        ((Object *) self)->inheritance[0] = "Object";
        ((Object *) self)->inheritance[1] = NULL;
        return (self);
        }
        """

        expected2 = """
        A *Func$A$new$P$A$$float(float a)
        {
        A *self;
        self = Func$A$alloc$P$A();
        Func$A$init$$void$P$A$$float(self, a);
        ((Object *) self)->name = "A";
        ((Object *) self)->vt = vtable_A;
        ((Object *) self)->inheritance = malloc((1 + 1) * sizeof (char *));
        ((Object *) self)->inheritance[0] = "Object";
        ((Object *) self)->inheritance[1] = NULL;
        return (self);
        }
        """

        for decl in res.body:
            if hasattr(decl, '_name') and decl._name == 'Func$A$new$P$A$$int' and hasattr(decl, 'body'):
                self.assertEqual(self.rmNull(str(decl.to_c())),
                                 self.rmNull(expected),
                                 'Fail test implementation new simple with inheritance')
            if hasattr(decl, '_name') and decl._name == 'Func$A$new$P$A$$float' and hasattr(decl, 'body'):
                self.assertEqual(self.rmNull(str(decl.to_c())),
                                 self.rmNull(expected2),
                                 'Fail test implementation new double')
                return
        self.assertTrue(False, 'Fail test implementation new double : (Decl not found)')


    def test_implementation_alloc_simple(self):
        res = self.kooc.parse("""
        @class A {
        @member void init(int);
        }
        @implementation A {
        void init(int a) {
        }
        }
        """)
        expected = """
        A *Func$A$alloc$P$A()
        {
        A *self;
        self = malloc(sizeof (A));
        return (self);
        }
        """
        for decl in res.body:
            if hasattr(decl, '_name') and decl._name == 'Func$A$alloc$P$A' and hasattr(decl, 'body'):
                self.assertEqual(self.rmNull(str(decl.to_c())),
                                 self.rmNull(expected),
                                 'Fail test implementation alloc simple')
                return
        self.assertTrue(False, 'Fail test implementation alloc simple : (Decl not found)')

    def test_implementation_delete_simple(self):
        res = self.kooc.parse("""
        @class A {
        @member void init(int);
        }
        @implementation A {
        void init(int a) {
        }
        }
        """)
        expected = """
        void Func$A$delete$$void$P$A(A *self)
        {
        ((Object *) self)->vt->clean$$void(self);
        }
        """
        for decl in res.body:
            if hasattr(decl, '_name') and decl._name == 'Func$A$delete$$void$P$A' and hasattr(decl, 'body'):
                self.assertEqual(self.rmNull(str(decl.to_c())),
                                 self.rmNull(expected),
                                 'Fail test implementation delete simple')
                return
        self.assertTrue(False, 'Fail test implementation delete simple : (Decl not found)')
