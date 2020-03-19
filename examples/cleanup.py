#!/usr/bin/python3

from palaso.sldr.ldml import Ldml, iterate_files
import sys

if sys.argv[1].endswith('.xml'):
    files = [sys.argv[1]]
else:
    files = iterate_files(sys.argv[1])

for f in files:
    l = Ldml(f)
    l.normalise()
    l.save_as(f)
