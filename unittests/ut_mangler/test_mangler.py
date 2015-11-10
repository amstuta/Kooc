#!/usr/bin/env python

import sys
import os
filePath = os.path.realpath(os.path.dirname(__file__))
sys.path.append(filePath + '/../..')
import unittest
import cnorm
import mangler
from kooc_class import *
import decl_keeper

class ManglerTestCase(unittest.TestCase):
    
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


        def test_mangle_int(self):
            res = self.kooc.parse("@module B {int i;}")
            self.moduleTransfo(res)
            decl = res.body[0]
            self.assertEqual(decl._name,
                             'Var$B$i$$int',
                             'Incorrect int mangling')

            
        def test_mangle_char(self):
            res = self.kooc.parse("@module B {char c;}")
            self.moduleTransfo(res)
            decl = res.body[0]
            self.assertEqual(decl._name,
                             'Var$B$c$$char',
                             'Incorrect char mangling')


        def test_mangle_pointer_char(self):
            res = self.kooc.parse("@module B {char *str;}")
            self.moduleTransfo(res)
            decl = res.body[0]
            self.assertEqual(decl._name,
                             'Var$B$str$P$char',
                             'Incorrect char* mangling')


        def test_mangle_function(self):
            res = self.kooc.parse("""@module B {void *f(); int strlen(char *);}""")
            expected = """
            void *Func$B$f$P$void();
            int  Func$B$strlen$$int$P$char(char*);
            """
            self.moduleTransfo(res)
            self.assertEqual(str(res.to_c()).replace(' ','').replace('\n',''),
                             expected.replace(' ','').replace('\n',''),
                             'Incorrect function mangling')

        def test_mangle_func_ptr(self):
            res = self.kooc.parse("""@module Ouesh {int *(*yoho)(int a, int b, int c, char *d, char **e, char ******t);}""")
            #expected = """
            #extern int *(*yoho)(int a, int b, int c, char *d, char **e, char ******t) Var$Ouesh$yoho$PFunc$int$$int$$int$$int$P$char$PP$char$PPPPPP$char;
            #"""
            self.moduleTransfo(res)
            decl = res.body[0]
            self.assertEqual(decl._name,
                             'Var$Ouesh$yoho$PFunc$$$int$$$int$$$int$$P$char$$PP$char$$PPPPPP$charP$int',
                             'Incorrect function pointer mangling')


            
