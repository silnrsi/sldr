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
ldmlmerge (in sldrtools/scripts) does most of the work for you. The following example command shows what is typically done:

```
    ldmlmerge -g -C base -d sldr -o cont_Latn.xml temp/cont_Latn.xml cont_Latn.xml
```

This command does a number of things:

*   Reads the input file `temp/cont_Latn.xml` and extracts the `sil:identity/@revid`
*   Extracts that version of `cont_Latn.xml` (the final parameter) having looked for it in the sldr source directory, as specified by the -d option
*   Finds the latest version of `cont_Latn.xml` and extracts that if it is newer than the one specified by @revid.
*   Flattens all the files internally
*   Does a 2 or 3 way merge incorporating @draft, @alt, sil:identity/@uid, etc.
*   Replaces the comments from the base file, assuming the sender has stripped them. If you trust that the
    sender has done the right thing with comments, then omit the -C option.
*   Strips out @uid and @revid from sil:identity and unflattens the result
*   Saves the output to `cont_Latn.xml` as specified by the -o option

Now you can review that file and perhaps diff it agains the one in sldr. After that you can replace the file
in sldr and commit your change.


## Importing CLDR Data

This section describes the process for importing a new version of CLDR data into the SLDR. Importing CLDR data is an activity that happens alongside regular editing of LDML files. As a result, the easiest way to manage this is to use a git branch. All changes to CLDR will be imported into a separate branch called `cldr` and then those changes are merged into the `master` branch. This means that only the changes between versions of the CLDR will be merged
into the data rather than confusion over who edited what and when.

Note that the commands used on a Windows machine differ slightly from those used on a Linux machine, so, if you are using a Windows machine, consult the relevant section below and determine what needs to be done differently.

### Linux Machine

Starting in the sldr repository, we switch to the `cldr` branch:

```
    git checkout cldr
```

The process of creating an SLDR file is more involved than simply copying a file. 
Files are flattened and then unflattened. 
This has the effect of stripping any information that is inherited. 
We do this because that is the process used to normalise data imports from other sources. 
We send out flat files and then unflatten them on import. 
To allow for good merging, therefore, it is necessary that the cldr files are held in the same form.

To do this, we use two temporary directories (`cldrdata` and `cldrflat`) that are not committed. 
If they already exist, they should be removed and rebuilt so that any files that have been removed from the CLDR or that would be removed by stub removal, do not remain and get propagated forward. 

```
    mkdir cldrdata
    mkdir cldrflat
```

Copy `common` from the latest CLDR release into current directory. 
(Alternatively, if you already have the CLDR repository on your computer, you can substitute the path to the CLDR `common` directory in place of `common` in the following command.)

Then we import the data:

```
    cldrimport -s -t common cldrdata    
    ldmlflatten -s -t -i cldrdata -o cldrflat -a
```

Now we unflatten the files to their sldr form and merge them into the sldr

```
    ldmlflatten -s -t -i cldrflat -o sldr -r -a
```

We now have a pristine CLDR data set for the cldr branch. 
So commit it (to the `cldr` branch of the SLDR repository.

```
    git add -A sldr
    git commit -m "CLDR import from version xxx"
    git push
```

At this point the directories used in the process (`common`, `cldrdata`, `cldrflat`) can be removed.

In order to tidy up and integrate, we use a separate `cldr_merge` branch in which we do the merging of master and cldr. This keeps cldr clean and allows review and editing before merging with master.

```
    git checkout cldr_merge
    git merge master
    git merge cldr
```

Resolve any conflicts. If there are just a few, you may want to hand edit, but otherwise use ldmlmerge set up as a git merge tool (see "Set up ldmlmerge as git mergetool" section below).

```
    git mergetool -t ldml
```

If there are files to commit, commit them now (to the `cldr_merge` branch of the SLDR repository).

```
    git status
    git commit -a -m "Integrate cldr"
    git push
```

Once the data in the `cldr_merge` branch has been reviewed, it can be merged into `master`.

```
    git checkout master
    git merge cldr_merge
    git push
```

### Set up ldmlmerge as git mergetool

If, when merging the `cldr` branch into the `cldr_merge` branch, you encounter merge conflicts, you'll need to use ldmlmerge to resolve them. Setting up ldmlmerge as a git mergetool enables this to be done automatically for the hundreds of files involved.

Starting in the sldr repository, use the following commands to set up `ldmlmerge` as a git mergetool. 
Note in particular that it is necessary to use single quote marks (rather than double quote marks) so that the command line will be properly read.

```
git config merge.tool ldml
git config mergetool.ldml.cmd 'ldmlmerge -v -G -C other -o $MERGED $LOCAL $BASE $REMOTE'
```

This requires that `ldmlmerge` is available in your path. It is available from the sldrtools project which should be installed.

To verify that your configuration is correct, you can use the config editor:

```
git config -e
```


### Windows Machine

Depending how Python is installed on the Windows computer, you may need to:
- explicitly include `python` before the script name
- include the path to the script with the script name

### Notes

The scripts used for this process (cldrimport, ldmlflatten, ldmlmerge) are in the `sldrtools` repository.

Bear in mind that one can use `pypy` instead of `python` in the above and life will run faster (in exchange for more memory usage). Although the benefits are reduced when using the faster python3.

## Updating the DTD

Importing a new version of CLDR may require a new version of the DTD definition in `ldml.dtd`.

```
# copy the ldml.dtd file
cp /cldr/common/dtd/ldml.dtd /sldr/doc
# use make/Makefile and scripts in bin/ to generate files 
cd /sldr
make
# make sure all locales pass the following test:
pytest test_validate.py::test_validate
# commit updated files
git add -A
git commit -m "update ldml.dtd"
git push
# copy updated file to sldrtools and commit
cp doc/sil.dtd /sldrtools/lib/sldr
cd /sldrtools
git add -A
git commit -m "update ldml.dtd"
git push
```