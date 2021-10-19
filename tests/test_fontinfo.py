### based on test_autonym.py
### not sure all these imports are needed
#import unittest
#import pytest
#import logging, re, unicodedata
#from lxml.etree import RelaxNG, parse, DocumentInvalid
#import sldr.UnicodeSets as usets
import os

def iscldr(ldml):
    i = ldml.ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.ldml.namespaces.items()})
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

def test_autonym(ldml):
    """ Test that the LDML file has font information """
    if iscldr(ldml):    # short circuit CLDR for now
        return
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference

    fonts = ldml.ldml.findall("special/sil:external-resources/sil:font")
    assert len(fonts) > 0 , filename + " has no font information"
