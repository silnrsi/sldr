#!/usr/bin/python

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import codecs
from argparse import ArgumentParser
import re
from collections import Counter
from ucdXML import ucdXML
import unicodedata
# from palaso.teckit import engine

def main() :
    parser = ArgumentParser()
    # parser.add_argument('this',help='File of interest')
    parser.add_argument('corpus',help='Corpus to read')
    # parser.add_argument('-o','--output',help="Output file")
    args = parser.parse_args()

    exemplars = Exemplars()
    corpus = codecs.open(args.corpus, 'r', encoding='utf-8')
    for line in corpus :
        exemplars.process(line)
    print exemplars.get_main()
    print exemplars.get_auxiliary()
    print exemplars.get_index()
    print exemplars.get_punctuation()

class UCD(ucdXML) :

    def normalize(self, form, unistr) :
        """Return the normal form form for the Unicode string unistr.

        Valid values for form are 'NFC', 'NFKC', 'NFD', and 'NFKD'.
        """

        return unicodedata.normalize(form, unistr)

    def has_prop(self, prop, chars):
        """Determine if all the characters in a string have a specific property."""
        for char in chars :
            if self.getprop(prop, char, 'N') == 'N' :
                return False
        return True


class Exemplars(object) :

    def __init__(self) :
        self.ucd = UCD('ucd.nounihan.grouped.xml', re.compile(r'.'))

        # User settable configuration.
        self.many_bases = 5

        # User data that should be accessed through methods.
        self.main = set()
        self.auxiliary = set()
        self.index = set()
        self.punctuation = set()

        # Internal parameters.
        # self.bases = Counter()
        # self.marks = Counter()
        self.clusters = set()
        self.bases_for_marks = dict()
        self.max_multigraph_length = 1

    def set_main(self, ldml_exemplars) :
        """Set LDML exemplars data for the main set."""
        self.main = self.ldml_read(ldml_exemplars)

    def set_auxiliary(self, ldml_exemplars) :
        """Set LDML exemplars data for the auxiliary set."""
        self.auxiliary = self.ldml_read(ldml_exemplars)

    def set_index(self, ldml_exemplars) :
        """Set LDML exemplars data for the index set."""
        self.index = self.ldml_read(ldml_exemplars)

    def set_punctuation(self, ldml_exemplars) :
        """Set LDML exemplars data for the punctuation set."""
        self.punctuation = self.ldml_read(ldml_exemplars)

    def get_main(self) :
        """Return LDML exemplars data for the main set."""
        self.analyze()
        return self.ldml_write(self.main)

    def get_auxiliary(self) :
        """Return LDML exemplars data for the auxiliary set."""
        return self.ldml_write(self.auxiliary)

    def get_index(self) :
        """Return LDML exemplars data for the index set."""
        return self.ldml_write(self.auxiliary)

    def get_punctuation(self) :
        """Return LDML exemplars data for the punctuation set."""
        return self.ldml_write(self.punctuation)

    def remove_bookends(self, start, end, text) :
        """Remove specified bookends if they exist."""
        if text.startswith(start) and text.endswith(end):
            return text[1:-1]
        return text

    def ldml_read(self, ldml_exemplars) :
        """Read exemplars from a string from a LDML formatted file."""
        ldml_exemplars = self.ucd.normalize('NFD', ldml_exemplars)
        list_exemplars = self.remove_bookends('[', ']', ldml_exemplars).split()
        exemplars = set()
        for exemplar in list_exemplars :
            exemplar = self.remove_bookends('{', '}', exemplar)
            self.max_multigraph_length = max(self.max_multigraph_length, len(exemplar))
            exemplars.add(exemplar)
        return exemplars

    def ldml_write(self, exemplars) :
        """Write exemplars to a string that can be written to a LDML formatted file."""
        list_exemplars = list()
        for exemplar in exemplars :
            exemplar = self.ucd.normalize('NFC', exemplar)
            if len(exemplar) > 1 :
                exemplar = u'{' + exemplar + u'}'
            list_exemplars.append(exemplar)
        list_exemplars.sort()
        return u'{}{}{}'.format(u'[', ' '.join(list_exemplars), u']')

    def analyze(self) :
        """Analyze the found exemplars and classify them."""
        for exemplar in self.clusters :

            # Split apart the exemplar into a base and marks.
            # The sequence of marks maybe empty.
            base = exemplar[0]
            marks = exemplar[1:]

            if len(marks) == 0 :
                self.main.add(exemplar)

            for mark in marks :
                if mark in self.bases_for_marks :
                    s = self.bases_for_marks[mark]

                    # If a mark has more than many_bases ...
                    if len(s) > self.many_bases :
                        # then add the base and mark separately.
                        self.main.add(base)
                        self.main.add(mark)
                    else :
                        # otherwise add the combined exemplar.
                        self.main.add(exemplar)

    def process(self, text) :
        """Analyze a string."""
        i = 0
        multigraph_length = 0
        text = self.ucd.normalize('NFD', text)
        while i < len(text) :

            # Look for multigraphs (from length of max_multigraph_length down to 1) character(s)
            # of multigraphs already specified in a LDML file.
            # Longest possible matches are looked at first.
            for multigraph_length in range(self.max_multigraph_length, 0, -1) :
                chars = text[i:i + multigraph_length]

                if chars in self.main :
                    i += multigraph_length
                    break

                if chars in self.auxiliary :
                    i += multigraph_length
                    break

                if chars in self.index :
                    i += multigraph_length
                    break

                if chars in self.punctuation :
                    i += multigraph_length
                    break

            # No multigraphs were found at this position,
            # so continue processing a single character
            # if we have not gone beyond the end of the text.
            if not i < len(text) :
                break

            char = text[i]

            # Test for punctuation.
            if self.ucd.category(char).startswith('P') :
                self.punctuation.add(char)
                i += 1
                continue

            # Find grapheme clusters.

            # First find a base character.
            if not self.ucd.has_prop('Alpha', char) :
                i += 1
                continue
            # self.bases[char] += 1

            # The current character is a base character.
            base = char

            # Then find the end of the cluster
            # (which may consist of only a base character).
            length  = 1
            while i + length < len(text) :
                mark = text[i + length]
                if self.ucd.category(mark).startswith('M') :
                    # A Mark was found, so the cluster continues.

                    # Count how many different bases this mark occurs on.
                    if mark in self.bases_for_marks :
                        s = self.bases_for_marks[mark]
                        s.add(base)
                    else :
                        s = set()
                        s.add(base)
                        self.bases_for_marks[mark] = s
                    # self.marks[mark] += 1

                    length += 1
                    continue
                else :
                    # No more marks, so the end of the cluster has been reached.
                    break

            # Extract cluster
            cluster = text[i:i + length]

            self.clusters.add(cluster)
            i += length


# this = Exemplars(args.this)
#
#  if not args.output :
#     outfh = sys.stdout
# else :
#     outfh = codecs.open(outf, "w", encoding="utf-8")
#
# this.serialize_xml(outfh.write)
#
# if args.output :
#     outfh.close()

if __name__ == '__main__' :
    main()
