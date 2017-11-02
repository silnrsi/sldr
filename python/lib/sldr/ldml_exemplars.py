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

from icu import Char, Script, UCharCategory, UScriptCode, Normalizer2, UNormalizationMode2, UnicodeString


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
    def isnukta(char):
        """True if the character is a nukta."""
        if Char.getCombiningClass(char) == 7:
            return True
        return False

    @staticmethod
    def is_specific_script(char):
        """True is the character has a specific Script property,
        that is, not the values Common or Inherited.
        """
        script = Script.getScript(char)
        script_code = Script.getScriptCode(script)
        if script_code == UScriptCode.COMMON or script_code == UScriptCode.INHERITED:
            return False
        return True

    @staticmethod
    def toupper(text):
        """Map string to uppercase."""
        lowercase = UnicodeString(text)
        uppercase = lowercase.toUpper()
        return unicode(uppercase)


class Exemplar(object):

    def __init__(self, base, marks=''):
        self.base = base
        self.marks = marks

    def _get_text(self):
        """Return the whole exemplar (base + mark)."""
        return self.base + self.marks

    text = property(_get_text)


class Exemplars(object):

    def __init__(self):
        self.ucd = UCD()

        # User settable configuration.
        self.many_bases = 5

        # User data that should be accessed through getters and setters.
        self._main = set()
        self._auxiliary = set()
        self._index = set()
        self._punctuation = set()

        # Internal parameters.
        self.clusters = set()
        self.bases_for_marks = dict()
        self.max_multigraph_length = 1

    def _set_main(self, ldml_exemplars):
        """Set LDML exemplars data for the main set."""
        self._main = self.ldml_read(ldml_exemplars)

    def _set_auxiliary(self, ldml_exemplars):
        """Set LDML exemplars data for the auxiliary set."""
        self._auxiliary = self.ldml_read(ldml_exemplars)

    def _set_index(self, ldml_exemplars):
        """Set LDML exemplars data for the index set."""
        self._index = self.ldml_read(ldml_exemplars)

    def _set_punctuation(self, ldml_exemplars):
        """Set LDML exemplars data for the punctuation set."""
        self._punctuation = self.ldml_read(ldml_exemplars)

    def _get_main(self):
        """Return LDML exemplars data for the main set."""
        return self.ldml_write(self._main)

    def _get_auxiliary(self):
        """Return LDML exemplars data for the auxiliary set."""
        return self.ldml_write(self._auxiliary)

    def _get_index(self):
        """Return LDML exemplars data for the index set."""
        return self.ldml_write(self._index)

    def _get_punctuation(self):
        """Return LDML exemplars data for the punctuation set."""
        return self.ldml_write(self._punctuation)

    main = property(_get_main, _set_main)
    auxiliary = property(_get_auxiliary, _set_auxiliary)
    index = property(_get_index, _set_index)
    punctuation = property(_get_punctuation, _set_punctuation)

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
        self.count_marks()
        self.analyze_marks()
        self.make_index()

    def count_marks(self):
        """Count how many different bases a mark occurs on."""
        for exemplar in self.clusters:
            for mark in exemplar.marks:
                if mark in self.bases_for_marks:
                    s = self.bases_for_marks[mark]
                    s.add(exemplar.base)
                else:
                    s = set()
                    s.add(exemplar.base)
                    self.bases_for_marks[mark] = s

    def analyze_marks(self):
        """Split clusters if needed before adding to exemplar list."""
        for exemplar in self.clusters:

            if len(exemplar.marks) == 0:
                self._main.add(exemplar.base)

            for mark in exemplar.marks:
                if mark in self.bases_for_marks:
                    s = self.bases_for_marks[mark]

                    # If a mark has more than many_bases ...
                    if len(s) > self.many_bases:
                        # then add the base and mark separately.
                        self._main.add(exemplar.base)
                        self._main.add(mark)
                    else:
                        # otherwise add the combined exemplar.
                        self._main.add(exemplar.text)

    def make_index(self):
        """Analyze the found exemplars for indices and classify them."""
        possible_index = self._main.union(self._auxiliary)
        for exemplar in possible_index:

            # An index should not be an isolated mark.
            if self.ucd.ismark(exemplar[0]):
                continue

            # Index exemplars are uppercase.
            uppercase = self.ucd.toupper(exemplar)
            self._index.add(uppercase)

    def allowable(self, char):
        """Make sure exemplars have the needed properties."""

        # Exemplars must be Alphabetic.
        if not Char.isUAlphabetic(char):
            return False

        # Exemplars must be lowercase.
        if Char.isUUppercase(char):
            return False

        # Exemplar must have a specific script.
        if not self.ucd.is_specific_script(char):
            return False

        # All conditions are met.
        return True

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

                if chars in self._main:
                    i += multigraph_length
                    break

                if chars in self._auxiliary:
                    i += multigraph_length
                    break

                if chars in self._index:
                    i += multigraph_length
                    break

                if chars in self._punctuation:
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
                self._punctuation.add(char)
                i += 1
                continue

            # Find grapheme clusters.

            # Ensure exemplar base has needed properties.
            if not self.allowable(char):
                i += 1
                continue

            # The current character is a base character.
            base = char

            # Then find the end of the cluster
            # (which may consist of only base characters).
            length = base_length = 1
            while i + length < len(text):
                mark = text[i + length]
                if self.ucd.ismark(mark):
                    # A Mark was found, so the cluster continues.
                    length += 1

                    # Nukta marks are considered part of the base.
                    if self.ucd.isnukta(mark):
                        # A nukta was found, so the base continues,
                        # as well as the cluster.
                        base_length += 1
                        base = text[i:i + base_length]
                    continue
                else:
                    # No more marks, so the end of the cluster has been reached.
                    break

            # Extract cluster

            # If no nuktas have been found,
            # then the base will be the single character already called base (or char).
            # If no non-nukta marks have been found,
            # then the marks variable will be an empty string.
            marks = text[i + base_length:i + length]
            exemplar = Exemplar(base, marks)

            self.clusters.add(exemplar)
            i += length


if __name__ == '__main__':
    main()
