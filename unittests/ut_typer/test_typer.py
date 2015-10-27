#!/usr/bin/env python3

import sys
import os
cur_path = os.getcwd()
while not cur_path.endswith('KOOC'):
    cur_path = cur_path[:cur_path.rfind('/')]
sys.path.append(cur_path)
import unittest
import cnorm
import mangler
from kooc_class import *
import kooc_typer
import decl_keeper

class ManglerTestCase(unittest.TestCase):
    
        def setUp(self):
            decl_keeper.reset()
            self.kooc = Kooc()

        def tearDown(self):
            pass


        def test_int(self):
            ast = self.kooc.parse("int a = 42;")
            ast.resolve_type()
            print(repr(ast.body[0].expr_type))


        def test_ptr(self):
            ast = self.kooc.parse("char* a = 0;")
            ast.resolve_type()
            print(repr(ast.body[0].expr_type))

        def test_ptr_deep(self):
            ast = self.kooc.parse("char * const * a = 0;")
            ast.resolve_type()
            print(repr(ast.body[0].expr_type))

        def test_func(self):
            ast = self.kooc.parse("int main();")
            ast.resolve_type()
            print(repr(ast.body[0].expr_type))

        def test_func_params(self):
            ast = self.kooc.parse("int main(int argc, char **argv);")
            ast.resolve_type()
            print(repr(ast.body[0].expr_type))


        def test_simple_func_call(self):
           ast = self.kooc.parse("int main(int argc, char **argv){ main(1, 0); }")
           ast.resolve_type() 
           print(repr(ast.body[0].expr_type))
           print(ast.body[0].body.body[0].expr.expr_type)

        def test_literal_str(self):
            ast = self.kooc.parse(""" char* a = "lol"; """)
            ast.resolve_type()
            print(repr(ast.body[0]._assign_expr.expr_type))

        def test_literal_int(self):
            ast = self.kooc.parse(""" int a = 12; """)
            ast.resolve_type()
            print(repr(ast.body[0]._assign_expr.expr_type))

        def test_dereference(self):
            ast = self.kooc.parse("int *a = 0; int b = *a;")
            ast.resolve_type()
            print(repr(ast.body[1]._assign_expr.expr_type))

        def test_getadress(self):
            ast = self.kooc.parse("int a = 0; int b = &a;")
            ast.resolve_type()
            print(repr(ast.body[1]._assign_expr.expr_type))


        def test_array(self):
            ast = self.kooc.parse("int a[12]; int b = a[0];")
            ast.resolve_type()
            print(repr(ast.body[1]._assign_expr.expr_type))
