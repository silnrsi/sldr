# Wordlist File Formats

## Introduction

There are various file formats for storing wordlists. Most of them are either
comma or tab separated lists. The columns of the lists usually have the lexical
entry as the first item with other information about the item as subsequent
columns which may be empty or marked empty.

## File Formats

### Unilex

A Unilex file is TSV but the first line contains column identifiers. Then there
is the header comment section which may have empty lines or comment lines
starting with a `#`. `*` marks an empty field.

Column Aliases which are not necessarily needed:

| Name | Field Id |
+------+----------+
| Form | word |
| Frequency | freq |
| Hyphenation | hyphen |
| PartOfSpeech | pos |
| MorphologyClass | morph |
| Features | features |
| Pronunciation | ipa |

Feature Aliases:

| Name | Field Id |
+------+----------+
| Number | gnumber |
| Person | gperson |

### Keyman

The lexical model wordlists are TSV with no header line but initial comments
with `#`.

The columns used in wordlist.tsv are:

    word, freq, notes

fields may be blank or even missing (no tab).

## Fields

Here we list the universal set of fields and their semantics, in summary. A file
format may use an alias to map from surface fields to the universal set.

| Field Id | Description |
+----------+-------------+
| word     | The word, lemma, form |
| freq     | The frequency count of this word in some corpus |
| hyphen   | The hyphenated word. |
| ipa      | Pronuncation using IPA with . for syllable breaks |
| pos      | Part of speech
| features | key=value, where key is a field id |
| morph    | morphology class |
| gnumber  | grammatical number |
| gperson  | grammatical person |
| notes    | Free form notes to the end of the line |

The hyphens may be from this set \u002D\u278A\u278B. I think \u278B is secondary
level of hyphenation.

