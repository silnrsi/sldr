# Exemplars

## Introduction

In principle, the creation of the main, auxiliary and punctuation exemplars is
straightforward. This document is a discussion of various examples and
considerations in creating various exemplars for an orthography.

### UTR 35 Instruction

Here is what UTR#35 has to say on the matter:

The basic exemplar character sets (main and auxiliary) contain the commonly used
letters for a given modern form of a language, which can be for testing and for
determining the appropriate repertoire of letters for charset conversion or
collation. ("Letter" is interpreted broadly, as anything having the property
Alphabetic in the [UAX44], which also includes syllabaries and ideographs.) It
is not a complete set of letters used for a language, nor should it be
considered to apply to multiple languages in a particular country. Punctuation
and other symbols should not be included in the main and auxiliary sets. In
particular, format characters like CGJ are not included.

There are five sets altogether: main, auxiliary, punctuation, numbers, and
index. The main set should contain the minimal set required for users of the
language, while the auxiliary exemplar set is designed to encompass additional
characters: those non-native or historical characters that would customarily
occur in common publications, dictionaries, and so on. Major style guidelines
are good references for the auxiliary set. So, for example, if Irish newspapers
and magazines would commonly have Danish names using å, for example, then it
would be appropriate to include å in the auxiliary exemplar characters; just not
in the main exemplar set. Thus English has the following:

```
<exemplarCharacters>[a b c d e f g h i j k l m n o p q r s t u v w x y z]</exemplarCharacters>  
<exemplarCharacters type="auxiliary">[á à ă â å ä ã ā æ ç é è ĕ ê ë ē í ì ĭ î ï ī ñ ó ò ŏ ô ö ø ō œ ú ù ŭ û ü ū ÿ]</exemplarCharacters>
```

For a given language, there are a few factors that help for determining whether
a character belongs in the auxiliary set, instead of the main set:

- The character is not available on all normal keyboards.
- It is acceptable to always use spellings that avoid that character.

For example, the exemplar character set for en (English) is the set [a-z]. This
set does not contain the accented letters that are sometimes seen in words like
"résumé" or "naïve", because it is acceptable in common practice to spell those
words without the accents. The exemplar character set for fr (French), on the
other hand, must contain those characters: [a-z é è ù ç à â ê î ô û æ œ ë ï ÿ].
The main set typically includes those letters commonly "alphabet".

The punctuation set consists of common punctuation characters that are used with
the language (corresponding to main and auxiliary). Symbols may also be included
where they are common in plain text, such as ©. It does not include characters
with narrow technical usage, such as dictionary punctuation/symbols or copy-edit
symbols. 

## Various Examples

### Kwaya

Kwaya [kya] is spoken and written in Tanzania. There is an
[orthography statement](https://www.sil.org/system/files/reapdata/11/80/96/118096820427572282340173471687806270977/Kwaya_Orthography_Statement_Final.pdf)
which describes the orthography and this discussion is based entirely on the
information in that document.

#### Description

The vowels are relatively straightforward, but the consonants and consonant
modifiers are somewhat more complex. Here is a space separated list of
consonants (Table 2.2-A):

```
bh ch d f g j k m n ng' ny p r s sh t w y
```

But this is not the complete list of consonant character sequences by any means.
There is:

- mb (p16) is a prenasalised bh
- n'y (p17) a palatalized n to contrast the ny consonant
- mm (p29) mi elided prefix before homomorphic nasal or pre nasal
- nn (p29) ni elided pregix before homomorphic nasal or pre nasal

Normally sequences of consonants do not occur, but consonants may also be
modified. Pre consonant modifiers are m or n, while post consonant modifiers are
w and y. A syllable may have both one pre consonant modifier and post consonant
modifier. There are constraints on precisely which sequences do occur.

Kwaya has a single lexical tone mark (\u0301) and three grammatical tone marks that
precede the word (: ^ ~)

Loan words are forced into Kwaya phonology and orthographic conventions and so
no characters are borrowed from other orthographies.

Explicitly identified punctuation marks are:

```
? . , : " ' - \u2018 \u2019 \u201C \u201D
```

#### Analysis for Exemplars

The question is what goes into the main exemplar and what into punctuation.
There are two characters that could go either way: ' and :.

There are two lexical uses of '

- ng' to identify the ng unit over the sequence of n and g (final and initial,
  or prenasalised g)
- n'y to identify the sequence n followed by y, a palatalized y, as opposed to a
  prenasalised y. This over against the consonant unit ny.

Due to the complexity of the orthgraphy in this regard, it is probably better to
give a full letter inventory rather than just a list of characters involved.
Thus a starting point for the main exemplar would be:

```
{bh} {ch} d f g j k m n {ng'} {ny} p r s {sh} t w y
```

To this is added:

- `b` which is a contextual variant of `bh` following a prenasal.
- `{n'}` which is a contextual variant of `n` preceding a `y` modifier.
- ̀ grave accent, a lexical tone mark

Thus we have:

```
b {bh} {ch} d f g j k m n {n'} {ng'} {ny} p r s {sh} t w y \u0301
```

The punctuation exemplar is relatively straightforward. The biggest question is
what to do with grammatical tone marks. Such marks are, by definition,
grammatical and therefore above a single word. This corresponds exactly with
what punctuation is: super word modifiers. In English they create pauses for
reading or intonation marks. Grammatical tone, therefore, seems to fit very well
into the category of punctuation.

```
^ ~ ? . , : " ' - \u2018 \u2019 \u201C \u201D
```

While ' occurs in both exemplars, it is not unconstrained in both lists.

### Emberá-Tadó

Emberá-Tadó [tdc] is spoken in Columbia. The only data available is picture
dictionary of very few words where an animal is listed in the sequence: "_animal_
nãɨya piruparima ...", which I guess translates to "_animal_ makes the sound ..." The list of
animals and their sounds is:

```
Bisi   bisi
Miista sẽeke sẽke
K'ṹara sio tere
Jep'a  sẽee
Chok'orro choorr
Bii    mee
T'usi  jei
Pẽrora jõe
Pok'orro jo do
Wɨrɨk'ɨk'ɨ  wɨrɨ k'ɨ
```

Not a lot to go on!

A first cut list for the main exemplar would be:

```
a {ã} b {ch} d e {ẽ} i ɨ j k m n o {õ} p r s t u {ṹ} w y '
```

We then start speculating wildly. Here are two speculations:

- ' is an ejective marker since it only occurs following a plosive.
- ~ is a vowel diacritic, perhaps nasalisation.

The choice now is do we constrain the ' or unconstrain the ~? We have no idea
whether ' is actually an apostrophe or a saltillo. Given we know so little, I
would be inclined to be more precise than less and constrain the ':

```
a {ã} b {ch} d e {ẽ} i ɨ j k {k'} m n o {õ} p {p'} r s t {t'} u {ṹ} w y
```

We know nothing more than this. Clearly more text would help.

#### More data!

A collation is available:

```
&a <<< A << á <<< Á << ã <<< Ã
&b <<< B << b̶
&c <<< C < ch
&d <<< D << d̶
&e <<< E << é <<< É << ẽ <<< Ẽ
&f <<< F
&g <<< G
&h <<< H
&i <<< I << í <<< Í << ĩ <<< Ĩ < ɨ <<< Ɨ << ɨ́ <<< Ɨ́ << ɨ̃ <<< Ɨ̃
&j <<< J
&k <<< K < k\'
&l <<< L
&m <<< M
&n <<< N < ñ <<< Ñ
&o <<< O << ó <<< Ó << õ <<< Õ
&p <<< P < p\'
&q <<< Q << qu
&r <<< R
&s <<< S
&t <<< T < t\'
&u <<< U << ú <<< Ú << ũ <<< Ũ
&v <<< V
&w <<< W
&x <<< X
&y <<< Y
&z <<< Z < \'
```

Given that a number of characters are added to the basic English alphabet, it is
probable that someone with knowledge of the orthography took the effort to enter
this sort order. There are obvious missing capitals for some of the additions.
But from this we can improve our exemplar.

The ' modified consonants are listed,
although adding ' at the end of the order implies it can occur in other places.
The question is: what other places? It is hard to analyse the use of apostrophe
in a text and so ' may just be left over from a default inclusion of it in a
list. I would suggest we remove it until further evidence justifies its
reinclusion.

In addition to the collation information we are given a list of every grapheme
cluster encountered in some text (which we don't have):

```
A-Z a-z Á Ã É Ë Í Ñ Ó Õ Ú Ü á ã é ë í ñ ó õ ú ü Ĩ ĩ Ũ ũ Ɨ ɨ Ṍ ṍ Ṹ ṹ Ẽ ẽ
{Ch} {K'} {P'} {Qu} {T'} {b̶} {ch} {d̶} {k'} {p'} {qu} {t'} {Ã́} {Ë́} {ã́} {ë́}
{Ĩ́} {ĩ́} {Ɨ́} {Ɨ̃} {Ɨ̃́} {ɨ́} {ɨ̃} {ɨ̃́} {Ẽ́} {ẽ́}
```

which fits with the collation. This can be simplified by removing upper case
characters for which there is a lower case equivalent.

```
a-z á ã é ë í ñ ó õ ú ü ĩ ũ ɨ ṍ ṹ ẽ {b̶} {ch} {d̶} {k'} {p'} {qu} {t'} {ã́} {ë́}
{ĩ́} {ɨ́} {ɨ̃} {ɨ̃́} {ẽ́}
```

The question is whether the sequences involving the acute and tilde diacritics
need to be listed or we can just list the diacritics. Given these characters
occur on all vowels and in sequence, it is probable that they have functions as
the particular characters and so it is better to include them on their own
rather than as ways of producing more vowels:

```
a-z ñ ɨ {b̶} {ch} {d̶} {k'} {p'} {qu} {t'} \u0301 \u0303
```

Notice we keep ñ since it is a primary collation element and you can't nasalise
a nasal (based on guessing that ~ is a nasalisation marker).

Given we know nothing about the use of ' in punctuation, it is probably wise to
not include it. But further analysis may allow us to remove the ' as an
unconstrained character from the main exemplar and add it to the punctuation
list.

