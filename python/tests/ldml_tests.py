#!/usr/bin/python

import unittest, sys, os
from StringIO import StringIO

try:
    from sldr.ldml import Ldml
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))
    from sldr.ldml import Ldml


class LDMLTests(unittest.TestCase):

    def setUp(self):
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
        self.ldml = Ldml(tf)
        self.tpath ='characters/exemplarCharacters[@type=""]' 

    def tearDown(self):
        if '-v' in sys.argv:
            self.ldml.serialize_xml(sys.stdout.write)

    def test_exemplar_basic(self):
        teststr = "[g e n e r a t e d]"
        e = self.ldml.ensure_path(self.tpath, draft="generated", matchdraft="draft")
        e[0].text = teststr
        x = self.ldml.ensure_path(self.tpath, draft="generated", matchdraft="draft")
        self.assertTrue(x[0].text == teststr)

    def test_exemplar_double(self):
        testdrafts = ('generated', 'suspect')
        testalts = {'generated': None, 'suspect': 'proposed2'}
        teststrs = dict((x, "[" + " ".join(x) + "]") for x in testdrafts)
        for t in testdrafts:
            e = self.ldml.ensure_path(self.tpath, draft=t, alt=testalts[t], matchdraft="draft")
            e[0].text = teststrs[t]
        for t in testdrafts:
            x = self.ldml.ensure_path(self.tpath, draft=t, matchdraft="draft")
            self.assertTrue(x[0].text == teststrs[t])

    def test_change_draft(self):
        testdrafts = ('generated', 'suspect')
        teststrs = dict((x, "[" + " ".join(x) + "]") for x in testdrafts)
        b = self.ldml.ensure_path(self.tpath)[0]
        e = self.ldml.ensure_path(self.tpath, draft='generated', matchdraft='draft')[0]
        e.text = teststrs['generated']
        n = self.ldml.change_draft(b, 'suspect')
        b = self.ldml.ensure_path(self.tpath)[0]
        self.assertTrue(b.text == teststrs['generated'])


if __name__ == '__main__':
    unittest.main()
