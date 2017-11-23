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
    from sldr.ldml_exemplars import UCD, Exemplars
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))
    from sldr.ldml_exemplars import UCD, Exemplars


class UCDTests(unittest.TestCase):

    def setUp(self):
        self.ucd = UCD()

    def tearDown(self):
        pass

    def ignore_findit(self):
        from icu import Char
        maxchar = 0x10ffff
        maxchar = 0xffff
        for usv in xrange(maxchar):
            char = unichr(usv)
            if ((not self.ucd.is_specific_script(char)) and
               (not self.ucd.is_exemplar_wordbreak(char)) and
               (not Char.isUAlphabetic(char))):
                print '%04X' % usv
        self.assertTrue(False)

    def test_mark_true(self):
        self.assertTrue(self.ucd.ismark(u'\u0301'))

    def test_mark_false(self):
        self.assertFalse(self.ucd.ismark(u'e'))

    def test_nukta_true(self):
        self.assertTrue(self.ucd.isnukta(u'\u093c'))

    def test_nukta_false(self):
        self.assertFalse(self.ucd.isnukta(u'\u0915'))

    def test_matra_true(self):
        self.assertTrue(self.ucd.is_indic_matra(u'\u093e'))

    def test_matra_false(self):
        self.assertFalse(self.ucd.is_indic_matra(u'\u0906'))

    def test_number_true(self):
        self.assertTrue(self.ucd.isnumber(u'1'))

    def test_number_false(self):
        self.assertFalse(self.ucd.isnumber(u'a'))

    def test_script_specific_true_latin(self):
        self.assertTrue(self.ucd.is_specific_script(u'\ua78c'))

    def test_script_specific_false_latin(self):
        self.assertFalse(self.ucd.is_specific_script(u'\u02bc'))

    def test_script_specific_false_chinese(self):
        self.assertFalse(self.ucd.is_specific_script(u'\ua700'))

    def test_script_specific_false_vedic(self):
        self.assertFalse(self.ucd.is_specific_script(u'\u1CD1'))

    def test_wordbreak_katakana(self):
        self.assertTrue(self.ucd.is_exemplar_wordbreak(u'\u309b'))

    def test_wordbreak_aletter(self):
        self.assertTrue(self.ucd.is_exemplar_wordbreak(u'\u05f3'))

    def test_wordbreak_midletter(self):
        self.assertTrue(self.ucd.is_exemplar_wordbreak(u'\u05f4'))

    def test_wordbreak_chinese(self):
        self.assertFalse(self.ucd.is_exemplar_wordbreak(u'\ua700'))

    def test_nfc(self):
        text = u'e\u0301'
        self.assertEqual(u'\u00e9', self.ucd.normalize('NFC', text))

    def test_nfd(self):
        text = u'\u00e9'
        self.assertEqual(u'e\u0301', self.ucd.normalize('NFD', text))

    def ignore_nfc_tus10(self):
        text = u'\u0061\u035C\u0315\u0300\u1DF6\u0062'
        self.assertEqual(u'\u00E0\u0315\u1DF6\u035C\u0062', self.ucd.normalize('NFC', text))

    def ignore_nfd_tus10(self):
        text = u'\u0061\u035C\u0315\u0300\u1DF6\u0062'
        self.assertEqual(u'\u0061\u0300\u0315\u1DF6\u035C\u0062', self.ucd.normalize('NFD', text))


class ExemplarsTests(unittest.TestCase):

    def setUp(self):
        self.exemplars = Exemplars()

    def tearDown(self):
        pass

    def test_simple_main(self):
        self.exemplars.process(u'[{cab.1}]')
        self.exemplars.analyze()
        self.assertEqual(u'[a b c]', self.exemplars.main)
        self.assertEqual(u'[1]', self.exemplars.digits)

    def test_simple_punctuation(self):
        self.exemplars.process(u'[{cab.1}]')
        self.exemplars.analyze()
        self.assertEqual(u'[. [ ] { }]', self.exemplars.punctuation)
        self.assertEqual(u'[1]', self.exemplars.digits)

    def test_japanese_katakana(self):
        """Characters with Word_Break property Katakana are letters."""
        self.exemplars.process(u'\u307b\u309b')
        self.exemplars.analyze()
        self.assertEqual(u'[\u307b \u309b]', self.exemplars.main)

    def test_hebrew_aletter(self):
        """Characters with Word_Break property ALetter are not punctuation."""
        self.exemplars.process(u'\u05d1\u05f3\u05d2')
        self.exemplars.analyze()
        self.assertEqual(u'[\u05d1 \u05d2 \u05f3]', self.exemplars.main)
        self.assertEqual(u'[]', self.exemplars.punctuation)

    def test_hebrew_midletter(self):
        """Characters with Word_Break property MidLetter are not punctuation."""
        self.exemplars.process(u'\u05f4\u05d0\u05f4')
        self.exemplars.analyze()
        self.assertEqual(u'[\u05d0 \u05f4]', self.exemplars.main)
        self.assertEqual(u'[]', self.exemplars.punctuation)

    def test_chinese(self):
        self.exemplars.process(u'\u6606\u660e\ua700')
        self.exemplars.analyze()
        self.assertEqual(u'[\u6606 \u660e]', self.exemplars.main)

    def test_png(self):
        """Digits are ignored, unless they have diacritics."""
        self.exemplars.process(u'[1\u0301 2\u0301 3\u0301 4\u0301 5\u0301 6\u0301]')
        self.exemplars.analyze()
        self.assertEqual(u'[1 2 3 4 5 6 \u0301]', self.exemplars.main)
        self.assertEqual(u'[]', self.exemplars.digits)

    def test_not_included(self):
        self.exemplars.process(u'\u034f\u00ad\u06dd')
        self.exemplars.analyze()
        self.assertEqual(u'[]', self.exemplars.main)

    def test_lithuanian_main(self):
        self.exemplars.process(u'\u00c1\u0328 \u00e1\u0328 I\u0307\u0301 i\u0307\u0301')
        self.exemplars.analyze()
        self.assertEqual(u'[{\u0105\u0301} {i\u0307\u0301}]', self.exemplars.main)

    def test_lithuanian_index(self):
        self.exemplars.process(u'a \u0105 b c A \u0104 B C Z')
        self.exemplars.analyze()
        self.assertEqual(u'[A \u0104 B C]', self.exemplars.index)

    def test_english_main(self):
        self.exemplars.auxiliary = u'[\u00e9]'
        self.exemplars.process(u'r\u00e9sum\u00e9')
        self.exemplars.analyze()
        self.assertEqual(u'[m r s u]', self.exemplars.main)

    def test_english_auxiliary_nfc(self):
        self.exemplars.auxiliary = u'[\u00e9]'
        self.exemplars.process(u'r\u00e9sum\u00e9')
        self.exemplars.analyze()
        self.assertEqual(u'[\u00e9]', self.exemplars.auxiliary)

    def test_english_auxiliary_nfd(self):
        self.exemplars.auxiliary = u'[{e\u0301}]'
        self.exemplars.process(u're\u0301sume\u0301')
        self.exemplars.analyze()
        self.assertEqual(u'[\u00e9]', self.exemplars.auxiliary)

    def test_english_index(self):
        self.exemplars.auxiliary = u'[\u00e9]'
        self.exemplars.process(u'r\u00e9sum\u00e9')
        self.exemplars.analyze()
        self.assertEqual(u'[\u00c9 M R S U]', self.exemplars.index)

    def test_spanish(self):
        """Marks occurring on a few bases are not separate."""
        self.exemplars.process(u'biling\u00fce')
        self.exemplars.analyze()
        self.assertEqual(u'[b e g i l n \u00fc]', self.exemplars.main)

    def test_french_main_nfc(self):
        """Marks occurring on many bases are separate, even if the characters are combined (NFC)."""
        self.exemplars.many_bases = 4
        self.exemplars.process(u'r\u00e9sum\u00e9 \u00e2 \u00ea \u00ee \u00f4 \u00fb')
        self.exemplars.analyze()
        self.assertEqual(u'[a e \u00e9 i m o r s u \u0302]', self.exemplars.main)

    def test_french_main_nfd(self):
        """Marks occurring on many bases are separate."""
        self.exemplars.many_bases = 4
        self.exemplars.process(u're\u0301sume\u0301 a\u0302 e\u0302 i\u0302 o\u0302 u\u0302')
        self.exemplars.analyze()
        self.assertEqual(u'[a e \u00e9 i m o r s u \u0302]', self.exemplars.main)

    def test_french_auxiliary(self):
        self.exemplars.process(u'r\u00e9sum\u00e9')
        self.exemplars.analyze()
        self.assertEqual(u'[]', self.exemplars.auxiliary)

    def test_french_count(self):
        """Infrequently occurring exemplars should go in the auxiliary list, not the main list."""
        self.exemplars.many_bases = 4
        self.exemplars.frequent = 80
        base = u'a e i o u'
        grave = u'\u00e0 \u00e8 \u00f9'
        circumflex = u'\u00e2 \u00ea \u00ee \u00f4 \u00fb'
        self.exemplars.process(base + grave + circumflex)
        self.exemplars.analyze()
        self.assertEqual(u'[a e i o u \u0302]', self.exemplars.main)
        self.assertEqual(u'[\u00e0 \u00e8 \u00f9]', self.exemplars.auxiliary)

    def test_french_index(self):
        self.exemplars.process(u'r\u00e9sum\u00e9')
        self.exemplars.analyze()
        self.assertEqual(u'[\u00c9 M R S U]', self.exemplars.index)

    def test_swahil_main(self):
        self.exemplars.main = u'[{ng} {ng\ua78c}]'
        self.exemplars.process(u'ran rang rang\ua78c')
        self.exemplars.analyze()
        self.assertEqual(u'[a n {ng} {ng\ua78c} r]', self.exemplars.main)

    def test_swahili_index(self):
        self.exemplars.main = u'[{ng} {ng\ua78c}]'
        self.exemplars.process(u'ran rang rang\ua78c')
        self.exemplars.analyze()
        self.assertEqual(u'[A N {NG} {NG\ua78b} R]', self.exemplars.index)

    def test_swahili_glottal(self):
        """Exemplars have a specific script, unless they have specific Word_Break properties.

        The script values of Common or Inherited are not considered to be a specific script.
        So U+A78C should be included as it has a specific script,
        and U+02BC or U+02C0 should be included as they have the needed Word_Break property.
        """
        self.exemplars.process(u'ng\ua78c ng\u02bc ng\u02c0')
        self.exemplars.analyze()
        self.assertEqual(u'[g n \u02bc \u02c0 \ua78c]', self.exemplars.main)

    def test_devanagari_many(self):
        """Indic matras are always separate."""
        self.exemplars.process(u'\u0958\u093e \u0959\u093e \u095a\u093e \u095b\u093e '
                               u'\u095c\u093e \u095d\u093e \u095e\u093e \u095f\u093e')
        self.exemplars.analyze()
        self.assertEqual(u'[{\u0915\u093c} {\u0916\u093c} {\u0917\u093c} {\u091c\u093c}'
                         u' {\u0921\u093c} {\u0922\u093c} {\u092b\u093c} {\u092f\u093c}'
                         u' \u093e]',
                         self.exemplars.main)

    def test_devanagari_few(self):
        """Indic matras are always separate (even on a few bases).

        Even though the matras (Marks) occur on few bases
        (which would otherwise classify them as not separate),
        they are considered separate.
        """
        self.exemplars.process(u'\u0958\u093e \u0959\u093e \u095a\u093e')
        self.exemplars.analyze()
        self.assertEqual(u'[{\u0915\u093c} {\u0916\u093c} {\u0917\u093c} \u093e]',
                         self.exemplars.main)

    def test_devanagari_index(self):
        self.exemplars.many_bases = 1
        self.exemplars.process(u'\u0905 \u0906 \u0915 \u0916 '
                               u'\u0915\u093e \u0916\u093e '
                               u'\u0958\u093e \u0959\u093e')
        self.exemplars.analyze()
        self.assertEqual(u'[\u0905 \u0906 \u0915 {\u0915\u093c} \u0916 {\u0916\u093c}]',
                         self.exemplars.index)

    def test_devanagari_vedic(self):
        """Exemplar bases should have a specific script, not the values Common or Inherited.

        The character U+1CD1 has a script value of Inherited, but it is a mark, so allow it.
        """
        self.exemplars.process(u'\u0915\u1cd1')
        self.exemplars.analyze()
        self.assertEqual(u'[{\u0915\u1cd1}]', self.exemplars.main)

    def test_kannada_main_old(self):
        """Clusters with virama, ZWJ."""
        self.exemplars.many_bases = 1
        self.exemplars.process(u'\u0cb0\u0ccd\u200d\u0c95 \u0c95\u0ccd\u200d\u0c95')
        self.exemplars.analyze()
        self.assertEqual(u'[\u0c95 \u0cb0 \u0ccd]', self.exemplars.main)

    def test_kannada_main_new(self):
        """Clusters with ZWJ, virama."""
        self.exemplars.many_bases = 1
        self.exemplars.process(u'\u0cb0\u200d\u0ccd\u0c95 \u0c95\u200d\u0ccd\u0c95')
        self.exemplars.analyze()
        self.assertEqual(u'[\u0c95 \u0cb0 \u0ccd]', self.exemplars.main)

    def test_kannada_auxiliary(self):
        """A Default_Ignorable_Code_Point such as ZWJ goes into the auxiliary exemplar."""
        self.exemplars.many_bases = 1
        self.exemplars.process(u'\u0cb0\u200d\u0ccd\u0c95')
        self.exemplars.analyze()
        self.assertEqual(u'[\u200d]', self.exemplars.auxiliary)

    def test_kannada_graphemes(self):
        """Clusters are useful for testing rendering."""
        self.exemplars.process(u'\u0cb0\u200d\u0ccd\u0c95 \u0cb0\u0ccd\u200d\u0c95')
        self.exemplars.analyze()
        self.assertEqual(u'\u0c95 \u0cb0\u200d\u0ccd \u0cb0\u0ccd\u200d', self.exemplars.graphemes)

    def test_yoruba(self):
        """If a set of diacritics has the sames bases, the diacritics are separate exemplars."""
        self.exemplars.process(u'a\u0301 a\u0300 a\u0304 '
                               u'e\u0301 e\u0300 e\u0304 '
                               u'i\u0301 i\u0300 i\u0304 '
                               u'o\u0301 o\u0300 o\u0304 '
                               u'u\u0301 u\u0300 u\u0304 ')
        self.exemplars.analyze()
        self.assertEqual(u'[a e i o u \u0300 \u0301 \u0304]', self.exemplars.main)


if __name__ == '__main__':
    unittest.main()
