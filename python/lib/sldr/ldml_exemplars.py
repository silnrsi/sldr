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

from icu import Char, Script, UCharCategory, UProperty, UScriptCode
from icu import Normalizer2, UNormalizationMode2, UnicodeString
from collections import Counter
import codecs

try:
    import sldr.UnicodeSets
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sldr', 'python', 'lib')))
    import sldr.UnicodeSets


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
        """Return the normal form form for the Unicode string text.

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

    def normalize_nfc(self, text):
        """Return the NFC form for the Unicode string text."""
        return self.normalize('NFC', text)

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

    def is_always_combine(self, char):
        """True if Mark always combines (logically) with the base character."""
        if self.isnukta(char):
            return True
        return False

    @staticmethod
    def is_sometimes_combine(char):
        """True if Mark sometimes combines (logically) with the base character."""
        if 0x0300 <= ord(char) <= 0x036F:
            return True
        return False

    def is_never_combine(self, char):
        """True if Mark never combines (logically) with the base character."""
        if self.is_always_combine(char):
            return False
        if self.is_sometimes_combine(char):
            return False
        return True

    @staticmethod
    def isnumber(char):
        """True if the character is a number (general category Nd or No)."""
        numeric_char_type = Char.charType(char)
        if (numeric_char_type == UCharCategory.DECIMAL_DIGIT_NUMBER or
           numeric_char_type == UCharCategory.OTHER_NUMBER):
            return True
        return False

    @staticmethod
    def isformat(char):
        """True if the character is a format character (general category Cf)."""
        numeric_char_type = Char.charType(char)
        if numeric_char_type == UCharCategory.FORMAT_CHAR:
            return True
        return False

    @staticmethod
    def is_space_separator(char):
        """True if the character is space separator (general category Zs)."""
        numeric_char_type = Char.charType(char)
        if numeric_char_type == UCharCategory.SPACE_SEPARATOR:
            return True
        return False

    @staticmethod
    def is_pua(char):
        """True if the character is a PUA character."""
        numeric_char = ord(char)
        if 0xE000 <= numeric_char <= 0xF8FF:
            return True
        if 0xFFF80 <= numeric_char < 0xFFFFE:
            return True
        if 0x10FF80 <= numeric_char < 0x10FFFE:
            return True
        return False

    @staticmethod
    def is_specific_script(char):
        """True if the character has a specific Script property,
        that is, not the values Common or Inherited.
        """
        script = Script.getScript(char)
        script_code = Script.getScriptCode(script)
        if script_code == UScriptCode.COMMON or script_code == UScriptCode.INHERITED:
            return False
        return True

    @staticmethod
    def is_exemplar_wordbreak(char):
        """True if the character has the Word_Break properties Katakana, ALetter, or MidLetter."""

        # The following should be exposed by PyICU, but does not seem to be implemented.
        # There are other values, but these are the ones need for this function.
        WB_ALETTER = 1
        WB_KATAKANA = 3
        # WB_MIDLETTER = 4

        numeric_wordbreak_type = Char.getIntPropertyValue(char, UProperty.WORD_BREAK)
        if (numeric_wordbreak_type == WB_KATAKANA or
           # numeric_wordbreak_type == WB_MIDLETTER or
           numeric_wordbreak_type == WB_ALETTER):
            return True
        return False

    def ispunct(self, char):
        """True if the character is punctuation for purposes of finding exemplars."""

        # Some punctuation characters have other properties
        # that means they are not punctuation exemplars.
        if self.is_exemplar_wordbreak(char):
            return False

        return Char.ispunct(char)

    @staticmethod
    def toupper(text):
        """Map string to uppercase."""
        #lowercase = UnicodeString(text)  # Python 2
        #uppercase = lowercase.toUpper()
        #return unicode(uppercase)

        return text.upper()


    def need_hex_escape(self, char, is_isolated):
        """Determine if a characters needs to be escaped with hex digits."""
        if self.ismark(char) and is_isolated:
            return True
        if Char.hasBinaryProperty(char, UProperty.DEFAULT_IGNORABLE_CODE_POINT):
            return True
        if self.isformat(char):
            return True
        if self.is_space_separator(char):
            return True
        if self.is_pua(char):
            return True
        return False


class Exemplar(object):

    def __init__(self, base, trailers=''):
        self.base = base
        self.trailers = trailers

    def _get_text(self):
        """Return the whole exemplar (base + mark)."""
        return self.base + self.trailers

    text = property(_get_text)

    def __str__(self):
        if self.trailers == '':
            return self.base
        else:
            return '{} {}'.format(self.base, self.trailers)

    def __repr__(self):
        base = codecs.encode(self.base, 'unicode_escape')
        if self.trailers == '':
            return "'Exemplar('{}')'".format(base)
        else:
            trailers = codecs.encode(self.trailers, 'unicode_escape')
            return "'Exemplar('{}', '{}')'".format(base, trailers)

    def __hash__(self):
        return hash((self.base, self.trailers))

    def __eq__(self, other):
        if self.base == other.base and self.trailers == other.trailers:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Exemplars(object):

    def __init__(self):
        self.ucd = UCD()

        # User settable configuration.
        self.many_bases = 5
        self.frequent = 1

        # User data that should be accessed through getters and setters.
        self._main = set()
        self._auxiliary = set()
        self._index = set()
        self._punctuation = set()
        self._digits = set()
        self._graphemes = list()
        self._frequency = list()

        # Internal parameters.
        self.clusters = Counter()
        self.scripts = Counter()
        self.codes_for_scripts = dict()
        self.bases_for_marks = dict()
        self.max_multigraph_length = 1
        self.always_separate_marks = set()
        self.need_splitting = True

        self.unittest = False

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

    def _set_digits(self, ldml_exemplars):
        """Set LDML exemplars data for the digits set."""
        self._digits = self.ldml_read(ldml_exemplars)

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

    def _get_digits(self):
        """Return LDML exemplars data for the digits set."""
        return self.ldml_write(self._digits)

    def _get_graphemes(self):
        """Return the list of found graphemes."""
        return self.ldml_write(self._graphemes, sort=False)

    def _get_frequency(self):
        """Return the list of found graphemes with frequency of occurrence."""
        return self.ldml_write(self._frequency, sort=False)

    def _get_script(self):
        """Return most frequently occurring script."""
        script_code_and_count_list = self.scripts.most_common(1)
        if len(script_code_and_count_list) == 0:
            return ''
        else:
            script_code_and_count = script_code_and_count_list[0]
            script_code = script_code_and_count[0]
            script = self.codes_for_scripts[script_code]
            script_name = Script.getShortName(script)
            return script_name

    main = property(_get_main, _set_main)
    auxiliary = property(_get_auxiliary, _set_auxiliary)
    index = property(_get_index, _set_index)
    punctuation = property(_get_punctuation, _set_punctuation)
    digits = property(_get_digits, _set_digits)
    graphemes = property(_get_graphemes)
    frequency = property(_get_frequency)
    script = property(_get_script)

    def ldml_read(self, ldml_exemplars):
        """Read exemplars from a string from a LDML formatted file."""
        if self.unittest:
            list_exemplars = ldml_exemplars.split()
        else:
            list_exemplars = sldr.UnicodeSets.us2list(ldml_exemplars)
        exemplars = set()
        for exemplar in list_exemplars:
            exemplar = self.ucd.normalize('NFD', exemplar)
            self.max_multigraph_length = max(self.max_multigraph_length, len(exemplar))
            exemplars.add(exemplar)
        return exemplars

    def ldml_write(self, exemplars, sort=True):
        """Write exemplars to a string that can be written to a LDML formatted file."""
        if sort:
            # Exemplars mentioned in UTS #35 need to be sorted.
            list_exemplars = list()
            for exemplar in sorted(exemplars):
                list_exemplars.append(exemplar)
        else:
            # Graphemes should be sorted by frequency,
            # and since they already are,
            # do nothing further here with the order.
            list_exemplars = exemplars

        list_nfc_exemplars = map(self.ucd.normalize_nfc, list_exemplars)
        if self.unittest:
            return ' '.join(list_nfc_exemplars)
        else:
            return sldr.UnicodeSets.list2us(list_nfc_exemplars, self.ucd)

    def analyze(self):
        """Analyze the found exemplars and classify them."""
        self.ignore_phantoms()
        self.find_punctuation()
        self.save_graphemes()
        self.find_numbers()
        self.count_marks()
        while self.need_splitting:
            self.need_splitting = False
            self.find_indic_matras_and_viramas()
            self.find_marks_on_same_bases()
            self.find_productive_marks()
            self.find_second_marks()
        self.parcel_ignorable()
        self.parcel_frequency()
        self.make_index()

    def ignore_phantoms(self):
        """Ignore phantom exemplars.

        Phantoms are exemplars that have been set in one of the exemplar fields
        (such as main or auxiliary) initially but not seen in the actual data processed.
        """
        self._main = set()
        self._auxiliary = set()
        self._index = set()
        self._punctuation = set()
        self._digits = set()

    def find_punctuation(self):
        """Put punctuation into the punctuation exemplar."""
        for exemplar in list(self.clusters.keys()):
            if self.ucd.ispunct(exemplar.base[0]):
                self._punctuation.add(exemplar.base)
                del self.clusters[exemplar]

    def save_graphemes(self):
        """Save the list of found graphemes."""
        for exemplar, count in self.clusters.most_common():
            self._graphemes.append(exemplar.text)
            self._frequency.append(u'{}:{}'.format(exemplar.text, count))

    def count_marks(self):
        """Count how many different bases a mark occurs on."""
        for exemplar in self.clusters.keys():
            for trailer in exemplar.trailers:
                if not self.ucd.ismark(trailer):
                    continue

                # Only Marks get counted (and added to self.bases_for_marks).
                mark = trailer
                if mark in self.bases_for_marks:
                    bases_for_mark = self.bases_for_marks[mark]
                    bases_for_mark.add(exemplar.base)
                else:
                    bases_for_mark = set()
                    bases_for_mark.add(exemplar.base)
                    self.bases_for_marks[mark] = bases_for_mark

    def find_numbers(self):
        """Numbers without diacritics go into the digits exemplar."""
        for exemplar in list(self.clusters.keys()):
            if self.ucd.isnumber(exemplar.base) and len(exemplar.trailers) == 0:
                self._digits.add(exemplar.base)
                del self.clusters[exemplar]

    def split_exemplar(self, exemplar, index, count):
        """Split an exemplar into separate exemplars."""

        # If the exemplar is already a separate mark,
        # the base of the exemplar will be an empty string,
        # and therefore no further processing is needed
        # on that exemplar.
        if exemplar.base == '':
            return

        mark = exemplar.trailers[index]
        before_current_mark = exemplar.trailers[:index]
        after_current_mark = exemplar.trailers[index+1:]

        exemplar_mark = Exemplar('', mark)
        self.clusters[exemplar_mark] += count

        new_exemplar = Exemplar(exemplar.base, before_current_mark + after_current_mark)
        self.clusters[new_exemplar] += count

        del self.clusters[exemplar]
        self.need_splitting = True

    def find_indic_matras_and_viramas(self):
        """Indic matras and viramas are always separate marks."""
        for exemplar in list(self.clusters.keys()):
            count = self.clusters[exemplar]
            for trailer_index in range(len(exemplar.trailers)):
                trailer = exemplar.trailers[trailer_index]
                if (self.ucd.is_never_combine(trailer) or
                   Char.hasBinaryProperty(trailer, UProperty.DEFAULT_IGNORABLE_CODE_POINT)):
                    self.split_exemplar(exemplar, trailer_index, count)

    def find_marks_on_same_bases(self):
        """If a set of diacritics has the sames bases, the diacritics are separate."""
        for exemplar in list(self.clusters.keys()):
            count = self.clusters[exemplar]
            for trailer_index in range(len(exemplar.trailers)):
                trailer = exemplar.trailers[trailer_index]
                if trailer in self.bases_for_marks:
                    # The trailer is a Mark, as it was found,
                    # and only Marks are in that data structure.
                    current_mark = trailer
                    current_bases = self.bases_for_marks[current_mark]

                    # Compare the current set of bases to all the other sets of bases.
                    for other_mark in self.bases_for_marks.keys():
                        if current_mark != other_mark:
                            other_bases = self.bases_for_marks[other_mark]
                            difference = current_bases.symmetric_difference(other_bases)
                            if len(difference) == 0:
                                self.split_exemplar(exemplar, trailer_index, count)

    def find_productive_marks(self):
        """Split clusters if a mark occurs on many bases."""
        for exemplar in list(self.clusters.keys()):
            count = self.clusters[exemplar]
            for trailer_index in range(len(exemplar.trailers)):
                trailer = exemplar.trailers[trailer_index]
                if trailer in self.bases_for_marks:
                    # The trailer is a Mark, as it was found,
                    # and only Marks are in that data structure.
                    mark = trailer
                    bases_for_mark = self.bases_for_marks[mark]

                    # If a mark has more than many_bases ...
                    if len(bases_for_mark) > self.many_bases:
                        # then the base and mark are separate exemplars.
                        self.split_exemplar(exemplar, trailer_index, count)

    def find_second_marks(self):
        """Split clusters if a mark is a second or later stacking diacritic."""
        for exemplar in list(self.clusters.keys()):
            count = self.clusters[exemplar]
            for trailer_index in range(len(exemplar.trailers)):
                trailer = exemplar.trailers[trailer_index]

                # If the mark has already been found to be a always separate mark,
                # split the exemplar.
                if trailer in self.always_separate_marks:
                    self.split_exemplar(exemplar, trailer_index, count)

                # Only graphemes with more than one mark need to be looked at
                # for finding stacking diacritics that are separate.
                if trailer_index > 0:

                    current_mark_ccc = Char.getCombiningClass(trailer)
                    previous_mark_ccc = Char.getCombiningClass(previous_trailer)

                    # If a mark has the same combining class (ccc) as the previous mark,
                    # then the mark is a second or later stacking diacritic and is a separate mark.
                    # Also, if the mark has already been found to be a always separate mark,
                    # split the exemplar.
                    if current_mark_ccc == previous_mark_ccc:
                        self.always_separate_marks.add(trailer)
                        self.split_exemplar(exemplar, trailer_index, count)

                previous_trailer = trailer

    def parcel_ignorable(self):
        """Move Default_Ignorable_Code_Point characters to auxiliary."""
        for exemplar in list(self.clusters.keys()):
            for trailer in exemplar.trailers:
                if trailer not in self.bases_for_marks:
                    # if Char.hasBinaryProperty(trailer, UProperty.DEFAULT_IGNORABLE_CODE_POINT):
                    # The trailer is a Default_Ignorable_Code_Point
                    # which needs to go in the auxiliary list.
                    self._auxiliary.add(trailer)
                    del self.clusters[exemplar]

    def parcel_frequency(self):
        """Parcel exemplars between main and auxiliary based on frequency."""
        total_count = sum(self.clusters.values())
        item_count = len(self.clusters)
        if item_count != 0:
            average = total_count / float(item_count)
        else:
            average = 0
        frequent = average * (self.frequent / float(100))

        for exemplar in self.clusters.keys():
            occurs = self.clusters[exemplar]
            if occurs > frequent:
                self._main.add(exemplar.text)
            else:
                self._auxiliary.add(exemplar.text)

    def make_index(self):
        """Analyze the found exemplars for indices and classify them."""
        possible_index = self._main  # .union(self._auxiliary)
        for exemplar in possible_index:

            # An index cannot be an empty string.
            # This case should not occur, but it does, uncomment the test below
            # to enable the script to run without errors until the bug that is
            # causing empty exemplars to be produced is fixed.
            # if exemplar == '':
            #     continue

            # An index should not be an isolated mark.
            if self.ucd.ismark(exemplar[0]):
                continue

            # Index exemplars are uppercase.
            uppercase = self.ucd.toupper(exemplar)
            self._index.add(uppercase)

    def allowable(self, char):
        """Make sure exemplars have the needed properties."""

        # Numbers with or without diacritics need to be allowed.
        if self.ucd.isnumber(char):
            return True

        # Exemplars must be lowercase.
        if Char.isUUppercase(char):
            return False

        # Characters with a specific script can be exemplars.
        if self.ucd.is_specific_script(char):
            return True

        # Some punctuation and symbols are handled as letters.
        if self.ucd.is_exemplar_wordbreak(char):
            return True

        # Other characters must be Alphabetic.
        if Char.isUAlphabetic(char):
            return True

        return False

    def process(self, text):
        """Analyze a string."""
        i = 0
        text = self.ucd.normalize('NFD', text)

        # Record script of each character.
        for char in text:
            script = Script.getScript(char)
            script_code = Script.getScriptCode(script)
            self.scripts[script_code] += 1
            self.codes_for_scripts[script_code] = script

        # Record clusters
        while i < len(text):

            # Look for multigraphs (from length of max_multigraph_length down to 1) character(s)
            # of multigraphs already specified in a LDML file.
            # Longest possible matches are looked at first.
            for multigraph_length in range(self.max_multigraph_length, 0, -1):
                multigraph = text[i:i + multigraph_length]

                if (multigraph in self._main or
                   multigraph in self._auxiliary or
                   multigraph in self._index or
                   multigraph in self._punctuation):
                    exemplar = Exemplar(multigraph)
                    self.clusters[exemplar] += 1
                    i += multigraph_length
                    break

            # No multigraphs were found at this position,
            # so continue processing a single character
            # if we have not gone beyond the end of the text.
            if not i < len(text):
                break

            char = text[i]

            # Test for punctuation.
            if self.ucd.ispunct(char):
                exemplar = Exemplar(char)
                self.clusters[exemplar] += 1
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
                trailer = text[i + length]
                if Char.hasBinaryProperty(trailer, UProperty.DEFAULT_IGNORABLE_CODE_POINT):
                    # A Default_Ignorable_Code_Point was found, so the cluster continues.
                    length += 1
                    continue
                if self.ucd.ismark(trailer):
                    # A Mark was found, so the cluster continues.
                    length += 1

                    # Marks such as nuktas are considered part of the base.
                    if self.ucd.is_always_combine(trailer):
                        # A Mark such as a nukta was found, so the base continues,
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
            # then the trailers variable will be an empty string.
            trailers = text[i + base_length:i + length]
            exemplar = Exemplar(base, trailers)

            self.clusters[exemplar] += 1
            i += length


if __name__ == '__main__':
    main()
