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
        rawnocurly = e.text[1:-1].strip().replace("\\", " \\").replace("{", " ").replace("}", " ").replace("  ", " ").split(' ') # adapted from the "get index exemplar" section of test_collation.py
        raw = e.text[1:-1].strip().split(' ') # adapted from the "get index exemplar" section of test_collation.py
        s = usets.parse(e.text or "", 'NFD')
        if not len(s):
            continue
        exemplars[t] = s[0]
        exemplars_raw[t] = raw
        exemplars_rawnocurly[t] = rawnocurly
        # The following lines test if unicode hex values in all exemplars are properly formatted
        for i in exemplars_rawnocurly[t]:
            if r"\u" in i:
                assert len(i)==6, filename + " unicode codepoint missing hex digits"
            if r"\U" in i:
                assert len(i)==10, filename + " unicode codepoint missing hex digits"
            # I'd also like to write a test that would detect if you were intending to write a unicode hex value but forgot the 'u' or something, but I can't think of how to make that work. 
    # The following lines are a test if characters are incorrectly unescaped.
    if 'punctuation' in exemplars:
        for p in exemplars_raw['punctuation']:
            if "-" in p:
                assert r"\-" in p, filename + " Unescaped hyphen in punctuation exemplar"
            if ":" in p:
                assert r"\:" in p, filename + " Unescaped colon in punctuation exemplar"
            if "&" in p:
                assert r"\&" in p, filename + " Unescaped ampersand in punctuation exemplar"
    if 'numbers' in exemplars:
        for n in exemplars_raw['numbers']:
            if "-" in n:
                assert r"\-" in n, filename + " Unescaped hyphen in numbers exemplar"
    #there are probably more but I can't think of them atm

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

def test_re(ldml):
    """ Test that exemplars are valid regular expressions: helps detect missing 'u' in unicode codepoints, some (but not all) unescaped special characters, and other errors """
    if iscldr(ldml):    # short circuit CLDR for now until they/we resolve the faults in their data
        return
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    for e in ldml.ldml.root.findall('.//characters/exemplarCharacters'): 
        t = e.get('type', None)
        rawstring = e.text[1:-1].strip().replace(" ", "") # adapted from the "get index exemplar" section of test_collation.py
        s = usets.parse(e.text or "", 'NFD')
        if not len(s):
            continue
        if t == None:
            t = "main"
        assert _test_re("\"\"[" + rawstring + "]\"\""), filename + " " + t + " exemplar isn't a valid regex"