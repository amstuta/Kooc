#! usr/bin/env python

import sys
import os
cur_path = os.getcwd()
while not cur_path.endswith('Kooc'):
    cur_path = cur_path[:cur_path.rfind('/')]
sys.path.append(cur_path)
import unittest
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
                break


    def test_empty_class_struct(self):
        res = self.kooc.parse("""@class A {}""")
        expected = """
        struct _kc_A {
        Object parent;
        };
        """
        for decl in res.body:
            if hasattr(decl, '_name') and decl._ctype._identifier == '_kc_A' \
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
            if hasattr(decl, '_name') and decl._ctype._identifier == '_kc_A' \
               and decl._ctype._storage == cnorm.nodes.Storages.AUTO:
                self.assertEqual(str(decl.to_c()).replace(' ','').replace('\n',''),
                                 expected.replace(' ','').replace('\n',''),
                                 'Fail test member class: struct')







        
