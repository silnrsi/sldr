#!/usr/bin/python

import unittest, sys, os
from StringIO import StringIO

try:
    from sldr.ldml import Ldml
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))
    from sldr.ldml import Ldml


class LDMLTests(unittest.TestCase):

    def _init_exemplar_test(self):
        tf = StringIO('''<?xml version="1.0"?>
<ldml xmlns:sil="urn://www.sil.org/ldml/0.1">
    <identity>
        <special>
            <sil:identity uid="test1"/>
        </special>
    </identity>
    <characters>
        <exemplarCharacters>[d e f a u l t]</exemplarCharacters>
    </characters>
</ldml>''')
        return tf

    def test_exemplar_basic(self):
        tf = self._init_exemplar_test()
        teststr = "[g e n e r a t e d]"
        ldml = Ldml(tf)
        e = ldml.ensure_path('characters/exemplarCharacters[@type=""]', draft="generated", matchdraft="draft")
        e[0].text = teststr
        x = ldml.ensure_path('characters/exemplarCharacters[@type=""]', draft="generated", matchdraft="draft")
        self.assertTrue(x[0].text == teststr)

    def test_exemplar_double(self):
        tf = self._init_exemplar_test()
        tpath = 'characters/exemplarCharacters[@type=""]'
        testdrafts = ('generated', 'suspect')
        testalts = {'generated': None, 'suspect': 'proposed2'}
        teststrs = dict((x, "[" + " ".join(x) + "]") for x in testdrafts)
        ldml = Ldml(tf)
        for t in testdrafts:
            e = ldml.ensure_path(tpath, draft=t, alt=testalts[t], matchdraft="draft")
            e[0].text = teststrs[t]
        for t in testdrafts:
            x = ldml.ensure_path(tpath, draft=t, matchdraft="draft")
            self.assertTrue(x[0].text == teststrs[t])

if __name__ == '__main__':
    unittest.main()
