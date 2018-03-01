#!/usr/bin/python

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import os
import sys
import unittest

try:
    from sldr.ldml_exemplars import UCD
    from sldr.UnicodeSets import list2us
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))
    from sldr.ldml_exemplars import UCD
    from sldr.UnicodeSets import list2us


class UnicodeSetsTests(unittest.TestCase):

    def setUp(self):
        self.ucd = UCD()

    def tearDown(self):
        pass

    def list2us_helper(self, text):
        """Wrap the list2us() function for ease of use."""
        return list2us(text.split(), self.ucd)

    # braces

    def test_braces(self):
        """Multiple characters sequences need braces around them."""
        self.assertEqual(u'[n {ng}]', self.list2us_helper(u'n ng'))

    # normalization

    def test_nfc(self):
        """NFC text."""
        self.assertEqual(u'[\u00E9]', self.list2us_helper(u'\u00e9'))

    # isolated marks

    def test_isolated_marks(self):
        """Isolated marks (that is, with no base character) need to be escaped."""
        self.assertEqual(u'[\\u0300 \\u0301 {\u0105\u0301}]', self.list2us_helper(u'\u0300 \u0301 \u0105\u0301'))


if __name__ == '__main__':
    unittest.main()
