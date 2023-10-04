import os, json
import requests
import logging, os, re, unicodedata
from langtag import langtag, lookup
from sldr.utils import find_parents


def iscldr(ldml):
    i = ldml.ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.ldml.namespaces.items()})
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

def test_core(ldml):
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    corereqs = {
        "characters/exemplarCharacters": "Main Exemplar Characters", 
        "characters/exemplarCharacters[@type='auxiliary']": "Auxiliary Exemplar Characters", 
        "characters/exemplarCharacters[@type='punctuation']": "Punctuation Exemplar Characters",
        "characters/exemplarCharacters[@type='numbers']": "Numbers Exemplar Characters",
    }
    coremissing = {}
    for r in corereqs.keys():
        req = ldml.ldml.root.find(r)
        if req is None:
            coremissing[r]=corereqs.get(r)
    if len(coremissing) == 0: 
        return
    assert False, filename + " is missing Core Requirement(s): " + str(list(coremissing.values()))