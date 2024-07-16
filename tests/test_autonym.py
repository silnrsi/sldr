### based on "test_exemplars" in test_validate.py
### not sure all these imports are needed
import unittest
import pytest
import logging, os, re, unicodedata
from lxml.etree import RelaxNG, parse, DocumentInvalid
import sldr.UnicodeSets as usets

allowed_chars = {
    "agd": "g",
    "aiw_Ethi": "\u1361",
    "fab": "\u0027",
}

def iscldr(ldml):
    i = ldml.ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.ldml.namespaces.items()})
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

def test_autonym(ldml):
    """ Test that all characters in the autonym are in the main exemplar """
    if iscldr(ldml):    # short circuit CLDR for now until they/we resolve the faults in their data
        return
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference

#   get main exemplar
    main = None
    for e in ldml.ldml.root.findall('.//characters/exemplarCharacters'):
        t = e.get('type', None)
        if t: continue
        main_exem = e.text
        if not main_exem or len(main_exem) <= 2:    ### 2021-10-22 pcg_Taml.xml is example where text is missing
#            assert False, filename + " has empty main exemplar" ### 2021-10-22 nuf.xml is ex where text is "[]"
            return
        main = usets.parse(main_exem, 'NFD')[0].asSet()
        break
    if not main:
#        assert False, filename + " has no main exemplar" ### should be target of another test
        return
#    assert "\u2019" not in main, filename + "U+2019 found in main exemplar, replace with apostrophe appropriate for orthography"

#   get language id
    lid = filename[:-4] #.replace("_", "-")
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
    if autonym is None or len(autonym) < 1: 
        longautonym = names.findall('language[@type="{0}"]'.format(lid))
        if longautonym is not None or len (longautonym)>1:
            assert False, filename + " " + lid + ": type needs to be changed to just the language, not the full langtag"
        assert False, filename + " " + lid + ": Name of language in this language is missing"
        return 
    autonym_text = unicodedata.normalize("NFD", autonym[0].text.lower())
    if len(autonym_text) < 1:
        assert False, filename + " " + lid + ": Name of language in this language is empty"
        return
#   The real test: is every character in lower case version of autonym in main exemplar?
    mainre = "^(" + "|".join(sorted(main, key=lambda x: (-len(x), x)) + ["\\s", ",", "-"] + [x for x in allowed_chars.get(lid,"")]) + ")*$"
    fullmain = []
    missing = ""
    missingcode = ""
    if allowed_chars.get(lid,"") != "":
        fullmain = sorted(main) +["\\s", ",", "-"] + [x for x in allowed_chars.get(lid,"")]
    else:
        fullmain = sorted(main) + ["\\s", ",", "-"]
    for c in autonym_text:
        if c not in fullmain and c not in missing:
            missing = missing + " " + c
            missingcode = missingcode + "U+" + format(ord(c), '04x') + ", "
#    assert re.match(mainre, autonym_text) is not None, \
#                filename + " " + lid + ": Name of language (" + autonym_text \
#                + ") contains characters not in main exemplar " + main_exem
    assert re.match(mainre, autonym_text) is not None, \
                filename + " " + lid + ": Name of language (" + autonym_text \
                + ") contains characters [" + missing + " ] (Codepoints: " + missingcode[:-2] + ") which are not in main exemplar " + main_exem
