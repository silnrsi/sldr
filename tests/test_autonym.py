### based on "test_exemplars" in test_validate.py
### not sure all these are needed
import unittest
import pytest
import logging, os
from lxml.etree import RelaxNG, parse, DocumentInvalid

def test_autonym(ldml):
#    if iscldr(ldml):    # short circuit CLDR for now until they/we resolve the faults in their data
#        return
#   get main exemplar
    main = None
    for e in ldml.ldml.root.findall('.//characters/exemplarCharacters'):
        t = e.get('type', None)
        if t: continue
        main_display = e.text
        main = set(e.text[1:-1].split(' '))
        break
    if not main:
        return # or flag error that there's no main exemplar!
#   get language id
    langid = ldml.ldml.root.find("identity/language").get("type")
#   get name of this language
    names = ldml.ldml.root.find("localeDisplayNames/languages")
    if names is None:
        # error: no Display Names
        return
    autonym = names.findall('language[@type="{0}"]'.format(langid))
    if autonym is None: 
        # error: name of language missing
        return 
    autonym_text = autonym[0].text.lower()
    if len(autonym_text) < 1:
        # error: name of language missing
        return
    
#   assert every character in lower case version of autonym is in main exemplar
    assert set("".join(autonym_text.split(" "))) < main, langid + ": Name of language (" + autonym_text + ") contains characters not in main exemplar " + main_display
