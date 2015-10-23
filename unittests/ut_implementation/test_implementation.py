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


class ImplementationTestCase(unittest.TestCase):
    def setUp(self):
        self.kooc = Kooc()
        pass

    def tearDown(self):
        pass

    def moduleTransfo(self, ast):

        for class_name in decl_keeper.implementations:
            imp = decl_keeper.implementations[class_name]
            for i in imp.imps:
                ast.body.append(i)
            ast.body.extend(imp.virtuals)


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


if __name__ == '__main__':
    print('\033[32mTests de implementation:\033[0m\n')
    unittest.main()
