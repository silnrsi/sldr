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
import itertools, re, os, sys
from collections import namedtuple

try:
    from . import UnicodeSets
except ValueError:
    if __name__ == '__main__':
        sys.path.insert(0, os.path.dirname(__file__))
        import UnicodeSets


CharCode = namedtuple('CharCode', ['primary', 'tertiary_base', 'tertiary', 'prebase'])
SortKey = namedtuple('SortKey', ['primary', 'index', 'tertiary', 'tiebreak'])
        

class Keyboard(object):

    def __init__(self, path):
        self.keyboards = []
        self.modifiers = {}
        self.transforms = {}
        self.settings = {}
        self.history = []
        self.context = ""
        self.parse(path)

    def _addrules(self, element, transform):
        if transform not in self.transforms:
            self.transforms[transform] = Rules(transform)
        rules = self.transforms[transform]
        for m in element:
            rules.append(m)

    def parse(self, fname):
        '''Read and parse an LDML keyboard layout file'''
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
                self._addrules(c, c.get('type'))
            elif c.tag == 'reorders':
                self._addrules(c, 'reorder')
            elif c.tag == 'backspaces':
                self._addrules(c, 'backspace')
            elif c.tag == 'settings':
                self.settings.update(c.attrib)
            elif c.tag == 'import':
                newfname = os.path.join(os.path.dirname(fname), c.get('path'))
                self.parse(newfname)

    def process_string(self, txt):
        '''Process a sequence of keystrokes expressed textually into a list
            of contexts giving the output after each keystroke'''
        self.initstring()
        keys = re.findall(ur'\[\s*(.*?)\s*\]', txt)
        res = []
        for k in keys:
            words = k.split()
            modifiers = [x.lower() for x in words[:-1]]
            yield self.process(words[-1], modifiers)

    def parse_modifiers(self, modifiers):
        '''Flatten a modifier list into a list of possible modifiers'''
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

    def initstring(self):
        '''Prepare to start processing a sequence of keystrokes'''
        self.history = []

    def process(self, k, mods):
        '''Process and record the results of a single keystroke given previous history'''
        chars = self.map_key(k, mods)
        if not len(self.history):
            ctxt = Context(chars)
        else:
            ctxt = self.history[-1].clone(chars)
        
        if k == 'BKSP':
            # normally we would simply undo, but test the backspace transforms
            if not self._process_backspace(ctxt, 'backspace'):
                return self.error(ctxt)
        else:
            if not self._process_simple(ctxt):
                return self.error()
            self._process_reorder(ctxt)
            if not self._process_simple(ctxt, 'final', handleSettings=False):
                return self.error()
        self.history.append(ctxt)
        return ctxt

    def error(self):
        '''Set error state'''
        if not len(self.history):
            res = Context()
        else:
            res = self.history[-1].clone()
        res.error = 1
        return res

    def map_key(self, k, mods):
        '''Apply the appropriate keyMap to a keystroke to get some chars'''
        modstr = " ".join(sorted(mods))
        try:
            res = self.keyboards[self.modifiers[modstr]][k]
        except KeyError:
            return ""
        return UnicodeSets.struni(res)

    def _process_empty(self, context, ruleset):
        '''Copy layer input to output'''
        context.reset_output(ruleset)
        output = context.input(ruleset)[context.offset(ruleset):]
        context.results(ruleset, len(output), output)

    def _process_simple(self, context, ruleset='simple', handleSettings=True):
        '''Handle a simple replacement transforms type'''
        if ruleset not in self.transforms:
            self._process_empty(context, ruleset)
            return True
        trans = self.transforms[ruleset]
        if handleSettings:
            partial = self.settings.get('transformPartial', "") == "hide"
            fail = self.settings.get('transformFailure', "") == 'omit'
            fallback = self.settings.get('fallback', "") == 'omit'
        else:
            partial = False
            fail = False
            fallback = False

        context.reset_output(ruleset)
        curr = context.offset(ruleset)
        instr = context.input(ruleset)
        while curr < len(instr):
            r = trans.match(instr[curr:], partial=partial, fail=fail)
            if r[0] is not None:
                if getattr(r[0], 'error', 0): return False
                context.results(ruleset, r[1], getattr(r[0], 'to', ""))
                curr += r[1]
            elif r[1] == 0 and not fallback:     # abject failure
                context.results(ruleset, 1, instr[curr:curr+1])
                curr += 1
            else:               # partial match waiting for more input
                break
        return True

    def _sort(self, begin, end, chars, keys):
        s = chars[begin:end]
        k = keys[:end-begin]
        # if there is no base, insert one
        if (0, 0) not in [(x.primary, x.tertiary) for x in k]:
            s += u"\u25CC"
            k += SortKey(0, 0, 0, 0)  # push this to the front
        # sort key is (primary, secondary, string index)
        return u"".join(s[y] for y in sorted(range(len(s)), key=lambda x:k[x]))

    def _padlist(self, val, num):
        boolmap = {'false' : 0, 'true': 1}
        res = [boolmap.get(x.lower(), x) for x in val.split()]
        if len(res) < num:
            res += [res[-1]] * (num - len(res))
        return res

    def _get_charcodes(self, instr, curr, trans):
        '''Returns a list of some CharCodes, 1 per char, for the string at curr''' 
        r = trans.match(instr[curr:])
        if r[0] is not None:
            orders = [int(x) for x in self._padlist(getattr(r[0], 'order', "0"), r[1])]
            bases = [bool(x) for x in self._padlist(getattr(r[0], 'tertiary_base', "false"), r[1])]
            tertiaries = [int(x) for x in self._padlist(getattr(r[0], 'tertiary', "0"), r[1])]
            prebases = [bool(x) for x in self._padlist(getattr(r[0], 'prebase', "false"), r[1])]
            return [CharCode(orders[i], bases[i], tertiaries[i], prebases[i]) for i in range(r[1])]
        else:
            return [CharCode(0, 0, 0, False)]

    def _process_reorder(self, context, ruleset='reorder'):
        '''Handle the reorder transforms'''
        if ruleset not in self.transforms:
            self._process_empty(context, ruleset)
            return
        trans = self.transforms[ruleset]
        instr = context.input(ruleset)
        context.reset_output(ruleset)

        # scan for start of sortable run. Normally empty
        startrun = context.offset(ruleset)
        curr = startrun
        while curr < len(instr):
            codes = self._get_charcodes(instr, curr, trans)
            for c in codes:
                if c.prebase or c.primary == 0:
                    break
                curr += 1
            else:
                continue        # if didn't break inner loop, don't break outer loop
            break               # if we broke in the inner loop, break the outer loop
        if curr > startrun:     # just copy the odd characters across
            context.results(ruleset, curr - startrun, instr[startrun:curr])

        startrun = curr
        keys = [None] * (len(instr) - startrun)
        isinit = True           # inside the start of a run (.{prebase}* .{order==0 && tertiary==0})
        currprimary = 0
        currbaseindex = curr
        while curr < context.len(ruleset):
            codes = self._get_charcodes(instr, curr, trans)
            for i, c in enumerate(codes):               # calculate sort key for each character in turn
                if c.tertiary and curr + i > startrun:      # can't start with tertiary, treat as primary 0
                    key = SortKey(currprimary, currbaseindex, c.tertiary, curr + i)
                else:
                    key = SortKey(c.primary, curr + i, 0, curr + i)
                    if c.primary == 0 or c.tertiary_base:   # primary 0 is always a tertiary base
                        currprimary = c.primary
                        currbaseindex = curr + i

                if ((key.primary != 0 or key.tertiary != 0) and not c.prebase) \
                        or (c.prebase and curr + i > startrun \
                            and keys[curr+i-startrun-1].primary == 0):  # prebase can't have tertiary
                    isinit = False      # After the prefix, so any following prefix char starts a new run

                # identify a run boundary
                if not isinit and ((key.primary == 0 and key.tertiary == 0) or c.prebase):
                    # output sorted run and reset for new run
                    context.results(ruleset, curr + i - startrun,
                                    self._sort(startrun, curr + i, instr, keys))
                    startrun = curr + i
                    keys = [None] * (len(instr) - startrun)
                    isinit = True
                keys[curr+i-startrun] = key
            curr += len(codes)
        if curr > startrun:
            # output but don't store any residue. Reprocess it next time.
            context.outputs[context.index(ruleset)] += self._sort(startrun, curr, instr, keys)

    def _process_backspace(self, context, ruleset='backspace'):
        '''Handle the backspace transforms in response to bksp key'''
        if ruleset not in self.transforms:
            self.chomp(context)
        trans = self.transforms[ruleset]
        # reverse the string
        instr = context.outputs[-1][::-1]
        # find and process one rule
        r = trans.match(instr)
        if r[0] is not None:
            if getattr(r[0], 'error', 0): return False
            instr[:r[1]] = getattr(r[0], 'to', "")
        else:       # no rule, so just remove a single character
            instr = instr[1:]
        # and reverse back again
        context.outputs[-1] = instr[::-1]
        return True


class Rules(object):
    '''Corresponds to a transforms element in an LDML file'''
    def __init__(self, ruletype):
        self.type = ruletype
        self.rules = Rule()
        self.reverse = ruletype == 'backspace'      # work backwards

    def append(self, transform):
        '''Insert or merge a rule into this set of rules'''
        f = transform.get('from')
        if self.reverse:
            chars = UnicodeSets.parse(f).reverse()
        else:
            chars = UnicodeSets.parse(f)
        jobs = set([self.rules])
        for i, k in enumerate(chars):
            isFinal = i + 1 == len(chars)
            newjobs = set()
            # inefficient trie is fine
            for j in jobs:
                j.fail = False
                for l in k:
                    if l not in j:
                        j[l] = Rule()
                    if not k.negative:
                        newjobs.add(j[l])
                if k.negative:
                    for d in j.keys():
                        if d not in k:
                            newjobs.add(j[d])
                    if j.default is None:
                        j.default = Rule()
                    newjobs.add(j.default)
                if isFinal:
                    for j, string in newjobs:
                        j.merge(transform.attrib)
            jobs = newjobs

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
                if curr.default:
                    curr = curr.default
                else:
                    return (last, lastind - start)
            curr = curr[s[ind]]
            ind += 1
            if curr.rule:
                newlast = curr.context_match(s, start, ind)
                if newlast is not None:
                    lastind = ind
                    last = newlast
        if partial and len(curr):
            return (None, ind - start)
        else:
            return (last, lastind - start)
        

class Rule(dict):
    '''A trie element that might do something. Corresponds to a
        flattened transform in LDML'''

    def __init__(self):
        self.rule = False
        self.default = None
        self.contexts = {}

    def __hash__(self):
        return hash(id(self))

    def merge(self, e):
        if 'before' in e or 'after' in e:
            before = UnicodeSets.flatten(e.get('before', ""))
            after = UnicodeSets.flatten(e.get('after', ""))
            for b in before or [""]:
                for a in after or [""]:
                    k = (b, a)
                    if k == ("", ""):
                        self._coremerge(e)
                        continue
                    if k not in self.contexts:
                        self.contexts[k] = Rule()
                    self.contexts[k]._coremerge(e) 
        else:
            self._coremerge(e)

    def _coremerge(self, e):
        for k, v in e.items():
            if k in ('from', 'before', 'after'):
                continue
            setattr(self, k, v)
        if 'to' in e:
            self.to = UnicodeSets.struni(e['to'])
        self.rule = True

    def _matchcontext(self, m, s, beg, end):
        return (not len(m[0]) or (len(m[0]) <= beg          and s[beg-len(m[0]):beg] == m[0])) \
           and (not len(m[1]) or (len(m[1]) <= len(s) - end and s[end:end+len(m[1])] == m[1]))

    def context_match(self, s, beg, end):
        if not len(self.contexts):
            return self
        for m, r in self.contexts.items():
            if self._matchcontext(m, s, beg, end):
                return r
        return None

class Context(object):
    '''Holds the processed state of each layer after a keystroke'''

    slotnames = {
        'base' : 0,
        'simple' : 1,
        'reorder' : 2,
        'final' : 3
    }
    def __init__(self, chars=""):
        self.stables = [""] * len(self.slotnames)   # stuff we don't need to reprocess
        self.outputs = [""] * len(self.slotnames)   # stuff to pass to next layer
        self.stables[0] = chars                     # basic input is always stable
        self.outputs[0] = chars                     # and copy it to its output
        self.offsets = [0] * len(self.slotnames)    # pointer into last layer output
                                                    # corresponding to end of stables
        self.offsets[0] = len(chars)
        self.error = 0                              # are we in an error state?

    def clone(self, chars=""):
        '''Copy a context and add some more input to the result'''
        res = Context("")
        res.stables = self.stables[:]
        res.outputs = self.outputs[:]
        res.offsets = self.offsets[:]
        res.stables[0] += chars
        res.outputs[0] += chars
        res.offsets[0] += len(chars)
        return res

    def __str__(self):
        if self.error:
            return "*"+self.outputs[-1]+"*"         # how we show an error state
        return self.outputs[-1]

    def index(self, name='base'):
        return self.slotnames[name]

    def len(self, name='simple'):
        '''Return length of input to this layer'''
        return len(self.outputs[self.slotnames[name]-1])

    def input(self, name='simple'):
        '''Return full input string to this layer'''
        return self.outputs[self.slotnames[name]-1]

    def offset(self, name='simple'):
        '''Returns the offset into input string that isn't in stables'''
        return self.offsets[self.slotnames[name]]

    def reset_output(self, name):
        '''Prepare output based on stables ready for more output to be added'''
        ind = self.index(name)
        self.outputs[ind] = self.stables[ind]

    def results(self, name, length, res):
        '''Remove from input, in effect, and put result into stables'''
        ind = self.index(name)
        leftlen = len(self.outputs[ind-1]) - self.offsets[ind] - length
        prevleft = len(self.outputs[ind-2]) - self.offsets[ind-1] if ind > 1 else 0
        self.outputs[ind] += res
        # only add to stables if everything to be consumed is already in the stables
        # of the previous layer. Otherwise, our results can only be temporary.
        if leftlen > prevleft:
            self.stables[ind] += res
            self.offsets[ind] += length


def main():
    '''Process a testfile of key sequences, one sequence per line,
        to give test results: comma separated for each keystroke,
        one sequence per line'''
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
            outfile.write(u", ".join(map(unicode, res)) + u"\n")
    outfile.close()

if __name__ == '__main__':
    main()
