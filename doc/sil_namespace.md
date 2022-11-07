# LDML SIL Namespace

## Introduction

This document has a short URL: [*https://goo.gl/pUKcS6*](https://goo.gl/pUKcS6)

[LDML](http://unicode.org/reports/tr35/) is the core grammar used for representing data stored in the CLDR. LDML is an extensible grammar and this allows us to add information that we need into data files for use in CLDR.

This document describes the grammar extensions that the sil namespace adds using the [RelaxNG](http://relaxng.org/compact-tutorial-20030326.html) compressed grammar language.

```rnc
namespace sil = "urn://www.sil.org/ldml/0.1"
namespace cldr = "urn://www.unicode.org/cldr/types/0.1"
```

The namespace URL.

The versioning of the namespace is based on what changes will force a version increase:

-   Removal or change of meaning of any element or attribute.
-   Addition of a required element or attribute to an existing element.

Any other additions do not require a version increase since it is presumed that all elements allow the addition of arbitrary attributes and elements within the namespace.

The grammar starts by including the standard LDML grammar and modifying it to hook the four special tags that elements in the namespace occur under.

```rnc
include "ldml.rnc" {
special = 
    element special {
        (sil.resources | sil.identity | sil.reordered | sil.simple | sil.names
         | (sil.matchedpairs?, sil.punctuation.patterns?, sil.quotation-marks?) | sil.exemplarCharacters
         | sil:note)
    }
}

attlist.sil.global &= attribute draft { "approved" | "contributed" | "provisional" |
                                        "unconfirmed" | "proposed" | "tentative" |
                                        "generated" | "suspect" }?
attlist.sil.global &= attribute alt { text }?
attlist.sil.global &= attribute references { text }*
```

```dtd
<!ENTITY % ldml-dtd
    SYSTEM "ldml.dtd">
%ldml-dtd;

<!ATTLIST ldml xmlns:sil CDATA #FIXED "urn://www.sil.org/ldml/0.1">
<!ELEMENT special (sil:external-resources | sil:identity | sil:reordered | sil:simple | sil:names
                   | (sil:matched-pairs?, sil:punctuation-patterns?, sil:quotation-marks?) | sil:exemplarCharacters+
                   | sil:note)>
<!ATTLIST special xmlns:sil CDATA #FIXED "urn://www.sil.org/ldml/0.1">

<?ATTDEF global draft (approved | contributed | provisional | unconfirmed | proposed | tentative | generated | suspect) "approved"?>
<!--@METADATA-->
<!--@DEPRECATED: proposed-->
<?ATTDEF global alt           NMTOKEN     #IMPLIED?>
<?ATTDEF global references    CDATA       #IMPLIED?>
<!--@METADATA-->
```

## Collation

LDML currently has only one descriptive language for collations. But collations may be described in various languages and then converted into the ICU based language. The LDML document wants to hold both the original source representation of the sort order, for user editing, and the ICU representation.

### Simple Collations

```rnc
# collation.special = element special {
#     (sil.reordered | sil.simple)?
# }

attlist.collation &= attribute sil:modified { "true" | "false" }?
attlist.sil.collation &= attribute sil:secondary { text }?
attlist.sil.collation &= attribute sil:prefrom { text }?
attlist.sil.collation &= attribute sil:preto { text }?
attlist.sil.collation &= attribute sil:needscompiling { xsd:boolean }?
```

```dtd
<!ATTLIST collation sil:modified          (true | false) "false">
<!--@METADATA-->
<?ATTDEF collation sil:secondary         CDATA #IMPLIED?>
<?ATTDEF collation sil:prefrom           CDATA #IMPLIED?>
<?ATTDEF collation sil:preto             CDATA #IMPLIED?>
<?ATTDEF collation sil:needscompiling    (true | 1 | false | 0) "false"?>
<!--@METADATA-->
```

For collations that are described in languages other than ICU tailoring rules, the LDML needs to store both the source collation description in its language and also an ICU tailoring form. Thus a collation would contain its ICU tailoring form and then a special containing the source form. There is no intention that there be more than one source form for a collation, although it is technically possible. 
The `modified` attribute is used in a flat LDML file to indicate that this collation differs from that in the root. It is not needed in normal LDML files.
For example (from the Akoose language):

```xml
<collation type="standard">
    <cr><!\[CDATA\[
        &B<ch<Ch &E<ǝ<<<Ə &N<ŋ<<<Ŋ &O<ɔ<<<Ɔ &Z<\u02BC<\u0027
        &[first primary ignorable] << \u030C << \u0301 << \u0302 << \u0304
    ]]></cr>
    <special xmlns:sil="urn://www.sil.org/ldml/0.1">
        <sil:simple sil:needscompiling="false" sil:secondary="&#x030C; &#x0301; &#x0302; &#x0304">
            <!\[CDATA\[
                a/A
                b/B
                Ch Ch
                d/D
                e/E
                ǝ/Ə
                f/F
                g/G
                h/H
                i/I
                j/J
                k/K
                l/L
                m/M
                n/N
                ŋ/Ŋ
                o/O
                ɔ/Ɔ
                p/P
                r/R
                s/S
                t/T
                u/U
                v/V
                w/W
                y/Y
                z/Z
                ʼ
                '
            ]]>
        </sil:simple>
    </special>
</collation>
```

The structure of the text in `sil:simple` is all the elements on the same line are sorted with the same primary key. Space separated elements are secondarily distinguished and ordered. Tertiary differences are separated by /.

Various attributes have been added to the main collation, since it is shared by all the forms of the collation.

|                    |                                                             |
|--------------------|-------------------------------------------------------------|
| **needscompiling** | Specifies that the ICU rules do not adequately represent the alternate representation of the collation and need to be recompiled. If absent, assumed to be false. (The example above has it to show using a sil attribute in a special element.) |
| **prefrom**        | This specifies a pre processing LDML transform that must be done on the string before it is then applied through the collation. This attribute specifies the source type of the transform. Notice that using such transforms will significantly slow down sorting and make the collation far less portable. |
| **preto**          | This specifies the transform target type. If prefrom is specified and preto is not, then the default value ‘sort’ is used. preto may not occur without prefrom. |
| **secondary**      | This specifies another sort that can be applied to provide secondary level of sorting of strings that are identically sorted at the first level. The strings must have identical sort keys to be considered for secondary sorting. The value is another collation identifier in this LDML file. |

### Reordered Collations

```rnc
sil.reordered = element sil:reordered {
    (attlist.sil.global & attlist.sil.collation), 
    (sil.reorder*, cr)
}

sil.reorder = element sil:reorder {
    attlist.sil.reorder
}
attlist.sil.reorder &= attribute match { text }
attlist.sil.reorder &= attribute reorder { text }

sil.simple = element sil:simple {
    (attlist.sil.simple & attlist.sil.global & attlist.sil.collation),
    text
}

attlist.sil.simple &= attribute secondaryonly { text }?
[cldr:value="true"]
attlist.sil.simple &= attribute xml:space { "preserve" }?
```

```dtd
<!ELEMENT sil:reordered (sil:reorder*, cr)>
<!ATTLIST sil:reordered match     CDATA #REQUIRED>
<!ATTLIST sil:reordered reorder   CDATA #REQUIRED>
<?ATTREF sil:reordered collation?>
<?ATTREF sil:reordered global?>

<!ELEMENT sil:simple (#PCDATA)>
<!ATTLIST sil:simple secondaryonly CDATA #IMPLIED>
<!ATTLIST sil:simple xml:space (preserve) #FIXED "preserve">
<?ATTREF sil:simple collation?>
<?ATTREF sil:simple global?>
```

Preprocessed collation adds a single element type to the default LDML collation language. The `sil:reorder` element describes a preprocessing step that matches on a regular expression, and using components of that regular expression, generates an output string that will be used for the actual collation. Multiple reorder elements may exist. The only requirement is that the input regular expressions be non-overlapping; that is, two reorder match expressions may not match the same string.

|             |                                               |
|-------------|-----------------------------------------------|
| **match**   | The regular expression language used in match uses the restricted regular expression language described later. |
| **reorder** | The reorder attribute is a corresponding transformation string to match. |

For simple sort specifications, the text of the `sil:simple` element is a list of space-separated elements in lines. All elements on a line have the same primary key with each element on the line being secondarily sorted in the given order. If an element consists of two strings separated by slashes then the subelements so formed are tertiary sorted in the given order (as per casing). Interpreters must expect the content of `sil:simple` to be multiline. The `secondaryonly` attribute is a list of space-separated elements that have no primary order and are secondarily sorted in the given order.

## External Resources

LDML files in the SLDR are version controlled. To aid in their management we include version information so that uploaded changes can be appropriately merged into the SLDR. An LDML file may also reference external resources that an application may need.

```rnc
# ldml.special = element special {
#    (sil.resources?)
#}

sil.resources = element sil:external-resources {
    (sil.font*,
     sil.kbdrsrc*,
     sil.spellcheck*,
     sil.transform*,
     sil.sampletext*,
     sil.wordlist*)
}
sil.url = element sil:url {
    attlist.sil.global,
    (xsd:anyURI)
}
```

```dtd
<!ELEMENT sil:external-resources (sil:case-tailoring | sil:font | sil:kbd | sil:spell-checking | sil:transform | sil:sampletext | sil:wordlist)*>
<!ELEMENT sil:url (#PCDATA)>
<?ATTREF sil:url global?>
```

External resources are writing system level information that describe system resources that are useful for processing data in this writing system. The particular resource is referenced via a URL. What the URL actually references is context and type specific and is described where this element is used.

For example:

```xml
<special xmlns:sil="urn://www.sil.org/ldml/0.1">
    <sil:external-resources>
        <sil:font name="Scheherazade" engines="gr ot" types="default">
            <sil:url>https://wirl.api.sil.org/Scheherazade</sil:url>
        </sil:font>
        <sil:kbd id="TunisianSpokenArabic" type="kmp">
            <sil:url>https://wirl.api.sil.org/TunisianSpokenArabic</sil:url>
        </sil:kbd>
        <sil:spell-checking type="hunspell">
            <sil:url>https://wirl.api.sil.org/aeb-DictList</sil:url>
        </sil:spell-checking>
    </sil:external-resources>
</special>
```

### Fonts

```rnc
sil.font = element sil:font {
    (attlist.sil.fontelement & attlist.sil.global),
    (sil.url*)
}
attlist.sil.fontelement &= attribute name { text }
[cldr:value="true"]
attlist.sil.fontelement &= attribute types { text }
# attlist.sil.fontelement &= attribute types
#     { "default" | "heading" | "emphasis" | "ui" | text }*
[cldr:value="true"]
attlist.sil.fontelement &= attribute size { xsd:decimal }?
[cldr:value="true"]
attlist.sil.fontelement &= attribute minversion { xsd:decimal }?
[cldr:value="true"]
attlist.sil.fontelement &= attribute features { text }?
[cldr:value="true"]
attlist.sil.fontelement &= attribute lang { text }?
[cldr:value="true"]
attlist.sil.fontelement &= attribute otlang { text }?
[cldr:value="true"]
attlist.sil.fontelement &= attribute engines { list { ("gr" | "ot")+ } }?
[cldr:value="true"]
attlist.sil.fontelement &= attribute subset { text }?
```

```dtd
<!ELEMENT sil:font (sil:url*)>
<!ATTLIST sil:font name CDATA #REQUIRED>
<!ATTLIST sil:font types NMTOKENS #IMPLIED>
<!--@VALUE-->
<!ATTLIST sil:font size CDATA #IMPLIED>
<!--@VALUE-->
<!ATTLIST sil:font minversion CDATA #IMPLIED>
<!--@VALUE-->
<!ATTLIST sil:font features CDATA #IMPLIED>
<!--@VALUE-->
<!ATTLIST sil:font lang NMTOKEN #IMPLIED>
<!--@VALUE-->
<!ATTLIST sil:font otlang NMTOKEN #IMPLIED>
<!--@VALUE-->
<!ATTLIST sil:font engines NMTOKENS #IMPLIED>
<!--@VALUE-->
<!ATTLIST sil:font subset CDATA #IMPLIED>
<!--@VALUE-->
<?ATTREF sil:font global?>
```

Font resources are associated with their application role. There may be more than one font that may be used in a particular role within an application, and a font may be used for more than one role. The **types** attribute may take any value, but for consistency across applications, some type are listed here:

|              |                                          |
|--------------|------------------------------------------|
| **default**  | Use this font when unsure which to use or for body text or the particular type required is missing \[default\]. |
| **heading**  | This font is for use with headings |
| **emphasis** | This font is for use when text is to be emphasised |
| **ui**       | This font is used for User Interface elements like menus |

Fallback between fonts is a little complicated. If a description includes a font for a particular type, e.g. heading, then all heading fonts from the parent are ignored. Thus a local font disables all inheritance of fonts of the same type. In addition, for the particular case of the default type, if a description includes a font for type default, all fonts from the parent for all types, are ignores. Thus a local default font disables inheritance of all fonts.

The urls reference font resources either as .ttf or .woff files and are stored in preferential order.

|                |                                        |
|----------------|----------------------------------------|
| **name**       | Internal public font name that an application may use to reference the font to the operating system. |
| **size**       | Relative size from Times New Roman, e.g. 1.6 for an older Thai font. If unspecified, the value is 1.0. |
| **minversion** | The minimum font version appropriate for use. |
| **features**   | This is a space separated list of key=value pairs using the = character to separate key and value. Keys, if not numeric, are assumed to right space pad to 4 chars. Values are numeric. For binary features, 1 enables the feature and 0 disables it. |
| **lang**       | It is assumed that the ISO639 language for the locale (/ldml/identity/language/@type) will be passed to a font for language specific rendering tailoring. If a different language is required for this font, then this should be specified here. It is an ISO639 language code. |
| **otlang**     | If the OpenType language differs from the standard mapping from ISO639 to the OpenType language, then the precise tag may be specified here. This is typically used for 4 letter tags. |
| **engines**    | This is a space separated list of engines to use to process text using this font, in priority order. The possible values in the list are: |
|                | **gr** - Graphite |
|                | **ot** - OpenType |
|                |  If this attribute is missing it is assumed to be "gr ot", but if the font does not support Graphite, then the "gr" is, in effect, ignored. The primary purpose of this attribute is to give some indication to applications as to the level of text rendering support they need to supply for this font. This is particularly for Graphite only fonts. \[Default: ot\]  |
| **subset**     | Specifies a subset name that can be used with this font in web contexts to use a font subset and reduce download time. I.e. if this attribute exists, an application may ignore it. |

For example:

```xml
<special xmlns:sil="urn://www.sil.org/ldml/0.1">
    <sil:external-resources>
        <sil:font name="Padauk" types="default">
            <sil:url>http://wirl.scripts.sil.org/padauk</sil:url>
        </sil:font>
    </sil:external-resources>
</special>
```

### Keyboards

```rnc
sil.kbdrsrc = element sil:kbd {
    (attrlist.sil.kbdrsrc & attlist.sil.global),
    (sil.url+)
}
attrlist.sil.kbdrsrc &= attribute id { text }
attrlist.sil.kbdrsrc &= attribute type { text }?
# attrlist.sil.kbdrsrc &= attribute type { "kmn" | "kmx" | "msklc" | "ldml" | "keylayout" | "kmp" | text }?
```
```dtd
<!ELEMENT sil:kbd (sil:url)+>
<?ATTREF sil:kbd global?>
<!ATTLIST sil:kbd id NMTOKEN #REQUIRED>
<!ATTLIST sil:kbd type NMTOKEN #IMPLIED>
```

|          |                                              |
|----------|----------------------------------------------|
| **id**   | Keyboard name                                |
| **type** | Specifies which language the keyboard is in: |
|          | **kmn** - The url references a .kmn source file. |
|          | **kmx** - The url references a .kmx compiled keyman file for use with Tavultesoft Keyman. |
|          | **kmp** - The url references a cross platform Keyman distribution package. |
|          | **msklc** - The url references a .klc source file. |
|          | **ldml** - The url references a keyboard layout LDML .xml file. |
|          | **keylayout** - Mac keyboard layout files. |
|          | There are other formats that may be needed, so this list is considered open, although we will try to keep it up to date. |

Keyboard elements are sorted alphabetically first by type and then by id. This follows the LDML attribute order given in supplementalData/metadata/attributeOrder.

### Spell Checking

```rnc
sil.spellcheck = element sil:spell-checking {
    (attlist.sil.spellcheck & attlist.sil.global),
    (sil.url+)
}

attlist.sil.spellcheck &= attribute type { text }
# attlist.sil.spellcheck &= attribute type { "hunspell", "wordlist", text }
```
```dtd
<!ELEMENT sil:spell-checking (sil:url)+>
<!ATTLIST sil:spell-checking type NMTOKEN #REQUIRED>
<?ATTREF sil:spell-checking global?>
```

Spell checking is more than a reference to a dictionary given that some spell checking engines handle morphology as well.

|          |                                                                          |
|----------|--------------------------------------------------------------------------|
| **type** | This specifies the type of information the URL(s) reference. Values are: |
|          | **hunspell** - The URL references the stem of the .aff and .dic files.   |
|          | **wordlist** - The URL references a text file with tab/space/comma delimited fields, one per line. The first field is the word. If present, the second field is a frequency count of word occurrences. Other fields are ignored and undefined. |

The type attribute is a distinguishing attribute between different spell-checking elements. Spellcheck elements are sorted alphabetically by their url content.

Example:

```xml
<special xmlns:sil="urn://www.sil.org/ldml/0.1">
    <sil:external-resources>
        <sil:spell-checking type="hunspell">
            <sil:url>https://wirl.api.sil.org/af_ZA-DictList</sil:url>
        </sil:spell-checking>
    </sil:external-resources>
</special>
```

### Transformations

```rnc
sil.transform = element sil:transform {
    (attlist.sil.transform & attlist.sil.global), 
    (sil.transform.caps?, sil.transform.dict?, sil.url+)
}

attlist.sil.transform &= attribute from { text }
attlist.sil.transform &= attribute to { text }
attlist.sil.transform &= attribute type { "cct" | "perl" | "python" | "teckit" | "cldr" }
[cldr:value="true"]
attlist.sil.transform &= attribute direction { "both" | "forward" | "backward" }
[cldr:value="true"]
attlist.sil.transform &= attribute function { text }?

sil.transform.dict = element sil:transform-dict {
    (attlist.sil.transform.dict & attlist.sil.global),
    (sil.url+)
}

attlist.sil.transform.dict &= attribute incol { text }
# attlist.sil.transform.dict &= attribute incol { "0" | text }
attlist.sil.transform.dict &= attribute outcol { text }
# attlist.sil.transform.dict &= attribute outcol { "1" | text }
[cldr:value="true"]
attlist.sil.transform.dict &= attribute nf { "nfd" | "nfc" }?

sil.transform.caps = element sil:transform-capitals {
    (attlist.sil.transform.caps & attlist.sil.global)
}

attlist.sil.transform.caps &= attribute opengroup { text }?
# attlist.sil.transform.caps &= attribute opengroup { '&quot;"\u{2018}\u{201C}\[{(<\u00AB' | text }?
attlist.sil.transform.caps &= attribute closegroup { text }?
# attlist.sil.transform.caps &= attribute closegroup { '&quot;"\u{2019}\u{201D}\]})>\u00BB' | text }?
attlist.sil.transform.caps &= attribute sentencefinal { text }?
# attlist.sil.transform.caps &= attribute sentencefinal { ".!?" | text }?
attlist.sil.transform.caps &= attribute startcaps { text }?
```
```dtd
<!ELEMENT sil:transform (sil:transform-capitals?, sil:transform-dict?, sil:url+)>
<!ATTLIST sil:transform from NMTOKEN #REQUIRED>
<!ATTLIST sil:transform to NMTOKEN #REQUIRED>
<!ATTLIST sil:transform type (cct | perl | python | teckit) #REQUIRED>
<!ATTLIST sil:transform direction (both | forward | backward) #REQUIRED>
<!--@VALUE-->
<!ATTLIST sil:transform function NMTOKEN #IMPLIED>
<!--@VALUE-->
<?ATTREF sil:transform global?>

<!ELEMENT sil:transform-dict (sil:url)+>
<!ATTLIST sil:transform-dict incol CDATA #REQUIRED>
<!ATTLIST sil:transform-dict outcol CDATA #REQUIRED>
<!ATTLIST sil:transform-dict nf (nfd | nfc) "nfc">
<!--@VALUE-->
<?ATTREF sil:transform-dict global?>

<!ELEMENT sil:transform-capitals EMPTY>
<!ATTLIST sil:transform-capitals opengroup CDATA #IMPLIED>
<!ATTLIST sil:transform-capitals closegroup CDATA #IMPLIED>
<!ATTLIST sil:transform-capitals sentencefinal CDATA #IMPLIED>
<!ATTLIST sil:transform-capitals startcaps CDATA #IMPLIED>
<?ATTREF sil:transform-capitals global?>
```

Issue: In LDML, transform is now part of supplemental data. Do we need to have a special supplemental data for the SIL namespace? Given this is really a reference to an external resource (which is the supplemental data in effect), we can keep it here. But it is a kind of global information.

The first few attributes for a **transform** element are copied from the LDML `transform` element, and have the same interpretation. The **type** attribute gives the processing type for the resource. The **from**, **to** and **type** attributes are all distinguishing attributes. This allows for there to be different implementations of the same transform. The **function** attribute is only needed for those transducer types that call a function in some code to do the mapping. For a **type** of `teckit`, there must be a url reference to a `.tec` file, in addition to any other references to `.map` or `.xml` files.

Transform elements are sorted alphabetically by attributes in the following priority order: type, from, to, direction, function; following the LDML standard ordering given in the supplementalData/metadata/attributeOrder element.

In addition to simple transformations, there are also more complex ones used for transforming between scripts. In such cases there are two extra considerations. The first is that not all transformations are purely algorithmic. There can be algorithmically arbitrary spelling differences. Such differences are handled using a simple mapping dictionary. A transform may reference such a dictionary. The two column attributes (incol, outcol) specify which columns in the simple CSV file, are used for input and output text. They default to 0 and 1 respectively. The nf attributes specifies in which normal form the input data is held.

The second consideration is conversion from a script with no case to one with case. For this automatic case insertion is desired. Not all case insertion can be done algorithmically, for example if proper names are to be capitalised, then such words will need to be added to the dictionary to fix the casing. The various attributes in the `sil:transform-capitals` element drive the algorithmic insertion of capitals. The default value for each attribute is given as the first string in the alternate. The **opengroup** and **closegroup** attributes are used to specify preceding and final punctuation that is to be ignored when either setting the capital on a first character after a sentence break (or at the start of a 'paragraph') or following a sentence final marker. In many languages when starting a subgroup (e.g. some quoted text, or a parenthetic group) the first letter in the group is automatically upper cased. The **startcaps** attribute specifies which initial characters will cause the first letter to be capitalised. If not specified, it is assumed to take the same value as the **opengroup** attribute.

### Case Tailoring

There are a few locales that do not convert between upper and lower case in the same way that most other locales do. The key difference in the known cases is that the orthography has a dotted upper case I and dotless lower case i. Thus upper case dotless I does not map to lower case dotted i. There are no known cases of other case tailorings, but we will define a mechanism just in case.

```rnc
sil.casetailor = element sil:case-tailoring {
    (attlist.sil.casetailor & attlist.sil.global)
}

attlist.sil.casetailor &= attribute alias { text }?
attlist.sil.casetailor &= attribute transform { text }?
```
```dtd
<!ELEMENT sil:case-tailoring EMPTY>
<!ATTLIST sil:case-tailoring alias CDATA #IMPLIED>
<!ATTLIST sil:case-tailoring transform CDATA #IMPLIED>
<?ATTREF sil:case-tailoring global?>
```

A case tailoring may either specify another locale as an alias to use when case tailoring text marked with this locale. The **alias** attribute is used to specify the replacement locale. Alternatively, it may reference an `sil:transform`, using the **transform** attribute. This value is used to index the @from attribute of an `sil:transform` element and the @to attribute is matched against the @from with one of `-Lower`, `-Upper` or `-Title` strings appended. If both attributes are present, a processor may use either. Currently, use of @alias is recommended over @transform. For example:

```xml
<special xmlns:sil="urn://www.sil.org/ldml/0.1">
    <sil:external-resources>
        <sil:case-tailoring alias="tr"/>
    </sil:external-resources>
</special>

<special xmlns:sil="urn://www.sil.org/ldml/0.1">
    <sil:external-resources>
        <sil:case-tailoring transform="qbx"/>
        <sil:transform from="qbx" to="qbx-Title"/>
    </sil:external-resources>
</special>
```

The former is preferred over the latter which would look for `<sil:transform from="qbx" to="qbx-Lower">` or `<sil:transform from="qbx" to="qbx-Upper">`, etc.

### Sample Text

A short sample text in the language and orthography is useful for all kinds of purposes. This element allows text to be stored either in the LDML file itself or via an external reference.

```rnc
sil.sampletext = element sil:sampletext {
    (attlist.sil.sampletext & attlist.sil.global),
    (sil.text | sil.url)
}
attlist.sil.sampletext &= attribute type { text }?
attlist.sil.sampletext &= attriute license { text }?
sil.text = element sil:text { text }
```
```dtd
<!ELEMENT sil:sampletext (sil:text | sil:url)>
<!ATTLIST sil:sampletext type CDATA #IMPLIED>
<!ATTLIST sil:sampletext license CDATA #IMPLIED>
<!--@VALUE-->
<?ATTREF sil:sampletext global?>
<!ELEMENT sil:text (#PCDATA)>
``` 

A sample text is stored in plain text with the only formatting being a blank line between paragraphs. An external reference is to such a plain text file, stored in UTF-8 with no Byte Order Mark. The license attribute gives the licensing of the text. The copyright is assumed to be owned by the owner of the linked text or the owner of the LDML file for internal texts. If the license attribute is missing for internal texts, then the license is the same as for the LDML file. For external files, it is unknonwn as per the copyright.

### Wordlists

Wordlists are lists of words. The simplest form is a text file with one word per line. But usually wordlists are tab separated with other information in later columns. The specification here allows the columns to be specified.

```rnc
sil.wordlist = element sil:wordlist {
    (attlist.sil.wordlist & attlist.sil.global),
    sil.url
}
attlist.sil.wordlist &= attribute type { text }?
attlist.sil.wordlist &= columns { xsd:NMTOKENS }?
attlist.sil.wordlist &= headerlines { text }?
```
```dtd
<!ELEMENT sil:wordlist (sil:url)>
<!ATTLIST sil:wordlist type CDATA #IMPLIED>
<!ATTLIST sil:wordlist columns NMTOKENS #IMPLIED>
<!--@VALUE-->
<!ATTLIST sil:wordlist headerlines CDATA #IMPLIED>
<!--@VALUE-->
<?ATTREF sil:wordlist global?>
```

The child URL gives the url to the wordlist resource. @type may take the following values:

|          |                                              |
|----------|----------------------------------------------|
| csv      | Comma separated columns, with " and "" escaping |
| tsv\*    | Tab separated columns. This is the default value |

A tsv or csv file may have initial header lines. The number is listed in the @headerlines attribute, with a default of 0. Following that may be any number of comment lines starting with a # or blank lines. The data lines may have multiple columns and the fields used may be listed in the @columns attribute:

| Field Id | Description                                            |
+----------+--------------------------------------------------------+
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

If there is no @columns attribute or it contains too few entries then a default @columns attribute consists of `word freq notes`.

## Identification

One part of the housekeeping of the SLDR is the ability for applications to submit revised LDML specifications back to the SLDR. To enable this without the SLDR having to keep a record of every LDML file downloaded by every application, the SLDR inserts an identifying attribute into the LDML it sends out, so that if an application submits LDML data it knows against which version of the LDML data that submission is made. Applications must keep this information and must not change it.

```rnc
# identity.special = element special {
#     attlist.identity,
#     (sil.identity)
# }

sil.identity = element sil:identity {
    (attlist.sil.identity & attlist.sil.global),
    (sil.identity.committer?)
}

attlist.sil.identity &= attribute revid { text }?
attlist.sil.identity &= attribute uid { text }?
attlist.sil.identity &= attribute fallbacks { text }*
attlist.sil.identity &= attribute source { text }?
# attlist.sil.identity &= attribute source { "cldr" | "cldrseed" | text }?
attlist.sil.identity &= attribute windowsLCID { text }?
attlist.sil.identity &= attribute defaultRegion { text }?
attlist.sil.identity &= attribute variantName { text }?
attlist.sil.identity &= attribute usage { "unused" | "developing" }?
attlist.sil.identity &= attribute toplevels { text }*
attlist.sil.identity &= attribute script { text }?

sil.identity.committer = element sil:committer {
    (attlist.sil.committer & attlist.sil.global),
    (text)
}

attlist.sil.committer &= attribute machid { text }?
```
```dtd
<!ELEMENT sil:identity (sil:committer)?>
<!ATTLIST sil:identity revid CDATA #IMPLIED>
<!ATTLIST sil:identity uid CDATA #IMPLIED>
<!ATTLIST sil:identity fallbacks NMTOKENS #IMPLIED>
<!ATTLIST sil:identity source CDATA #IMPLIED>
<!ATTLIST sil:identity windowsLCID CDATA #IMPLIED>
<!ATTLIST sil:identity defaultRegion NMTOKEN #IMPLIED>
<!ATTLIST sil:identity variantName CDATA #IMPLIED>
<!ATTLIST sil:identity usage (unused | developing) #IMPLIED>
<!ATTLIST sil:identity toplevels NMTOKENS #IMPLIED>
<!ATTLIST sil:identity script NMTOKEN #IMPLIED>
<?ATTREF sil:identity global?>

<!ELEMENT sil:committer (#PCDATA)>
<!ATTLIST sil:committer machid CDATA #IMPLIED>
<?ATTREF sil:committer global?>
```

As of namespace version 0.2 the attributes @defaultRegion, @variantName and @script will be removed since such information, may be found in alltags.txt. *Discuss before then!*

If present **windowsLCID** specifies a decimal windows locale ID to use for this locale. The **defaultRegion** specifies a default region for this locale. This is different to the `identity/territory` which is part of the locale specification. It is informative only, giving region information when not by the language tag. This attribute is used for locales with no territory specified. Likewise for the **script** attribute. There is value in storing a variant name for private use variants, and this information is stored in **variantName**. The **usage** attribute gives an indication of the usage of the writing system among its user community. Absence of this attribute implies the writing system is established and in general use.

|                |                                               |
|----------------|-----------------------------------------------|
| **unused**     | The writing system is no longer in use by the user community for whatever reason (it was developing but never caught on and has been abandoned, or there was a revision and this writing system has been abandoned) |
| **developing** | The writing system is under development and is not considered established by the user community. |

The **committer** element contains a string giving contact information for the person committing this version of the file. This element should only be used when submitting data to the repository. It should not be found in files within the repository itself. The information is only for use by the SLDR administration for offline contact with the submitter regarding improvements to the file. The **machid** attribute is a machine generated id which provides another way of identification. It is a required attribute if the information is being submitted automatically, through the web API.

The **toplevels** is a space separated list of top level elements that are included in this file. The existence of this attribute indicates that this file is an ldml fragment and that only the listed top level elements should be processed when merging this data with the full ldml description. Notice that all fragments must have the identity top level element.

|            |                                                   |
|------------|---------------------------------------------------|
| **revid**  | This contains the SHA of the git revision that was current when the user pulled the LDML file. This attribute is stripped from files before inclusion in the SLDR. |
| **uid**    | This holds a unique id that identifies a particular editor of a file. Notice that no two uids will be the same even across LDML files. Thus the uid is a unique identifier for an LDML file as edited by a user. If a user downloads a file and they don't already have a uid for that file then they should use the given uid. On subsequent downloads they must update the uid to the existing uid for that file. 
|            |  In implementation terms the UID is calculated as the 32-bit timestamp of the file request from the server, with another 16-bit collision counter appended and represented in MIME64 as 8 characters. This attribute is stripped from files before inclusion in the SLDR.|
| **draft**  | This specifies the default draft level for the whole file. The SLDR uses these draft values, in addition to those used by the CLDR (approved, contributed, provisional, unconfirmed): |
|            | **unconfirmed** - This is the basic level of new information that is considered to be provided by the community |
|            | **proposed** - The data is considered checked by either the user community or a consultant but not both. |
|            | **tentative** - This is for data a user is unsure about. |
|            | **generated** - This is for auto-generated information. |
|            | **suspect** - For retaining data that is considered wrong. |
|            |  The default value, if draft is unspecified is proposed. This attribute differs from a top level @draft attribute in that it can take additional values. It also means that applications do not have to set @draft attributes on the values they change, if the default is higher than their level (i.e. if the value is higher than proposed). This attribute is used by the sldr import to convert changes into draft entries at the appropriate level. The two most common use cases are that the attribute is missing (defaulting to 'unconfirmed') or it is set to 'approved' to indicate that the data has come from the CLDR. The assumption is that any changes made will be at the 'proposed' level. If an application wants to indicate something different, then it should set this attribute to either 'unconfirmed' or 'tentative'.  |
| **source** | This specifies where data comes from. The current values are: |
|            | **cldr** - This data comes from a CLDR release. The draft attribute is set to approved. |
|            | **cldrseed** - This data has been imported from CLDR seed. The draft attribute is set to unconfirmed. |

Given that an arbitrary edit is assumed to have a draft value of proposed, if an existing value exists with a draft value greater than the level set by the user (given we allow them to upvote and downvote their values), then their contribution will be included as an alternative with @alt="proposed-*\<uid\>*" with the uid of the file inserted in the alt attribute. If such an element already exists, it is overridden. If the draft value of their submission is sufficient that they can replace the existing value, and an alternative exists with their uid in, then that alternative is deleted. If there is no uid specified then the @alt value is "proposed" with the consequent danger of overwriting other proposed data from other users.

In addition to the sil:identity element, the SLDR will also honour the identity/fallback element as the parent locale to use for this file as held in the **fallbacks** attribute. This corresponds to an entry in the parentLocales supplemental data element. But rather than having to maintain such information centrally, it is held in the file itself. This increases extensibility. The value of the element is the language tag of the parent locale.

For example:
```xml
<special xmlns:sil="urn://www.sil.org/ldml/0.1">
    <sil:identity source="cldr" draft="approved"/>
</special>
```

## LocaleDisplayNames

The primary use of localeDisplayNames is to hold various key names as expressed in the orthography the LDML is describing. But this can become problematic when adding a new writing system. The addition of a file to the repository means editing some of the core writing system files like en.xml. This means that a single edit is spread across multiple files. It would be easier if some of that information was kept in the LDML of the orthography itself. So we extend the localeDisplayNames to allow the orthography name to be kept in the file. Then tools can be used to synchronise the other orthography ldml files to update their localeDisplayNames.

```rnc
# localeDisplayNames.special = element special { 
#     (sil.names?)
# }

sil.names = element sil:names {
    (sil.name+)
}

sil.name = element sil:name {
    (attlist.silname & attlist.sil.global),
    (text)
}

attlist.silname &= attribute xml:lang { text }
```
```dtd
<!ELEMENT sil:names (sil:name)+>

<!ELEMENT sil:name (#PCDATA)>
<!ATTLIST sil:name xml:lang NMTOKEN #IMPLIED>
<?ATTREF sil:name global?>
```

## Delimiters

This section includes such issues as punctuation patterns, quotation marks and matching pairs. LDML as it stands has limited quotation mark support, we embrace and extend this using a special and also add punctuation patterns and matching pairs.

```rnc
# delimiters.special = element special {
#     attlist.delimiters,
#     (sil.matchedpairs?,
#      sil.punctuation.patterns?,
#      sil.quotation-marks?)
# }

sil.quotation-marks = element sil:quotation-marks {
    (attlist.sil.quotation-marks & attlist.sil.global),
    ( (element sil:quotationContinue { text } |
        element sil:alternateQuotationContinue { text } |
      sil.quotation*)*)
}

attlist.sil.quotation-marks &= attribute paraContinueType { "all" | "outer" | "inner" | "none" }?

sil.quotation = element sil:quotation {
    (attlist.sil.quotation & attlist.sil.global)
}

attlist.sil.quotation &= attribute open { text }
attlist.sil.quotation &= attribute close { text }?
attlist.sil.quotation &= attribute continue { text }?
attlist.sil.quotation &= attribute level { text }
attlist.sil.quotation &= attribute type { text }?
# attlist.sil.quotation &= attribute type { "narrative" | text }?
```
```dtd
<!ELEMENT sil:quotation-marks (sil:quotationContinue | sil:alternateQuotationContinue | sil:quotation)+>
<!ATTLIST sil:quotation-marks paraContinueType (all | outer | inner | none) #IMPLIED>
<?ATTREF sil:quotation-marks global?>

<!ELEMENT sil:quotationContinue (#PCDATA)>
<!ELEMENT sil:alternateQuotationContinue (#PCDATA)>

<!ELEMENT sil:quotation EMPTY>
<!ATTLIST sil:quotation open CDATA #REQUIRED>
<!ATTLIST sil:quotation close CDATA #IMPLIED>
<!ATTLIST sil:quotation continue CDATA #IMPLIED>
<!ATTLIST sil:quotation level CDATA #REQUIRED>
<!ATTLIST sil:quotation type NMTOKEN #IMPLIED>
<?ATTREF sil:quotation global?>
```

**paraContinueType** specifies how quotations are handled at the start of a continuation paragraph. If the attribute is not present then it is assumed there are no quotation marks at the start of a paragraph. In the situation where two quotation marking systems are in use, the **type** attribute is used to distinguish them. The **level** attribute is a number from 1 indicating the quotation level. For example:

```xml
<delimiters>
    <quotationStart>«</quotationStart>
    <quotationEnd>»</quotationEnd>
    <alternateQuotationStart>“</alternateQuotationStart>
    <alternateQuotationEnd>”</alternateQuotationEnd>
    <special xmlns:sil="urn://www.sil.org/ldml/0.1)">
        <sil:quotation-marks paraContinueType="all">
            <sil:quotationContinue>»</sil:quotationContinue>
            <sil:alternateQuotationContinue>”</sil:alternateQuotationContinue>
            <sil:quotation level="3" open="‘" close="’" continue="’"/>
            <sil:quotation type="narrative" level="1" open="—"/>
        </sil:quotation-marks>
    </special>
</delimiters>
```

This example is for Spanish where they use em dash to mark the start of narrative quotations.

```rnc
sil.punctuation.patterns = element sil:punctuation-patterns {
    (sil.punctuation.pattern+)
}

sil.punctuation.pattern = element sil:punctuation-pattern {
    (attlist.sil.punctuation-pattern & attlist.sil.global)
}

attlist.sil.punctuation-pattern &= attribute pattern { text }
attlist.sil.punctuation-pattern &= attribute context { "init" | "medial" | "final" | "break" | "isolate" }?
```
```dtd
<!ELEMENT sil:punctuation-patterns (sil:punctuation-pattern)+>
<!ELEMENT sil:punctuation-pattern EMPTY>
<!ATTLIST sil:punctuation-pattern pattern CDATA #REQUIRED>
<!ATTLIST sil:punctuation-pattern context (init | medial | final | break | isolate) #IMPLIED>
<?ATTREF sil:punctuation-pattern global?>
```

Punctuation patterns give valid punctuation sequences in a text. The sequence is specified as a string with “\_” indicating whitespace. The **context** attribute specifies where the punctuation may occur. The values have the following meanings:

|             |                                              |
|-------------|----------------------------------------------|
| **init**    | The string occurs at the start of a word. |
| **medial**  | The punctuation string occurs within a word but is not word forming, and has no space around it. |
| **final**   | The string occurs at the end of a word. |
| **break**   | The string constitutes a word break with no whitespace around it. |
| **isolate** | The string occurs on its own surrounded by whitespace. |

Punctuation pattern elements are ordered by attribute in the following priority order: context, string; following conventional attribute order.

```rnc
sil.matchedpairs = element sil:matched-pairs {
    (sil.matchedpair+)
}

sil.matchedpair = element sil:matched-pair {
    attlist.sil.matched-pair & attlist.sil.global
}

attlist.sil.matched-pair &= attribute open { text }
attlist.sil.matched-pair &= attribute close { text }
[cldr:value="true"]
attlist.sil.matched-pair &= attribute paraClose { xsd:boolean }?
```
```dtd
<!ELEMENT sil:matched-pairs (sil:matched-pair)+>
<!ELEMENT sil:matched-pair EMPTY>
<!ATTLIST sil:matched-pair open CDATA #REQUIRED>
<!ATTLIST sil:matched-pair close CDATA #REQUIRED>
<!ATTLIST sil:matched-pair paraClose (true | false | 0 | 1) "false">
<!--@VALUE-->
<?ATTREF sil:matched-pair global?>
```

Matched pairs are simply pairs of characters that are required to be balanced in normal text usage. Thus for each **open** string there should be a corresponding **close** string. The **paraClose** attribute if set indicates whether the end of a paragraph may be used as an alternative to the occurrence of the **close** string. If the close string is empty then it assumed that the open string is no longer in a pair, and the corresponding close string of the original pair will also be considered unpaired. The root.xml contains pairings, with **paraClose** false, for:

    ( ), [ ], { }, « », ‹ ›

In addition, quotation marks that occur elsewhere in the delimiters information should not be included in paired punctuation.

Matched pair elements are ordered by the close attribute then the open attribute (to following conventional attribute sorting).

## Characters

The purpose of adding a special to the characters section of LDML is to add extra exemplar sets that are not currently supported by LDML. See [*Character Examplars*](https://docs.google.com/document/d/1DxI9kzPRgA-30U-C-PbF8wr2jVNE_rzQetexMvRX0H8/edit#heading=h.villpww8wak8).

```rnc
# characters.special = element special {
# }

sil.exemplarCharacters = element sil:exemplarCharacters {
        (attlist.sil.exemplarCharacters & attlist.sil.global),
        text
    }*
attlist.sil.exemplarCharacters &= attribute type { text }
```
```dtd
<!ELEMENT sil:exemplarCharacters (#PCDATA)>
<?ATTREF sil:exemplarCharacters global?>
<!ATTLIST sil:exemplarCharacters type NMTOKEN #REQUIRED>
```

The `sil:exemplarCharacters` element follows the LDML `exemplarCharacters` element in every way except that the type is unlimited. Some expected values for type include:

|                       |                                           |
|-----------------------|-------------------------------------------|
| **footnotes**         | A list of characters to use for footnote callers, in sequence. The sequence repeats. The list is for alphabetic characters, possibly mixed with specific symbols. Specifying this does not require the list to be used, particularly if a particular document prefers to use numeric footnote callers. |
| **requiredLigatures** | A list of character sequences that are required to ligate. This is particularly for Indic conjuncts, but may include other ligatures in other scripts as well. |
| **commonLigatures**   | A list of character sequences that commonly ligate but are not required to. This is particular for Indic conjuncts, but may include other ligatures in other scripts as well. |
| **graphemes**         | A list of grapheme clusters. This list contains all the base + modifiers sequences found in the language. |

`exemplarCharacters` elements are ordered by their type attribute.

For example:

```xml
<characters>
    <exemplarCharacters>
        [a b t s e c k x i d q r f g o l m n u w h y]
    </exemplarCharacters>
    <exemplarCharacters type="auxiliary">[j p v z]</exemplarCharacters>
    <exemplarCharacters type="index">
        [A B T S E C K X I D Q R F G O L M N U W H Y]
    </exemplarCharacters>
    <exemplarCharacters type="punct">[. ; : ! ? -]</exemplarCharacters>
</characters>
```

## Notes

The `sil:note` element is a general textual note storing markdown text for notes on the LDML, for example addressing issues in the LDML. While ethnographic information may be stored in a note, the note should not be presumed to contain it or any particular information.

```rnc

sil.note = element sil:note {
        text
    }
```
```dtd
<!ELEMENT sil:note (#PCDATA)>
```


## Miscellaneous

### Regular Expressions

In dealing with character level data it is common to work with a limited window for processing text or to even transform regular expressions into other forms. For this reason, the regular expression language used in LDML is a restricted regular expression language. In particular it does not allow klein \* or +. Thus all such regular expression have a predeterminable maximum and minimum length of string matched.

For greater processability the restricted regular expression language is limited to:

-   \[\] class matching
-   {*n*,*m*} range matching
-   ? optional match
-   () grouping which may be referenced in the reorder attribute
-   | alternation
-   *ab* sequence
-   *a* character
-   . any character

As a result the following characters need to be escaped with a preceding \\

   \[ \] { ( ) ? | . \\

In many cases such a regular expression is used to match a string which is then transformed in relation to that regular expression. Such transformation strings may use the following elements:

-   *a* character
-   \\*n* group reference

Not all matched groups need to be referenced.

### Supplemental Metadata

This section contains changes that would need to be made to the Supplemental Metadata if these extensions were added to the main LDML specification. It is somewhat technical in nature and is primarily of concern for those wishing to produce canonical LDML with these extensions.

One of the basic principles of LDML encoding is that there cannot be two elements with the same parent and the same distinguishing attribute values. If that is the case, then either something has to change or the elements must be serially ordered and their parent becomes a blocking element for inheritance purposes.

#### serialElements

The `supplementalData/metadata/serialElements` contains a list of elements which are not sorted by attributes but are kept in the order specified. I.e. order for these elements carries meaning within the parent. The following elements would be added: sil:reorder, sil:quotation, sil:url, sil:font.

#### attributeOrder

The `supplementalData/metadata/attributeOrder` element contains a list of attribute names in sorted order. When elements are stored, attributes are stored within the element in the order given by this element, and failing that, at the end of the list in alphabetical order. More importantly, this attribute order is the one used to sort elements of the same type within their parent. Currently there are no additions required to this list.

#### elementOrder

The `supplementalData/metadata/elementOrder` element contains a list of elements in relative order. All extension elements in this document have a namespace prefix and so are outside the scope of this list, even if their local name were the same. Currently no extension elements are ordered outside of alphabetical ordering and so no list is needed.

#### distinguishing

The `supplementalData/metadata/distinguishing` element holds information about which attributes in which elements are considered distinguishing for inheritance purposes. The following elements would be added: string. In addition, in the element sil:matched-pair, the attributes: open and close are distinguishing.

#### blocking

The `supplementalData/metadata/blocking` element holds lists of elements that are to be treated as a single unit for inheritance purposes. The following elements would be added: sil:fontrole, sil:kbd, sil:spell-checking, sil:transform, sil:quotation-marks, sil:matched-pairs.

## Implementation

This section considers aspects of implementation with regard to clients applications using LDML with the SIL namespace.

### Alias

LDML has a special element that can occur: alias. Details may be found here [*http://www.unicode.org/reports/tr35/\#Alias\_Elements*](http://www.unicode.org/reports/tr35/#Alias_Elements). An alias element requires the XML processor to requery the locale with a different xpath relative to the one it is on. Ideally, it should be possible to flatten an LDML hierarchy such that all inheritances are resolved and aliases are resolved too. This is possible, and at least one tool exists to do the inheritance flattening. But the flattening is not the problem. Difficulties arise when the hierarchy is being rebuilt from a flattened file. Consider the following example:

```xml
<special>
    <sil:external-resources>
        <sil:font name="Padauk" engines="gr ot" type="default">
            <sil:url>http://wirl.scripts.sil.org/padauk</sil:url>
        </sil:font>
        <sil:font name="Padauk" engines="gt ot" type="bodytext">
            <alias source="locale" path="../sil:font\[@type='default'\]"/>
        </sil:fontrole>
    </sil:external-resources>
</special>
```

The problem arises when, after flattening such that there are in effect two copies of the `sil:url` element, the user changes the information for the `sil:font[@type="default"]`. Due to the alias, the `sil:font[@type="bodytext"]` should update to have the same value. Also upon unflattening back to a hierarchy, it is not possible for the tool to work out whether the `sil:font[@type="bodytext"]` value has changed from being an inherited alias to being the actual value or whether the alias should remain and the value deleted. The fact that alias elements may only occur in the root.xml does not resolve this issue.

One approach that would make life easier for clients is if we add a general attribute `sil:alias="xpath"` (where *xpath* is the same as the `@path` element in the alias) that may be added to any element. If present it specifies that the value in the element has come from an alias. If a user edits that element, the client must delete the attribute. This still does not solve the issue of a user changing the value of the source xpath (as in changing the default font in the example above), but it does: allow the client to update its value based on the alias; indicate that the alias is being overridden by a user's explicit edit and allow the client to ignore aliases in general if all they want to do is look up a value. When the hierarchy is reconstituted, the tool can then see whether an aliased value has been edited or to ignore the value (interpretting it as a previous value of the alias source, however wrong that may be) and stick with the alias.

## Issues

Here we collect and discuss issues before they are resolved into the main body of the text.

### From fw namespace

The following are things that we may or may not want to merge from the fw namespace:

|                        |                                         |
|------------------------|-----------------------------------------|
| fontfeatures           | /ldml/special/sil:external-resources/font/@features |
| graphiteEnabled        | /ldml/special/sil:external-resources/font/@disableGraphite |
|                        | \[cp\] This is really an application setting and could happily be stored elsewhere. |
| matchedPairs           | /ldml/delimiters/special/sil:matched-pairs/matched-pair |
| quotationMarks         | /ldml/delimiters has support for 2 levels of quotations. |
|                        | /ldml/delimiters/special/sil:quotation-marks/@paraContinueType  |
|                        | /ldml/delimiters/special/sil:quotation-marks/@paraContinueMark |
|                        |  Extra levels are stored in: |
|                        |  /ldml/delimiters/special/sil:quotation-marks/quotation |
| regionName             | /ldml/identity/special/sil:identity/@regionName (Note this value may be other than covered in ISO 3166, although such a changed value will require careful review). This is a UI name for the region. Instead a mapping through en.xml or whatever the intended UI locale being used of ldml/identity/territory/@type |
| scriptName             | /ldml/identity/special/sil:identity/@scriptName (Note this value may be other than that covered by ISO 15924, although such a changed value will require careful review). UI presentation forms should be of ldml/identity/script/@type mapped through the UI locale ldml. |
| variantName            | /ldml/identity/special/sil:identity/@variantName (PUA variants are liable to occur. Would a more general comment field that says: this is what I am trying to say in my language tag, be more helpful)? |
| validChars/WordForming | /ldml/characters/exemplarCharacters\[@type=”main”\] (do we also want to include \[@type=”auxiliary”\]?) (or perhaps use character properties) |
| validChars/Numeric     | /ldml/numberingSystems/numberingSystem/\[@type=”numeric”\]/@digits (watch out for non-numeric systems!) |
| validChars/Other       | /ldml/characters/exemplarCharacters\[@type=”punctuation”\] |
| windowsLCID            | /ldml/identity/special/sil:identity/@windowsLCID  |
| legacyMapping          | /ldml/special/sil:external-resources/font/@isLegacy. Is this really required? |

## Paratext

Paratext currently has its own writing system definition. We are trying to achieve more interoperability between Paratext and SIL software. It would be helpful if Paratext used the same writing system definition. Do these extensions meet Paratext’s requirements?

Here are some things we are *not* going to store in LDML, until we change our minds!

|                             |                                                           |
|-----------------------------|-----------------------------------------------------------|
| default paragraph direction | This is inferred using the bidi algorithm. The only reason for changing it is if we get PUA based projects that are rtl. This is highly unlikely now since we know of no unencoded rtl scripts. And if we did, we would encode them double quick! |
| cross reference sequence    | This is considered project specific, unlike footnote caller sequence which we will include in LDML. |
| usfm continue paths         | This is not LDML information and can be kept in the project. |
