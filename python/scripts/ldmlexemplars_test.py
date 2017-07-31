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

import unittest
import ldmlexemplars

class ExemplarsTests(unittest.TestCase):

    def setUp(self) :
        self.exemplars = ldmlexemplars.Exemplars()

    def tearDown(self) :
        pass

    def test_simple_main(self) :
        self.exemplars.process(u'cab.')
        self.assertEqual(u'[a b c]', self.exemplars.get_main())

    def test_simple_punctuation(self) :
        self.exemplars.process(u'cab.')
        self.assertEqual(u'[.]', self.exemplars.get_punctuation())

    def test_english_main(self) :
        self.exemplars.set_auxiliary(u'[\u00e9]')
        self.exemplars.process(u'r\u00e9sum\u00e9')
        self.assertEqual(u'[e m r s u]', self.exemplars.get_main())

    def test_english_auxiliary(self) :
        self.exemplars.set_auxiliary(u'[\u00e9]')
        self.exemplars.process(u'r\u00e9sum\u00e9')
        self.assertEqual(u'[\u00e9]', self.exemplars.get_auxiliary())

    def test_french_main(self):
        self.exemplars.process(u'r\u00e9sum\u00e9')
        self.assertEqual(u'[m r s u \u00e9]', self.exemplars.get_main())

    def test_french_auxiliary(self):
        self.exemplars.process(u'r\u00e9sum\u00e9')
        self.assertEqual(u'[]', self.exemplars.get_auxiliary())

if __name__ == '__main__' :
    unittest.main()
