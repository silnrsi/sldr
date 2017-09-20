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

import re
import unittest
import ldml_exemplars


class UCDTests(unittest.TestCase):

    def setUp(self):
        self.ucd = ldml_exemplars.UCD('ucd.nounihan.grouped.xml', re.compile(r'.'))

    def tearDown(self):
        pass

    def test_prop_true(self):
        self.assertTrue(self.ucd.has_prop('Alpha', u'cab'))

    def test_prop_false(self):
        self.assertFalse(self.ucd.has_prop('Alpha', u'cab.1'))

    def test_nfc(self):
        text = u'e\u0301'
        self.assertEqual(u'\u00e9', self.ucd.normalize('NFC', text))

    def test_nfd(self):
        text = u'\u00e9'
        self.assertEqual(u'e\u0301', self.ucd.normalize('NFD', text))

    def test_nfc_new(self):
        text = u'\u0061\u035C\u0315\u0300\u1DF6\u0062'
        self.assertEqual(u'\u00E0\u0315\u1DF6\u035C\u0062', self.ucd.normalize('NFC', text))

    def test_nfd_new(self):
        text = u'\u0061\u035C\u0315\u0300\u1DF6\u0062'
        self.assertEqual(u'\u0061\u0300\u0315\u1DF6\u035C\u0062', self.ucd.normalize('NFD', text))


class ExemplarsTests(unittest.TestCase):

    def setUp(self):
        self.exemplars = ldml_exemplars.Exemplars()

    def tearDown(self):
        pass

    def test_simple_main(self):
        self.exemplars.process(u'[{cab.1}]')
        self.assertEqual(u'[a b c]', self.exemplars.get_main())

    def test_simple_punctuation(self):
        self.exemplars.process(u'[{cab.1}]')
        self.assertEqual(u'[. [ ] { }]', self.exemplars.get_punctuation())

    def test_not_included(self):
        self.exemplars.process(u'\u034f\u00ad\u06dd')
        self.assertEqual(u'[]', self.exemplars.get_main())

    def test_lithuanian_main(self):
        self.exemplars.process(u'\u00e1\u0328 i\u0307\u0301')
        self.assertEqual(u'[{i\u0307\u0301} {\u0105\u0301}]', self.exemplars.get_main())

    def test_lithuanian_index(self):
        self.exemplars.process(u'a \u0105 b c A \u0104 B C Z')
        self.assertEqual(u'[A \u0104 B C]', self.exemplars.get_index())

    def test_english_main(self):
        self.exemplars.set_auxiliary(u'[\u00e9]')
        self.exemplars.process(u'r\u00e9sum\u00e9')
        self.assertEqual(u'[m r s u]', self.exemplars.get_main())

    def test_english_auxiliary_nfc(self):
        self.exemplars.set_auxiliary(u'[\u00e9]')
        self.exemplars.process(u'r\u00e9sum\u00e9')
        self.assertEqual(u'[\u00e9]', self.exemplars.get_auxiliary())

    def test_english_auxiliary_nfd(self):
        self.exemplars.set_auxiliary(u'[{e\u0301}]')
        self.exemplars.process(u're\u0301sume\u0301')
        self.assertEqual(u'[\u00e9]', self.exemplars.get_auxiliary())

    def test_french_main_nfc(self):
        self.exemplars.many_bases = 4
        self.exemplars.process(u'r\u00e9sum\u00e9 \u00e2 \u00ea \u00ee \u00f4 \u00fb')
        self.assertEqual(u'[a e i m o r s u \u00e9 \u0302]', self.exemplars.get_main())

    def test_french_main_nfd(self):
        self.exemplars.many_bases = 4
        self.exemplars.process(u're\u0301sume\u0301 a\u0302 e\u0302 i\u0302 o\u0302 u\u0302')
        self.assertEqual(u'[a e i m o r s u \u00e9 \u0302]', self.exemplars.get_main())

    def test_french_auxiliary(self):
        self.exemplars.process(u'r\u00e9sum\u00e9')
        self.assertEqual(u'[]', self.exemplars.get_auxiliary())

    def test_swahili(self):
        self.exemplars.set_main(u'[{ng} {ng\ua78c}]')
        self.exemplars.process(u'ran rang rang\ua78c')
        self.assertEqual(u'[a n r {ng} {ng\ua78c}]', self.exemplars.get_main())

    def test_devanagari_generatively(self):
        self.exemplars.process(u'\u0958 \u0959 \u095A \u095B \u095C \u095D \u095E \u095F')
        self.assertEqual(u'[\u0915 \u0916 \u0917 \u091C \u0921 \u0922 \u092B \u092F \u093C]',
                         self.exemplars.get_main())

    def test_devanagari_few(self):
        self.exemplars.process(u'\u0958 \u0959 \u095A')
        self.assertEqual(u'[{\u0915\u093C} {\u0916\u093C} {\u0917\u093C}]',
                         self.exemplars.get_main())

    def test_devanagari_index(self):
        self.exemplars.process(u'\u0905 \u0906 \u0915 \u0916 \u0915\u093e \u0916\u093f')
        self.assertEqual(u'[\u0905 \u0906 \u0915 \u0916]', self.exemplars.get_main())


if __name__ == '__main__':
    unittest.main()
