import unittest
import pytest
import re
import icu
import os
import logging, unicodedata
from lxml.etree import RelaxNG, parse, DocumentInvalid

curlybraces = re.compile(r"""\{
    ([^}]+)
    \}""",re.VERBOSE)

def iscldr(ldml):
    i = ldml.ldml.find(".//identity/special/sil:identity")
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

def test_collation(ldml):
    """ Test that index exemplar is sorted according to the default collation """
    if iscldr(ldml):    # short circuit CLDR for now until they/we resolve the faults in their data
        return
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference

#   is there a collation?
    defcol = ldml.ldml.root.find(".//collations/defaultCollation")
    defcollation = defcol.text if defcol is not None else "standard"
    col_el = ldml.ldml.root.find(".//collations/collation[@type='" + defcollation + "']/cr")
    if col_el == None:
        return
    try:
        rbc = icu.RuleBasedCollator(col_el.text)
    except icu.ICUError:
        assert False, filename + " has invalid ICU collation"
        return

#   get index exemplar
    index_el = ldml.ldml.root.find('.//characters/exemplarCharacters[type="index"]')
    if index_el == None:
#        assert False, filename + " has no index exemplar" ### could be target of another test
        return
    index_list_raw = index_el.text[1:-1].split(' ')     # make a list of index characters
    index_list = [re.sub(curlybraces, "\\1", c) for c in index_list_raw]   # remove curly braces
    sort_list = sorted(index_list, key=rbc.getSortKey)

    assert index_list == sort_list, filename + " index exemplar inconsistent with collation"
