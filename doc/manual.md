# SLDR Management Manual

This manual provides details on various scenarios.

## Preparing to Serve

Having cloned the SLDR github repository, how do we get hold of the flattened and unflattened files
for distributing to applications and users?

    python/scripts/ldmlflatten -o flat -i sldr -a --revid=`git rev-parse HEAD`
    python/scripts/ldmlflatten -o unflat -i sldr -a -c --revid=`git rev-parse HEAD`

The `git rev-parse HEAD` returns a string which is the SHA identifier for this revision. This is then
inserted into all the generated files.

## Manually Accepting a Contribution

A user has edited an LDML file and sent it to you. The file is a flattened file. What do you do now?

The first step is to unflatten the file against the revision that the file originated from.
The file has an `ldml/identity/revid` element whose value is the SHA of the revision that the
file originated from (or perhaps a later version, but it's OK to go back to here). You don't
need to use the whole SHA value, but cut and paste is easy enough.

    git checkout -b wip 0123456789abcdefdeadbeeffeedcafe

If you really want to be cute and not have to deal in sha values at all you can do
(and you have xmlstarlet installed):

    git checkout -b wip `xmlstarlet sel -N sil='urn://www.sil.org/ldml/0.1' -t -v "/ldml/identity/special/sil:identity/@revid" temp/cont_Latn.xml`

Now we have to unflatten the contributed file to get it back to something that can be put into the
sldr directory, without a `identity/revid` or `identity/script`.

    python python/scripts/ldmlflatten -i temp -r -o sldr -l cont_Latn -s

Then we need to commit the change

    git commit -a -m "Update cont_Latn from my friend"
    git rebase master
    git checkout master
    git merge wip

This takes some explaining. We draw some diagrams. Initially we have this state:

    C---D---E---F master

And let D have the SHA in the file. After `git checkout -b wip 0123456` we have

        wip
    C---D---E---F master

Then we commit our change:

          G wip
         /
    C---D---E---F master

After the rebase we get:

                  G wip
                 /
    C---D---E---F master

Finally we have to move master to the end of the chain. We do this by checking out master
and then merging in wip, which fast forwards master to wip:

    C---D---E---F---G master

At this point we do not care what wip is pointing at. It will get moved by a later checkout.


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
would be removed by stub removal, do not remain and get propagated forward

    mkdir cldrdata
    mkdir flat

Then we import the data:

    python python/scripts/cldrimport ~/mycldrsource/common cldrdata
    python python/scripts/ldmlflatten -i cldrdata -o flat

Bear in mind that one can use `pypy` instead of `python` in the above and life will
run faster (in exchange for more memory usage).

To ensure that files that need to be deleted, are, we rebuild the sldr directory from
scratch. Notice that git is quite happy with this.

    rm -fr sldr
    mkdir sldr
    python python/scripts/ldmlflatten -i flat -o sldr -r

Now we are ready to commit our changes. First we stage all the additions, changes and removals
and then we commit and merge into master

    git add -A sldr
    git commit -m "CLDR import from svn revision xxxxx"
    git checkout master
    git merge cldr
    git push
