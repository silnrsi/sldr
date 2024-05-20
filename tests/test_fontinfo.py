### based on test_autonym.py
### not sure all these imports are needed
#import unittest
#import pytest
#import logging, re, unicodedata
#from lxml.etree import RelaxNG, parse, DocumentInvalid
#import sldr.UnicodeSets as usets
from langtag import langtag, lookup
import os
from sldr.ldml import Ldml, _alldrafts
from sldr.utils import find_parents
#change this once the find parent stuff has a new home

exempt = [
    "test.xml",
    "template.xml",
    "exemplar_template.xml"
]

def iscldr(ldml):
    i = ldml.ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.ldml.namespaces.items()})
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

def isempty(ldml):
    blocklist = []
    for b in ldml.ldml.root:
        blocklist.append(b.tag)     #gives me list of all the major element blocks, starting with 'identity' 
    if blocklist == ['identity']:
        return True
    return False

def test_fontinfo(ldml, langid):
    """ Test that the LDML file has font information """

    if iscldr(ldml):    # short circuit CLDR for now
        return
    if isempty(ldml):   #skips font test if file is only an identity block
        return
    
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    fonts = ldml.ldml.findall("special/sil:external-resources/sil:font")
    assert len(ldml.ldml.root) == 1 or len(fonts) > 0 , filename + " has no font information"
    allfontnames = {}
    for f in fonts:
        n = f.get('name')
        assert n not in allfontnames, filename + " has repeated sil:font@name = {}".format(n)
        allfontnames[n] = 1
