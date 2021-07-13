import unittest
import pytest
import logging, os
from lxml.etree import DTD, RelaxNG, parse, DocumentInvalid
import sldr.UnicodeSets as usets
from unicodedata import normalize

@pytest.fixture(scope="session")
def validator(request):
    # return RelaxNG(file=os.path.join(os.path.dirname(__file__), '..', 'doc', 'sil.rng'))
    return DTD(file=os.path.join(os.path.dirname(__file__), '..', 'auxdata', 'sil.dtd'))

def iscldr(ldml):
    i = ldml.ldml.find(".//identity/special/sil:identity")
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

