# SLDR Management Manual

This manual provides details on various scenarios.

## Preparing to Serve

Having cloned the SLDR github repository, how do we get hold of the flattened and unflattened files
for distributing to applications and users?

    python/scripts/ldmlflatten -o flat -i sldr -a -A --revid=`git rev-parse HEAD`
    python/scripts/ldmlflatten -o unflat -i sldr -a -c --revid=`git rev-parse HEAD`

The `git rev-parse HEAD` returns a string which is the SHA identifier for this revision. This is then
inserted into all the generated files.

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
