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
    
    def test_parents(langid):
        lt = langtag(os.path.splitext(os.path.basename(langid))[0]) #gets basic langtag data based on file name
        tagset = lookup(str(lt).replace("_", "-"), default="", matchRegions=True)
        lt_text = str(tagset) #technically never used, but kept just in case need to compare old & new if test is updated or made more complex later
        root_tag = lt_text
        root_tagset = tagset
        
        def _has_sldr(root_tagset):
            return getattr(root_tagset, "sldr", None)
        
        print("data pre-test")
        print(root_tag)
        print(root_tagset)
        print(root_tagset.script)

        def _remove_private(root_tag):
            r = root_tag.rfind('-x')
            if r > 0:
                root_tag = root_tag[:r]
            root_tagset = lookup(str(root_tag).replace("_", "-"), default="", matchRegions=False)
            print("after removed private:")
            print(root_tag)
            print(root_tagset)
            return root_tag, root_tagset

        def _trim_tag(root_tag, root_tagset):
            r = root_tag.rfind('-')
            if r > 0:
                root_tag_temp = root_tag[:r]
                root_tagset_temp = lookup(str(root_tag_temp).replace("_", "-"), default="", matchRegions=False)
                print("after a tag trim iteration:")
                print(root_tag_temp)
                print(root_tagset_temp)
                print(root_tagset_temp.script)
                if root_tagset_temp == root_tagset:
                    print("tagsets still match, trim again!")
                    _trim_tag(root_tag_temp, root_tagset)
                elif root_tagset_temp.script == root_tagset.script:
                    if _has_sldr(root_tagset_temp):
                        print("new root found with sldr file :)")
                        root_tag = root_tag_temp
                    print("scripts still match, trim again!")
                    _trim_tag(root_tag_temp, root_tagset)
                elif root_tagset_temp == "":
                    print("no tagset found that matches, idk how bc that's not how it works but this error is here anyway just in case")
                    _trim_tag(root_tag_temp, root_tagset)
                else:
                    print("trimmed file has different script OR has no sldr file, final root tag is the last one we trimmed!")
                    root_tagset = root_tagset_temp
            else:
                print("no more trimming, final root is the last one we trimmed!")
            return root_tag, root_tagset            

        root_tag, root_tagset = _remove_private(root_tag)
        root_tag, root_tagset = _trim_tag(root_tag, root_tagset)
        
        if root_tagset == tagset:
            print("this is the root tagset, proceed to test for font!")
            return False
        return True
            
    if test_parents(langid):
        return    
    fonts = ldml.ldml.findall("special/sil:external-resources/sil:font")
    assert len(fonts) > 0 , filename + " has no font information"
