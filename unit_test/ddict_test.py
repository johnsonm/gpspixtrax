#!/usr/bin/python
#
# Copyright 2013 Michael K Johnson
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import unittest

from gpspixtrax import ddict

class Test_ddict(unittest.TestCase):
    def test_ddict_empty(self):
        d = ddict.ddict()
        self.assertEqual(not d, True)
        d = ddict.ddict({})
        self.assertEqual(not d, True)

    def test_ddict_attribute(self):
        d = ddict.ddict({'a':1})
        self.assertEqual(d['a'], 1)
        self.assertEqual(d.a, 1)
        self.assertRaises(KeyError, lambda: d['b'])
        self.assertRaises(KeyError, lambda: d.b)
        def assign():
            d.b = 4
        self.assertRaises(KeyError, assign)
        self.assertRaises(KeyError, lambda: d.b)
        d['b'] = 3
        self.assertEqual(d['b'], 3)
        self.assertEqual(d.b, 3)
        d.b = 4
        self.assertEqual(d['b'], 4)
        self.assertEqual(d.b, 4)
