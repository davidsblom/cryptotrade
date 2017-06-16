# Copyright 2017 Ihar Hrachyshka <ihar.hrachyshka@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import tempfile
import unittest

from cryptotrade import config


class TestGetConfig(unittest.TestCase):

    def setUp(self):
        super(TestGetConfig, self).setUp()
        self.fp, self.fname = tempfile.mkstemp()
        os.close(self.fp)

    def tearDown(self):
        os.remove(self.fname)
        super(TestGetConfig, self).tearDown()

    def test_empty_file(self):
        self.assertRaises(config.TargetNotFound, config.get_config, self.fname)

    def test_file_with_ini_contents(self):
        contents = (
            '[core]\n'
            'opt0 = val0\n'
            'target = ETH=0.5;BTC=0.5\n'
            '[poloniex]\n'
            'opt1 = val1\n'
            'opt2 = val2\n'
            '[unknown]\n'
            'opt3 = val3\n'
        )
        with open(self.fname, 'w') as f:
            f.write(contents)
        res = config.get_config(self.fname)
        self.assertIn('core', res)
        self.assertIn('poloniex', res)
        self.assertNotIn('unknown', res)

    def test_target(self):
        contents = (
            '[core]\n'
            'target = ETH=0.5;BTC=0.3;XMR=0.2\n'
        )
        with open(self.fname, 'w') as f:
            f.write(contents)
        res = config.get_config(self.fname)
        target = res.get('core', {}).get('target', {})
        self.assertEqual(
            {'ETH': 0.5, 'BTC': 0.3, 'XMR': 0.2}, target)

    def test_target_numbers_dont_add_up_to_1(self):
        contents = (
            '[core]\n'
            'target = ETH=0.3;BTC=0.8;XMR=0.3\n'
        )
        with open(self.fname, 'w') as f:
            f.write(contents)
        self.assertRaises(
            config.UnbalancedTarget, config.get_config, self.fname)