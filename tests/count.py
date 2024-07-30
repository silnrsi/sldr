import os, json
import requests
import logging, re, unicodedata
from langtag import langtag, lookup
from sldr.utils import find_parents
from argparse import ArgumentParser
from sldr.ldml import Ldml, _alldrafts, getldml

def iscldr(ldml):
    i = ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.namespaces.items()})
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

root_sldr = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sldr")
filelist = []
for (root, dirs, file) in os.walk(root_sldr):
    for f in file:
        if '.xml' in f:
            filelist.append(f)
for f in filelist:
    if f == "root.xml" or f == "test.xml":
        continue
    tag = f[:-4].replace("_", "-")
    filep = os.path.join(root_sldr, tag[0], f)
    #file path from root_sldr to the actual file: see under 'root_sldr' about needing to change if this file is moved
    if os.path.exists(filep):
        ldml = Ldml(filep)
    filename = os.path.basename(ldml.fname)    # get filename for reference
    if iscldr(ldml):
        continue
    print(filename)