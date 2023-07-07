### based on test_autonym.py
### not sure all these imports are needed
#import unittest
#import pytest
#import logging, re, unicodedata
#from lxml.etree import RelaxNG, parse, DocumentInvalid
#import sldr.UnicodeSets as usets
from langtag import langtag, lookup
import os, requests
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

#    if iscldr(ldml):    # short circuit CLDR for now
#        return
    if isempty(ldml):   #skips font test if file is only an identity block
        return
    
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    for x in exempt:
        if filename == x:
            return
            
    is_root = find_parents(langid, False, True, True, False)[0]
    if is_root == False:
        return
    else:
        fonts = ldml.ldml.findall("special/sil:external-resources/sil:font")
        assert len(fonts) > 0 , filename + " has no font information"


def test_current(ldml, langid):
    filename = os.path.basename(ldml.ldml.fname)
    if ldml.ldml.root.findall("special/sil:external-resources/sil:font", {v:k for k,v in ldml.ldml.namespaces.items()}) is None:
        return
    url = "https://raw.githubusercontent.com/silnrsi/fonts/main/families.json"
    familiesjson = requests.get(url).json()
    goodnames = ["Charis SIL Literacy", "Charis SIL Mali", "Khmer Barkaew", "Khmer Dakdam"]
        #   add/remove exceptions to this list as needed
    for keys, value in familiesjson.items():
        if "status" not in value.keys() and value["distributable"] == True:
            goodnames.append(value["family"])
        if "status" in value.keys() and value["status"] == "current":
            goodnames.append(value["family"])
    #    if "status" in value.keys() and value["status"] == "archived":
    #        goodnames.append(value["family"])
#    print(goodnames)
    badnames = []
    for i in ldml.ldml.root.findall("special/sil:external-resources/sil:font", {v:k for k,v in ldml.ldml.namespaces.items()}):
        name = i.get("name", None)
#        print(name)
        print("Namdhinggo SIL" in goodnames)
        if name not in goodnames:
            badnames.append(name)
#    print(badnames)
#    print(len(badnames)<1)
    assert (len(badnames) < 1), filename + " has one or more fonts with depreciated names: " + str(badnames)
