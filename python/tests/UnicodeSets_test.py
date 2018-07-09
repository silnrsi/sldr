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
    import sldr.UnicodeSets
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))
    from sldr.ldml_exemplars import UCD
    import sldr.UnicodeSets


class UnicodeSetsTests(unittest.TestCase):

    def setUp(self):
        self.ucd = UCD()

    def tearDown(self):
        pass

    def list2us_helper(self, text):
        """Wrap the list2us() function for ease of use."""
        return sldr.UnicodeSets.list2us(text.split(' '), self.ucd)

    # braces

    def test_braces(self):
        """Multiple characters sequences need braces around them."""
        self.assertEqual(u'[n {ng}]', self.list2us_helper(u'n ng'))

    # normalization

    def test_nfc(self):
        """NFC text."""
        self.assertEqual(u'[\u00E9]', self.list2us_helper(u'\u00e9'))

    # isolated marks

    def test_isolated_marks_bmp(self):
        """Isolated marks (that is, with no base character) need to be escaped."""
        self.assertEqual(u'[\\u0300 \\u0301 {\u0105\u0301}]', self.list2us_helper(u'\u0300 \u0301 \u0105\u0301'))

    def test_isolated_marks_nonbmp(self):
        """Isolated marks (outside of the BMP as well) need to be escaped."""
        self.assertEqual(u'[\U00011315 \\U0001133c]', self.list2us_helper(u'\U00011315 \U0001133C'))

    # characters used in Unicode Set syntax

    def ignore_control_escape(self):
        """Some ASCII control characters should be escaped with a backslash.

        These maybe already listed in the variable simpleescs.
        """
        self.assertEqual(u'[\u0007 \u0008 \u0009 \u000A \u000B \u000C \u000D]',
                         self.list2us_helper(u'\u0007 \u0008 \u0009 \u000A \u000B \u000C \u000D'))

    def test_syntax_escape(self):
        """Some characters used in Unicode Set syntax need to be escaped with a backslash.

        The following characters are escaped: []{}\\&-|^$:
        They are all used in Unicode Set format
        https://unicode.org/reports/tr35/tr35.html#Unicode_Sets
        except for |. We escape | anyway, it should still work.
        """
        self.assertEqual(u'[\\[ \\] \\{ \\} \\\\ \\& \\- \\| \\^ \\$ \\:]',
                         self.list2us_helper(u'[ ] { } \\ & - | ^ $ :'))

    # escape some characters with hex digits

    def test_ignorable(self):
        """Characters having the Default_Ignorable_Code_Point property need to be escaped."""
        self.assertEqual(u'[\\u3164]', self.list2us_helper(u'\u3164'))

    def test_format(self):
        """Characters having the format character (general category Cf) property need to be escaped."""
        self.assertEqual(u'[\\u06dd]', self.list2us_helper(u'\u06dd'))

    def test_space(self):
        """Space like characters need to be escaped."""
        self.assertEqual(u'[\\u200a]', self.list2us_helper(u'\u200a'))

    def test_pua_bmp(self):
        """PUA characters (in the BMP) need to be escaped."""
        self.assertEqual(u'[\\ue000]', self.list2us_helper(u'\ue000'))

    def test_pua_nonbmp_a(self):
        """PUA characters (outside of the BMP) need to be escaped."""
        self.assertEqual(u'[\\U000fff80]', self.list2us_helper(u'\U000fff80'))

    def test_pua_nonbmp_b(self):
        """PUA characters (outside of the BMP and SMP) need to be escaped."""
        self.assertEqual(u'[\\U0010ff80]', self.list2us_helper(u'\U0010ff80'))


if __name__ == '__main__':
    unittest.main()
