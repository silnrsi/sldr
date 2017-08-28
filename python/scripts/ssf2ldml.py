# Read a Paratext .ssf file, convert the relevant data to LDML, and insert into an LDML file.


import sys
import collections
import codecs
import copy
import os
import unicodedata

from ConfigParser import RawConfigParser

supplementalPath = "/../lib/sldr/"

t = os.path.dirname(__file__) + supplementalPath
t = os.path.abspath(t)

try:
    import ldml
except ImportError:
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + supplementalPath))
    import ldml
    
import ducet

##import xml.etree.cElementTree as etree
# lxml preserves comments, also handles namespaces better:
from lxml import etree
from cStringIO import StringIO

silns = {'sil' : "urn://www.sil.org/ldml/0.1" }


def run() :

    mainPath = "C:/WS_Tech/SSF2LDML/"
    inputPath = mainPath + "testdata/"

    #testLangs = [('aau','Latn'), ('aca','Latn')]
    testLangs = [('zzz', 'Latn')]
    
    ldml.test_import()

    import sys
    if sys.maxunicode == 0x10FFFF:
        print 'Python built with UCS4 (wide unicode) support'
    else:
        print 'Python built with UCS2 (narrow unicode) support'

    print os.path.dirname(__file__)
    t = os.path.dirname(__file__) + supplementalPath
    os.path.abspath(os.path.dirname(__file__) + supplementalPath)
    ducetDict = ducet.readDucet("")

    #t  = ducet.ducetCompare(ducetDict, u'\u00e1', 'A')
    #t = ducet.ducetCompare(ducetDict, u'\u2461', u'\U0001D7F8')

    for (langCode, scriptCode) in testLangs:
        ssfFilename = inputPath + langCode + '/' + langCode + ".ssf"
        ldsFilename = inputPath + langCode + '/' + langCode + ".lds"
        if os.path.isfile(ssfFilename):
            ssfFile = file(ssfFilename)

            if os.path.isfile(ldsFilename):
                ldsFile = file(ldsFilename)
                ldsConfig = RawConfigParser()
                try:
                    ldsConfig.read(ldsFilename)
                except:
                    print "Could not parse .lds file: ", ldsFilename
            else:
                print "Missing .lds file: " + ldsFilename

            ssfLangData = {  # initializing everything to None simplies the processing
                'DefaultFont': None,
                'DefaultFontSize': None,
                'ValidCharacters': None,
                'Pairs': None,
                'Quotes': None,
                'InnerQuotes': None,
                'InnerInnerQuotes': None,
                'ContinueQuotes': None,
                'ContinueInnerQuotes': None,
                'Continuer': None,
                'InnerContinuer': None,
                'InnerInnerContinuer': None,
                'VerboseQuotes': None,
                'ValidPunctuation': None}
            
            for (event, e) in etree.iterparse(ssfFile, events=('start', 'end')) :
                ##print event + ": " + e.tag
                if event == 'start' :
                    if e.tag in ssfLangData :
                        ssfLangData[e.tag] = e.text
            # end of for loop

            ldmlFilename = inputPath + langCode + '/' + langCode + "_" + scriptCode + ".xml"
            ldmlOutputFilename = inputPath + langCode + '/' + langCode + "_" + scriptCode + "_out.xml"
            if not os.path.isfile(ldmlFilename) :
                # Output a minimal LDML file
                ldmlFilename = inputPath + langCode + '/' + langCode + "_" + scriptCode + "_min.xml"
                createMinimalLdml(ldmlFilename, langCode, scriptCode)

            ldmlFile = file(ldmlFilename)
            ldmlTree = etree.parse(ldmlFilename)
            #ldmlObj = ldml.LdmlObject(ldmlFilename)

            addSsfData(ldmlTree, ssfLangData)

            addLdsData(ldmlTree, ldsConfig, ducetDict)

            writeLdmlFile(ldmlTree, ldmlOutputFilename)
            #writeLdmlFile(ldmlObj)

        else :
            print "missing SSF file: " + ssfFilename

    # end of for (langCode, scriptCode)
                
    print ""  
    print "Done"

# end of run


def createMinimalLdml(ldmlFilename, langCode, scriptCode) :
    fileContents = \
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n" +\
        "<!-- Please enter language data in the fields below.  All data should be entered in English -->\n" +\
        "<ldml xmlns:sil=\"urn://www.sil.org/ldml/0.1\">\n" +\
        "  <identity>\n" +\
        "    <language type=\"" + langCode + "\"/>\n" +\
        "    <script type=\"" + scriptCode + "\"/>\n" +\
        "  </identity>\n" +\
        "</ldml>\n"

#        "    <special>\n" +\
#        "      <sil:identity defaultRegion=\"??\"/>\n" +\
#        "    </special>\n" +\

    ldmlFile = open(ldmlFilename, "w")
    ldmlFile.write(fileContents)
    ldmlFile.close()
    
# end of createMinimalLdml

    
def addSsfData(ldmlTree, ssfData) :
    
    ldmlRoot = ldmlTree.getroot()
    
    if ssfData['DefaultFont'] or ssfData['DefaultFontSize'] :
        _addSsfDataFont(ldmlRoot, ssfData['DefaultFont'], ssfData['DefaultFontSize'])
        
    if ssfData['Pairs'] :
        _addSsfDataPairs(ldmlRoot, ssfData['Pairs'])
        
    if ssfData['Quotes'] :
        _addSsfDataQuotes(ldmlRoot, ssfData['Quotes'])
    if ssfData['InnerQuotes'] :
        _addSsfDataInnerQuotes(ldmlRoot, ssfData['InnerQuotes'])
    if ssfData['InnerInnerQuotes'] :
        _addSsfDataInnerInnerQuotes(ldmlRoot, ssfData['InnerInnerQuotes'])
        
#    if ssfData['ContinueQuotes'] or ssfData['ContinueInnerQuotes'] :
#        _addSsfDataContinueQuotes(ldmlRoot, ssfData['ContinueQuotes'], ssfData['ContinueInnerQuotes'])

# end of addSsfData


def _addSsfDataFont(ldmlRoot, defaultFontValue, defaultSizeValue) :
    
    # DefaultFont, DefaultFontSize ->
    # special/sil:external-resources/sil:fontrole[@types="default"]/sil:font[@name, @size]
    
    silnsPrfx = _silnsPrfx()
    
    specialElem = ldmlRoot.find('special')
    if specialElem is None :
        specialElem = etree.SubElement(ldmlRoot, 'special')
    silExtResElem = specialElem.find('sil:external-resources', silns)
    if silExtResElem is None :
        silExtResElem = etree.SubElement(specialElem, silnsPrfx + 'external-resources')
        
    fontRoleElem = silExtResElem.find('sil:fontrole', silns)
    if fontRoleElem is None or fontRoleElem.get('types') != "default" :
        fontRoleElem = etree.SubElement(silExtResElem, silnsPrfx + 'fontrole')
    fontRoleElem.set('types', 'default')
    
    fontElem = fontRoleElem.find('sil:font', silns)
    if fontElem is None:
        fontElem = etree.SubElement(fontRoleElem, silnsPrfx + 'font')
    if defaultFontValue :
        fontElem.set('name', defaultFontValue)
    if defaultSizeValue :
        fontElem.set('size', defaultSizeValue)

# end of _addSsfDataFont


def _addSsfDataPairs(ldmlRoot, pairsValue) :
    
    silnsPrfx = _silnsPrfx()
    
    # Pairs ->
    # delimiters/special/sil:matched-pairs/sil:matched-pair/@open, @close
        
    delimElem = ldmlRoot.find('delimiters')
    if delimElem is None :
        delimElem = etree.SubElement(ldmlRoot, 'delimiters')
    specialElem = delimElem.find('special')
    if specialElem is None:
        specialElem = etree.SubElement(delimElem, 'special')
    matchedElem = specialElem.find('sil:matched-pairs', silns)
    if matchedElem is None :
        print "new matchedElem"
        matchedElem = etree.SubElement(specialElem, silnsPrfx + 'matched-pairs')
    
    # Get a list of existing pairs
    existingPairs = matchedElem.findall('sil:matched-pair', silns)
    
    pairList = pairsValue.split(' ')
    for pair in pairList :
        (openVal, closeVal) = pair.split('/')
        openVal = openVal.strip()
        closeVal = closeVal.strip()
        if not _findPair(existingPairs, openVal, closeVal) :
            matchElem = etree.SubElement(matchedElem, silnsPrfx + 'matched-pair')
            matchElem.set('open', openVal)
            matchElem.set('close', closeVal)
        # else it's already there
    
#end of _addSsfDataPairs


def _findPair(pairElements, openValue, closeValue) :
    for elem in pairElements :
        if elem.get('open') == openValue and elem.get('close') == closeValue :
            return True
    return False
    
    
def _addSsfDataQuotes(ldmlRoot, quotesValue) :
       
    # Quotes ->
    # delimiters/quotationStart, delimiters/quotationEnd
        
    delimElem = ldmlRoot.find('delimiters')
    if delimElem is None :
        delimElem = etree.SubElement(ldmlRoot, 'delimiters')
    qStartElem = delimElem.find('quotationStart')
    if qStartElem is None:
        qStartElem = etree.SubElement(delimElem, 'quotationStart')
    qEndElem = delimElem.find('quotationEnd')
    if qEndElem is None:
        qEndElem = etree.SubElement(delimElem, 'quotationEnd')
    
    (qStart, qEnd) = quotesValue.split(' ')
    qStartElem.text = qStart
    qEndElem.text = qEnd

#end of _addSsfDataQuotes


def _addSsfDataInnerQuotes(ldmlRoot, quotesValue) :
       
    # InnerQuotes ->
    # delimiters/alternateQuotationStart, delimiters/alternateQuotationEnd
        
    delimElem = ldmlRoot.find('delimiters')
    if delimElem is None :
        delimElem = etree.SubElement(ldmlRoot, 'delimiters')
    qStartElem = delimElem.find('alternateQuotationStart')
    if qStartElem is None:
        qStartElem = etree.SubElement(delimElem, 'alternateQuotationStart')
    qEndElem = delimElem.find('alternateQuotationEnd')
    if qEndElem is None:
        qEndElem = etree.SubElement(delimElem, 'alternateQuotationEnd')
    
    (qStart, qEnd) = quotesValue.split(' ')
    qStartElem.text = qStart
    qEndElem.text = qEnd

#end of _addSsfDataInnerQuotes

def _addSsfDataInnerInnerQuotes(ldmlRoot, quotesValue) :
       
    silnsPrfx = _silnsPrfx()
    
    # InnerInnerQuotes ->
    # delimiters/special/sil:quotation-marks[@level="3"]/@open, @close
        
    delimElem = ldmlRoot.find('delimiters')
    if delimElem is None :
        delimElem = etree.SubElement(ldmlRoot, 'delimiters')
    specialElem = delimElem.find('special')
    if specialElem is None :
        specialElem = etree.SubElement(delimElem, 'special')    
    qMarksElem = specialElem.find('sil:quotation-marks', silns)
    if qMarksElem is None :
        qMarksElem = etree.SubElement(specialElem, silnsPrfx + 'quotation-marks')
        
    existingQuotes = specialElem.findall('sil:quotation', silns)
    
    qMark3Elem = _findQuotes(existingQuotes, "3")
    if qMark3Elem is None :
        qMark3Elem = etree.SubElement(qMarksElem, silnsPrfx + 'quotation')
        qMark3Elem.set('level', "3")
            
    (qStart, qEnd) = quotesValue.split(' ')
    qMark3Elem.set('open', qStart)
    qMark3Elem.set('close', qEnd)

#end of _addSsfDataInnerInnerQuotes


def _addSsfDataContinueQuotes(ldmlRoot, contValue, contInnerValue) :
       
    silnsPrfx = _silnsPrfx()
    
    # ContinueQuotes ->
    # delimiters/special/sil:quotation-marks[@paraContinueType]/@open, @close
        
    delimElem = ldmlRoot.find('delimiters')
    if delimElem is None :
        delimElem = etree.SubElement(ldmlRoot, 'delimiters')
    specialElem = delimElem.find('special')
    if specialElem is None :
        specialElem = etree.SubElement(delimElem, 'special')
        
    existingQuotes = specialElem.findall('sil:quotation-marks', silns)
    
    if _valueNotNo(contValue) :
        quoteAtLevelElem = _findQuotes(existingQuotes, "1")
        if quoteAtLevelElem is None :
            quoteAtLevelElem = etree.SubElement(specialElem, silnsPrfx + 'quotation-marks')
        quoteAtLevelElem.set('level', "1")
        quoteAtLevelElem.set('paraContinueType', contValue)
            
    if _valueNotNo(contInnerValue) :
        quoteAtLevelElem = _findQuotes(existingQuotes, "2")
        if quoteAtLevelElem is None :
            quoteAtLevelElem = etree.SubElement(specialElem, silnsPrfx + 'quotation-marks')
        quoteAtLevelElem.set('level', "2")
        quoteAtLevelElem.set('paraContinueType', contInnerValue)

#end of _addSsfDataInnerInnerQuotes


def _findQuotes(quoteElements, level) :
    for elem in quoteElements :
        if elem.get('level') == level :
            return elem
    return None


def _valueNotNo(value) :
    if value is None :
        return False
    if value.lower() == "no" :
        return False
    if value.lower() == "false" :
        return False
    return True


def addLdsData(ldmlTree, ldsConfig, ducetDict) :
    
    valueList = []

    # Read sorted characters lists from .lds file.
    if ldsConfig.has_section('Characters') :
        cntr = 1
        keepGoing = True
        while keepGoing :  ### and cntr < 100:
            strCntr = str(cntr)
            if len(strCntr) < 2 : strCntr = '0' + strCntr
            key = 'Chr' + strCntr
            
            if not ldsConfig.has_option('Characters', key) :
                keepGoing = False
            else :
                value = ldsConfig.get('Characters', key)
                valueList.append(value)
                
            cntr = cntr + 1

    # Generate a data structure similar to a sort tailoring for the list of characters.
    sortResult = []
    if len(valueList) > 0 :
        for value in valueList :
            uValue = value.decode('utf-8')
            spaceItems = uValue.split(' ')

            if len(spaceItems) == 2 and _caseEquivalent(spaceItems[0], spaceItems[1]) :
                # Kludge: deal with a limitation of Paratext. Since these items are case equivalent, the user probably
                # intended x/X rather than x X and was not permitted by Paratext.
                value = value.replace(' ', '/')
                uValue = value.decode('utf-8')
                spaceItems = uValue.split(' ')

            sortSpecItems = []
            spaceSep = "&"
            prevSlashItems = None
            for spaceItem in spaceItems :
                slashItems = spaceItem.split('/')

                # Kludge to handle something like xX which should really be x/X
                if len(slashItems) == 1 and len(slashItems[0]) == 2 :
                    c1 = (slashItems[0])[0:1]
                    c2 = (slashItems[0])[1:]
                    if ducet.ducetCompare(ducetDict, c1, c2) == 3 : # case equivalent with x <<< X
                        # Assume a typo where they left out the slash.
                        slashItems = [c1, c2]
                # end of if

                for i in range(0, len(slashItems)) : slashItems[i] = _charToInt(slashItems[i])
                #if prevSlashItems is not None and differByDiacs(prevSlashItems[0], slashItems[0]) :
                slashSep = "<<"

                if len(slashItems) == 2 :  ### and _caseEquivalent(slashItems[0], slashItems[1]) :
                    # upper/lower
                    # TODO: remove this branch
                    sortSpecItems.append(spaceSep)
                    sortSpecItems.append(slashItems[0])
                    sortSpecItems.append("<<<")
                    sortSpecItems.append(slashItems[1])
                else :
                    sortSpecItems.append(spaceSep)
                    #sortResult += spaceSep
                    slashSep = None
                    for slashItem in slashItems :
                        if slashSep is not None : sortSpecItems.append(slashSep)
                        sortSpecItems.append(slashItem)
                        slashSep = "<<<"
                
                spaceSep = "<<"
                prevSlashItems = slashItems
                
            sortResult.append(sortSpecItems)

    if len(sortResult) > 0 :
        # Minimize the sort spec to only include things that don't fit the DUCET.
        sortResult =_minimizeSortSpec(sortResult, ducetDict)

        if len(sortResult) > 0 :
            # Generate the sort spec string.
            sortSpecString = "\n                    "
            for sortLine in sortResult :
                for item in sortLine :
                    if item == "&" :
                        sortSpecString += item
                    elif isinstance(item, str) and (item[0:1]) == "&" :
                        sortSpecString += item + " "
                    elif item == "<" :
                        sortSpecString += "  < "
                    elif item == "<<" or item == "<<<" or item == "=" :
                        sortSpecString += " " + item + " "
                    else :
                        sortSpecString += _unicodeEntity(item)
                sortSpecString += "\n                       "
        else : sortSpecString = ""
    else :
        sortSpecString = None
    
    ldmlRoot = ldmlTree.getroot()
    collationsElem = ldmlRoot.find('collations')
    if collationsElem is None :
        collationsElem = etree.SubElement(ldmlRoot, 'collations')
    collationElem = collationsElem.find('collation')
    if collationElem is not None :
        anyElem = collationElem.findall('*')
    else :
        anyElem = []
    if collationElem is None or len(anyElem) == 0 :
        if sortSpecString is not None :
            if collationElem is None :
                collationElem = etree.SubElement(collationsElem, 'collation')
            collationElem.set('type', 'standard')
            crElem = etree.SubElement(collationElem, 'cr')
            crElem.text = etree.CDATA(sortSpecString)
            ###crElem.text = '<!--[CDATA[' + sortResult + ']]-->'
        # else nothing to do and nothing to fix
    else :
        # We have one already, ignore the .lds file data.
        # But make sure it is using CDATA; it probably needs it.
        crElem = collationElem.find('cr')
        if crElem is not None :
            crElem.text = etree.CDATA(crElem.text)
        specialElem = collationElem.find('special')
        if specialElem is not None :
            etree.dump(specialElem)
            simpleElem = specialElem.find('simple', silns)
            if simpleElem is not None :
                etree.dump(simpleElem)
                print "fix CDATA"
                simpleElem.text = etree.CDATA(simpleElem.text)

# end of addLdsData


def _minimizeSortSpec(sortSpec, ducetDict) :

    # First, look at each line individually and see which have information we need to retain.
    # Note that we don't try to minimize the lines themselves, just the set of lines.
    needLines = {}
    for iline in range(0, len(sortSpec)) :
        thisLine = sortSpec[iline]
        needThisLine = False
        prevItems = None
        # Try to find something in this line that doesn't fit the DUCET; if so, we definitely need this line.
        for iitem in range(0,len(thisLine)) :
            cExpected = _compareToken(thisLine[iitem])
            if cExpected >= 0 :
                cVal = ducet.ducetCompare(ducetDict, _intToUnichr(thisLine[iitem-1]), _intToUnichr(thisLine[iitem+1]))
                if cVal != cExpected :
                    needThisLine = True
                    break # out of loop over items
        # end of for items
        needLines[iline] = needThisLine
    # end of for lines

    ampIline = 0
    ampItem = (sortSpec[0])[1]  # most recent item before an &

    for iline in range(0, len(sortSpec)-1) :
        thisLine = sortSpec[iline]
        nextLine = sortSpec[iline+1]
        debugThis = _debugStr(thisLine[1])
        debugNext = _debugStr(nextLine[1])
        # Compare end of this line and start of next:
        cVal = ducet.ducetCompare(ducetDict, _intToUnichr(thisLine[-1]), _intToUnichr(nextLine[1]))
        if cVal != 1 or needLines[iline]: # something funny about this line
            firstItem = thisLine[1] if thisLine[0] == "&"  else ampItem
            # Compare start of this line (current &) and start of next:
            cValAmp = ducet.ducetCompare(ducetDict, _intToUnichr(firstItem), _intToUnichr(nextLine[1]))
        else :
            cValAmp = cVal

        if cVal == 1 and cValAmp == 1 :
            # Order and level match.
            ilineFirstOfGroup = iline
        elif cVal > 1 and cValAmp > 0:
            # Order matches, but not level; merge.
            nextLine[0] = "<"
            needLines[iline] = True
            needLines[iline+1] = True
            ilineFirstOfGroup = iline
        elif cVal < 0 and cValAmp > 0 :
            # Initial items are in order, but this line not so much; merge them.
            needLines[iline] = True
            needLines[iline+1] = True
            nextLine[0] = "<"
            ilineFirstOfGroup = iline
        else :
            howFarThis = _howFarOff(sortSpec, _intToUnichr(thisLine[1]), iline, 1, ducetDict)
            howFarNext = _howFarOff(sortSpec, _intToUnichr(nextLine[1]), iline+1, -1, ducetDict)
            if howFarThis == 1 :
                # Next line is out of order; we need: this < next < nextnext.
                nextLine[0] = "<"
                needLines[iline] = True
                needLines[iline+1] = True
                if iline < len(sortSpec) - 2 :
                    nextNextLine = sortSpec[iline+2]
                    nextNextLine[0] = "<"
                    needLines[iline+2] = True
                ilineFirstOfGroup = iline
            elif howFarNext == -1 :
                # This line is out of order.
                if iline == 0 :
                    # Do something special for the first line.
                    thisLine[0] = "&[before 1]a <"
                    # DON'T merge with the following line; it is not necessary and has the effect of creating a long chain.
                    needLines[iline] = True
                    ilineFirstOfGroup = iline
                else :
                    # We need: prev < this < next.
                    thisLine[0] = "<"
                    nextLine[0] = "<"
                    needLines[iline - 1] = True
                    needLines[iline] = True
                    needLines[iline + 1] = True
                    ilineFirstOfGroup = iline - 1
            else :
                # We don't know what we can assume; so we need: prev < this < next < nextnext.
                nextLine[0] = "<"
                needLines[iline] = True
                needLines[iline+1] = True
                if iline > 0 :
                    thisLine[0] = "<"
                    needLines[iline-1] = True
                    ilineFirstOfGroup = iline - 1
                else :
                    ilineFirstOfGroup = iline
                if iline < len(sortSpec) - 1 :
                    nextNextLine = sortSpec[iline+2]
                    nextNextLine[0] = "<"
                    needLines[iline+2] = True

        # end of if...else

        # Remember the current last &.
        fogLine = sortSpec[ilineFirstOfGroup]
        if fogLine[0] == "&" :
            ampIline = ilineFirstOfGroup
            ampItem = fogLine[1]

    #  end of for lines

    # Retain only the lines we need.
    minSpec = []
    for iline in range(0, len(sortSpec)) :
        if needLines[iline] :
            ss = sortSpec[iline]
            minSpec.append(ss)

    return minSpec

# end of _minimizeSortSpec


def _howFarOff(sortSpec, uChar, iline, dir, ducetDict) :
    if dir == 1 :
        lim = len(sortSpec)
        rng = range(iline + 1, lim)
    else :
        lim = 0
        rng = range( iline - 1, -1, -1)

    for iline2 in rng :
        if (sortSpec[iline2])[0] == "&" :
            cVal = ducet.ducetCompare(ducetDict, uChar, _intToUnichr((sortSpec[iline2])[1]))
            if cVal >= (1 * dir) :
                return iline2 - iline

    return iline2 - iline


def _compareToken(token):
    if token == "<": return 1
    if token == "<<": return 2
    if token == "<<<": return 3
    if token == "=": return 0
    return -1  # not a token


def _charToInt(charsStr) :
    result = []
    i = 0
    while i < len(charsStr):
        if charsStr[i:i+2] == "\u" :
            result.append(int(charsStr[i+2:i+6], 16))
            i = i + 5
        elif charsStr[i:i+2] == "\U" :
            result.append(int(charsStr[i+2:i+10], 16))
            i = i + 9
        else : ### isinstance(charItem, list) :
            result.append(ord(charsStr[i]))
        i = i + 1
    # end of while

    return result


def _unicodeEntity(ordValue) :
    if isinstance(ordValue, int) :
        ordValue = [ordValue]

    result = ""
    for x in ordValue :
        if (x) < 128 :
            result += chr(x)
        else :
            uitem = unichr(x)
            hexStr = hex(ord(uitem))
            hexStr = hexStr.replace('0x', '')
            while len(hexStr) < 4 :
                hexStr = '0' + hexStr
            hexStr = '\\u' + hexStr
            result += hexStr

    return result


def _intToUnichr(item) :
    if isinstance(item, int) :
        return unichr(item)

    result = []
    for i in range(0, len(item)) :
        x = item[i]
        if item[i] == ord('\\') and item[i+1] == ord('u') :
            sval = "".join(item[i+2,i+6])
            result.append(unichr(int(sval, 16)))
            i = i + 5
        elif item[i] == ord('\\') and item[i+1] == ord('U') :
            sval = "".join(item[i+2,i+10])
            result.append(unichr(int(sval, 16)))
            i = i + 9
        else :
            result.append(unichr(x))
    return result


def _debugStr(item) :
    if isinstance(item, int) :
        item = [item]
    result = ""
    for x in item :
        if x < 256 :
            result += chr(x)
        else :
            result += "\u" + hex(x)
    result += " ="
    for x in item : result += " " + hex(x)
    return result


def writeLdmlFile_NEW(ldmlTree, ldmlFilename):
    etwr = ETWriter(ldmlTree, silns)
    ldmlOut = Ldml(etwr)
    ldmlOut.normalise()
    ldmlFile = open(ldmlFilename, "wb")
    ldmlOut.serialize_xml(ldmlFile.write)
    ldmlFile.close()


def writeLdmlFile(ldmlTree, ldmlFilename):
    #####ldmlTree.write(ldmlOutputFilename, encoding="utf-8", xml_declaration=True)

    # A simple write() call does not format the new data nicely. Hence the following:
    addTreeWrapping(ldmlTree.getroot())

    outputFile = open(ldmlFilename, "wb")
    sio = StringIO()
    sio.write('<?xml version="1.0" encoding="utf-8"?>\n')
    ldmlTree.write(sio, encoding="utf-8")

    # Annoyingly, the comment right at the beginning of the file needs a newline after.
    fContents = sio.getvalue().replace('><ldml', '>\n<ldml')

    fContents = fContents.replace(' />', '/>')

    outputFile.write(fContents)
    sio.close()
    outputFile.close()


# end of writeLdmlFile


# Make the newly added nodes wrap nicely.
def addTreeWrapping(treeRoot, depth=0, indent=2):
    subElemList = treeRoot.findall('*')
    n = len(subElemList)
    if n:
        treeRoot.text = "\n" + (' ' * (depth + indent))
        for i in range(n):
            addTreeWrapping(subElemList[i], depth + indent, indent)
            subElemList[i].tail = "\n" + (' ' * (depth + indent if i < n - 1 else depth))


def _silnsPrfx():
    silnsPrefix = '{' + silns['sil'] + '}'  # for adding elements using this namespace
    return silnsPrefix


###############################################


# CURRENTLY NOT USED
def _caseEquivalent(item1, item2):
    if item1.lower() == item2 :
        return True
    elif item2.lower() == item1 :
        return True

    return False


# CURRENTLY NOT USED
def _differByDiacs(item1, item2):
    item1 = unichr(ord(item1))
    item2 = unichr(ord(item2))

    decomp1 = _unichrDecomposition(item1)
    decomp2 = _unichrDecomposition(item2)

    # TODO: improve this logic
    if decomp1[0] == decomp2[0] :  # same base
        return True

    return False


# CURRENTLY NOT USED
def _unichrDecomposition(item):
    decomp = unicodedata.decomposition(item)  # produces a string like "0061 0301".

    if decomp == '':
        result = [item]  # no decomposition
    else:
        charDigitList = decomp.split(' ')
        result = []
        for charDigit in charDigitList :
            if charDigit != '' :
                result.append(unichr(int(charDigit, 16)))

    # print item,result
    return result


def _minimizeSortSpecOBSOLETE(sortSpec, ducetDict) :

    needLines = {}
    for iline in range(0, len(sortSpec)) :
        thisLine = sortSpec[iline]
        needThisLine = False
        prevItems = None
        # Try to find something in this line that doesn't fit the DUCET; if so, we definitely need this line.
        for iitem in range(0,len(thisLine)) :
            cExpected = _compareToken(thisLine[iitem])
            if cExpected >= 0 :
                cVal = ducet.ducetCompare(ducetDict, unichr(thisLine[iitem-1]), unichr(thisLine[iitem+1]))
                if cVal != cExpected :
                    needThisLine = True
                    break # out of loop over items
        # end of for ittem
        needLines[iline] = needThisLine
    # end of for iline

    # Now try to find lines that aren't needed with respect to each other.
    actions = {}
    for iline in range(0, len(sortSpec)) :
        thisLine = sortSpec[iline]
        if iline > 0 :
            prevLine = sortSpec[iline-1]
            thisChar = thisLine[1]
            #prevCharFirst = prevLine[1]
            prevChar = prevLine[-1]
            cVal = ducet.ducetCompare(ducetDict, unichr(prevChar), unichr(thisChar)) # end of prev line, start of this
            if cVal == "unknown" :
                actionPrev = "merge"
            elif cVal > 0 :
                # fits DUCET order
                if needLines[iline-1] :  # something non-std in the previous line
                    actionPrev = "merge"
                else :
                    actionPrev = "toss"  # all standard
            else :
                actionPrev = "merge" # something non-std between prev line and this
        else :
            actionPrev = "toss"

        if iline < len(sortSpec)-1 :
            nextLine = sortSpec[iline+1]
            #thisCharFirst = thisLine[1]
            thisChar = thisLine[-1]
            nextChar = nextLine[1]
            cVal = ducet.ducetCompare(ducetDict, unichr(thisChar), unichr(nextChar))
            if cVal == "unknown" :
                actionNext = "merge"
            elif cVal > 0 :
                # fits DUCET order
                if needLines[iline+1] :  # something non-std in the next line
                    actionNext = "merge"
                else :
                    actionNext = "toss"  # all standard
            else :
                actionNext = "merge" # something non-std between this line and next
        else :
            actionNext = "toss"

        if needLines[iline] :
            if actionPrev == "merge" and actionNext == "merge" :
                action = "mergeBoth"
            elif actionPrev == "merge" :
                action = "mergePrev"
            elif actionNext == "merge" :
                action = "mergeNext"
            else :
                action = "newline"
        else :
            if actionPrev == "merge" and actionNext == "merge" :
                action = "mergeBoth"
            elif actionPrev == "merge" :
                action = "mergePrevFirst"
            elif actionNext == "merge" :
                action = "mergeNextLast"
            else :
                action = "toss"

        actions[iline] = action

    # end of for iline...

    minSpec = []
    for iline in range(0, len(sortSpec)) :
        if actions[iline] != "toss" :
            ss = sortSpec[iline]
            if actions[iline] == "mergePrev" or actions[iline] == "mergePrevFirst" :
                ss[0] = "<"
            minSpec.append(ss)

    return minSpec

# end of _minimizeSortSpec



# Top level

run()