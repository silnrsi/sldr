#!/usr/bin/python

import re, copy
from math import log10

def escape(s):
    res = ""
    escs = ['\\&[]/<']
    for k in s:
        if k in escs:
            res += u"\\" + k
            continue
        i = ord(k)
        if 32 < i < 127:
            res += k
        elif i > 0xFFFF:
            res += u'\\U' + ("00000000" + (hex(i)[2:]))[:-8]
        else:
            res += u'\\' + ("0000" + (hex(i)[2:]))[:-4]
    return res

def unescape(s):
    s = re.sub(ur'(?:\\U([0-9A-F]{8})|\\u([0-9A-F]{4}))', lambda m:unichr(int(m.group(m.lastindex), 16)), s, re.I)
    s = re.sub(ur'\\(.)', ur'\1', s)
    return s

def ducetSortKey(d, k):
    res = [[], [], []]
    i = len(k)
    while i > 0:
        try:
            b = d[k[:i]]
        except KeyError:
            i -= 1
            continue
        key = ducet._generateSortKey(b, separate=True)
        res = [key[i] + res[i] for i in range(3)]
        k = k[i:]
        i = len(k)
    return res

class Collation(dict):

    def __init__(self, ducetDict):
        self.ducet = ducetDict

    def parse(self, string):
        """Parse LDML/ICU sort tailoring"""
        for run in string.split('&'):
            bits = [x.strip() for x in re.split(ur'([<=]+)', run)]
            base = unescape(bits[0])
            for i in range(1, len(bits), 2):
                if bits[i] == '=': l = 4
                else:
                    l = bits[i].count('<')
                key = unescape(bits[i+1])
                self[key] = CollElement(base, l)
                base = key

    def _setSortKeys(self):
        inc = 1. / pow(10, int(log10(len(self)))+1)
        for v in self.values():
            v.sortkey(self, self.ducet, inc)

    def asICU(self):
        """Returns ICU tailoring syntax of this Collation"""
        self._setSortKeys()
        lastk = None
        res = ""
        for k, v in sorted(self.items(), key=lambda x:x[1].key):
            if v.base != lastk:
                res += "\n&" + escape(v.base)
            if v.level == 4:
                res += "="
            else:
                res += " " + ("<<<"[:v.level]) + " "
            res += escape(k)
            lastk = k
        return res[1:] if len(res) else ""

    def minimise(self):
        self._setSortKeys()
        deleteme = set()
        for k, v in sorted(self.items(), key=lambda x:x[1].key):
            currlevel = min(4, v.level)
            b = v.base
            while b in self and (b not in deleteme or b not in self.ducet):
                currlevel = min(currlevel, self[b].level)
                b = self[b].base
            if b not in self.ducet:
                continue
            bsort = ducetSortKey(self.ducet, b)
            ksort = ducetSortKey(self.ducet, k)
            for i in range(currlevel):
                diff = cmp(bsort[i], ksort[i])
                if diff != 0 :
                    break
            if diff < 0:
                deleteme.add(k)
        for k in deleteme:
            del self[k]
            

class CollElement(object):

    def __init__(self, base, level):
        self.base = base
        self.level = level

    def __repr__(self):
        return ">>>>"[:self.level] + self.base

    def sortkey(self, collations, ducetDict, inc):
        if hasattr(self, 'key'):
            return self.key
        if self.base in collations:
            basekey = copy.deepcopy(collations[self.base].sortkey(collations, ducetDict, inc))
        else:
            basekey = copy.deepcopy(ducetSortKey(ducetDict, self.base))
        basekey[self.level-1][0] += inc
        self.key = basekey
        return basekey

if __name__ == '__main__':
    import sys
    import ducet
    ducetDict = ducet.readDucet()
    coll = Collation(ducetDict)
    if len(sys.argv) > 1:
        coll.parse(sys.argv[1])
        coll.minimise()
        print coll.asICU()
