import unittest
import pytest
import logging, os
from lxml.etree import RelaxNG, parse, DocumentInvalid
import palaso.sldr.UnicodeSets as usets
from unicodedata import normalize

@pytest.fixture(scope="session")
def validator(request):
    return RelaxNG(file=os.path.join(os.path.dirname(__file__), '..', 'doc', 'sil.rng'))

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
        assert not len(diff), filename + " Not all index entries found in main or auxiliary"
