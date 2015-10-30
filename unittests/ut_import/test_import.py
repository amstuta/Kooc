f#!/usr/bin/env python

import sys
import os
filePath = os.path.realpath(os.path.dirname(__file__))
sys.path.append(filePath + '/../..')
import unittest
import cnorm
from kooc_class import *

class ImportTestCase(unittest.TestCase):
    
        def setUp(self):
            self.kooc = Kooc()

        def tearDown(self):
            pass

        def test_mangle_int(self):
            res = self.kooc.parse(""" @import "main.kh" """)
            expected = """ #include "main.h" """
            self.assertEqual(str(res.to_c()).replace(' ','').replace('\n',''),
                             expected.replace(' ',''),
                             'Incorrect output for import test')
