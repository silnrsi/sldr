# alltags.txt Description

The alltags.txt file contains information regarding language tags and how they
relate to each other. There are 3 primary relationships:

* `=` equivalence. The two tags are equivalent to each other
* `>` inheritance. The left hand tag is a specialisation of the right hand tag.
* `|` empty inheritance. There exist data sets for the two tags but one (the right hand)
is simply an empty specialisation of the left.

If a tag starts with an asterisk `*`, there exists a data file for that tag by
that name in the SLDR.

Each line contains one equivalence set. There can be more than one equivalence set
that contains the same tag. For example:

```
*am = am-Ethi | *am-ET = am-Ethi-ET
*am = am-IL = am-Ethi-IL
```

This says that `am-ET` has an empty inheritance relationship with `am` and that
`am-IL` is equivalent to `am`, but not to `am-ET`, at least not formally. There
is nothing to say that these relational sets cannot be merged inside an application.

Another fun example is:

```
*az = az-Arab-IR = az-IR
*az | *az-Latn | *az-Latn-AZ = az-AZ
*az-Cyrl = az-Cyrl-RU = az-RU
*az-Cyrl-AZ
*az-Latn = az-Latn-AM
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
