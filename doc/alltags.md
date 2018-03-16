# alltags.txt Description

There are two versions of this file:

* alltags.txt. This contains a simple list of equivalencies
* alltags_inheritance.txt. This contains full inheritance relationships

Both files contain much in common. The file is structured as a series of
lines. Each line corresponds to an equivalent set of language tags. Each
tag is separated by the next on the line by an operator. In addition, a tag
may be prefixed by a `*`. This indicates that there is a corresponding
sldr file for that tag.

## alltags.txt

The alltags.txt file contains information regarding language tags and how they
relate to each other. There are 2 relationships given:

* `=` equivalence. The two tags are equivalent to each other
* `|` specialisation. The following tag has a corresponding file that is
a specialisation of a preceding tag with a file. The difference may be
negligable or there may be content differences.

If a tag starts with an asterisk `*`, there exists a data file for that tag by
that name in the SLDR.

### Examples
Each line contains one equivalence set. There cannot be more than one equivalence
set that contains the same tag. For example:

```
*aa | *aa-ET = aa-Latn = am-Latn-ET
aa-Ethi = aa-Ethi-ET
```

This says that `aa-ET` has an inheritance relationship with `aa` and that
`aa-Ethi` is equivalent to `aa-Ethi-ET`.

Another fun example is:

```
az-Arab = az-Arab-IR
*az = az-AZ | *az-Latn | *az-Latn-AZ
*az-Cyrl = az-Cyrl-RU = az-RU
*az-Cyrl-AZ
```

This says that the default script for `az` is `Arab`, but that there is no difference
between `az-Latn` and `az`! What it says is that if you receive the tag `az` then
you can interpret it as `az-Arab-IR`. But with regard to data sets, there is no
difference between `az` and `az-Latn`, since the `az` data set is in Latin script
rather than Arabic. Notice that there is no relationship listed between
`az-Cyrl-AZ` and `az-Cyrl` because none is specified in the data sets.

The problem here is that the `az` data set is in
Latn while the dominant script is Arab. What is needed is an az_Arab.xml and
this will sort itself out. All this to say that things aren't as clean as they
might be and that some hand curation may be required.

## alltags_inherited.txt

This file contains many more operators and describes the inheritance
relationships between SLDR files. The following operators are used:

* `=` The two tags are equivalent
* `|=` The second tag is a file that inherits from the tag preceding it. But the only difference is in the identity block. I.e. there is no real content difference. It also says (through the `=`) that the tags are equivalent/
* `<=` The second tag is a file that inherits from the tag preceding it. There is content difference. In effect, this should not happen since the `=` says that the the tags are equivalent and that there is no locale difference between them, but the inheritance says there is a difference.
* `>` The first tag is a file (so has a `*` prefix) that inherits from the second file (also with a `*` prefix). But the second tag is not equivalent to anything else in the set. I.e. the second tag is not part of the equivalence set.

### Examples

```
*az = az-AZ |= *az-Latn |= *az-Latn-AZ
az-Arab = az-Arab-IR
*az-Cyrl = az-Cyrl-RU
*az-Cyrl-AZ > *az-Cyrl
```
