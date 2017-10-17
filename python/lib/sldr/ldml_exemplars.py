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

from icu import Char, UCharCategory, Normalizer2, UNormalizationMode2, UnicodeString


def main():
    pass


class UCD(object):

    def __init__(self):
        # Maybe in new versions of PyICU the following
        # (now commented out) shorthand function is defined.
        # self.normalizer_nfc = Normalizer2.getNFCInstance()

        # Since it is not, use the non-shorthand function with the needed parameters
        self.normalizer_nfc = Normalizer2.getInstance(None, 'nfc', UNormalizationMode2.COMPOSE)
        self.normalizer_nfd = Normalizer2.getInstance(None, 'nfc', UNormalizationMode2.DECOMPOSE)
        self.normalizer_nfkc = Normalizer2.getInstance(None, 'nfkc', UNormalizationMode2.COMPOSE)
        self.normalizer_nfkd = Normalizer2.getInstance(None, 'nfkc', UNormalizationMode2.DECOMPOSE)

    def normalize(self, form, text):
        """Return the normal form form for the Unicode string unistr.

        Valid values for form are 'NFC', 'NFKC', 'NFD', and 'NFKD'.
        """

        if form == 'NFC':
            return self.normalizer_nfc.normalize(text)
        elif form == 'NFD':
            return self.normalizer_nfd.normalize(text)
        elif form == 'NFKC':
            return self.normalizer_nfkc.normalize(text)
        elif form == 'NFKD':
            return self.normalizer_nfkd.normalize(text)

    @staticmethod
    def ismark(char):
        """True if the character is a mark (general category M)."""

        numeric_char_type = Char.charType(char)
        if (numeric_char_type == UCharCategory.NON_SPACING_MARK or
            numeric_char_type == UCharCategory.COMBINING_SPACING_MARK or
            numeric_char_type == UCharCategory.ENCLOSING_MARK):
            return True
        return False

    @staticmethod
    def tolower(text):
        """Map string to lowercase."""
        uppercase = UnicodeString(text)
        lowercase = uppercase.toLower()
        return unicode(lowercase)

    @staticmethod
    def toupper(text):
        """Map string to uppercase."""
        lowercase = UnicodeString(text)
        uppercase = lowercase.toUpper()
        return unicode(uppercase)


class Exemplars(object):

    def __init__(self):
        self.ucd = UCD()

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

    def set_main(self, ldml_exemplars):
        """Set LDML exemplars data for the main set."""
        self.main = self.ldml_read(ldml_exemplars)

    def set_auxiliary(self, ldml_exemplars):
        """Set LDML exemplars data for the auxiliary set."""
        self.auxiliary = self.ldml_read(ldml_exemplars)

    def set_index(self, ldml_exemplars):
        """Set LDML exemplars data for the index set."""
        self.index = self.ldml_read(ldml_exemplars)

    def set_punctuation(self, ldml_exemplars):
        """Set LDML exemplars data for the punctuation set."""
        self.punctuation = self.ldml_read(ldml_exemplars)

    def get_main(self):
        """Return LDML exemplars data for the main set."""
        self.analyze()
        return self.ldml_write(self.main)

    def get_auxiliary(self):
        """Return LDML exemplars data for the auxiliary set."""
        return self.ldml_write(self.auxiliary)

    def get_index(self):
        """Return LDML exemplars data for the index set."""
        self.analyze()
        return self.ldml_write(self.index)

    def get_punctuation(self):
        """Return LDML exemplars data for the punctuation set."""
        return self.ldml_write(self.punctuation)

    @staticmethod
    def remove_bookends(start, end, text):
        """Remove specified bookends if they exist."""
        if text.startswith(start) and text.endswith(end):
            return text[1:-1]
        return text

    def ldml_read(self, ldml_exemplars):
        """Read exemplars from a string from a LDML formatted file."""
        ldml_exemplars = self.ucd.normalize('NFD', ldml_exemplars)
        list_exemplars = self.remove_bookends('[', ']', ldml_exemplars).split()
        exemplars = set()
        for exemplar in list_exemplars:
            exemplar = self.remove_bookends('{', '}', exemplar)
            self.max_multigraph_length = max(self.max_multigraph_length, len(exemplar))
            exemplars.add(exemplar)
        return exemplars

    def ldml_write(self, exemplars):
        """Write exemplars to a string that can be written to a LDML formatted file."""
        list_exemplars = list()
        # sort first so {} don't group together
        for exemplar in sorted(exemplars):
            exemplar = self.ucd.normalize('NFC', exemplar)
            if len(exemplar) > 1:
                exemplar = u'{' + exemplar + u'}'
            list_exemplars.append(exemplar)
        return u'[{}]'.format(' '.join(list_exemplars))

    def analyze(self):
        """Analyze the found exemplars and classify them."""
        self.analyze_marks()
        self.analyze_index()

    def analyze_marks(self):
        """Analyze the found exemplars for marks and classify them."""
        for exemplar in self.clusters:

            # Split apart the exemplar into a base and marks.
            # The sequence of marks maybe empty.
            base = exemplar[0]
            marks = exemplar[1:]

            if len(marks) == 0:
                self.main.add(exemplar)

            for mark in marks:
                if mark in self.bases_for_marks:
                    s = self.bases_for_marks[mark]

                    # If a mark has more than many_bases ...
                    if len(s) > self.many_bases:
                        # then add the base and mark separately.
                        self.main.add(base)
                        self.main.add(mark)
                    else:
                        # otherwise add the combined exemplar.
                        self.main.add(exemplar)

    def analyze_index(self):
        """Analyze the found exemplars for indices and classify them."""
        possible_index = self.main.union(self.auxiliary)
        for exemplar in possible_index:

            # An index should not be an isolated mark.
            if self.ucd.ismark(exemplar[0]):
                continue

            # The lowercase version of an index must be in the main or auxiliary lists.
            lowercase = self.ucd.tolower(exemplar)
            if lowercase in possible_index:
                uppercase = self.ucd.toupper(exemplar)
                self.index.add(uppercase)

    def process(self, text):
        """Analyze a string."""
        i = 0
        text = self.ucd.normalize('NFD', text)
        while i < len(text):

            # Look for multigraphs (from length of max_multigraph_length down to 1) character(s)
            # of multigraphs already specified in a LDML file.
            # Longest possible matches are looked at first.
            for multigraph_length in range(self.max_multigraph_length, 0, -1):
                chars = text[i:i + multigraph_length]

                if chars in self.main:
                    i += multigraph_length
                    break

                if chars in self.auxiliary:
                    i += multigraph_length
                    break

                if chars in self.index:
                    i += multigraph_length
                    break

                if chars in self.punctuation:
                    i += multigraph_length
                    break

            # No multigraphs were found at this position,
            # so continue processing a single character
            # if we have not gone beyond the end of the text.
            if not i < len(text):
                break

            char = text[i]

            # Test for punctuation.
            if Char.ispunct(char):
                self.punctuation.add(char)
                i += 1
                continue

            # Find grapheme clusters.

            # First find a base character.
            if not Char.isUAlphabetic(char):
                i += 1
                continue
            # self.bases[char] += 1

            # The current character is a base character.
            base = char

            # Then find the end of the cluster
            # (which may consist of only a base character).
            length = 1
            while i + length < len(text):
                mark = text[i + length]
                if self.ucd.ismark(mark):
                    # A Mark was found, so the cluster continues.

                    # Count how many different bases this mark occurs on.
                    if mark in self.bases_for_marks:
                        s = self.bases_for_marks[mark]
                        s.add(base)
                    else:
                        s = set()
                        s.add(base)
                        self.bases_for_marks[mark] = s
                    # self.marks[mark] += 1

                    length += 1
                    continue
                else:
                    # No more marks, so the end of the cluster has been reached.
                    break

            # Extract cluster
            cluster = text[i:i + length]

            self.clusters.add(cluster)
            i += length


if __name__ == '__main__':
    main()
