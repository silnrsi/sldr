import os
import logging, os, re, unicodedata
from langtag import langtag, lookup

#   IMPORTANT: 'exempt_lts' is a list of langtags that have been updated with new information in the most recent release cycle.
#   Since new information is not reflected in langtags.json until the following release, these files will always
#   fail until the next release cycle and are therefore excluded from the test. 
exempt_lts = [
    "apn",
    "bcw",
    "byr",
    "cmo_Khmr",
    "cof",
    "cok",
    "dwr",
    "dwr_Ethi", 
    "fmp",
    "loy",
    "mgc",
    "taq_Latn",
    "bcw",
]
#   With each new langtags release, please CLEAR AND RESTART this list and update the date listed below.
#   Most Recent Langtags Release: 16 Nov 2022  

def iscldr(ldml):
    i = ldml.ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.ldml.namespaces.items()})
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

def test_compautonym(ldml, langid):
    """ Test if the autonym matches the autonym listed in langtags. This test assumes the file passes test_basic """
#   NOTICE THAT THIS TEST REFERENCES THE BUILD VERSION OF LANGTAGS AND NOT THE WORKING COPY IN GITHUB
    
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
        autonym_text = unicodedata.normalize("NFD", autonym[0].text.lower())
    else:
        autonym_text = None

#   get autonym from langtags
    tagset = lookup(str(lt).replace("_", "-"), default="", matchRegions=True)
    lname_list = getattr(tagset, "localnames", None) #attempt to output the first in the list version, should be the same as the singular. 
    lname_str = getattr(tagset, "localname", None) #outputs the singular autonym, for some reason they aren't updated atm so it's secondary.
    lname = ""
    lname_text = ""
    if lname_list is not None:
        lname = lname_list[0]
    elif lname_str is not None:
        lname = lname_str
    else: 
        lname_text = None
    if lname_text is not None:
        lname_text = unicodedata.normalize("NFD", lname.lower()) 

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
        assert False, filename + " SLDR autonym (" + autonym_text + ") does not match langtags autonym (" + lname_text + ")"



    #test section for making sure variables work right
    print(lt) 
    print(names is None)
    print(autonym_text is None) 
    print(lname) 
    print(lname_text) 

    #assert False, "test"