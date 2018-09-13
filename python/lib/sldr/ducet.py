#!/usr/bin/python

# Py2 and Py3 compatibility
from __future__ import print_function

import os, re


# Read the DUCET file and return a corresponding data structure.
def readDucet(path="") :

    ducetFilename = os.path.abspath(os.path.dirname(__file__) + path + "/allkeys.txt")

    try :
        with open(ducetFilename, 'r') as f :
            content = f.readlines()
    except :
        print("ERROR: unable to read DUCET data in allkeys.txt")
        return {}

    result = {}
    keyre = re.compile(r'([0-9A-F]{4})', re.I)
    valre = re.compile(r'\[[.*]([0-9A-F]{4})\.([0-9A-F]{4})\.([0-9A-F]{4})\]', re.I)

    for lineno, contentLine in enumerate(content):
        if contentLine[0] == '#':
            continue
        parts = contentLine.split(';')
        if len(parts) != 2:
            continue

        ####if lineno < 9500 or lineno > 10000: continue

        try:
            key = u"".join(chr(int(x, 16)) for x in keyre.findall(parts[0]))
            vals = valre.findall(parts[1])
            result[key] = tuple(tuple(int(x, 16) for x in v) for v in vals)
        except:
            print("Error processing DUCET line: " + str(lineno + 1))

    return result

# end of readDucet


def ducetCompare(ducetDict, str1, str2) :
    try:
        sortKey1 = _generateSortKey(ducetDict[str1])
        sortKey2 = _generateSortKey(ducetDict[str2])
    except KeyError:
        return "unknown"

    minSKlen = min(len(sortKey1), len(sortKey2))

    level1 = 1
    level2 = 1
    for i in range(minSKlen) :
        if sortKey1[i] < sortKey2[i] :
            return min(level1, level2)
        elif sortKey1[i] > sortKey2[i] :
            return min(level1, level2) * -1
        if sortKey1[i] == 0 :
            level1 += 1
        if sortKey2[i] == 0 :
            level2 += 1

    # sort keys are equal as far as they go
    return cmp(len(sortKey1), len(sortKey2)) * 4


# For looking up the sort key in the DUCET table;
# eg, "ab" -> "0061 0062"
# Supplementary plane characters come in as two surrogates but are returned as 32-bit strings.
def _ducetKey(str1) :
    result = ""
    state = "normal"
    res = []
    for c in str1 :
        decVal = ord(c)
        if 0xD800 <= decVal and decVal < 0xDC00 :  # high-half surrogate for supp. plane char
            highHalf = (decVal - 0xD800) * 0x400   # shift left 10 bits
            state = "utf32_1"
            continue
        elif 0xDC00 <= decVal and decVal < 0xDFFF :
            if state != "utf32_1" :
                return "invalid"
            lowHalf = (decVal - 0xDC00)
            decVal = 0x10000 + highHalf + lowHalf
            state = "normal"
        hexStr = hex(decVal)
        if hexStr[0:2] == '0x' : hexStr = hexStr[2:]
        hexStr = ("0000"+hexStr)[-4:]
        res.append(hexStr)
    return " ".join(res).upper()


def _generateSortKey(rawSortKey, separate=False) :
    leveledResult = zip(*rawSortKey)
    if separate:
        return leveledResult
    else:
        return [x + (0,) for x in leveledResult]


### [.1C47.0020.0002][.0000.0026.0002][.0000.0024.0002]

#def trimSpaces(str) :
#    while str.endswith(" ") : str = str[:-1]
#    while str.startswith(" ") : str = str[1]
            
# leveledResult = [[ki[level] for ki in rawSortKey] for level in range(3)]
  


