import os

# Read the DUCET file and return a corresponding data structure.
def readDucet(path) :

    ducetFilename = os.path.abspath(os.path.dirname(__file__) + path + "/allkeys.txt")

    try :
        with open(ducetFilename, 'r') as f :
            content = f.readlines()
    except :
        print "ERROR: unable to read DUCET data in allkeys.txt"
        return {}

    result = {}
    
    lineCnt = 0
    for contentLine in content :
        if contentLine[0] == '#' :
            continue
        if contentLine[0] == '@' :
            continue
        if contentLine == "" :
            continue
        if len(contentLine) < 2 :
            continue
            
        #print "'" + contentLine + "'"
        lineCnt = lineCnt + 1
        
        charsPlusSortKeys = contentLine.split(';')
        if len(charsPlusSortKeys) != 2 :
            continue
        charsStr = charsPlusSortKeys[0].strip()
        sortKeysFullStr = charsPlusSortKeys[1]

        #chars = charsStr.split(' ')

        closeB = 1
        sortKeysFull = []
        while closeB > 0 :
            openB = sortKeysFullStr.find('[', closeB) + 1
            x = sortKeysFullStr[openB]
            #if sortKeysFullStr[openB] == '*' :
            #    closeB = -1  # ignore variable weightings
            #elif openB > 0 :
            if openB > 0 :
                closeB = sortKeysFullStr.find(']', openB)
            else :
                closeB = -1
            if closeB > 0 :
                sortKeysStr = sortKeysFullStr[openB+1:closeB]    # eg, '1DDD.0020.0002'
                sortKeysTmp = sortKeysStr.split('.')
                sortKeyValues = []
                for sk in sortKeysTmp :
                    if sk == '' :
                        pass
                    else :
                        sortKeyValues.append(int(sk, 16))

                sortKeysFull.append(sortKeyValues)

        if len(sortKeysFull) > 0 :
            result[charsStr] = sortKeysFull

        #if lineCnt > 30 : break

    # end of for contentLine in content

    print "got ducet"

    return result

# end of readDucet


def ducetCompare(ducetDict, str1, str2) :
    charHexKey1 = _ducetKey(str1)
    charHexKey2 = _ducetKey(str2)

    try :
        rawSortKey1 = ducetDict[charHexKey1]
        rawSortKey2 = ducetDict[charHexKey2]
    except :
        return "unknown"

    sortKey1 = _generateSortKey(rawSortKey1)
    sortKey2 = _generateSortKey(rawSortKey2)

    minSKlen = min(len(sortKey1), len(sortKey2))

    level1 = 1
    level2 = 1
    for i in range(0,minSKlen) :
        if sortKey1[i] < sortKey2[i] :
            return min(level1, level2)
        if sortKey1[i] > sortKey2[i] :
            return min(level1, level2) * -1
        if sortKey1[i] == 0 :
            level1 = level1 + 1
        if sortKey2[i] == 0 :
            level2 = level2 + 1

    # sort keys are equal as far as they go
    if len(sortKey1) < len(sortKey2) :
        return 4
    if len(sortKey1) > len(sortKey2) :
        return -4

    return 0  # equal

# end of ducetCompare


# For looking up the sort key in the DUCET table;
# eg, "ab" -> "0061 0062"
# Supplementary plane characters come in as two surrogates but are returned as 32-bit strings.
def _ducetKey(str1) :
    sep = ''
    result = ""
    state = "normal"
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
        while len(hexStr) < 4 : hexStr = '0' + hexStr
        result += sep + hexStr
        sep = ' '
    return result.upper()


def _generateSortKey(rawSortKey) :
    leveledResult = [[], [], []]
    for level in range(0,3) :
        for ipart in range(0, len(rawSortKey)) :
            k = (rawSortKey[ipart])[level]
            if k != 0 :
                leveledResult[level].append((rawSortKey[ipart])[level])
        leveledResult[level].append(0)

    # Flatten out the list.
    result = leveledResult[0]
    result.extend(leveledResult[1])
    result.extend(leveledResult[2])
    return result

# end of _generateSortKey


### [.1C47.0020.0002][.0000.0026.0002][.0000.0024.0002]

#def trimSpaces(str) :
#    while str.endswith(" ") : str = str[:-1]
#    while str.startswith(" ") : str = str[1]
            
  
# end of readDucet

