import os
from langtag import langtag

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
                inf = ldml.ldml.ensure_path('identity/{}[@type="{}"]'.format(k, val))
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
            inf = ldml.ldml.ensure_path('identity/variant[@type="{}"]'.format(var))
            ldml.dirty = True
        else:
            assert False, "identity/variant missing in {}".format(langid)
    elif var != inf.get("type").lower():
        if fixdata:
            inf.set("type", var)
            ldml.dirty = True
        else:
            assert False, "identity/variant type {} does not match tag in {}".format(inf.get("type"), langid)

