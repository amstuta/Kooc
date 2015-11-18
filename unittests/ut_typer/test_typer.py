#!/usr/bin/env python3

import sys
import os
filePath = os.path.realpath(os.path.dirname(__file__))
sys.path.append(filePath + '/../..')
import unittest
import cnorm
import mangler
from kooc_class import *
from kooc_typer import *
import decl_keeper

class TyperTestCase(unittest.TestCase):
        def setUp(self):
            decl_keeper.reset()
            self.kooc = Kooc()

        def tearDown(self):
            pass


        def test_cmp_types(self):
            t = Type("int")
            t2 = Type("int")
            self.assertTrue(t == t2)

        def test_cmp_types_false(self):
            t = Type("int")
            t2 = Type("float")
            self.assertFalse(t == t2)

        def test_cmp_ptrtype(self):
            t = Pointer(int_type)
            t2 = Pointer(int_type)
            self.assertTrue(t == t2)

        def test_cmp_ptrtype_false(self):
            t = Pointer(int_type)
            t2 = Pointer(char_type)
            self.assertFalse(t == t2)

        def test_cmp_ptrtype_void(self):
            t = voidptr_type
            t2 = Pointer(int_type)
            self.assertTrue(t == t2)

        def test_cmp_ptrtype_void2(self):
            t = voidptr_type
            t2 = Pointer(voidptr_type)
            self.assertTrue(t == t2)

        def test_cmp_func_noparam(self):
            t = Function(void_type)
            t2 = Function(void_type)
            t3 = Function(int_type)
            self.assertTrue(t == t2)
            self.assertFalse(t == t3)

        def test_cmp_func_param(self):
            t = Function(void_type, [ int_type, voidptr_type, int_type ])
            t2 = Function(void_type, [ int_type, voidptr_type, int_type ])
            t3 = Function(int_type, [ int_type, voidptr_type, int_type ])
            t4 = Function(void_type, [ int_type ])
            t5 = Function(void_type, [ int_type, void_type, int_type ])
            self.assertTrue(t == t2)
            self.assertFalse(t == t3)
            self.assertFalse(t == t4)
            self.assertFalse(t == t5)

        def test_cmp_var_types(self):
            t = Variable("idx", int_type)
            t2 = int_type
            self.assertTrue(t == t2)
            self.assertTrue(t2 == t)
            t3 = char_type
            self.assertFalse(t == t3)

        def test_cmp_var2(self):
            t = Variable("idx", int_type)
            t2 = int_type
            t3 = char_type
            self.assertTrue(t2.__eq__(t))
            self.assertFalse(t3.__eq__(t))

        def test_cmp_struct(self):
            field1 = int_type
            field2 = char_type
            field3 = voidptr_type
            t = Struct("%S", [ field1, field2, field3 ])
            t2 = Struct("%S", [ field1, field2, field3 ])
            t3 = Struct("%S", [ field2, field3, field1 ])
            self.assertTrue(t == t2)
            self.assertFalse(t3 == t)

        def test_set_eq(self):
            s = TypesSet([ int_type, char_type ])
            s2 = TypesSet([ int_type ])
            s3 = TypesSet([ voidptr_type ])
            s4 = TypesSet([ int_type, char_type ])
            self.assertFalse(s == s2)
            self.assertFalse(s == s3)
            self.assertTrue(s == s4)

        def test_set_intersect_type(self):
            s = TypesSet([ int_type, char_type ])
            self.assertTrue(s.intersect(void_type) is None)
            self.assertTrue(s.intersect(int_type) == int_type)

        def test_set_intersect_set(self):
            s = TypesSet([ int_type, char_type, str_type ])
            s2 = TypesSet([ voidptr_type, int_type, str_type ])
            r = s.intersect(s2)
            expected = TypesSet([ int_type, str_type ])
            self.assertTrue(r == expected)

        def test_int(self):
            ast = self.kooc.parse("int a = 42;")
            expected = Type("int")
            ast.resolve_type()
            self.assertTrue(ast.body[0].expr_type == expected)

        def test_ptr(self):
            ast = self.kooc.parse("char* a = 0;")
            expected = Pointer(Type("char"))
            ast.resolve_type()
            self.assertTrue(ast.body[0].expr_type == expected)

        def test_ptr_deep(self):
            ast = self.kooc.parse("char * const * a = 0;")
            ast.resolve_type()
            expected = Pointer(str_type)
            self.assertTrue(ast.body[0].expr_type == expected)

        def test_func(self):
            ast = self.kooc.parse("int main();")
            ast.resolve_type()
            expected = Function(int_type)
            self.assertTrue(ast.body[0].expr_type == expected)

        def test_func_params(self):
            ast = self.kooc.parse("int main(int argc, char **argv);")
            ast.resolve_type()
            expected = Function(int_type, [ int_type, Pointer(str_type) ])
            self.assertTrue(ast.body[0].expr_type == expected)


        def test_simple_func_call(self):
           ast = self.kooc.parse("int main(int argc, char **argv){ main(1, 0); }")
           ast.resolve_type()
           expected = int_type
           self.assertTrue(ast.body[0].body.body[0].expr.expr_type == expected)

        def test_literal_str(self):
            ast = self.kooc.parse(""" char* a = "lol"; """)
            ast.resolve_type()
            expected = str_type
            self.assertTrue(ast.body[0]._assign_expr.expr_type == expected)

        def test_literal_int(self):
            ast = self.kooc.parse(""" int a = 12; """)
            ast.resolve_type()
            expected = int_type
            self.assertTrue(ast.body[0]._assign_expr.expr_type == expected)

        def test_dot_array(self):
            ast = self.kooc.parse("""
                struct A { int a; };

                int main(int argc, char **argv)
                {
                    struct A a, *b;
                    return a.a;
                    return b->a;
                }
                """)
            ast.resolve_type()
            expected = int_type
            self.assertTrue(ast.body[1].body.body[2].expr.expr_type == expected)
            self.assertTrue(ast.body[1].body.body[3].expr.expr_type == expected)

        def test_paren(self):
            ast = self.kooc.parse("""
                int main(int argc, char **argv)
                {
                    return (1);
                }
                """)
            ast.resolve_type()
            expected = int_type
            self.assertTrue(ast.body[0].body.body[0].expr.expr_type == expected)


        def test_sizeof(self):
            ast = self.kooc.parse(""" int main() { return sizeof(int); } """)
            ast.resolve_type()
            expected = int_type
            self.assertTrue(ast.body[0].body.body[0].expr.expr_type == expected)

        def test_post(self):
            ast = self.kooc.parse(""" int main() { int a; a++; } """)
            ast.resolve_type()
            expected = int_type
            self.assertTrue(ast.body[0].body.body[1].expr.expr_type)

        def test_binary(self):
            ast = self.kooc.parse(""" int main() { return 1 == 2; } """)
            ast.resolve_type()
            expected = int_type
            self.assertTrue(ast.body[0].body.body[0].expr.expr_type)

        def test_typedef(self):
            ast = self.kooc.parse("""
                    typedef int z;
                    typedef struct a b;
                    struct a {
                        int a;
                    };

                    typedef struct x_s {
                        float a;
                    } x;
                    int main(int argc, char **argv)
                    {
                        z a = 12;
                        b b;
                        x c;
                        return c.a;
                    }
                    """)
            ast.resolve_type()
            expected = Type("float")
            self.assertTrue(ast.body[4].body.body[3].expr.expr_type == expected)

        def test_dereference(self):
            ast = self.kooc.parse("int *a = 0; int b = *a;")
            ast.resolve_type()
            expected = int_type
            self.assertTrue(ast.body[1]._assign_expr.expr_type == int_type)

        def test_getadress(self):
            ast = self.kooc.parse("int a = 0; int b = &a;")
            ast.resolve_type()
            expected = Pointer(int_type)
            self.assertTrue(ast.body[1]._assign_expr.expr_type == expected)


        def test_array(self):
            ast = self.kooc.parse("int a[12]; int b = a[0];")
            ast.resolve_type()
            expected = int_type
            self.assertTrue(ast.body[1]._assign_expr.expr_type == expected)

        def test_struct(self):
            ast = self.kooc.parse("struct Test { int a; int b; };")
            ast.resolve_type()
            expected = Struct("Test", [ Variable("a", int_type), Variable("b", int_type) ])
            self.assertTrue(ast.body[0].expr_type == expected)

        def test_struct_decl(self):
            ast = self.kooc.parse("""
                int f(int x);
                struct Test { int a; int b; };
                struct Test a = { f(0), 2 };
                """)
            ast.resolve_type()
            expected = Struct("%S", [ int_type, int_type ])
            self.assertTrue(ast.body[2]._assign_expr.expr_type == expected)

        def test_module(self):
            ast = self.kooc.parse("""
            @module A
            {
                int a;
                float b;

                int f(int a);
                int f(float a);
                float f();
            };

            int main(int argc, char **argv)
            {
                return [A f :[A f :0]];
                return [A f :@!(float)[0]];
                return [A f];
                return [A f :argc];
            }
            """)
            ast.resolve_type()
            expected = int_type
            expected2 = Type("float")
            main_f = ast.body[5];
            self.assertTrue(main_f.body.body[0].expr.expr_type == expected)
            self.assertTrue(main_f.body.body[1].expr.expr_type == expected)
            self.assertTrue(main_f.body.body[2].expr.expr_type == expected2)
            self.assertTrue(main_f.body.body[3].expr.expr_type == expected)

        def test_bidon(self):
            ast = self.kooc.parse("int* p;")
            #print(ast.body)

        def test_class(self):
            from misc import create_header
            create_header()
            ast = self.kooc.parse("""
            @class B
            {
                @virtual int b(int a);
            }

            @class A : B
            {
                @member int c(int a);
            }

            int main(int argc, char **argv)
            {
                A *zzzz;
                [zzzz c :argc];

            }
            """)
            ast.resolve_type()

        def test_cast(self):
            ast = self.kooc.parse("""
                    int main() {
                        int b = @!(int)[1];
                    }
            """)
            ast.resolve_type()
            expected = int_type
            self.assertTrue(ast.body[0].body.body[0].expr_type == expected)

