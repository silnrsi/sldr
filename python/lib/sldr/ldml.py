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

from __future__ import print_function
from xml.etree import ElementTree as et
from xml.etree import ElementPath as ep
import re, os, codecs
import xml.parsers.expat
from functools import reduce
from six import string_types
from .py3xmlparser import XMLParser, TreeBuilder

_elementprotect = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;' }
_attribprotect = dict(_elementprotect)
_attribprotect['"'] = '&quot;'

class ETWriter(object):
    """ General purpose ElementTree pretty printer complete with options for attribute order
        beyond simple sorting, and which elements should use cdata """

    nscount = 0
    indent = "\t"

    def __init__(self, et, namespaces = None, attributeOrder = {}, takesCData = set()):
        self.root = et
        if namespaces is not None:
            self.namespaces = namespaces
        if self.namespaces is None:
            self.namespaces = {}
        self.attributeOrder = attributeOrder
        self.takesCData = takesCData

    def _localisens(self, tag):
        if tag[0] == '{':
            ns, localname = tag[1:].split('}', 1)
            qname = self.namespaces.get(ns, '')
            if qname:
                return ('{}:{}'.format(qname, localname), qname, ns)
            else:
                self.nscount += 1
                return (localname, 'ns_' + str(self.nscount), ns)
        else:
            return (tag, None, None)

    def _protect(self, txt, base=_attribprotect):
        return re.sub(u'['+u"".join(base.keys())+u"]", lambda m: base[m.group(0)], txt)

    def _nsprotectattribs(self, attribs, localattribs, namespaces):
        if attribs is not None:
            for k, v in attribs.items():
                (lt, lq, lns) = self._localisens(k)
                if lns and lns not in namespaces:
                    namespaces[lns] = lq
                    localattribs['xmlns:'+lq] = lns
                localattribs[lt] = v
        
    def _sortedattrs(self, n, attribs=None):
        def getorder(x):
            return self.attributeOrder.get(n.tag, {}).get(x, self.maxAts)
        return sorted((attribs if attribs is not None else n.keys()), key=lambda x:(getorder(x), x))

    def serialize_xml(self, write, base = None, indent = '', topns = True, namespaces = {}):
        """Output the object using write() in a normalised way:
                topns if set puts all namespaces in root element else put them as low as possible"""
        if base is None:
            base = self.root
            write('<?xml version="1.0" encoding="utf-8"?>\n')
        (tag, q, ns) = self._localisens(base.tag)
        localattribs = {}
        if ns and ns not in namespaces:
            namespaces[ns] = q
            localattribs['xmlns:'+q] = ns
        if topns:
            if base == self.root:
                for n,q in self.namespaces.items():
                    localattribs['xmlns:'+q] = n
                    namespaces[n] = q
        else:
            for c in base:
                (lt, lq, lns) = self._localisens(c.tag)
                if lns and lns not in namespaces:
                    namespaces[lns] = q
                    localattribs['xmlns:'+lq] = lns
        self._nsprotectattribs(getattr(base, 'attrib', None), localattribs, namespaces)
        for c in getattr(base, 'comments', []):
            write(u'{}<!--{}-->\n'.format(indent, c))
        write(u'{}<{}'.format(indent, tag))
        if len(localattribs):
            def getorder(x):
                return self.attributeOrder.get(tag, {}).get(x, self.maxAts)
            def cmpattrib(x, y):
                return cmp(getorder(x), getorder(y)) or cmp(x, y)
            for k in self._sortedattrs(base, localattribs):
                write(u' {}="{}"'.format(self._localisens(k)[0], self._protect(localattribs[k])))
        if len(base):
            write('>\n')
            for b in base:
                self.serialize_xml(write, base=b, indent=indent + self.indent, topns=topns, namespaces=namespaces.copy())
            write('{}</{}>\n'.format(indent, tag))
        elif base.text:
            if tag not in self.takesCData:
                t = self._protect(base.text.replace('\n', '\n' + indent), base=_elementprotect)
            else:
                t = "<![CDATA[\n\t" + indent + base.text.replace('\n', '\n\t' + indent) + "\n" + indent + "]]>"
            write(u'>{}</{}>\n'.format(t, tag))
        else:
            write('/>\n')
        for c in getattr(base, 'commentsafter', []):
            write(u'{}<!--{}-->\n'.format(indent, c))

    def add_namespace(self, q, ns):
        if ns in self.namespaces: return self.namespaces[ns]
        self.namespaces[ns] = q
        return q

    def addnode(self, parent, tag, **kw):
        return et.SubElement(parent, tag, **kw)

    def unify_path(self, path, base=None, draft=None, alt=None, matchdraft=None):
        '''Path contains a list of tags or (tag, attrs) to search in succession'''
        if base is None:
            base = self.root
        newcurr = [base]
        if matchdraft is not None:
            realalt = self.alt(alt)
        for i, p in enumerate(path):
            curr = newcurr
            newcurr = []
            if isinstance(p, tuple):
                tag, attrs = p
            else:
                tag, attrs = (p, {})
            for job in curr:
                for c in job:
                    if c.tag != tag:
                        continue
                    for k, v in attrs.items():
                        if c.get(k, '') != v:
                            break
                    else:
                        newcurr.append(c)
            if matchdraft is not None and i == len(path)-1:
                temp = newcurr
                newcurr = []
                # matchdraft == 'draft' (find all alternates with given draf, including not alternate)
                # matchdraft == 'alt' (find all alternates with given alt)
                # matchdraft == 'both' (find all alternates with given alt and draft)
                for c in temp:
                    if matchdraft == 'draft' and c.get('draft', '') == draft:
                        newcurr.append(c)
                    if not hasattr(c, 'alternates'):
                        continue
                    if matchdraft == 'draft':
                        tests = c.alternates.keys()
                    else:
                        tests = [realalt]
                    for r in (c.alternates.get(t, None) for t in tests):
                        if r is None:
                            continue
                        elif matchdraft == 'alt' or r.get('draft', '') == draft:
                            newcurr.append(r)
            if not len(newcurr):
                job = curr[0]
                if draft is not None:
                    attrs['draft'] = draft
                se = self.addnode(job, tag, attrib=attrs, alt=alt)
                newcurr.append(se)
        return newcurr

    def ensure_path(self, path, base=None, draft=None, alt=None, matchdraft=None):
        if path.startswith("/"):
            raise SyntaxError
        steps = []
        for s in path.split("/"):
            parts = re.split(r"\[(.*?)\]", s)
            tag = parts.pop(0)
            tag = self._reverselocalns(tag)
            if not len(parts):
                steps.append(tag)
                continue
            attrs = {}
            for p in parts:
                if not len(p): continue
                (k, v) = p.replace(' ','').split("=")
                if k.startswith("@") and v[0] in '"\'':
                    attrs[k[1:]] = v[1:-1]
            steps.append((tag, attrs))
        return self.unify_path(steps, base=base, draft=draft, alt=alt, matchdraft=matchdraft)

    def _reverselocalns(self, tag):
        '''Convert ns:tag -> {fullns}tag'''
        nsi = tag.find(":")
        if nsi > 0:
            ns = tag[:nsi]
            for k, v in self.namespaces.items():
                if ns == v:
                    tag = "{" + k + "}" + tag[nsi+1:]
                    break
        return tag

    def subelement(self, parent, tag, **k):
        '''Create a new SubElement and do localns replacement as in ns:tag -> {fullns}tag'''
        tag = self._reverselocalns(tag)
        return et.SubElement(parent, tag, **k)


def etwrite(et, write, topns = True, namespaces = None):
    if namespaces is None: namespaces = {}
    base = ETWriter(et, namespaces)
    base.serialize_xml(write, topns = topns)
    
_alldrafts = ('approved', 'contributed', 'provisional', 'unconfirmed', 'tentative', 'generated', 'suspect')
draftratings = dict(map(lambda x: (x[1], x[0]), enumerate(_alldrafts)))

class _arrayDict(dict):
    def set(self, k, v):
        if k not in self:
            self[k] = []
        self[k].append(v)

    def pop(self, k, v=None):
        if k not in self: return v
        res = self[k].pop()
        if not len(self[k]): del self[k]
        return res

    def remove(self, k, v):
        if k not in self: return
        self[k].remove(v)
        if not len(self[k]): del self[k]
        

class _minhash(object):
    _maxbits = 56
    _bits = 4
    _mask = 0xFFFFFFFFFFFFFFFF

    def __init__(self, hasher = hash, nominhash = True):
        self.minhash = None if nominhash else (1 << self._maxbits) - 1
        self.hashed = 0
        self.hasher = hasher

    def __eq__(self, other):
        return self.hashed == other.hashed and self.minhash == other.minhash

    def __repr__(self):
        return "<{} {:0X}>".format(type(self), self.hashed)

    def __hash__(self):
        return self.hashed

    def update(self, *vec):
        h = map(self.hasher, vec)
        if self.minhash is not None: map(self._minhashupdate, h)
        self.hashed = reduce(lambda x,y:x * 1000003 + y, h, self.hashed) & self._mask

    def merge(self, aminh):
        if self.minhash is not None and aminh.minhash is not None: self._minhashupdate(aminh.minhash)
        self.hashed = (self.hashed * 1000003 + aminh.hashed) & self._mask

    def _minhashupdate(self, ahash):
        x = (1 << self._bits) - 1
        for i in range(self._maxbits / self._bits):
            if (ahash & x) < (self.minhash & x):
                self.minhash = (self.minhash & ~x) | (ahash & x)
            x <<= self._bits

    def hamming(self, amin):
        x = (1 << self._bits) - 1
        res = 0
        for i in range(self._maxbits / self._bits):
            if (self.minhash & x) != (amin & x): res += 1
            x <<= self._bits
        return res


class Ldml(ETWriter):
    takesCData = set(('cr',))
    silns = "urn://www.sil.org/ldml/0.1"
    use_draft = None

    @classmethod
    def ReadMetadata(cls, fname = None):
        """Reads supplementalMetadata.xml from CLDR to get useful structural information on LDML"""
        cls.ReadDTD()
        if fname is None:
            fname = os.path.join(os.path.dirname(__file__), 'supplementalMetadata.xml')
        doc = et.parse(fname)
        base = doc.getroot().find('metadata')
        # l = base.findtext('attributeOrder').split()
        # cls.attributeOrder = dict(zip(l, range(1, len(l) + 1)))
        # l = base.findtext('elementOrder').split()
        # cls.elementOrder = dict(zip(l, range(1, len(l) + 1)))
        # cls.maxEls = len(cls.elementOrder) + 1
        # cls.maxAts = len(cls.attributeOrder) + 1
        cls.variables = {}
        for v in base.findall('validity/variable'):
            name = v.get('id')[1:]
            if v.get('type') == 'choice':
                cls.variables[name] = v.text.split()
            elif v.text:
                cls.variables[name] = v.text.strip()
        cls.blocks = set(base.find('blocking/blockingItems').get('elements', '').split())
        cls.nonkeyContexts = {}         # cls.nonkeyContexts[element] = set(attributes)
        cls.keyContexts = {}            # cls.keyContexts[element] = set(attributes)
        cls.keys = set()
        for e in base.findall('distinguishing/distinguishingItems'):
            if 'elements' in e.attrib:
                if e.get('exclude', 'false') == 'true':
                    target = cls.nonkeyContexts
                else:
                    target = cls.keyContexts
                localset = set(e.get('attributes').split())
                for a in e.get('elements').split():
                    if a in target:
                        target[a].update(localset)
                    else:
                        target[a] = set(localset)
            else:
                cls.keys.update(e.get('attributes').split())
        cls.keyContexts['{'+cls.silns+'}matched-pair'] = set(['open', 'close'])
        cls.keyContexts['{'+cls.silns+'}quotation'] = set(['level'])

    @classmethod
    def ReadSupplementalData(cls, fname = None):
        """Reads supplementalData.xml from CLDR to get useful structural information on LDML"""
        if fname is None:
            fname = os.path.join(os.path.dirname(__file__), 'supplementalData.xml')
        doc = et.parse(fname)
        cls.parentLocales = {}
        ps = doc.getroot().find('parentLocales')
        for p in ps.findall('parentLocale'):
            parent = p.get('parent')
            for l in p.get('locales').split():
                if l in cls.parentLocales:
                    cls.parentLocales[l].append(parent)
                else:
                    cls.parentLocales[l] = [parent]
        cls.languageInfo = {}
        ps = doc.getroot().find('languageData')
        for p in ps.findall('language'):
            ss = []; ts = []
            if p.get('type') in cls.languageInfo:
                ss, ts = cls.languageInfo[p.get('type')]
            if p.get('scripts'):
                if p.get('alt') == 'secondary':
                    ss += p.get('scripts').split(' ')
                else:
                    ss = p.get('scripts').split(' ') + ss
            if p.get('territories'):
                ts += p.get('territories').split(' ')
            cls.languageInfo[p.get('type')] = [ss, ts]

    @classmethod
    def ReadLikelySubtags(cls, fname = None):
        """Reads the likely subtag mappings"""
        if fname is None:
            fname = os.path.join(os.path.dirname(__file__), 'likelySubtags.xml')
        doc = et.parse(fname)
        cls.likelySubtags = {}
        ps = doc.getroot().find('likelySubtags')
        for p in ps.findall('likelySubtag'):
            cls.likelySubtags[p.get('from')] = p.get('to')

    @classmethod
    def ReadDTD(cls, fname = None):
        """Reads LDML DTD to get element and attribute orders"""
        if fname is None:
            fname = os.path.join(os.path.dirname(__file__), 'ldml.dtd')
        elementCount = [0]
        cls.attributeOrder = {}
        cls.elementOrder = {}
        attribCount = {}
        def elementDecl(name, model):
            elementCount[0] += 1
            cls.elementOrder[name] = elementCount[0]
            cls.attributeOrder[name] = {}
            attribCount[name] = 0
        def attlistDecl(elname, attname, xmltype, default, required):
            attribCount[elname] += 1
            cls.attributeOrder[elname][attname] = attribCount[elname]
        parser = xml.parsers.expat.ParserCreate()
        parser.ElementDeclHandler = elementDecl
        parser.AttlistDeclHandler = attlistDecl
        with open(fname) as f :
            ldmltext = "".join(f.readlines())
        parsetext = "<?xml version='1.0'?>\n<!DOCTYPE LDML [\n" + ldmltext + "]>\n"
        parser.Parse(parsetext)
        cls.maxEls = elementCount[0] + 1
        cls.maxAts = max(attribCount.values()) + 1

    def __init__(self, fname, usedrafts=True):
        if not hasattr(self, 'elementOrder'):
            self.__class__.ReadMetadata()
        self.namespaces = {}
        self.namespaces[self.silns] = 'sil'
        self.useDrafts = usedrafts
        curr = None
        comments = []

        if fname is None:
            self.root = et.Element('ldml')
            self.root.document = self
            self.default_draft = 'unconfirmed'
            return
        elif isinstance(fname, string_types):
            self.fname = fname
            fh = open(self.fname, 'rb')     # expat does utf-8 decoding itself. Don't do it twice
        else:
            fh = fname
        if hasattr(et, '_Element_Py'):
            tb = TreeBuilder(element_factory=et._Element_Py)
        else:
            tb = TreeBuilder()
        parser = XMLParser(target=tb, encoding="UTF-8")
        def doComment(data):
            # resubmit as new start tag=!-- and sort out in main loop
            parser.parser.StartElementHandler("!--", ('text', data))
            parser.parser.EndElementHandler("!--")
        parser.parser.CommentHandler = doComment
        for event, elem in et.iterparse(fh, events=('start', 'start-ns', 'end'), parser=parser):
            if event == 'start-ns':
                self.namespaces[elem[1]] = elem[0]
            elif event == 'start':
                elem.document = self
                if elem.tag == '!--':
                    comments.append(elem.get('text'))
                else:
                    if len(comments):
                        elem.comments = comments
                        comments = []
                    if curr is not None:
                        elem.parent = curr
                    else:
                        self.root = elem
                    curr = elem
            elif elem.tag == '!--':
                if curr is not None:
                    curr.remove(elem)
            else:
                if len(comments) and len(elem):
                    elem[-1].commentsafter = comments
                    comments = []
                curr = getattr(elem, 'parent', None)
        fh.close()
        self.analyse()
        self.normalise(self.root, usedrafts=usedrafts)

    def copynode(self, n, parent=None):
        res = n.copy()
        for a in ('contentHash', 'attrHash', 'comments', 'commentsafter', 'parent', 'document'):
            if hasattr(n, a):
                setattr(res, a, getattr(n, a, None))
        if parent is not None:
            res.parent = parent
        return res

    def addnode(self, parent, tag, attrib={}, alt=None, **attribs):
        attrib = dict((k,v) for k,v in attrib.items() if v) # filter @x=""
        attrib.update(attribs)
        tag = self._reverselocalns(tag)
        e = parent.makeelement(tag, attrib)
        e.parent = parent
        e.document = parent.document
        if self.useDrafts:
            alt = self.alt(alt)
            if 'draft' not in e.attrib and self.use_draft is not None:
                e.set('draft', self.use_draft)
            self._calc_hashes(e, self.useDrafts)
            equivs = [x for x in parent if x.attrHash == e.attrHash]
            if len(equivs):
                if 'alt' not in e.attrib:
                    e.set('alt', alt)
                return self._add_alt_leaf(equivs[0], e, default=e.get('draft', None), leaf=True, alt=alt)
        parent.append(e)
        return e

    def _add_alt_leaf(self, target, origin, default='unconfirmed', leaf=True, alt=None):
        odraft = self.get_draft(origin, default)
        res = origin
        if leaf:
            tdraft = self.get_draft(target, default)
            if odraft < tdraft:
                self._promote(target, origin, alt=alt)
                (origin, target) = (target, origin)
                res = target
            if not hasattr(target, 'alternates'):
                target.alternates = {}
            elif alt in target.alternates:
                v = target.alternates[alt]
                if self.get_draft(v, default) < odraft:
                    return v
            target.alternates[alt] = origin
            if hasattr(origin, 'alternates'):
                for k, v in origin.alternates.items():
                    if k not in target.alternates or \
                            (self.get_draft(v, default) > self.get_draft(target.alternates[k], default)):
                        target.alternates[k] = v
        elif hasattr(target, 'alternates') and alt in target.alternates:
            v = target.alternates[alt]
            if self.get_draft(v, default) >= odraft:
                del target.alternates[alt]
        return res
            
    def _find_best(self, node, threshold=len(draftratings), alt=None):
        maxr = len(draftratings)
        if not hasattr(node, 'alternates'):
            return None
        res = None
        if alt is not None:
            bestalt = node.alternates.get(alt, None)
            if bestalt is not None:
                bestalt = draftratings.get(bestalt.get('draft', None), maxr)
            else:
                bestalt = None
        else:
            bestalt = None

        for k, v in node.alternates.items():
            d = draftratings.get(v.get('draft', self.use_draft), maxr)
            if d < threshold:
                res = k
                threshold = d
        if bestalt is not None and threshold == bestalt:
            res = alt
        return res

    def _promote(self, old, new, alt=None):
        nalt = getattr(new, 'alternates', None)
        oalt = getattr(old, 'alternates', {})
        if nalt is not None:
            old.alternates = nalt
        if oalt is not None:
            new.alternates = oalt
        if alt is None:
            alt = new.get('alt', None)
        elif 'alt' in new.attrib and new.attrib['alt'] in new.alternates:
            del new.alternates[new.attrib['alt']]
        new.alternates[alt] = old
        if 'alt' in new.attrib:
            del new.attrib['alt']
            old.set('alt', alt)
        for i, e in enumerate(old.parent):
            if id(e) == id(old):
                break
        old.parent.insert(i, new)
        old.parent.remove(old)
        return new

    def change_draft(self, node, draft, alt=None):
        alt = self.alt(alt)
        best = self._find_best(node, draftratings.get(draft, len(draftratings)), alt=alt)
        node.set('draft', draft)
        if best is None:
            return node
        elif alt is None:
            alt = best
        return self._promote(node, node.alternates[best], alt=alt)

    def ensure_path(self, path, base=None, draft=None, alt=None, matchdraft=None):
        draft = self.use_draft if draft is None else draft
        return super(Ldml, self).ensure_path(path, base=base,
                        draft=draft, alt=alt, matchdraft=matchdraft)

    def find(self, path, elem=None):
        def nstons(m):
            for (k, v) in self.namespaces.items():
                if m.group(1) == v:
                    return "{"+k+"}"
            return ""

        if elem is None:
            elem = self.root
        path = re.sub(r"([a-z0-9]+):", nstons, path)
        return elem.find(path)

    def get_parent_locales(self, name):
        if not hasattr(self, 'parentLocales'):
            self.__class__.ReadSupplementalData()
        fall = self.root.find('fallback')
        if fall is not None:
            return fall.split()
        elif name in self.parentLocales:
            return self.parentLocales[name]
        else:
            return []

    def normalise(self, base=None, addguids=True, usedrafts=False):
        """Normalise according to LDML rules"""
        _digits = set('0123456789.')
        if base is None:
            base = self.root
        if len(base):
            for b in base:
                self.normalise(b, addguids=addguids, usedrafts=usedrafts)
            def getorder(x):
                return self.attributeOrder.get(base.tag, {}).get(x, self.maxAts)
            def cmpat(x, y):
                return cmp(getorder(x), getorder(y)) or cmp(x, y)
            def keyel(x):
                xl = self._sortedattrs(x)
                res = [self.elementOrder.get(x.tag, self.maxEls), x.tag]
                for k, a in ((l, x.get(l)) for l in xl):
                    if k == 'id' and all(q in _digits for q in a):
                        res += (k, float(a))
                    else:
                        res += (k, a)
                return res
            def cmpel(x, y):   # order by elementOrder and within that attributes in attributeOrder
                res = cmp(self.elementOrder.get(x.tag, self.maxEls), self.elementOrder.get(y.tag, self.maxEls) or cmp(x.tag, y.tag))
                if res != 0: return res
                xl = self._sortedattrs(x)
                yl = self._sortedattrs(y)
                for i in range(len(xl)):
                    if i >= len(yl): return -1
                    res = cmp(xl[i], yl[i])
                    if res != 0: return res
                    a = x.get(xl[i])
                    b = y.get(yl[i])
                    if xl[i] == 'id' and all(q in _digits for q in a) and all(q in _digits for q in b):
                        res = cmp(float(a), float(b))
                    else:
                        res = cmp(a, b)
                    if res != 0: return res
                if len(yl) > len(xl): return 1
                return 0
            children = sorted(base, key=keyel)              # if base.tag not in self.blocks else list(base)
            base[:] = children
        if base.text:
            t = base.text.strip()
            base.text = re.sub(r'\s*\n\s*', '\n', t)       # content hash has text in lines
        base.tail = None
        if usedrafts or addguids:
            self._calc_hashes(base, usedrafts=usedrafts)
        if usedrafts:                                       # pack up all alternates
            temp = {}
            for c in base:
                a = c.get('alt', None)
                if a is None or a.find("proposed") == -1:
                    temp[c.attrHash] = c
            tbase = list(base)
            for c in tbase:
                a = c.get('alt', '')
                if a.find("proposed") != -1 and c.attrHash in temp:
                    #a = re.sub(r"-?proposed.*$", "", a)
                    t = temp[c.attrHash]
                    if not hasattr(t, 'alternates'):
                        t.alternates = {}
                    t.alternates[a] = c
                    base.remove(c)

    def analyse(self):
        identity = self.root.find('./identity/special/{' + self.silns + '}identity')
        if identity is not None:
            self.default_draft = identity.get('draft', 'unconfirmed')
            self.uid = identity.get('uid', None)
        else:
            self.default_draft = 'unconfirmed'
            self.uid = None

    def _calc_hashes(self, base, usedrafts=False):
        base.contentHash = _minhash(nominhash = True)
        for b in base:
            base.contentHash.merge(b.contentHash)
        if base.text: base.contentHash.update(*(base.text.split("\n")))
        distkeys = set(self.keys)
        if base.tag in self.nonkeyContexts:
            distkeys -= self.nonkeyContexts[base.tag]
        if base.tag in self.keyContexts:
            distkeys |= self.keyContexts[base.tag]
        if usedrafts:
            distkeys.discard('draft')
        base.attrHash = _minhash(nominhash = True)
        base.attrHash.update(base.tag)                      # keying hash has tag
        for k, v in sorted(base.items()):                      # any consistent order is fine
            if usedrafts and k == 'alt' and v.find("proposed") != -1:
                val = re.sub(r"-?proposed.*$", "", v)
                if len(val):
                    base.attrHash.update(k, val)
            elif k in distkeys:
                base.attrHash.update(k, v)        # keying hash has key attributes
            elif not usedrafts or (k != 'draft' and k != 'alt' and k != '{'+self.silns+'}alias'):
                base.contentHash.update(k, v)     # content hash has non key attributes
        base.contentHash.merge(base.attrHash)               #   and keying hash

    def serialize_xml(self, write, base = None, indent = '', topns = True, namespaces = {}):
        if self.uid is not None:
            self.ensure_path('identity/special/sil:identity[@uid="{}"]'.format(self.uid))
        if self.useDrafts:
            n = base if base is not None else self.root
            draft = n.get('draft', '')
            if draft and (len(n) or draft == self.default_draft):
                del n.attrib['draft']
            offset = 0
            alt = n.get('alt', '')
            for (i, c) in enumerate(list(n)):
                if not hasattr(c, 'alternates'): continue
                for a in sorted(c.alternates.keys()):
                    c.alternates[a].set('alt', (alt+"-"+a if alt else a))
                    offset += 1
                    n.insert(i + offset, c.alternates[a])
                    c.alternates[a].tempnode = True
        super(Ldml, self).serialize_xml(write, base, indent, topns, namespaces)
        if self.useDrafts:
            n = base if base is not None else self.root
            for c in list(n):
                if hasattr(c, 'tempnode') and c.tempnode:
                    n.remove(c)

    def get_draft(self, e, default=None):
        ldraft = e.get('draft', None) if e is not None else None
        if ldraft is not None: return draftratings.get(ldraft, 5)
        return draftratings.get(default, self.default_draft)

    def overlay(self, other, usedrafts=False, this=None):
        """Add missing information in self from other. Honours @draft attributes"""
        if this == None: this = self.root
        other = getattr(other, 'root', other)
        for o in other:
            # simple if for now, if more use a dict
            if o.tag == '{'+self.silns+'}external-resources':
                self._overlay_external_resources(o, this, usedrafts)
            else:
                self._overlay_child(o, this, usedrafts)

    def _overlay_child(self, o, this, usedrafts):
        addme = True
        for t in filter(lambda x: x.attrHash == o.attrHash, this):
            addme = False
            if o.contentHash != t.contentHash:
                if o.tag not in self.blocks:
                    self.overlay(o, usedrafts=usedrafts, this=t)
                elif usedrafts:
                    self._merge_leaf(other, t, o)
            break  # only do one alignment
        if addme and (o.tag != "alias" or not len(this)):  # alias in effect turns it into blocking
            this.append(o)

    def _overlay_external_resources(self, other, this, usedrafts):
        """Handle sil:font fallback mechanism"""
        silfonttag = '{'+self.silns+'}font'
        fonts = []
        this = filter(lambda x: x.attrHash == o.attrHash, this)[0]
        for t in list(this):
            if t.tag == silfonttag:
                fonts.append(t)
                this.remove(t)
        for o in other:
            if o.tag == silfonttag:
                types = o.get('types', '').split(' ')
                if not len(types):
                    types = ['default']
                for t in types:
                    if t == 'default':
                        fonts = []
                        break
                    else:
                        for f in fonts:
                            tt = f.get('types', 'default').split(' ')
                            if t in tt:
                                f.set('types', " ".join(filter(lambda x: x != t, tt)))
                        fonts = filter(lambda x: x.get('types', '') != '', fonts)
                this.append(o)
            else:
                self._overlay_child(o, this, usedrafts)
        for f in fonts:
            this.append(f)

    def _merge_leaf(self, other, b, o):
        """Handle @draft and @alt"""
        if not hasattr(o, 'alternates'): return
        if hasattr(b, 'alternates'):
            for (k, v) in o.items():
                if k not in b.alternates: b.alternates[k] = v
        else:
            b.alternates = o.alternates
            
    def resolve_aliases(self, this=None, _cache=None):
        if this is None: this = self.root
        hasalias = False
        if _cache is None:
            _cache = set()
        for (i, c) in enumerate(list(this)):
            if c.tag == 'alias':
                v = c.get('path', None)
                if v is None: continue
                this.remove(c)
                count = 1
                for res in this.findall(v + "/*"):
                    res = self.copynode(res, parent=this)
                    # res.set('{'+self.silns+'}alias', "1")
                    # self.namespaces[self.silns] = 'sil'
                    if v in _cache:
                        print("Alias loop discovered: %s in %s" % (v, self.fname))
                        return True
                    _cache.add(v)
                    self.resolve_aliases(res, _cache)
                    _cache.remove(v)
                    this.insert(i+count, res)
                    count += 1
                hasalias = True
            else:
                hasalias |= self.resolve_aliases(c)
        if hasalias and self.useDrafts:
            self._calc_hashes(this)
            return True
        return False

    def alt(self, *a):
        proposed = a[0] if len(a) > 0 and a[0] else 'proposed'
        res = ((a[1] + "-") if len(a) > 1 and a[1] else "") + proposed
        if hasattr(self, 'uid') and self.uid is not None:
            return res + "-" + str(self.uid)
        else:
            return res
        
    def difference(self, other, this=None):
        """Strip out everything that is in other, from self, so long as the values are the same."""
        if this == None: this = self.root
        other = getattr(other, 'root', other)
        # if empty elements, test .text and all the attributes
        if not len(other) and not len(this):
            return (other.contentHash == this.contentHash)
        for o in other:
            for t in filter(lambda x: x.attrHash == o.attrHash, this):
                if o.contentHash == t.contentHash or (o.tag not in self.blocks and self.difference(o, this=t)):
                    if hasattr(t, 'alternates') and hasattr(o, 'alternates'):
                        for (k, v) in o.alternates:
                            if k in t.alternates and v.contentHash == t.alternates[k].contentHash:
                                del t.alternates[k]
                        if len(t.alternates) == 0:
                            this.remove(t)
                    else:
                        this.remove(t)
                break
        return not len(this) and (not this.text or this.text == other.text)

    def _align(self, this, other, base):
        """Internal method to merge() that aligns elements in base and other to this and
           records the results in this. O(7N)"""
        olist = dict(map(lambda x: (x.contentHash, x), other)) if other is not None else {}
        blist = dict(map(lambda x: (x.contentHash, x), base)) if base is not None else {}
        for t in list(this):
            t.mergeOther = olist.get(t.contentHash, None)
            t.mergeBase = blist.get(t.contentHash, None)
            if t.mergeOther is not None:
                del olist[t.contentHash]
                if t.mergeBase is not None:
                    del blist[t.contentHash]
            elif t.mergeBase is not None:
                del blist[t.contentHash]
        odict = _arrayDict()
        for v in olist.values(): odict.set(v.attrHash, v)
        if base is not None:
            bdict = _arrayDict()
            for v in blist.values(): bdict.set(v.attrHash, v)
        for t in filter(lambda x: x.mergeOther == None, this):     # go over everything not yet associated
            # this is pretty horrible - find first alignment on key attributes. (sufficient for ldml)
            t.mergeOther = odict.pop(t.attrHash)
            if t.mergeOther is not None:
                del olist[t.mergeOther.contentHash]
            if t.mergeBase is None and base is not None:
                if t.mergeOther is not None and t.mergeOther.contentHash in blist:
                    t.mergeBase = blist.pop(t.mergeOther.contentHash)
                    if t.mergeBase is not None: bdict.remove(t.mergeBase.attrHash, t.mergeBase)
                if t.mergeBase is None:
                    t.mergeBase = bdict.pop(t.attrHash)
                    if t.mergeBase is not None: del blist[t.mergeBase.contentHash]
        for e in olist.values():       # pick up stuff in other but not in this
            newe = self.copynode(e, this.parent)
            if base is not None and e.contentHash in blist:
                newe.mergeBase = blist.pop(e.contentHash)
            elif base is not None:
                newe.mergeBase = bdict.pop(e.attrHash)
                while newe.mergeBase is not None and newe.mergeBase.contentHash not in blist:
                    newe.mergeBase = bdict.pop(e.attrHash)
                if newe.mergeBase is not None:
                    del blist[newe.mergeBase.contentHash]
            else:
                newe.mergeBase = None
            newe.mergeOther = None     # don't do anything with this in merge()
            this.append(newe)

    def _merge_with_alts(self, base, other, target, default=None, copycomments=None):
        """3-way merge the alternates putting the results in target. Assumes target content is the required ending content"""
        res = False
        if default is None:
            default = base.default_draft
        # if base != target && base better than target
        if base is not None and base.contentHash != target.contentHash and (base.text or base.tag in self.blocks) and self.get_draft(base) < self.get_draft(target, default):
            res = True
            self._add_alt(base, target, default=default)  # add target as alt of target
            target[:] = base                                # replace content of target
            for a in ('text', 'contentHash', 'comments', 'commentsafter'):
                if hasattr(base, a):
                    setattr(target, a, getattr(base, a, None))
                elif hasattr(target, a):
                    delattr(target, a)
            if 'alt' in target.attrib:
                del target.attrib['alt']
            if self.get_draft(base) != target.document.default_draft:
                target.set('draft', _alldrafts[self.get_draft(base)])
        elif base is None and other is not None and other.contentHash != target.contentHash and (target.text or target.tag in self.blocks):
            res = True
            if self.get_draft(target, default) < self.get_draft(other, default):
                self._add_alt(target, other, default=default)
            else:
                self._add_alt(other, target, default=default)
                target[:] = other
                for a in ('text', 'contentHash', 'comments', 'commentsafter'):
                    if hasattr(other, a):
                        setattr(target, a, getattr(other, a, None))
                    elif hasattr(target, a):
                        delattr(target, a)
                if 'alt' in target.attrib:
                    del target.attrib['alt']
                if self.get_draft(other) != target.document.default_draft:
                    target.set('draft', _alldrafts[self.get_draft(other)])
        elif copycomments is not None:
            commentsource = base if copycomments == 'base' else other
            if comentsource is not None:
                for a in ('comments', 'commentsafter'):
                    if hasattr(commentsource, a):
                        setattr(target, a, getattr(commentsource, a))
                    elif hasattr(target, a):
                        delattr(target, a)
        res |= self._merge_alts(base, other, target, default)
        return res

    def _merge_alts(self, base, other, target, default='unconfirmed'):
        if other is None or not hasattr(other, 'alternates'): return False
        res = False
        if not hasattr(target, 'alternates'):
            target.alternates = dict(other.alternates)
            return (len(target.alternates) != 0)
        balt = getattr(base, 'alternates', {}) if base is not None else {}
        allkeys = set(balt.keys() + target.alternates.keys() + other.alternates.keys())
        for k in allkeys:
            if k not in balt:
                if k not in other.alternates: continue
                if k not in target.alternates or self.get_draft(target.alternates[k], default) > self.get_draft(other.alternates, default):
                    target.alternates[k] = other.alternates[k]
                    res = True
            elif k not in other.alternates:
                if k not in target.alternates or self.get_draft(target.alternates[k], default) > self.get_draft(balt[k]):
                    target.alternates[k] = balt[k]
                    res = True
            elif k not in target.alternates:
                if k not in other.alternates or self.get_draft(other.alternates[k], default) > self.get_draft(balt[k]):
                    target.alternates[k] = balt[k]
                else:
                    target.alternates[k] = other.alternates[k]
                res = True
            elif self.get_draft(target.alternates[k], default) > self.get_draft(other.alternates[k], default):
                target.alternates[k] = other.alternates[k]
                res = True
            elif self.get_draft(target.alternates[k], default) > self.get_draft(balt[k]):
                target.alternates[k] = balt[k]
                res = True
            elif other.alternates[k].contentHash != balt[k].contentHash:
                target.alternates[k] = other.alternates[k]
                res = True
        return res

    
    def _add_alt(self, target, origin, default='unconfirmed'):
        self._add_alt_leaf(target, origin.copy(),
                default=default, leaf=origin.contentHash is not None,
                alt = self.alt())

    def merge(self, other, base, this=None, default=None, copycomments=None):
        """ Does 3 way merging of self/this and other against a common base. O(N), base or other can be None.
            Returns True if any changes were made."""
        res = False
        if this == None: this = self.root
        if other is not None and hasattr(other, 'root'): other = other.root
        if base is not None and hasattr(base, 'root'): base = base.root
        self._align(this, other, base)
        # other and base can be None
        for t in list(this):       # go through children merging them
            if t.mergeBase is None:
                if self.useDrafts and t.mergeOther is not None and t.mergeOther.contentHash != t.contentHash:
                    self._merge_with_alts(t.mergeBase, t.mergeOther, t, default=default, copycomments=copycomments)
                continue
            if t.mergeOther is not None and t.mergeOther.contentHash != t.contentHash:     # other differs
                if t.mergeBase.contentHash == t.contentHash:   # base doesn't
                    if self.useDrafts:
                        res |= self._merge_with_alts(t.mergeBase, t.mergeOther, t, default=default, copycomments=copycomments)
                    else:
                        this.remove(t)                                  # swap us out
                        this.append(t.mergeOther)
                        res = True
                elif t.mergeBase.contentHash != t.mergeOther.contentHash:
                    res |= self.merge(t.mergeOther, t.mergeBase, t)        # could be a clash so recurse
                elif self.useDrafts:       # base == other
                    res |= self._merge_with_alts(t.mergeBase, t.mergeOther, t, default=default, copycomments=copycomments)
            elif t.mergeOther is None and t.mergeBase.contentHash == t.contentHash:
                this.remove(t)
                res = True
            elif self.useDrafts:
                res |= self._merge_with_alts(t.mergeBase, t.mergeOther, t, default=default, copycomments=copycomments)
        if base is not None and this.text == base.text:
            if other is not None:
                res = res or (this.text != other.text)
                this.text = other.text
                this.contentHash = other.contentHash
            elif this.text is not None:
                res = True
                this.text = None
                this.contentHash = None
            if self.useDrafts: res |= self._merge_with_alts(base, other, this, default=default, copycomments=copycomments)
        elif base is not None and other is not None and other.text != base.text:
            self.clash_text(this.text, other.text, (base.text if base is not None else None),
                                        this, other, base, usedrafts=self.useDrafts)
            if self.useDrafts:
                res |= self._merge_with_alts(base, other, this, default=default, copycomments=copycomments)
                return res
        elif self.useDrafts:
            res |= self._merge_with_alts(base, other, this, default=default, copycomments=copycomments)
        oattrs = set(other.keys() if other is not None else [])
        for k in this.keys():                                  # go through our attributes
            if k in oattrs:
                if k in base.attrib and base.get(k) == this.get(k) and this.get(k) != other.get(k):
                    res = True
                    this.set(k, other.get(k))                       # t == b && t != o
                elif this.get(k) != other.get(k):
                    self.clash_attrib(k, this.get(k), other.get(k), base.get(k), this, other, base, usedrafts=self.useDrafts)    # t != o
                    res = True
                oattrs.remove(k)
            elif base is not None and k in base.attrib:                        # o deleted it
                this.attrib.pop(k)
                res = True
        for k in oattrs:                                       # attributes in o not in t
            if base is None or k not in base.attrib or base.get(k) != other.get(k):
                this.set(k, other.get(k))                           # if new in o or o changed it and we deleted it
                res = True
        return res

    def clash_text(self, ttext, otext, btext, this, other, base, usedrafts = False, default=None):
        if usedrafts:
            if default is None:
                default = self.default_draft
            bdraft = self.get_draft(base)
            tdraft = self.get_draft(this)
            odraft = self.get_draft(other)
            if tdraft < odraft:
                self._add_alt(this, other, default=default)
                return
            elif odraft < tdraft:
                self._add_alt(this, this, default=default)
                this.text = otext
                this.contentHash = other.contentHash
                return
            elif tdraft >= bdraft:
                self._add_alt(this, this, default=default)
                self._add_alt(this, other, default=default)
                this.text = btext
                this.contentHash = base.contentHash
                return
        if not hasattr(this, 'comments'): this.comments = []
        this.comments.append('Clash: "{}" or "{}" from "{}"'.format(ttext, otext, btext))

    def clash_attrib(self, key, tval, oval, bval, this, other, base, usedrafts = False):
        if not hasattr(this, 'comments'): this.comments = []
        this.comments.append('Attribute ({}) clash: "{}" or "{}" from "{}"'.format(key, tval, oval, bval))
        return tval        # not sure what to do here. 'We' win!

    def get_script(self, name):
        """Analyses the language name and code and anything it can find to identify the script for this file"""
        start = name.find('_')
        if start > 0:
            end = name[start+1:].find('_')
            if end < 0:
                end = len(name)
            else:
                end += start + 1
            if (end - start) == 5:
                return name[start+1:end]
        l = self.root.find('identity/language')
        if l is not None:
            lang = l.get('type')
        else:
            lang = name
        scripts = []
        if not hasattr(self, 'languageInfo'): self.__class__.ReadSupplementalData()
        if lang in self.languageInfo:
            scripts = self.languageInfo[lang][0]
            if len(scripts) == 1: return scripts[0]
        if not hasattr(self, 'likelySubtags'): self.__class__.ReadLikelySubtags()
        if lang in self.likelySubtags:
            return self.likelySubtags[lang].split('_')[1]
        if len(scripts): return scripts[0]
        return None

    def get_default_territory(self, name):
        start = name.find('_')
        if start > 0: lang = name[0:start]
        elif len(name): lang = name
        else:
            l = self.root.find('identity/language')
            if l is not None:
                lang = l.get('type')
            else: return None
        if not hasattr(self, 'likelySubtags'): self.__class__.ReadLikelySubtags()
        if lang in self.likelySubtags:
            subtags = self.likelySubtags[lang].split('_')
            if len(subtags) > 2:
                return subtags[2]
        return None
        
    def remove_private(self):
        """ Remove private elements and return them as a list of elements """
        res = []
        if self.root is None: return res
        for n in ('contacts', 'comments'):
            for e in self.root.findall(n):
                res.append(e)
                self.root.remove(e)
                e.parent = None
        return res

    def add_silidentity(self, **kws):
        """Inserts attributes in identity/special/sil:identity"""
        i = self.root.find('identity')
        if i is not None:
            s = i.find('special/{'+self.silns+'}identity')
            if s is None:
                se = et.SubElement(i, 'special')
                if 'sil' not in self.namespaces:
                    self.namespaces[self.silns] = 'sil'
                s = et.SubElement(se, '{'+self.silns+'}identity')
            for k, v in kws.items():
                s.set(k, v)

    def flag_nonroots(self):
        """Add @sil:modified="true" to key elements"""
        for n in self.root.findall('collations/collation'):
            n.set('{'+self.silns+'}modified', 'true')

    def flatten_collation(self, collstr, importfn):
        """Flattens [import] statements in a collation tailoring"""
        def doimport(m):
            return self.flatten_collation(importfn(m.group('lang'), m.group('coll')), importfn)
        return re.sub(r'\[import\s*(?P<lang>.*?)-u-co-(?P<coll>.*?)\s*\]', doimport, collstr)


def _prepare_parent(next, token):
    def select(context, result):
        for elem in result:
            if hasattr(elem, 'parent'):
                yield elem.parent
    return select
ep.ops['..'] = _prepare_parent

def flattenlocale(lname, dirs=[], rev='f', changed=set(), autoidentity=False, skipstubs=False, fname=None, flattencollation=False):
    """ Flattens an ldml file by filling in missing details from the fallback chain.
        If rev true, then do the opposite and unflatten a flat LDML file by removing
        everything that is the same in the fallback chain.
        changed contains an optional set of locales that if present says that the operation
        is only applied if one or more of the fallback locales are in the changed set.
        autoidentity says to insert or remove script information from the identity element.
        Values for rev: f - flatten, r - unflatten, c - copy"""
    def trimtag(s):
        r = s.rfind('_')
        if r < 0:
            return ''
        else:
            return s[:r]

    def getldml(lname, dirs):
        for d in dirs:
            f = os.path.join(d, lname + '.xml')
            if os.path.exists(f):
                return Ldml(f)
            f = os.path.join(d, lname[0].lower(), lname + '.xml')
            if os.path.exists(f):
                return Ldml(f)
        return None

    if isinstance(lname, Ldml):
        l = lname
        lname = fname
    elif not isinstance(lname, string_types):
        l = Ldml(lname)
        lname = fname
    else:
        l = getldml(lname, dirs)
    if l is None: return l
    if skipstubs and len(l.root) == 1 and l.root[0].tag == 'identity': return None
    if rev != 'c':
        fallbacks = l.get_parent_locales(lname)
        if not len(fallbacks):
            fallbacks = [trimtag(lname)]
        if 'root' not in fallbacks and lname != 'root':
            fallbacks += ['root']
        if len(changed):       # check against changed
            dome = False
            for f in fallbacks:
                if f in changed:
                    dome = True
                    break
            if not dome: return None
        dome = True
        for f in fallbacks:    # apply each fallback
            while len(f):
                o = getldml(f, dirs)
                if o is not None:
                    if rev == 'r':
                        l.difference(o)
                        dome = False
                        break   # only need one for unflatten
                    else:
                        if f == 'root':
                            l.flag_nonroots()
                        l.overlay(o)
                f = trimtag(f)
            if not dome: break
    if skipstubs and len(l.root) == 1 and l.root[0].tag == 'identity': return None
    if autoidentity:
        i = l.root.find('identity')
        if i is not None:
            jobs = (('script', l.get_script(lname)),
                    ('territory', l.get_default_territory(lname)))
            for (n, j) in jobs:
                if j is None: continue
                curr = i.find(n)
                if rev == 'r':
                    if curr is not None and curr.get('type') == j:
                        i.remove(curr)
                elif curr is None:
                    l.addnode(i, n, type=j)
    if flattencollation:
        collmap = {'phonebk' : 'phonebook'}
        def getcollator(lang, coll):
            try:
                if l.fname.endswith(lang+'.xml'):
                    c = l
                else:
                    c = getldml(('root' if lang == 'und' else lang), dirs)
                col = c.root.find('collations/collation[@type="{}"]/cr'.format(collmap.get(coll, coll)))
                return col.text
            except:
                return ''
            
        for i in l.root.findall('collations/collation/cr'):
            i.text = l.flatten_collation(i.text, getcollator)

    return l

if __name__ == '__main__':
    import sys, codecs
    l = Ldml(sys.argv[1])
    if len(sys.argv) > 2:
        for f in sys.argv[2:]:
            if f.startswith('-'):
                o = Ldml(f[1:])
                l.difference(o)
            else:
                o = Ldml(f)
                l.overlay(o)
    l.normalise()
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)
    l.serialize_xml(sys.stdout.write) #, topns=False)

