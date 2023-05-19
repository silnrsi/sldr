from langtag import langtag, lookup
import os
from sldr.ldml import Ldml, _alldrafts

### THIS WHOLE THING PROBABLY DOESN'T BELONG IN THIS REPO IT'S PROBABLY AN SLDR TOOLS THING :P

def _has_sldr(root_tagset):
    return getattr(root_tagset, "sldr", None)
    
def _remove_private(root_tag):
    r = root_tag.rfind('-x-')
    if r > 0:
        root_tag = root_tag[:r]
    ran_private = True
    return root_tag, ran_private

def trim_tag(root_tag):
    r = root_tag.rfind('-')
    root_tag_trim = root_tag
    if r > 0:
        root_tag_trim = root_tag[:r]
    c = root_tag_trim.count('-')
    if c > 0:
        trimmable = True
    else:
        trimmable = False
    return root_tag_trim, trimmable

def mintag_file(langid, prev_tagset):
    mintags = [str(getattr(prev_tagset, "tag", None))]
    tags = getattr(prev_tagset, "tags", None)
    this_file = str(os.path.splitext(os.path.basename(langid).replace("_", "-"))[0])
    redundant = False
    if mintags[0] == this_file:
        return redundant
    for tag in tags:
        mintags.append(str(tag))
    print(mintags)
    for mintag in mintags:
        if mintag != this_file:
            mintag_file = os.path.join("..", "sldr", (mintag[0]), (mintag.replace("-", "_") + ".xml"))
            print(mintag_file)
            print(os.path.isfile(mintag_file))
            print(mintag)
            if os.path.isfile(mintag_file):
                redundant = True
                break
    print("is redunant?:" + str(redundant))
    return redundant

def find_parents(langid, to_root = True, needs_sldr = False, match_script = True, match_region = False):    
    """ 
        Parameters: 
            to_root:        If true, will go all the way to the root. If false, will stop if it can just find one parent file. 
            needs_sldr:     If true, will output last parent with an SLDR file
            match_script:   If true, will stop at the last parent with a matching script
            match_region:   If true, will stop at the last parent with a matching region
    """
    lt = langtag(os.path.splitext(os.path.basename(langid))[0]) #gets basic langtag data based on file name
    tagset = lookup(str(lt).replace("_", "-"), default="", matchRegions=True)
    #this next section is for variants, private use areas that don't refer back to their non-private versions in langtags, and other weirdness
    if tagset == "":
        print("no tagset found, shaving last langtag value to try to find it")
        r = str(lt).rfind('-')
        if r == -1:
            return True, str(tagset), tagset, [str(tagset)]
        variant = str(lt)[r+1:]
        lt_trim = str(lt)[:r]
        tagset = lookup(str(lt_trim).replace("_", "-"), default="", matchRegions=True)
        if tagset == "":
            r = str(lt).rfind('-x-')
            lt_trim = str(lt)[:r]
            tagset = lookup(str(lt_trim).replace("_", "-"), default="", matchRegions=True)
            if to_root == False:
                if (needs_sldr and _has_sldr(tagset)) or needs_sldr == False:
                    return False, str(tagset), tagset, [str(tagset)]
        if variant == "001":
            if to_root == False:
                return False, str(tagset), tagset, [str(tagset)]
        if hasattr(tagset, "variants") and variant in tagset.variants:
            if to_root == False:
                if (needs_sldr and _has_sldr(tagset)) or needs_sldr == False:
                    return False, str(tagset), tagset, [str(tagset)]
                
    lt_text = str(tagset) #technically never used, but kept just in case need to compare old & new if test is updated or made more complex later
    root_tag = lt_text
    root_tagset = tagset
    parent_path = [root_tag]
    print(root_tag.count('-'))
    
    print("data pre-test")
    print(root_tag)
    print(root_tagset)
    print(root_tagset.script)

    def parent_loop(root_tag:str, root_tagset, to_root = True, needs_sldr = False, match_script = True, match_region = False):
        trimmable = True
        ran_private = False
        redundant = False
        root_tag_temp = root_tag
        while trimmable:
            prev_tagset = lookup(root_tag_temp.replace("_", "-"), default="", matchRegions=False)
            if ran_private == False:
                redundant = False
                print("remove private")
                root_tag_trim, ran_private = _remove_private(root_tag_temp)
                print(root_tag)
                print(root_tag_trim) 
            else:
                redundant = mintag_file(langid, prev_tagset)
                if redundant and (to_root == False):
                    return root_tag, redundant
                root_tag_trim, trimmable = trim_tag(root_tag_temp)
                print("after a tag trim iteration:")
                print(root_tag)
                print(root_tag_trim) 
            root_tag_temp = root_tag_trim
            root_tagset_temp = lookup(str(root_tag_trim).replace("_", "-"), default="", matchRegions=False)
            print(root_tagset_temp)
            if root_tagset_temp == root_tagset or root_tagset_temp == prev_tagset:
                print("tagsets still match, trim again!")
                continue
            elif match_region and match_script == False:
                if root_tagset_temp.region == root_tagset.region:
                    if (needs_sldr and _has_sldr(root_tagset_temp)) or needs_sldr == False:
                        print("new parent found")
                        root_tag = root_tag_trim
                        parent_path.append(root_tag)
                        if to_root == False:
                            return root_tag, redundant
                    if to_root or (needs_sldr and (_has_sldr(root_tagset_temp) == False)):
                        print("regions still match, trim again!")
                        continue
            elif match_script and match_region == False:
                if root_tagset_temp.script == root_tagset.script:
                    if (needs_sldr and _has_sldr(root_tagset_temp)) or needs_sldr == False:
                        print("new parent found")
                        root_tag = root_tag_trim
                        parent_path.append(root_tag)
                        if to_root == False:
                            return root_tag, redundant
                    if to_root or (needs_sldr and (_has_sldr(root_tagset_temp) == False)):
                        print("scripts still match, trim again!")
                        continue
            elif match_region and match_script:
                if (root_tagset_temp.script == root_tagset.script) and (root_tagset_temp.region == root_tagset.region):
                    if (needs_sldr and _has_sldr(root_tagset_temp)) or needs_sldr == False:
                        print("new parent found")
                        root_tag = root_tag_trim
                        parent_path.append(root_tag)
                        if to_root == False:
                            return root_tag, redundant
                    if to_root or (needs_sldr and (_has_sldr(root_tagset_temp) == False)):
                        print("scripts and regions still match, trim again!")
                        continue
            elif root_tagset_temp == "":
                print("no tagset found that matches, idk how bc that's not how it works but this error is here anyway just in case")
                continue
        else:
            print("no more trimming, final parent is the last one we trimmed!")
            return root_tag, redundant

    root_tag, redundant = parent_loop(root_tag, root_tagset, to_root, needs_sldr, match_script, match_region)
    root_tagset = lookup(str(root_tag).replace("_", "-"), default="", matchRegions=False)
    is_root = False
    if root_tagset == tagset and redundant == False:
        is_root = True

    print("final results")
    print("is root?:" + str(is_root))
    print(root_tag)
    print(root_tagset)
    print(parent_path)
    return is_root, root_tag, root_tagset, parent_path

    


        #end results:
        # lt = LangTag. original langtag, even if it doesnt have a tagset to match
        # tagset = LangTag. original tagset, or the closest one if there is variant weirdness
        # lt_text = String. tagset in string form
        # root_tag = String. parent tag based on arguments given 
        # root_tagset = LangTag. parent tagset based on arguments given
