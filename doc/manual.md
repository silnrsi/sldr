# SLDR Management Manual

This manual provides details on various scenarios.

## Language Tags

Language tags are deceptively simple ideas. In this discussion of how language tags are used in the SLDR,
we consider three alternatives for a given tag:

* *Shortest tag* is the shortest form of a tag that will refer to the same file as the
  original tag
* *Longest tag* is the longest form of a tag that will refer to the same file as the original tag.
* *Canonical tag* is a tag that is conformant to the canonical form as specified using the IANA registry.
  In particular, canonical tags have any suppressed scripts removed.

The CLDR, and therefore the SLDR, holds files according to their longest and shortest canonical tags. Thus
there are files `en.xml` and `en_US.xml` because Latn is a suppressed script for `en`. But there is only
`bng_Latn.xml` due to the lack of any script supression for `bng`. Examining `en_US.xml` in the CLDR will
result in a file with no content beyond an identity block. This is because `en.xml` is actually the US
locale. This relationship can be identified from the supplemental data file `likelyTags.xml` which lists
the full expansion of `en` as `en-Latn-US`.

When a query comes in for `en`, therefore, the ldml server expands this to its longest corresponding tag
using `likelyTags.xml`. It then uses any combination of lang, script, region and variant to search for a
corresponding file in the SLDR. If it finds one, it takes the longest filename and uses that as the
required tag. If this tag is not the same as the tag submitted, the server returns a redirect.

For example, on requesting `en`, this is expanded to `en-Latn-US`. The longest filename found is `en_US.xml`.
And since `en_US` is not `en` (even though `en.xml` exists) the server returns a redirect to `en_US`.
This may seem counter intuitive at first, but it is actually the required behaviour (if somewhat
convoluted) in that the user wants the request tag to correspond to the information inside the identity
block. `en.xml`, in the SLDR when prepared for use by the server has a `script="Latn"` and `territory="US"`
since that is what the data reflects.

The effect of all this is that the SLDR holds files for the shortest and longest canonical forms of a given tag.
Notice that `en_GB` is its own shortest form since `en` corresponds to `en_US`.

## Preparing to Serve

Having cloned the SLDR github repository, how do we get hold of the flattened and unflattened files
for distributing to applications and users?

    python/scripts/ldmlflatten -o flat -i sldr -a -A -g
    python/scripts/ldmlflatten -o unflat -i sldr -a -c -g

An alternative to using `-g` is to use ``--revid=`git rev-parse HEAD` ``.
The `git rev-parse HEAD` returns a string which is the SHA identifier for this revision.
This is then inserted into all the generated files. `-g` does a better job by finding the last revision in which
each particular file was last changed. This reduces the churn on applications querying whether a file has changed.

## Manually Accepting a Contribution

A user has edited an LDML file and sent it to you. The file is a flattened file. What do you do now?
ldmlmerge does most of the work for you. The following example command shows what is typically done:

    pythons/scripts/ldmlmerge -g -C base -d sldr -o cont_Latn.xml temp/cont_Latn.xml cont_Latn.xml

This command does a number of things:

*   Reads the input file `temp/cont_Latn.xml` and extracts the `sil:identity/@revid`
*   Extracts that version of cont_Latn.xml (the final parameter) having looked for it in the sldr source directory,
    as specified by the -d option
*   Finds the latest version of cont_Latn.xml and extracts that if it is newer than the one specified by @revid.
*   Flattens all the files internally
*   Does a 2 or 3 way merge incorporating @draft, @alt, sil:identity/@uid, etc.
*   Replaces the comments from the base file, assuming the sender has stripped them. If you trust that the
    sender has done the right thing with comments, then omit the -C option.
*   Strips out @uid and @revid from sil:identity and unflattens the result
*   Saves the output to cont_Latn.xml as specified by the -o option
*   Updates the date in the identity block if there has been any changes.

Now you can review that file and perhaps diff it agains the one in sldr. After that you can replace the file
in sldr and commit your change.


## Importing CLDR Data

This document describes the process for importing a new version of CLDR data into the SLDR.

Importing CLDR data is an activity that happens alongside regular editing of LDML files.
As a result, the easiest way to manage this is to use a git branch. All changes to CLDR will
be imported into a separate branch called `cldr` and then those changes are merged into the
`master` branch. This means that only the changes between versions of the CLDR will be merged
into the data rather than confusion over who edited what and when.

We start by switching to the `cldr` branch:

```
git checkout cldr
```

The process of creating an SLDR file is slightly more involved than simply copying a file. Files
are flattened and then unflattened. This has the effect of stripping any information that is
inherited. We do this because that is the process used to normalise data imports from other
sources. We send out flat files and then unflatten them on import. To allow for good merging,
therefore, it is necessary that the cldr files are held in the same form.

To do this, we use two temporary directories that are not committed. If they already exist, they
should be removed and rebuilt so that any files that have been removed from the CLDR or that
would be removed by stub removal, do not remain and get propagated forward. It also allows us to
merge back from master for things like tools.

    mkdir cldrdata
    mkdir flat

Then we import the data:

    python python/scripts/cldrimport --hg ~/mycldrsource/common cldrdata
    python python/scripts/ldmlflatten -i cldrdata -o flat -a

Bear in mind that one can use `pypy` instead of `python` in the above and life will
run faster (in exchange for more memory usage).

Now we unflatten the files to their sldr form and merge them into the sldr

    python python/scripts/ldmlflatten -i flat -o sldr -r -a

Now we are ready to commit our changes. First we stage all the additions, changes and removals
and then we commit and merge into master

    git add -A sldr
    git commit -m "CLDR import from svn revision xxxxx"
    git checkout master
    git merge cldr
    git push


## Editing LDML Files

There are various ways of editing an LDML file.

### Text editor

One approach is to use a text editor of your choice. But once the editing is complete,
before a file can be committed, it should be normalised. The following command will
normalise a file:

    python python/scripts/ldmlflatten -c -i *srcdir* -o *outputdir* -l *locale*

for example:

    python python/scripts/ldmlflatten -c -i sldr -o sldr -l en_US

Yes you can use the same input and output directories. Although the source file will be
overwritten in that case. Caveat emptor.

If ldmlflatten fails, it can be helpful to run it single process which will give
more helpful? error messages:

    python python/scripts/ldmlflatten -s -c -i sldr -o sldr -l en_US

