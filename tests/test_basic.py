import os
from langtag import langtag, lookup

def notest_language(ldml, fixdata):
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

idblocks = {
    'language': 'lang',
    'script': 'script',
    'territory': 'region'
}
def test_identity(ldml, langid, fixdata):
    """ Test and fix the identity block wrt language, script, territory, variant """
    lt = langtag(os.path.splitext(os.path.basename(langid))[0])
    if lt.lang is None:     # e.g. Root (ends up in script)
        return
    ident = ldml.ldml.find("identity")
    if ident is None:
        if fixdata:
            ident = ldml.ldml.ensure_path("identity")[0]
            ldml.dirty = True
        else:
            assert False, "{} missing identity block".format(langid)
    for k, v in idblocks.items():
        val = getattr(lt, v, None)
        inf = ldml.ldml.find(k, ident)
        if val is None:
            if inf is not None:
                if fixdata:
                    ldml.ldml.remove_path("identity/{}".format(k))
                    ldml.dirty = True
                else:
                    assert False, "Unexpected {} of {} in identity block in {}".format(k, inf.get("type"), langid)
        elif inf is None:
            if fixdata:
                inf = ldml.ldml.ensure_path('identity/{}[@type="{}"]'.format(k, val))[0] ###
                ldml.dirty = True
            else:
                assert False, "{} missing {} in identity block".format(langid, k)
        elif val != inf.get("type"):
            if fixdata:
                inf.set("type", val)
                ldml.dirty = True
            else:
                assert False, "{} type {} does not match tag in {}".format(k, val, langid)
    var = "-".join(sorted(lt.vars)) if lt.vars is not None else ""
    if lt.ns is not None:
        for k, v in sorted(lt.ns.items()):
            var += "-".join([k] + v)
    inf = ldml.ldml.find("variant", ident)
    if var == "":
        if inf is not None:
            if fixdata:
                ldml.ldml.remove_path("identity/variant")
                ldml.dirty = True
            else:
                assert False, "Unexpected variant of {} in identity block in {}".format(inf.get("type"), langid)
    elif inf is None:
        if fixdata:
            inf = ldml.ldml.ensure_path('identity/variant[@type="{}"]'.format(var))[0] ###
            ldml.dirty = True
        else:
            assert False, "identity/variant missing in {}".format(langid)
    elif var != inf.get("type").lower():
        if fixdata:
            inf.set("type", var)
            ldml.dirty = True
        else:
            assert False, "identity/variant type {} does not match tag in {}".format(inf.get("type"), langid)
    # Now fill in the sil:identity from the langtag
    if lt.script is None or lt.region is None:
        tagset = lookup(str(lt).replace("_", "-"), default="", matchRegions=True)
        if fixdata:
            assert tagset != "", "Unknown langtag {}".format(lt)
        silid = ldml.ldml.find("identity/special/sil:identity")
        if silid is None:
            if fixdata:
                silid = ldml.ldml.ensure_path("identity/special/sil:identity")[0] ###
                ldml.dirty = True
        if tagset != "" and silid is not None:
            for k, v in {"script": "script", "defaultRegion": "region"}.items():
                if getattr(lt, v, None) is None:
                    silval = getattr(tagset, v)
                    silidval = silid.get(k, "")
                    if silval != silidval:
                        if fixdata:
                            silid.set(k, silval)
                            ldml.dirty = True
                        else:
                            assert silidval == "", "sil:identity {} {} is not {} in {}".format(k, silidval, silval, langid)
