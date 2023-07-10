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
                for a in (("-", "hyphen"), (":", "colon"), ("&", "ampersand"), ("[", "square bracket"), ("]", "square bracket"), ("{", "curly bracket"), ("}", "curly bracket"), ("$", "dollar sign")):
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

def test_diacritics (ldml):
    """Tests if the exemplars have diacritics listed separately rather than in their composed form. Only tests Latn diacritics atm"""
#    if iscldr(ldml):    # short circuit CLDR for now until they/we resolve the faults in their data
#        return
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    comb_diacritics = ["\u0300","\u0301","\u0302","\u0303","\u0304","\u0305","\u0306","\u0307",
                  "\u0308","\u0309","\u030A","\u030B","\u030C","\u030D","\u030E","\u030F",
                  "\u0310","\u0311","\u0312","\u0313","\u0314","\u0315","\u0316","\u0317",
                  "\u0318","\u0319","\u031A","\u031B","\u031C","\u031D","\u031E","\u031F",
                  "\u0320","\u0321","\u0322","\u0323","\u0324","\u0325","\u0326","\u0327",
                  "\u0328","\u0329","\u032A","\u032B","\u032C","\u032D","\u032E","\u032F",
                  "\u0330","\u0331","\u0332","\u0333","\u0334","\u0335","\u0336","\u0337",
                  "\u0338","\u0339","\u033A","\u033B","\u033C","\u033D","\u033E","\u033F",
                  "\u1AB0","\u1AB1","\u1AB2","\u1AB3","\u1AB4","\u1AB5","\u1AB6","\u1AB7",
                  "\u1AB8","\u1AB9","\u1ABA","\u1ABB","\u1ABC","\u1ABD","\u1ABE","\u1ABF",
                  "\u1AC0","\u1AC1","\u1AC2","\u1AC3","\u1AC4","\u1AC5","\u1AC6","\u1AC7",
                  "\u1AC8","\u1AC9","\u1ACA","\u1ACB","\u1ACC","\u1ACD","\u1ACE",
                  "\u1DC0","\u1DC1","\u1DC2","\u1DC3","\u1DC4","\u1DC5","\u1DC6","\u1DC7",
                  "\u1DC8","\u1DC9","\u1DCA","\u1DCB","\u1DCC","\u1DCD","\u1DCE","\u1DCF",
                  "\u1DD0","\u1DD1","\u1DD2","\u1DD3","\u1DD4","\u1DD5","\u1DD6","\u1DD7",
                  "\u1DD8","\u1DD9","\u1DDA","\u1DDB","\u1DDC","\u1DDD","\u1DDE","\u1DDF",
                  "\u1DE0","\u1DE1","\u1DE2","\u1DE3","\u1DE4","\u1DE5","\u1DE6","\u1DE7",
                  "\u1DE8","\u1DE9","\u1DEA","\u1DEB","\u1DEC","\u1DED","\u1DEE","\u1DEF",
                  "\u1DF0","\u1DF1","\u1DF2","\u1DF3","\u1DF4","\u1DF5","\u1DF6","\u1DF7",
                  "\u1DF8","\u1DF9","\u1DFA","\u1DFB","\u1DFC","\u1DFD","\u1DFE","\u1DFF"]
    exemplars = {}
    for e in ldml.ldml.root.findall('.//characters/exemplarCharacters'): 
        t = e.get('type', None)
        n = t or "main"
        print (t)
        print(n)
        print(e.text)
        if n == "punctuation" or n == "numbers":
            continue
        if not len(usets.parse(e.text, 'NFC')):
            continue
        exemplars[n] = usets.parse(e.text, 'NFC')[0].asSet()
        print(exemplars[n])
        for c in exemplars[n]:
            print (c)
            assert c not in comb_diacritics, filename + " diacritics aren't composed"

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
