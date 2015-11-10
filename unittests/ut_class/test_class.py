#! usr/bin/env python

import sys
import os
filePath = os.path.realpath(os.path.dirname(__file__))
sys.path.append(filePath + '/../..')
from kooc_class import *
import cnorm
import unittest

class ClassTestCase(unittest.TestCase):

    def setUp(self):
        create_header()
        self.kooc = Kooc()

        
    def test_typedef_class(self):
        res = self.kooc.parse(""" @class A {} """)
        expected = "typedef struct _kc_A A;"
        for decl in res.body:
            if hasattr(decl, '_name') and decl._name == 'A':
                self.assertEqual(str(decl.to_c()).replace(" ", "").replace("\n", ""),
                                 expected.replace(' ','').replace('\n',''),
                                 'Fail test typedef class')


    def test_empty_class_struct(self):
        res = self.kooc.parse("""@class A {}""")
        expected = """
        struct _kc_A {
        Object parent;
        };
        """
        for decl in res.body:
            if decl._ctype._identifier == '_kc_A' \
               and decl._ctype._storage == cnorm.nodes.Storages.AUTO:
                self.assertEqual(str(decl.to_c()).replace(' ','').replace('\n',''),
                                 expected.replace(' ','').replace('\n',''),
                                 'Fail test empty class: struct')


    def test_member_class_struct(self):
        res = self.kooc.parse("""
        @class A 
        {
        @member int i;
        @member float i;
        }
        """)
        expected = """struct _kc_A {
        Object parent;
        int Var$A$i$$int;
        float Var$A$i$$float;
        };"""
        for decl in res.body:
            if decl._ctype._identifier == '_kc_A' \
               and decl._ctype._storage == cnorm.nodes.Storages.AUTO:
                self.assertEqual(str(decl.to_c()).replace(' ','').replace('\n',''),
                                 expected.replace(' ','').replace('\n',''),
                                 'Fail test member class: struct')


    def test_member_class_protos(self):
        res = self.kooc.parse("""
        @class A
        {
        @member void *get_void();
        }
        """)
        expected = "void *Func$A$get_void$P$void$P$A(A *self);"
        for decl in res.body:
            if hasattr(decl, '_name') and decl._name == 'Func$A$get_void$P$void$P$A':
                self.assertEqual(str(decl.to_c()).replace(' ','').replace('\n',''),
                                 expected.replace(' ',''),
                                 'Fail test class member: proto')
                return
        self.assertTrue(False, 'Fail test class member: protos (Decl not found)')


    def test_virtual_class_vt(self):
        res = self.kooc.parse("""
        @class A
        {
        @virtual void *get_void();
        }
        """)
        expected = """
        struct _kc_vt_A {
        void (*clean$P$void)(Object *);
        int (*isKindOf$P$int)(Object *, const char *);
        int (*isKindOf$P$int)(Object *, Object *);
        int (*isInstanceOf$P$int)(Object *, const char *);
        int (*isInstanceOf$P$int)(Object *, Object *);
        void (**get_void$$void)(A *self);
        };
        """
        for decl in res.body:
            if decl._ctype._identifier == '_kc_vt_A' \
               and decl._ctype._storage == cnorm.nodes.Storages.AUTO:
                pass
                #self.assertEqual(str(decl.to_c()).replace(' ','').replace('\n',''),
                #                 expected.replace(' ','').replace('\n',''),
                #                 'Fail test virtual class: struct')


            

    def test_inheritance_simple(self):
        res = self.kooc.parse("""
        @class A {}
        @class B : A {} 
        """)
        expected = """
        struct _kc_B {
        A parent;
        };
        """
        for decl in res.body:
            if decl._ctype._identifier == '_kc_B' \
               and decl._ctype._storage == cnorm.nodes.Storages.AUTO:
                self.assertEqual(str(decl.to_c()).replace(' ','').replace('\n',''),
                                 expected.replace(' ','').replace('\n',''),
                                 'Fail test inheritance simple')



    def test_vtable_instanciation_simple(self):
        res = self.kooc.parse("""
        @class A
        {
        @virtual void get_void();
        }
        """)
        expected = """
        extern vt_A vtable_A;
        """
        for decl in res.body:
            if hasattr(decl, '_assign_expr') and isinstance(decl._assign_expr, cnorm.nodes.BlockInit):
                self.assertEqual(str(decl.to_c()).replace(' ','').replace('\n',''),
                                 expected.replace(' ','').replace('\n',''),
                                 'Fail test vtable instanciation simple')


    def test_vtable_instanciation_full(self):
        res = self.kooc.parse("""
        @class A
        {
        @virtual void get_void();
        }
        @class B : A
        {
        @virtual void izi();
        }
        """)
        expected = """
        extern vt_B vtable_B;
        """
        for decl in res.body:
            if hasattr(decl, '_name') and decl._name == 'vtable_B':
                self.assertEqual(str(decl.to_c()).replace(' ','').replace('\n',''),
                                 expected.replace(' ','').replace('\n',''),
                                 'Fail test vtable instanciation full')



    def test_class_full(self):
        res = self.kooc.parse("""
        @class A
        {
        @member int i;
        void  f();
        float f(int);
        @virtual int get_int();
        }
        """)
        expected = """
        typedef struct _kc_A A;
        typedef struct _kc_vt_A vt_A;
        
        struct _kc_vt_A
        {
        void (*clean$$void)(Object *);
        int (*isKindOf$$int$P$char)(Object *, const char *);
        int (*isKindOf$$int$P$Object)(Object *, Object *);
        int (*isInstanceOf$$int$P$char)(Object *, const char *);
        int (*isInstanceOf$$int$P$Object)(Object *, Object *);
        int (*get_int$$int)(A *self);
        };
        struct _kc_A
        {
        Object  parent;
        int     Var$A$i$$int;
        };
        A     *Func$A$alloc$P$A();
        void  Func$A$delete$$void$P$A(A *);
        void  Func$A$f$$void();
        float Func$A$f$$float$$int(int);
        int   Func$A$get_int$$int$P$A(A *self);
        extern vt_A vtable_A;
        """
        self.assertEqual(str(res.to_c()).replace(' ','').replace('\n', ''),
                         expected.replace(' ','').replace('\n',''),
                         'Incorrect output for full class test')


        


