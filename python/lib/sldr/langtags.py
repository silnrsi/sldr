#!/usr/bin/python
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

from xml.etree import ElementTree as et
from xml.etree import ElementPath as ep
import os, re
from ldml import Ldml

class LangTag(str) :

    _hasFile = False
    _parent = None
    _isParent = False
    _fname = None

    @property
    def hasFile(self) :
        return self._hasFile

    @hasFile.setter
    def hasFile(self, val) :
        self._hasFile = val

    @property
    def parent(self) :
        return self._parent

    @parent.setter
    def parent(self, val) :
        self._parent = val

    @property
    def isParent(self) :
        return self._isParent

    @isParent.setter
    def isParent(self, val) :
        self._isParent = val

    def test_hasFile(self, dirs) :
        lname = self.replace('-', '_')
        for d in dirs :
            f = os.path.join(d, lname + '.xml')
            if os.path.exists(f) :
                self._hasFile = True
                self._fname = f
                return
            f = os.path.join(d, lname[0].lower(), lname + '.xml')
            if os.path.exists(f) :
                self._hasFile = True
                self._fname = f
                return
        self._hasFile = False

    def test_isParent(self) :
        if not self._hasFile :
            self._isParent = 2      # equivalent
            return
        l = Ldml(self._fname)
        if len(l.root) > 1 :
            self._isParent = 0      # inherit
        else :
            self._isParent = 1      # identical inherit
        

class LangTags(object) :

    def __init__(self, paths = None) :
        """ Everything is keyed by language """
        self.likelySubtags = {}
        self.suppress = {}
        self.scripts = {}
        self.territories = {}
        # keyed by langtag
        self.regions = {}
        self.tags = {}
        # keyed by region
        self.tinfo = {}
        self.paths = paths

        self.readLikelySubtags()
        self.readIana()
        self.readSupplementalData()

    def readLikelySubtags(self, fname = None) :
        """Reads the likely subtag mappings"""
        if fname is None :
            fname = os.path.join(os.path.dirname(__file__), 'likelySubtags.xml')
        doc = et.parse(fname)
        ps = doc.getroot().find('likelySubtags')
        for p in ps.findall('likelySubtag') :
            self.likelySubtags[p.get('from')] = p.get('to')

    def readIana(self, fname = None) :
        """Reads the iana registry, particularly ths suppress script info"""
        if fname is None :
            fname = os.path.join(os.path.dirname(__file__), "language-subtag-registry.txt")
        with open(fname) as f :
            currlang = None
            mode = None
            for l in f.readlines() :
                l = l.strip()
                if l.startswith("Type: ") :
                    mode = l[6:]
                elif l.startswith("Subtag: ") :
                    if mode == "language" :
                        currlang = l[8:]
                elif l.startswith("Suppress-Script: ") and currlang is not None :
                    self.suppress[currlang] = l[17:]

    def readSupplementalData(self, fname = None) :
        """Reads supplementalData.xml from CLDR to get useful structural information on LDML"""
        if fname is None :
            fname = os.path.join(os.path.dirname(__file__), 'supplementalData.xml')
        doc = et.parse(fname)
        ps = doc.getroot().find('languageData')
        for p in ps.findall('language') :
            lang = p.get('type')
            ss = self.scripts.get(lang, [])
            ts = self.territories.get(lang, [])
            if p.get('scripts') :
                ss += p.get('scripts').split(' ')
                self.scripts[lang] = ss
            if p.get('territories') :
                ts += p.get('territories').split(' ')
                self.territories[lang] = ts
        ps = doc.getroot().find('territoryInfo')
        for p in ps.findall('territory') :
            r = p.get('type')
            self.tinfo[r] = []
            self.tinfo[p.get('type')] = [l.get('type') for l in p.findall('languagePopulation')]
            for l in p.findall('languagePopulation') :
                lt = l.get('type')
                self.tinfo[r].append(lt)
                if lt not in self.regions : self.regions[lt] = []
                self.regions[lt].append(r)

    def _isregion(self, tag) :
        return (len(tag) == 2 and tag.isalpha()) or (len(tag) == 3 and tag.isdigit())

    def _get_components(self, tag) :
        temp = tag.replace("_", "-")
        res = temp.split("-")
        s = ''
        r = ''
        v = []
        # no extlang support
        l = res[0].lower()
        if len(res) > 1 and len(res[1]) == 4 :
            s = res[1].title()
            if len(res) > 2 and self._isregion(res[2]) :
                r = res[2].upper()
                if len(res) > 3 :
                    v = res[3:]
            elif len(res) > 2 :
                v = res[2:]
        elif len(res) > 1 and self._isregion(res[1]) :
            r = res[1].upper()
            if len(res) > 2 :
                v = res[2:]
        elif len(res) > 1 :
            v = res[1:]
        if r == '' and l in self.regions and len(self.regions[l]) == 1 : r = self.regions[l][0]
        if s == '' and l in self.suppress : s = self.suppress[l]
        if s == '' and l in self.scripts and len(self.scripts[l]) == 1 : s = self.scripts[l][0]
        if r == '' and s and l+"-"+s in self.regions and len(self.regions[l+"-"+s]) == 1 : r = self.regions[l+"-"+s][0]
        if l in self.likelySubtags :
            (l1, s1, r1) = self.likelySubtags[l].split('_')
            if len(v) == 0 and (s == '' or s == s1) and (r == '' or r == r1) :
                s = s1
                r = r1
        return [l, s, r] + v

    def addTag(self, tag) :
        if tag in self.tags :
            return self.tags[tag]
        else :
            lt = LangTag(tag)
            self.tags[tag] = lt
            if self.paths is not None :
                lt.test_hasFile(self.paths)
            return lt

    def _join(self, elements) :
        res = "-".join([e for e in elements if e is not None])
        res = re.sub(r'-(?=-|$)', '', res)
        return self.addTag(res)

    def get_lang(self, tag) :
        return self._get_components(tag)[0]

    def get_script(self, tag) :
        return self._get_components(tag)[1]

    def get_region(self, tag) :
        return self._get_components(tag)[2]

    def get_variants(self, tag) :
        cs = self._get_components(tag)
        if len(cs) > 3 : return cs[3:]
        else : return []
 
    def get_shortest(self, tag) :
        cs = self._get_components(tag)
        l = cs[0]
        if l in self.likelySubtags :
            o = self.likelySubtags[l].split('_')
            if o == cs : return l
        if l in self.suppress and self.suppress[l] == cs[1] : cs[1] = ''
        if l in self.territories and len(self.territories[l]) == 1 and self.territories[l][0] == cs[2] : cs[2] = ''
        return self._join(cs)

    def get_longest(self, tag) :
        return self._join(self._get_components(tag))
        
    def get_canonical(self, tag) :
        cs = self._get_components(tag)
        l = cs[0]
        if l in self.suppress and self.suppress[l] == cs[1] : cs[1] = ''
        return self._join(cs)

    def get_all_forms(self, tag) :
        cs = self._get_components(tag)
        l = cs[0]
        res = []
        b = self.addTag(l)
        if l in self.likelySubtags and cs == self.likelySubtags[l].split('_') :
            n = self._join(cs[0:2])
            if b.hasFile :
                n.parent = b
            elif n.hasFile :
                b.parent = n
            elif l in self.suppress and self.suppress[l] == cs[1] :
                n.parent = b
            else :
                b.parent = n
            n.test_isParent()
            b.test_isParent()

            r = self._join([cs[0], cs[2]])
            f = self._join(cs)
            if r.hasFile :
                f.parent = r
                r.parent = n if n.hasFile else b
            elif f.hasFile :
                r.parent = f
                f.parent = n if n.hasFile else b
            elif l in self.suppress and self.suppress[l] == cs[1] :
                f.parent = r
            else :
                r.parent = f
            r.test_isParent()
            f.test_isParent()
            res.extend([b, n, r, f])
            return res
        f = self._join(cs)
        res.append(f)
        if cs[1] and cs[2] :
            n = self._join(cs[0:2]).replace('-', '_')
            curr = f
            if n not in self.regions or cs[2] not in self.regions[n] :
                s = self._join([l, cs[2]] + (cs[3:] if len(cs) > 3 else []))
                if s.hasFile :
                    f.parent = s
                    curr = s
                elif f.hasFile :
                    s.parent = f
                elif l in self.suppress and self.suppress[l] == cs[1] :
                    f.parent = s
                    curr = s
                else :
                    s.parent = f
                s.test_isParent()
                res.append(s)
            if not curr.hasFile and curr.parent is None :
                r = self._join(cs[0:2] + (cs[3:] if len(cs) > 3 else []))
                if r.hasFile :
                    curr.parent = r
                    res.append(r)
                elif b.hasFile :
                    curr.parent = b
                    res.append(b)
                curr.test_isParent()
        f.test_isParent()
        return res

    def get_all_equivalences(self, tag, history) :
        def addstar(x) :
            return "*"+x if x.hasFile else x
        def findequivs(n, a, level = 2) :
            return filter(lambda x: x.isParent == level and x.parent is n, a)
        def outchildren(n, a) :
            res = addstar(n) 
            for s in findequivs(n, a) :
                res += " = " 
                a.remove(s)
                res += outchildren(s, a)
            for s in findequivs(n, a, level = 1) :
                res += " | " 
                a.remove(s)
                res += outchildren(s, a)
            return res # if ' ' in res or res[0] == '*' else ""
        ress = []
        a = set(t.get_all_forms(tag))
        if any([r not in history for r in a]) :
            top = set(filter(lambda x : x.parent is None, a))
            r = a - top
            for n in top :
                temp = r
                res = outchildren(n, temp)
                if res : ress.append(res)
                for s in findequivs(n, temp, level = 0) :
                    res = outchildren(s, temp)
                    res += " > " + addstar(n)
                    if res : ress.append(res)
        history.update(a)
        return ress
    

if __name__ == '__main__' :
    import sys
    indir = ['sldr']
    t = LangTags(paths=indir)
    alltags = set()
    allres = []
    for l in sorted([sys.argv[1]] if len(sys.argv) > 1 else t.regions.keys()) :
        for s in t.regions[l] :
            allres.extend(t.get_all_equivalences(l+"-"+s, alltags))
    alllocales = set()
    if len(sys.argv) < 2 :
        for d in indir :
            for l in os.listdir(d) :
                if l.endswith('.xml') :
                    alllocales.add(l[:-4])
                elif os.path.isdir(os.path.join(d, l)) :
                    for s in os.listdir(os.path.join(d, l)) :
                        if s.endswith('.xml') :
                            alllocales.add(s[:-4])
        for l in alllocales - alltags :
            allres.extend(t.get_all_equivalences(l, alltags))
        print "\n".join(sorted(allres, key=lambda x : x.replace('*','')))
    else :
        print "\n".join(allres)
