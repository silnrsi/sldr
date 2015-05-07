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

class LangTags(object) :

    def __init__(self) :
        """ Everything is keyed by language """
        self.likelySubtags = {}
        self.suppress = {}
        self.scripts = {}
        self.territories = {}
        # keyed by langtag
        self.regions = {}
        # keyed by region
        self.tinfo = {}

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
        # no extlang support yet
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

    def _join(self, elements) :
        res = "-".join([e for e in elements if e is not None])
        return re.sub(r'-(?=-|$)', '', res)

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
        if l in self.likelySubtags :
            o = self.likelySubtags[l].split('_')
            if o == cs :
                res.append(l)
                res.append(self._join(cs[0:2]))
                res.append(self._join(cs))
                res.append(self._join([cs[0], cs[2]]))
                return res
        res.append(self._join(cs))
        if l in self.territories and len(self.territories[l]) == 1 and self.territories[l][0] == cs[2] :
            res.append(self._join(cs[0:2] + (cs[3:] if len(cs) > 3 else [])))
        if l in self.suppress and self.suppress[l] == cs[1] :
            res.append(self._join([l, cs[2]] + (cs[3:] if len(cs) > 3 else [])))
        return res

if __name__ == '__main__' :
    t = LangTags()
    alltags = set()
    for l in sorted(t.regions.keys()) :
        for s in t.regions[l] :
            r = t.get_all_forms(l+"-"+s)
            if not any([a in alltags for a in r]) :
                print " = ".join(t.get_all_forms(l+"-"+s))
            alltags.update(a)
