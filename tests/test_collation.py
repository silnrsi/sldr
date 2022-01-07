import unittest
import pytest
import re
import icu
### from icu import UCollAttribute # needed for additional check for primary sorting in index exemplar
### from icu import UCollAttributeValue
import os
import logging, unicodedata
from lxml.etree import RelaxNG, parse, DocumentInvalid

curlybraces = re.compile(r"""\{
    ([^}]+)
    \}""",re.VERBOSE)

def iscldr(ldml):
    i = ldml.ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.ldml.namespaces.items()})
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

def test_collation(ldml):
    """ Test that index exemplar is sorted according to the default collation """
    if iscldr(ldml):    # short circuit CLDR for now until they/we resolve the faults in their data
        return
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference

#   is there a collation? If not, "" will use default.
    defcol = ldml.ldml.root.find(".//collations/defaultCollation")
    defcollation = defcol.text if defcol is not None else "standard"
    col_el = ldml.ldml.root.find(".//collations/collation[@type='" + defcollation + "']/cr")
    col = col_el.text if col_el is not None else ""
    try:
        rbc = icu.RuleBasedCollator(col)
    except icu.ICUError:
        assert False, filename + " has invalid ICU collation"
        return

#   get index exemplar
    index_el = ldml.ldml.root.find('.//characters/exemplarCharacters[@type="index"]')
    if index_el == None:
#        assert False, filename + " has no index exemplar" ### could be target of another test
        return
    index_list_raw = index_el.text[1:-1].strip().split(' ')     # make a list of index characters
    index_list = [re.sub(curlybraces, "\\1", c) for c in index_list_raw]   # remove curly braces
    sort_list = sorted(index_list, key=rbc.getSortKey)

    assert index_list == sort_list, filename + " index exemplar inconsistent with collation"

### Eventually add check that index exemplar elements are in primary sort relationship
#    rbc.setAttribute(UCollAttribute.STRENGTH, UCollAttributeValue.PRIMARY)
#    prev = b""
#    for i in index_list:
#         curr = rbc.getSortKey(i)
#         assert prev < curr, filename + " index exemplar not sorting at primary level"
#         prev = curr
