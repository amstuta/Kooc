#!/usr/bin/env python3

import sys
import os
filePath = os.path.realpath(os.path.dirname(__file__))
sys.path.append(filePath + '/../..')
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

        def test_struct(self):
            ast = self.kooc.parse("struct Test { int a; int b; };")
            ast.resolve_type()
            print(repr(ast.body[0].expr_type))

        def test_struct_decl(self):
            ast = self.kooc.parse("""
                int f(int x);
                struct Test { int a; int b; };
                struct Test a = { f(0), 2 };
                """)
            ast.resolve_type()
            print(repr(ast.body[2]._assign_expr.expr_type))

        def test_module(self):
            ast = self.kooc.parse("""
            @module A
            {
                int a;
                float b;
            };
            """)
            print(ast.body)
