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
import itertools, re, os

def struni(s):
    return re.sub(ur'\\u\{([0-9a-fA-F]+)\}', lambda m:unichr(int(m.group(1), 16)), unicode(s))


class Keyboard(object):

    def __init__(self, path):
        self.keyboards = []
        self.modifiers = {}
        self.transforms = {}
        self.settings = {}
        self.history = []
        self.context = ""
        self.parse(path)

    def parse(self, fname):
        doc = et.parse(fname)
        for c in doc.getroot():
            if c.tag == 'keyMap':
                kind = len(self.keyboards)
                maps = {}
                self.keyboards.append(maps)
                if 'modifiers' in c.attrib:
                    for m in self.parse_modifiers(c.get('modifiers')):
                        self.modifiers[" ".join(m)] = kind
                else:
                    self.modifiers[""] = kind
                for m in c:
                    maps[m.get('iso')] = m.get('to')
            elif c.tag == 'transforms':
                if c.get('type') not in self.transforms:
                    rules = Rules()
                    self.transforms[c.get('type')] = rules
                rules = self.transforms[c.get('type')]
                for m in c:
                    rules.append(m)
            elif c.tag == 'settings':
                self.settings.update(c.attrib)
            elif c.tag == 'import':
                newfname = os.path.join(os.path.dirname(fname), c.get('path'))
                self.parse(newfname)

    def process_string(self, txt):
        self.initstring()
        keys = re.findall(ur'\[\s*(.*?)\s*\]', txt)
        res = []
        for k in keys:
            words = k.split()
            modifiers = [x.lower() for x in words[:-1]]
            yield self.process(words[-1], modifiers)

    def parse_modifiers(self, modifiers):
        resn = []
        reso = []
        for m in modifiers.lower().split():
            for mod in m.lower().split('+'):
                if mod.endswith("?"):
                    reso.append(mod)
                else:
                    resn.append(mod)
        yield sorted(resn)
        for i in range(len(reso)):
            for c in itertools.combinations(reso, i):
                yield sorted(resn + c)

    def map_key(self, k, mods):
        modstr = " ".join(sorted(mods))
        try:
            res = self.keyboards[self.modifiers[modstr]][k]
        except KeyError:
            return ""
        return struni(res)

    def initstring(self):
        self.history = []

    def process(self, k, mods):
        chars = self.map_key(k, mods)
        if not len(self.history):
            curr = Context(chars)
        else:
            curr = self.history[-1].clone(chars)
        self.history.append(curr)
        self._process_simple(curr)
        self._process_reorder(curr)
        self._process_simple(curr, 'final', handleSettings=False)
        res = self.diff(self.context, curr)
        self.context = curr
        return res

    def diff(self, context, curr):
        return curr.outputs[-1]

    def sort(self, txt, orders, secondarys):
        return u"".join(txt[y] for y in sorted(range(len(txt)), key=lambda x:(orders[x], secondarys[x], x)))

    def _process_simple(self, curr, ruleset='simple', handleSettings=True):
        if ruleset not in self.transforms:
            output = curr.input(ruleset)[curr.offset(ruleset):]
            curr.results(ruleset, len(output), output)
            return
        trans = self.transforms[ruleset]
        if handleSettings:
            partial = self.settings.get('transformPartial', "") == "hide"
            fail = self.settings.get('transformFailure', "") == 'omit'
            fallback = self.settings.get('fallback', "") == 'omit'
        else:
            partial = False
            fail = False
            fallback = False
        curr.reset_output(ruleset)
        start = curr.offset(ruleset)
        instr = curr.input(ruleset)
        while start < len(instr):
            r = trans.match(instr[start:], partial=partial, fail=fail)
            if r[0] is not None:
                curr.results(ruleset, r[1], getattr(r[0], 'to', instr[start:start+r[1]]))
                start += r[1]
            elif r[1] == 0 and not fallback:     # abject failure
                curr.results(ruleset, 1, instr[start:start+1])
                start += 1
            else:               # partial match waiting for more input
                break

    def _process_reorder(self, curr, ruleset='reorder'):
        if ruleset not in self.transforms:
            output = curr.input(ruleset)[curr.offset(ruleset):]
            curr.results(ruleset, len(output), output)
            return
        trans = self.transforms[ruleset]
        instr = curr.input(ruleset)
        # scan for start of sortable run, should be quick
        startrun = curr.offset(ruleset)
        start = startrun
        curr.reset_output(ruleset)
        while start < len(instr):
            r = trans.match(instr[start:])
            if r[0] is None or not hasattr(r[0], 'secondary') or getattr(r[0], 'order', 0) == 0 \
                    or hasattr(r[0], 'prebase'):
                break
            start += r[1]   # can't be 0 else would have break
        if start > startrun:
            curr.results(ruleset, start - startrun, instr[startrun:start])

        startrun = start
        orders = [0] * (len(instr) - startrun)
        secondarys = orders[:]
        isinit = True
        while start < curr.len(ruleset):
            r = trans.match(instr[start:])
            secondary = 0
            order = 0
            if r[0] is not None:
                if hasattr(r[0], 'secondary') and start > 0:
                    order = orders[start - startrun - 1]                # inherit primary order
                    secondary = int(getattr(r[0], 'secondary', '0'))
                else:
                    order = getattr(r[0], 'order', 0)
            if ((order != 0 or secondary != 0) and not hasattr(r[0], 'prebase')) \
                    or (hasattr(r[0], 'prebase') and start > startrun and orders[start - startrun - 1] == 0):
                isinit = False
            length = r[1] or 1  # if 0 advance by 1 anyway
            if not isinit and ((order == 0 and secondary == 0) or hasattr(r[0], 'prebase')):
                curr.results(ruleset, start - startrun,
                        self.sort(instr[startrun:start], orders[:start-startrun], secondarys[:start-startrun]))
                startrun = start
                orders = [0] * (len(instr) - startrun)
                secondarys = orders[:]
                isinit = True
            orders[start-startrun:start-startrun+length] = [order] * length
            secondarys[start-startrun:start-startrun+length] = [secondary] * length
            start += length
        if start > startrun:
            if isinit and orders[start-1-startrun] > 0:
                outtext = u"\u25CC"
            else:
                outtext = ""
            outtext += u"".join(self.sort(instr[startrun:start], orders[:start-startrun], secondarys[:start-startrun]))
            curr.outputs[curr.index(ruleset)] += outtext


class Rules(object):
    def __init__(self):
        self.rules = {}

    def append(self, transform):
        f = struni(transform.get('from'))
        for k in self._flatten(f):
            # big ol' slow trie is fine for a few short strings
            curr = self.rules
            for l in k:
                if l not in curr:
                    curr[l] = Rule()
                curr = curr[l]
            curr.merge(transform.attrib)

    def match(self, s, ind=0, partial=False, fail=False):
        '''Finds the merged rule for the given passed in string.
            Returns (rule, length) where length is how many chars from
            string were used to match rule.
            Returns (None, 0) on failure'''
        start = ind
        last = None
        lastind = start
        curr = self.rules
        if fail and s[ind] in curr:
            lastind = start + 1
        while ind < len(s):
            if s[ind] not in curr:
                return (last, lastind - start)
            curr = curr[s[ind]]
            ind += 1
            if hasattr(curr, 'isrule'):
                last = curr
                lastind = ind
        if partial and len(curr):
            return (None, ind - start)
        else:
            return (last, lastind - start)
        
    def _flatten(self, s):
        vals = []
        lens = []
        while len(s):
            if s[0] == '[':
                e = s.index(']')
                l = re.sub(ur'(.)-(.)', lambda m: u"".join(map(unichr, range(ord(m.group(1)), ord(m.group(2))))), s[1:e])
                vals.append(l)
                s = s[e+1:]
                lens.append(len(l))
            else:
                vals.append(s[0])
                s = s[1:]
                lens.append(1)
        indices = [0] * len(lens)
        yield u"".join(vals[i][x] for i, x in enumerate(indices))
        while True:
            for i in range(len(lens)):
                if indices[i] == lens[i] - 1:
                    indices[i] = 0
                else:
                    indices[i] += 1
                    break
            else:       # no break encountered so back to all 0s
                return
            yield u"".join(vals[i][x] for i, x in enumerate(indices))

class Rule(dict):
    '''A trie element that might do something'''

    def merge(self, e):
        for k, v in e.items():
            if k == 'from': continue
            setattr(self, k, v)
        if 'to' in e:
            self.to = struni(e['to'])
        self.isrule = True
        if 'order' in e:
            self.order = int(e['order'])

class Context(object):

    slotnames = {
        'base' : 0,
        'simple' : 1,
        'reorder' : 2,
        'final' : 3
    }
    def __init__(self, chars):
        self.stables = [""] * len(self.slotnames)
        self.outputs = [""] * len(self.slotnames)
        self.stables[0] = chars
        self.outputs[0] = chars
        self.offsets = [0] * len(self.slotnames)

    def clone(self, chars):
        res = Context("")
        res.stables = self.stables[:]
        res.outputs = self.outputs[:]
        res.offsets = self.offsets[:]
        res.stables[0] += chars
        res.outputs[0] += chars
        return res

    def index(self, name='base'):
        return self.slotnames[name]

    def len(self, name='simple'):
        return len(self.outputs[self.slotnames[name]-1])

    def input(self, name='simple'):
        return self.outputs[self.slotnames[name]-1]

    def offset(self, name='simple'):
        return self.offsets[self.slotnames[name]]

    def reset_output(self, name):
        ind = self.index(name)
        self.outputs[ind] = self.stables[ind]

    def results(self, name, length, res):
        ind = self.index(name)
        leftlen = len(self.outputs[ind-1]) - self.offsets[ind] - length
        prevleft = len(self.outputs[ind-2]) - self.offsets[ind-1] if ind > 1 else 0
        self.outputs[ind] += res
        if leftlen > prevleft:
            self.stables[ind] += res
            self.offsets[ind] += length


def main():
    import argparse, codecs, sys

    parser = argparse.ArgumentParser()
    parser.add_argument('file',help='Input LDML keyboard file')
    parser.add_argument('-t','--testfile',help='File of key sequences, one per line')
    parser.add_argument('-o','--outfile',help='Where to send results')
    args = parser.parse_args()

    kbd = Keyboard(args.file)
    if args.outfile:
        outfile = codecs.open(args.outfile, "w", encoding="utf-8")
    else:
        outfile = codecs.EncodedFile(sys.stdout, "utf-8")
    with open(args.testfile) as inf:
        for l in inf.readlines():
            res = list(kbd.process_string(l))
            outfile.write(", ".join(res) + "\n")
    outfile.close()

if __name__ == '__main__':
    main()
