import unittest
import pytest
import logging, os
from lxml.etree import DTD, RelaxNG, parse, DocumentInvalid
import sldr.UnicodeSets as usets
from unicodedata import normalize
import re

@pytest.fixture(scope="session")
def validator(request):
    # return RelaxNG(file=os.path.join(os.path.dirname(__file__), '..', 'doc', 'sil.rng'))
    return DTD(file=os.path.join(os.path.dirname(__file__), '..', 'auxdata', 'sil.dtd'))

def iscldr(ldml):
    i = ldml.ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.ldml.namespaces.items()})
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

def test_validate(ldml, validator, fixdata):
    """ Test LDML file conforms to sil/ldml rng """
    xml = parse(ldml.path)
    try:
        validator.assertValid(xml)
    except DocumentInvalid as e:
        # import pdb; pdb.set_trace()
        if fixdata and str(e).startswith("Did not expect element"):
            tag = str(e)[23:]
            tag = tag[:tag.find(" ")]
            if tag in ("generation", "language"):
                ldml.ldml.ensure_path('identity/version[@number="0.0.1"]', before=tag)
                ldml.dirty = True
                return
        assert False, str(e)

def test_exemplars(ldml):
    """ Test for overlaps between exemplars. Test that index chars are all in main exemplar """
    if iscldr(ldml):    # short circuit CLDR for now until they/we resolve the faults in their data
        return
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    exemplars = {}
    for e in ldml.ldml.root.findall('.//characters/exemplarCharacters'):
        t = e.get('type', None)
        s = usets.parse(e.text or "", 'NFD')
        if not len(s):
            continue
        exemplars[t] = s[0]
    if None not in exemplars:
        return
    else:
        main = exemplars[None]
    for k, v in exemplars.items():
        if k in (None, "index", "numbers"):
            continue
        diff = main & v
        assert not len(diff), filename + " Overlap found between main and %s" % (k)
    if 'index' in exemplars:
        if 'auxiliary' in exemplars:
            test = main.union(exemplars['auxiliary'])
        else:
            test = main
        m = set([x.lower() for x in exemplars['index']])
        diff = m - test
        # The following lines (down to the assert) added to handle digraphs whose components are present
        digraphcheck = True
        for digraph in diff:
            for c in digraph:
                if c not in test:
                    digraphcheck = False
                    break
        assert digraphcheck or not len(diff), filename + " Not all index entries found in main or auxiliary"

# THE WHOLE NEXT TEST IS EMILY CODE and is therefore probably JANKY
def test_syntax(ldml):
    """ Test for syntax errors in exemplars """
    if iscldr(ldml):    # short circuit CLDR for now until they/we resolve the faults in their data
        return
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    exemplars = {}
    exemplars_raw = {}
    exemplars_rawnocurly = {}
    for e in ldml.ldml.root.findall('.//characters/exemplarCharacters'): 
        t = e.get('type', None)
        n = t or "main"
        exemplars_rawnocurly[t] = e.text[1:-1].strip().replace("\\", " \\").replace("{", " ").replace("}", " ").replace("  ", " ").split(' ') # adapted from the "get index exemplar" section of test_collation.py
        exemplars_raw[t] = e.text[1:-1].strip().split(' ') # adapted from the "get index exemplar" section of test_collation.py
        rawstring = e.text[1:-1].strip().replace(" ", "") # adapted from the "get index exemplar" section of test_collation.py
        s = usets.parse(e.text or "", 'NFD')
        if not len(s):
            continue
        exemplars[t] = s[0]
        # The following lines test if unicode hex values in all exemplars are properly formatted
        for i in exemplars_rawnocurly[t]:
            if "\\" in i:
                if r"\u" in i:
                    assert len(i)==6, filename + " " + n + " exemplar has unicode codepoint(s) missing hex digits: " + i
                if r"\U" in i:
                    assert len(i)==10, filename + " " + n + " exemplar has unicode codepoint(s) missing hex digits: " + i
                #this next assert does assume that spaces were added between units in an exemplar, since exemplars_rawnocurly can only insert a space BEFORE a backslash. So far nothing fails incorrectly because of that
                assert len(i)<3 or len(i)==6 or len(i)==10, filename + " " + n + " exemplar has unicode codepoint(s) missing 'u' or 'U': " + i
        # The following lines are a test if characters are incorrectly unescaped.
        # The problem with these coming tests is that if there are ranges that use special characters intentionally, they'll ping as errors. 
        # However we can't solely test for "is it a valid regex" bc they might make a valid regex on accident. 
        # Also it seems rare to use special characters intentionally in punctuation and numbers, so if this false error does happen, it'll be very uncommon.
        if 'punctuation' in exemplars:
            for p in exemplars_raw['punctuation']:
                for a in (("-", "hyphen"), (":", "colon"), ("&", "ampersand"), ("[", "square bracket"), ("]", "square bracket"), ("{", "curly bracket"), ("}", "curly bracket")):
                    if a[0] in p:
                        assert "\\"+a[0] in p, filename + " Unescaped " + a[1] + " in punctuation exemplar"
                #not sure how to test for a non-escaped backslash since that's used intentionally EVERYWHERE. 
        if 'numbers' in exemplars:
            for n in exemplars_raw['numbers']:
                for b in (("-", "hyphen"), (":", "colon")):
                    if b[0] in n:
                        assert "\\"+b[0] in n, filename + " Unescaped " + b[1] + " in numbers exemplar"
        # there are probably more but I can't think of them atm
        # Assert below tests that exemplars are valid regular expressions: it's a catch-all for anything the tests above might miss
        assert _test_re("\"\"[" + rawstring + "]\"\""), filename + " " + n + " exemplar isn't a valid regex"

def _duplicate_test(base, ldml, path=""):
    filename = os.path.basename(ldml.fname)    # get filename for reference
    idents = set()
    for c in base:
        if c.tag in ("variable",):
            continue
        ident = [c.tag]
        ident.extend(["{}={}".format(k, v) for k, v in sorted(c.attrib.items())])
        #for n in list(ldml.keyContexts.get(c.tag, ldml.keys)) + ['draft']:
        #    v = c.get(n, None)
        #    if v is not None:
        #        ident.append("{}={}".format(n, v))
        i = ":".join(ident)
        if len(ident) > 1:
            assert i not in idents, filename + " Found overlapping elements for " + path + "/" + i
        idents.add(i)
        if len(c) and _duplicate_test(c, ldml, path=path + "/" + i):
            return True
    return False

def test_duplicates(ldml):
    """ Test that no two elements have the same identifying feature values """
    _duplicate_test(ldml.ldml.root, ldml.ldml)

def _test_re(string):
    """ Return True if string is a valid regular expression; False otherwise """
    try:
        x = re.compile(string)
        return True
    except re.error:
        return False

# the test below is REDUNDANT and now is done with at the end of the syntax test. 
def test_re(ldml):
    """ Test that exemplars are valid regular expressions: helps detect some missing 'u' in unicode codepoints, some (but not all) unescaped special characters, and other errors """
    if iscldr(ldml):    # short circuit CLDR for now until they/we resolve the faults in their data
        return
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    for e in ldml.ldml.root.findall('.//characters/exemplarCharacters'): 
        t = e.get('type', None)
        n = t or "main"
        rawstring = e.text[1:-1].strip().replace(" ", "") # adapted from the "get index exemplar" section of test_collation.py
        assert _test_re("\"\"[" + rawstring + "]\"\""), filename + " " + n + " exemplar isn't a valid regex"