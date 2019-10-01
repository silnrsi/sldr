import os

def test_language(ldml, fixdata):
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    if "_" in filename:
        lname = filename[:filename.find("_")]
    else:
        lname = filename[:filename.find(".")]
    lnode = ldml.ldml.root.find('.//identity/language')
    lang = lnode.get('type')
    if lang != lname:
        if fixdata:
            lnode.set('type', lname)
            ldml.dirty = True
        else:
            assert False, "{}, unexpected language of {}".format(filename, lang)

