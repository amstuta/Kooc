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
        self.kooc = Kooc()
        pass

    def test_simpleClass(self):
        print('\033[35mTest Class simple\033[0m')
        res = self.kooc.parse("""
        @class A
        {
        
        }
        """)

        expected = """typedef struct {} A;"""

        self.assertEqual(str(res.to_c()).replace(" ", "").replace("\n", ""), expec, "Fail Test Class simple")
