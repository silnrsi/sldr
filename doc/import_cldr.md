# Importing CLDR Data

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

```
mkdir cldrdata
mkdir flat
```

Then we import the data:

```
PYTHONPATH=python/lib python python/scripts/cldrimport ~/mycldrsource/common cldrdata
PYTHONPATH=python/lib python python/scripts/ldmlflatten -i cldrdata -o flat
```

To ensure that files that need to be deleted, are, we rebuild the sldr directory from
scratch. Notice that git is quite happy with this.

```
rm -fr sldr
mkdir sldr
PYTHONPATH=python/lib python python/scripts/ldmlflatten -i flat -o sldr -r
```

Now we are ready to commit our changes. First we stage all the additions, changes and removals
and then we commit and merge into master

```
git add -A sldr
git commit -m "CLDR import from svn revision xxxxx"
git checkout master
git merge cldr
git push
```
