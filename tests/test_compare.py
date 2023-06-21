import os
import logging, os, re, unicodedata
from langtag import langtag, lookup
from test_parents import find_parents
#from sldr.utils import find_parents
#change this once the find parent stuff has a new home


#   IMPORTANT: 'exempt_lts' is a list of langtags that have been updated with new information in the most recent release cycle.
#   Since new information is not reflected in langtags.json until the following release, these files will always
#   fail until the next release cycle and are therefore excluded from the test. 
exempt_lts = [
    "acr",
    "amr",
    "apb",
    "bbk",
    "blt_Latn",
    "bcw",
    "cof",
    "fmp",
    "gdg",
    "kek",
    "lns",
    "mgc",
    "mim",
    "miz",
    "mxb",
    "mxv",
    "mzp",
    "she",
    "stp",
    "vau",
    "xtn",
    "zpu",
]
#   With each new langtags release, please CLEAR AND RESTART this list and update the date listed below.
#   Most Recent Langtags Release: 04 May 2023 

exempt_always = [
    "test.xml",
    "template.xml",
    "exemplar_template.xml"
]

def iscldr(ldml):
    i = ldml.ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.ldml.namespaces.items()})
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

def test_compautonym(ldml, langid):
    """ Test if the autonym matches the autonym listed in langtags. This test assumes the file passes test_basic """
#   NOTICE THAT THIS TEST REFERENCES THE LANGTAGS API AND NOT THE COPY IN GITHUB
    
    if iscldr(ldml):    # short circuit CLDR for now until they/we resolve the faults in their data
        return
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    lt = langtag(os.path.splitext(os.path.basename(langid))[0]) #gets basic langtag data based on file name
    lid = filename[:-4] 

#   automatically pass if the file's name (w/o the .xml extension) is in the 'exempt_lts' list
    for x in exempt_lts:
        if x == lid:
            return
        pass
    
#   get autonym from sldr file
    names = ldml.ldml.root.find("localeDisplayNames/languages") #after this if there is no names block it returns None
    autonym_text = ""
    if names is not None: 
        autonym = names.findall('language[@type="{0}"]'.format(lid)) #after this if there is no autonym it returns none
        if autonym == []:
            autonym_text = None
        else:
            autonym_text = unicodedata.normalize("NFD", autonym[0].text.lower())
    else:
        autonym_text = None

#   get autonym from langtags
    tagset = lookup(str(lt).replace("_", "-"), default="", matchRegions=True)
    lname_list = getattr(tagset, "localnames", None) 
    lname_str = getattr(tagset, "localname", None) 
    lname = ""
    lname_text = ""
    lname_list_text = []
    multautonyms = False
    if lname_list is not None:
        if len(lname_list) > 1: 
            multautonyms = True
        for x in lname_list:
            x_text = unicodedata.normalize("NFD", x.lower()).strip()
            if x_text == autonym_text:
                return  #this says that if there are multiple autonyms in the list and ANY match, that's good enough for now
            else:
                lname_list_text.append(x_text)  #this makes a list of all the autonyms for assert message
                lname_list_text_str = ', '.join(lname_list_text)
        lname = lname_list[0]
    elif lname_str is not None:
        lname = lname_str
    else: 
        lname_text = None
    if lname_text is not None:
        lname_text = unicodedata.normalize("NFD", lname.lower()).strip() 

    #at this point, autonym_text should either have the sldr autonym or be None, and lname_text should have the langtags autonym or be None. 

#   compare autonyms
    if autonym_text == lname_text:
        return
        #this will pass if both are None or if both match 
    elif autonym_text == None:
        assert False, filename + " langtags autonym (" + lname_text + ") missing from SLDR, no autonym listed in SLDR"
    elif lname_text == None:
        assert False, filename + " SLDR autonym (" + autonym_text + ") missing from langtags.json, no autonym listed in langtags.json"
    else:
        assert multautonyms == False, filename + " SLDR autonym (" + autonym_text + ") does not match any langtags autonyms (" + lname_list_text_str + ")"
        assert False, filename + " SLDR autonym (" + autonym_text + ") does not match langtags autonym (" + lname_text + ")"

    #test section for making sure variables work right
    print(lt) 
    print(names is None)
    print(autonym_text is None) 
    print(lname) 
    print(lname_text) 
    assert False, "test"

    #extra test for theoretical addition of variant/alternative autonyms in sldr
    if len(lname_list) > 1: 
        # Insert Logic Here: Are ALL of these in the alt autonyms of sldr file? how to check that idk yet need to think about it this is just an idea. 
        # maybe do a fixdata thing or something to add them in idk? 
        assert False, filename + " blah blah something something missing stuff idk "


# THIS WHOLE NEXT TEST IS SUPER SKECTH AND JUST A THOUGHT EXPERIMENT 
def test_singvplu(ldml, langid):
    """ this test basically asks which things in sldr do WE have autonyms listed for that ethnologue does not"""
    """follow up question ideally is then to ask if we can confirm these are right and if so can we send them to ethnologue"""
    if iscldr(ldml):    # short circuit CLDR for now until they/we resolve the faults in their data
        return
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    lt = langtag(os.path.splitext(os.path.basename(langid))[0]) #gets basic langtag data based on file name
    tagset = lookup(str(lt).replace("_", "-"), default="", matchRegions=True)
    lname_list = getattr(tagset, "localnames", None) 
    lname_str = getattr(tagset, "localname", None)
    if lname_list is None and lname_str is not None:
        assert False, filename + "has an autonym when data pulled from Ethnologue has none"


#note: this next test should definitely live somewhere else that isn't this particular file longterm but this is where i'm sticking it for now
def test_redundantsil(ldml, langid):
    """this test is supposed to tell me if there is sil:external-resources blocks in a file that only otherwise has an id block"""
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    for x in exempt_always:
        if filename == x:
            return
    blocklist = []
    is_root = find_parents(langid, False, True, True, False)[0]
    for b in ldml.ldml.root:
        blocklist.append(b.tag)     #gives me list of all the major element blocks, starting with 'identity' 
    if blocklist == ['identity', 'special'] and is_root == False:
        assert False, filename + " Redundant sil:external-resources detected"