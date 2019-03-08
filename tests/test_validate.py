import unittest
import pytest
import logging, os
from lxml.etree import RelaxNG, parse, DocumentInvalid
import palaso.sldr.UnicodeSets as usets

@pytest.fixture(scope="session")
def validator(request):
    return RelaxNG(file=os.path.join(os.path.dirname(__file__), '..', 'doc', 'sil.rng'))

def iscldr(ldml):
    i = ldml.ldml.find(".//identity/special/sil:identity")
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

def test_validate(ldml, validator):
    xml = parse(ldml.path)
    try:
        validator.assertValid(xml)
    except DocumentInvalid as e:
        # import pdb; pdb.set_trace()
        if str(e).startswith("Did not expect element"):
            tag = str(e)[23:]
            tag = tag[:tag.find(" ")]
            if tag == "language":
                ldml.ldml.ensure_path('identity/version[@number="0.0.1"]', before="language")
                ldml.dirty = True
                return
        assert False, str(e)

def test_exemplars(ldml):
    if iscldr(ldml):    # short circuit CLDR for now until they/we resolve the faults in their data
        return
    exemplars = {}
    for e in ldml.ldml.root.findall('.//characters/exemplarCharacters'):
        t = e.get('type', None)
        s = usets.parse(e.text)
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
        assert not len(main & v), "Overlap found between main and %s" % (k)
    if 'index' in exemplars:
        if 'auxiliary' in exemplars:
            test = main.union(exemplars['auxiliary'])
        else:
            test = main
        m = set([x.lower() for x in exemplars['index']])
        assert not len(m - test), "Not all index entries found in main or auxiliary"
