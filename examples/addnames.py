#!/usr/bin/python3

from langtag import lookup
from palaso.sldr.ldml import Ldml, iterate_files
import argparse, os

parser = argparse.ArgumentParser()
parser.add_argument("indir",help="Root of SLDR file tree")
parser.add_argument("-l","--ldml",help="ldml file identifier (without .xml)")
args = parser.parse_args()

if args.ldml:
    allfiles = [os.path.join(args.indir, args.ldml[0], args.ldml+".xml")]
else:
    allfiles = iterate_files(args.indir)

for f in allfiles:
    l = Ldml(f)
    if len(l.root) == 1 and l.root[0].tag == "identity":
        continue
    ident = l.find(".//identity/special/sil:identity")
    if ident is None or ident.get("source", "") == "cldr":
        continue
    name = os.path.splitext(os.path.basename(f))[0].replace("_", "-")
    tagset = lookup(name, "")
    if tagset == "":
        print("No langtag for " + name)
        continue
    ename = getattr(tagset, "name", None)
    if ename is not None:
        nameel = l.ensure_path('localeDisplayNames/special/sil:names/sil:name[@xml:lang="en"]')[0]
        if nameel.text is None:
            nameel.text = ename
    lnames = getattr(tagset, "localnames", [None])
    lname = getattr(tagset, "localname", lnames[0])
    if lname is not None:
        nameel = l.ensure_path('localeDisplayNames/languages/language[@type="{}"]'.format(name))[0]
        if nameel.text is None:
            nameel.text = lname
        elif nameel.text != lname and nameel.text not in lnames:
            print("Name difference for {} has {}, want to add {}".format(name, nameel.text, lname))
    l.normalise()
    l.save_as(f)

    

