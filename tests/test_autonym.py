### based on "test_exemplars" in test_validate.py
### not sure all these imports are needed
import unittest
import pytest
import logging, os
from lxml.etree import RelaxNG, parse, DocumentInvalid
import palaso.sldr.UnicodeSets as usets

def iscldr(ldml):
    i = ldml.ldml.find(".//identity/special/sil:identity")
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

def test_autonym(ldml):
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference

    if iscldr(ldml):    # short circuit CLDR for now until they/we resolve the faults in their data
        return

#   get main exemplar
    main = None
    for e in ldml.ldml.root.findall('.//characters/exemplarCharacters'):
        t = e.get('type', None)
        if t: continue
        main_exem = e.text
        main = usets.parse(main_exem, 'NFD')
        break
    if not main:
#        assert False, filename + " has no main exemplar" ### should be target of another test
        return

#   get language id
    langid = ldml.ldml.root.find("identity/language").get("type")
    ### should be target of another test:
    ### could check that filename.split('_')[0] == langid
    #assert filename.split('_')[0] == langid, filename + " " + langid + " don't correspond" 

#   get name of this language
    names = ldml.ldml.root.find("localeDisplayNames/languages")
    if names is None:
#        assert False, filename + " has no localeDisplayNames"
        return
    autonym = names.findall('language[@type="{0}"]'.format(langid))
    if autonym is None: 
        assert False, filename + " " + langid + ": Name of language in this language is missing"
        return 
    autonym_text = autonym[0].text.lower()
    if len(autonym_text) < 1:
        assert False, filename + " " + langid + ": Name of language in this language is empty"
        return
#   The real test: is every character in lower case version of autonym in main exemplar?
    nameset = usets.parse("[" + " ".join(set(autonym_text)) + "]", 'NFD')
    assert nameset <= main, filename + " " + langid + ": Name of language (" + autonym_text + ") contains characters not in main exemplar " + main_exem
