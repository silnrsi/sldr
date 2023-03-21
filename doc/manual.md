# SLDR Management Manual

This manual provides details on various scenarios.

## Note on Linux vs Windows

On Linux, Python scripts (such as `ldmlflatten`) are installed and available to run on the command line.
On Windows you may need to explicitly invoke Python and include the path to the script (such as `python pathinfo\ldmlflatten`).
This document will use the Linux form and Windows users will need to adjust accordingly.

## Preparing to Serve 

Note: This no longer needs to be done manually. It is done automatically via GitHub actions when data is pushed to SLDR (master or release branches).

Having cloned the SLDR github repository, how do we get hold of the flattened and unflattened files
for distributing to applications and users?

    ldmlflatten -o flat -i sldr -a -A --revid=`git rev-parse HEAD`
    ldmlflatten -o unflat -i sldr -a -c --revid=`git rev-parse HEAD`

The `git rev-parse HEAD` returns a string which is the SHA identifier for this revision. This is then
inserted into all the generated files.

## Manually Accepting a Contribution

A user has edited an existing LDML file (`cont_Latn.xml`) and sent it to you. The file is a flattened file. What do you do now?
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
git commit -a -m "update ldml.dtd"
git push
# copy updated file to sldrtools and commit
cp doc/sil.dtd /sldrtools/lib/sldr
cd /sldrtools
git commit -a -m "update ldml.dtd"
git push
```
## Importing CLDR Data

This section describes the process for importing a new version of CLDR data into the SLDR. Importing CLDR data is an activity that happens alongside regular editing of LDML files. As a result, the easiest way to manage this is to use a git branch. All changes to CLDR will be imported into a separate branch called `cldr` and then those changes are merged into the `master` branch. This means that only the changes between versions of the CLDR will be merged
into the data rather than confusion over who edited what and when. A `cldr_merge` branch is used for the actual merge.

Starting in the sldr repository, we switch to the `cldr` branch:

```
    git checkout cldr
```

Copy the `common` folder from the latest CLDR release into current directory (or access it directly in a local copy of the CLDR repository).
Consider whether the DTD needs to be updated (see section above).

Then we import the data:

```
    cldrimport -s -t common cldrdata    
```

We now have a pristine CLDR data set for the cldr branch. 
So commit it (to the `cldr` branch of the SLDR repository), including the CLDR version number (xx).

```
    git add sldr
    git commit -m "CLDR import from version xx"
    git push
```

At this point, if a copy of the `common` directory was made for use in the process, it can be removed.

In order to tidy up and integrate, we use a separate `cldr_merge` branch in which we do the merging of master and cldr. This keeps the `cldr` branch clean and allows review and editing before merging with master.

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

### Make a copy of supplemental data

Copy the following files from the CLDR repository cldr/common/supplemental folder to sldrtools/lib/sldr:

```
    likelySubtags.xml
    supplementalData.xml
    supplementalMetadata.xml
```

and push the changes.

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

NB: As of 2022-01, setting up ldmlmerge as a mergetool on Windows has not succeeded. Use a Linux VM instead.

### Notes

The scripts used for this process (cldrimport, ldmlflatten, ldmlmerge) are in the `sldrtools` repository.

Bear in mind that one can use `pypy` instead of `python` in the above and life will run faster (in exchange for more memory usage). Although the benefits are reduced when using the faster python3.
