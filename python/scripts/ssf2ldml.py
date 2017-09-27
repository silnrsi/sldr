#!/usr/bin/python

# Read a Paratext .ssf file, convert the relevant data to LDML, and insert into an LDML file.
import sys
import collections
import codecs
import copy
import os
import unicodedata

# For calling DBLAuthV1 class:
# The requests module may need to be installed separately; it does not appear to be part of the standard Python.
import requests
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime

# The authorization key is stored in a different file:
try:
    import dblauthkey
except ImportError:
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    import dblauthkey

import json

from ConfigParser import RawConfigParser

supplementalPath = "/../lib/sldr/"

try:
    from ldml import Ldml
except ImportError:
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + supplementalPath))
    from ldml import Ldml
    
import ducet

##import xml.etree.cElementTree as etree
# lxml preserves comments, also handles namespaces better:
from xml.etree import ElementTree as etree
from cStringIO import StringIO

silns = {'sil' : "urn://www.sil.org/ldml/0.1" }


class DBLAuthV1(requests.auth.AuthBase):
    authorization_header = 'X-DBL-Authorization'

    def __init__(self, api_token, private_key):
        super(DBLAuthV1, self).__init__()
        self.api_token = api_token.lower()
        self.private_key = private_key.lower()

    def __call__(self, r):
        r.headers[self.authorization_header] = self.make_authorization_header(r)
        return r

    def make_authorization_header(self, request):
        import hmac
        import hashlib

        mac = hmac.new(self.api_token, None, hashlib.sha1)
        mac.update(self.signing_string_from_request(request))
        mac.update(self.private_key.lower())
        return 'version=v1,token=%s,signature=%s' % (self.api_token, mac.hexdigest().lower())

    def signing_string_from_request(self, request):
        dbl_header_prefix = 'x-dbl-'
        signing_headers = ['content-type', 'date']

        method = request.method
        # use request uri, but not any of the arguments.
        path = request.path_url.split('?')[0]
        collected_headers = {}

        for key, value in request.headers.iteritems():
            if key == self.authorization_header:
                continue
            k = key.lower()
            if k in signing_headers or k.startswith(dbl_header_prefix):
                collected_headers[k] = value.strip()

        # these keys get empty strings if they don't exist
        if 'content-type' not in collected_headers:
            collected_headers['content-type'] = ''
        if 'date' not in collected_headers:
            collected_headers['date'] = ''

        sorted_header_keys = sorted(collected_headers.keys())

        buf = "%s %s\n" % (method, path)
        for key in sorted_header_keys:
            val = collected_headers[key]
            if key.startswith(dbl_header_prefix):
                buf += "%s:%s\n" % (key, val)
            else:
                buf += "%s\n" % val
        return buf

# end of class DBLAuthV1


class DBLReader(object):

    def __init__(self):
        (key1, key2) = dblauthkey.authkey()
        self.auth = DBLAuthV1(key1, key2)

    def testAccess(self):
        response = requests.get('https://thedigitalbiblelibrary.org', auth=self.auth,
                                headers={'Date': format_date_time(mktime(datetime.now().timetuple())),
                                         'Content-Type': 'application/json'})
        return response.status_code

    def getLicenses(self):
        response = requests.get('https://thedigitalbiblelibrary.org/api/licenses', auth=self.auth,
                                headers={'Date': format_date_time(mktime(datetime.now().timetuple())),
                                         'Content-Type': 'application/json'})
        if response.status_code == 200:
            licensesJson = response.content
            result = json.loads(licensesJson)
        return response.status_code

    def getEntries(self):
        response = requests.get('https://thedigitalbiblelibrary.org/api/publishable_entries_list', auth=self.auth,
                                headers={'Date': format_date_time(mktime(datetime.now().timetuple())),
                                         'Content-Type': 'application/json'})
        if response.status_code == 200:
            entriesJson = response.content
            result = json.loads(entriesJson)
            return result
        else:
            entriesJson = ""
            result = {}
            return response.status_code


    def getOneEntry(self, entryId):
        # 8 = Creative Commons
        # 126 = WBT Non-Commercial Digital Text Distribution Agreement with YouVersion
        response = requests.get('https://thedigitalbiblelibrary.org/api/entries/' + entryId + "/revision/latest/license/8",
                                auth=self.auth,
                                headers={'Date': format_date_time(mktime(datetime.now().timetuple())),
                                         'Content-Type': 'application/json'})
        if response.status_code == 200:
            entryJson = response.content
            result = json.loads(entryJson)
            return result
        else:
            entryJson = ""
            result = {}
            return response.status_code


#end of class DBLReader


def loadssf(ldml, ssfFilename):
    if isinstance(ssfFilename, basestring):
        ssfFile = open(ssfFilename, 'rb')
    else:
        ssfFile = ssfFilename

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

    if ssfLangData['DefaultFont'] or ssfLangData['DefaultFontSize'] :
        _addSsfDataFont(ldml, ssfLangData['DefaultFont'], ssfLangData['DefaultFontSize'])
    if ssfLangData['Pairs'] :
        _addSsfDataPairs(ldml, ssfLangData['Pairs'])
    if ssfLangData['Quotes'] :
        _addSsfDataQuotes(ldml, ssfLangData['Quotes'])
    if ssfLangData['InnerQuotes'] :
        _addSsfDataInnerQuotes(ldml, ssfLangData['InnerQuotes'])
    if ssfLangData['InnerInnerQuotes'] :
        _addSsfDataInnerInnerQuotes(ldml, ssfLangData['InnerInnerQuotes'])


def loadlds(ldml, ldsFilename, ducetDict):
    if isinstance(ldsFilename, basestring):
        ldsFile = open(ldsFilename, 'r')
    else:
        ldsFile = ldsFilename
    ldsConfig = RawConfigParser()
    ldsConfig.read(ldsFilename)     # let exception rise up
    sortSpecString = calcSortLdsData(ldml, ldsConfig, ducetDict)

    if not len(sortSpecString):
        return

    collationElem = ldml.ensure_path('collations/collation[@type="standard"]')[0]
    if not collationElem.find('cr'):
        crElem = etree.SubElement(collationElem, 'cr')
        crElem.text = sortSpecString
        # CDATA handling done by ldml object, we hope


def _addSsfDataFont(ldml, defaultFontValue, defaultSizeValue) :
    # DefaultFont, DefaultFontSize ->
    # special/sil:external-resources/sil:fontrole[@types="default"]/sil:font[@name, @size]
    # TODO: this isn't quite right since it should handle an existing sil:fontrole[@types="default heading"]
    fontElem = ldml.ensure_path('special/sil:external-resources/sil:fontrole[@types="default"]/sil:font')[0]
    if defaultFontValue :
        fontElem.set('name', defaultFontValue)
    if defaultSizeValue :
        fontElem.set('size', defaultSizeValue)


def _addSsfDataPairs(ldml, pairsValue) :
    # Pairs ->
    # delimiters/special/sil:matched-pairs/sil:matched-pair/@open, @close
    matchedElem = ldml.ensure_path('delimiters/special/sil:matched-pairs')[0]
    for pair in pairsValue.split(' '):
        (openVal, closeVal) = pair.split('/')
        openVal = openVal.strip()
        closeVal = closeVal.strip()
        if not _findPair(matchedElem, openVal, closeVal) :
            matchElem = ldml.subelement(matchedElem, 'sil:matched-pair',
                                        attrib={'open': openVal, 'close': closeVal})

def _findPair(pairElements, openValue, closeValue) :
    for elem in pairElements :
        if elem.get('open') == openValue and elem.get('close') == closeValue :
            return True
    return False

    
def _addSsfDataQuotes(ldml, quotesValue) :
    # Quotes ->
    # delimiters/quotationStart, delimiters/quotationEnd
    qStartElem = ldml.ensure_path('delimiters/quotationStart')[0]
    qEndElem = ldml.ensure_path('delimiters/quotationEnd')[0]
    (qStart, qEnd) = quotesValue.split(' ')
    qStartElem.text = qStart
    qEndElem.text = qEnd


def _addSsfDataInnerQuotes(ldml, quotesValue) :
    # InnerQuotes ->
    # delimiters/alternateQuotationStart, delimiters/alternateQuotationEnd
    qStartElem = ldml.ensure_path('delimiters/alternateQuotationStart')[0]
    qEndElem = ldml.ensure_path('delimiters/alternateQuotationEnd')[0]
    (qStart, qEnd) = quotesValue.split(' ')
    qStartElem.text = qStart
    qEndElem.text = qEnd

#end of _addSsfDataInnerQuotes

def _addSsfDataInnerInnerQuotes(ldml, quotesValue) :
    # InnerInnerQuotes ->
    # delimiters/special/sil:quotation-marks[@level="3"]/@open, @close
    qMark3Elem = ldml.ensure_path('delimiters/special/sil:quotation-marks[@level="3"]')[0]
    (qStart, qEnd) = quotesValue.split(' ')
    qMark3Elem.set('open', qStart)
    qMark3Elem.set('close', qEnd)


def _addSsfDataContinueQuotes(ldml, contValue, contInnerValue) :
    # ContinueQuotes ->
    # delimiters/special/sil:quotation-marks[@paraContinueType]/@open, @close
    if _valueNotNo(contValue):
        ldml.ensure_path('delimiters/special/sil:quotation-marks[@level="1"][@paraContinueType="{}"]'.format(contValue))
    if _valueNotNo(contInnerValue):
        ldml.ensure_path('delimiters/special/sil:quotation-marks[@level="2"][@paraContinueType="{}"]'.format(contInnerValue))

def _valueNotNo(value) :
    if value is None :
        return False
    if value.lower() == "no" :
        return False
    if value.lower() == "false" :
        return False
    return True


def calcSortLdsData(ldml, ldsConfig, ducetDict) :
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

            if len(spaceItems) == 2 and spaceItems[0].lower() == spaceItems[1].lower():
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

                #for i in range(len(slashItems)) : slashItems[i] = _charToInt(slashItems[i])
                slashItems = [_charToInt(x) for x in slashItems]
                #if prevSlashItems is not None and differByDiacs(prevSlashItems[0], slashItems[0]) :
                slashSep = "<<"

                if len(slashItems) == 2 :  ### and _caseEquivalent(slashItems[0], slashItems[1]) :
                    # upper/lower
                    # TODO: remove this branch
                    sortSpecItems.extend((spaceSep, slashItems[0], "<<<", slashItems[1]))
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
                    elif isinstance(item, str) and (item[0]) == "&" :
                        sortSpecString += item[0] + _unicodeEntity(item[1:]) + " "
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

    return sortSpecString


def _minimizeSortSpec(sortSpec, ducetDict) :
    # First, look at each line individually and see which have information we need to retain.
    # Note that we don't try to minimize the lines themselves, just the set of lines.
    needLines = {}
    for iline in range(len(sortSpec)) :
        thisLine = sortSpec[iline]
        needThisLine = False
        prevItems = None
        # Try to find something in this line that doesn't fit the DUCET; if so, we definitely need this line.
        for iitem in range(len(thisLine)) :
            cExpected = _compareToken(thisLine[iitem])
            if cExpected >= 0 :
                cVal = ducet.ducetCompare(ducetDict, _intToUnichr(thisLine[iitem-1]), _intToUnichr(thisLine[iitem+1]))
                if cVal != cExpected :
                    needThisLine = True
                    break # out of loop over items
        needLines[iline] = needThisLine

    ampIline = 0
    ampItem = (sortSpec[0])[1]  # most recent item before an &

    for iline in range(len(sortSpec)-1) :
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

        # Remember the current last &.
        fogLine = sortSpec[ilineFirstOfGroup]
        if fogLine[0] == "&" :
            ampIline = ilineFirstOfGroup
            ampItem = fogLine[1]

    # Retain only the lines we need.
    minSpec = []
    for iline in range(len(sortSpec)) :
        if needLines[iline] :
            minSpec.append(sortSpec[iline])

    return minSpec

def _howFarOff(sortSpec, uChar, iline, dir, ducetDict) :
    if dir == 1 :
        rng = range(iline + 1, len(sortSpec))
    else :
        rng = range(iline - 1, -1, -1)

    for iline2 in rng :
        if (sortSpec[iline2])[0] == "&" :
            cVal = ducet.ducetCompare(ducetDict, uChar, _intToUnichr((sortSpec[iline2])[1]))
            if cVal >= (1 * dir) :
                return iline2 - iline

    return iline2 - iline

def _compareToken(token):
    if token == "<": return 1
    elif token == "<<": return 2
    elif token == "<<<": return 3
    elif token == "=": return 0
    return -1  # not a token

def _charToInt(charsStr) :
    # There's a codec that will do this
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
        # what about \, &, < and other escaped chars (e.g. < 33)
        if (x) < 128 :
            result += chr(x)
        # and \U support?
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
    for i in range(len(item)) :
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
    result = "".join(map(unichr, item))
    result += " =" + " ".join(map(hex, item))
    return repr(result)


# Top level
def _run() :
    mainPath = "C:/WS_Tech/SSF2LDML/"
    inputPath = mainPath + "testdata/"

    #(key1, key2) = dblauthkey.authkey()
    #tauth = DBLAuthV1(key1, key2)
    #response = requests.get('https://thedigitalbiblelibrary.org/api/publishable_entries_list', auth=tauth,
    #                        headers={'Date': format_date_time(mktime(datetime.now().timetuple())),
    #                                 'Content-Type': 'application/json'})

    dblreader = DBLReader()
    code = dblreader.testAccess()
    t = dblreader.getLicenses()
    if code != 200:
        print "ERROR in accessing DBL; HTTP response code = ",code
    entriesDict = dblreader.getEntries()
    if isinstance(entriesDict, int):
        print "ERROR in obtaining DBL entries; HTTP response code = ",code
    else:
        entriesCnt = entriesDict['count']
        entriesList = entriesDict['list']
        for entry in entriesList:
            entryId = entry['id']
            entryLangCode = entry['language_code']
            entryInfo = dblreader.getOneEntry(entryId)


    #testLangs = [('aau','Latn'), ('aca','Latn')]
    testLangs = [('zzz', 'Latn')]
    
    #ldml.test_import()

    import sys
    if sys.maxunicode == 0x10FFFF:
        print 'Python built with UCS4 (wide unicode) support'
    else:
        print 'Python built with UCS2 (narrow unicode) support'

    ducetDict = ducet.readDucet()

    for (langCode, scriptCode) in testLangs:
        ldmlFilename = inputPath + langCode + '/' + langCode + "_" + scriptCode + ".xml"
        if os.path.exists(ldmlFilename):
            ldml = Ldml(ldmlFilename, ducetDict)
        else:
            ldml = Ldml(None, ducetDict)

        ssfFilename = inputPath + langCode + '/' + langCode + ".ssf"
        ldsFilename = inputPath + langCode + '/' + langCode + ".lds"
        if os.path.isfile(ssfFilename):
            loadssf(ldml, ssfFilename)
            if os.path.isfile(ldsFilename):
                loadlds(ldml, ldsFilename)
            ldmlFile = open(ldmlOutputFilename, 'rb')
            ldml.serialize_xml(ldmlFile.write)
        else :
            print "missing SSF file: " + ssfFilename

    print ""  
    print "Done"



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--ldml',help='input LDML base file')
    parser.add_argument('-s','--ssf',help='input SSF file')
    parser.add_argument('-d','--lds',help='input LDS file')
    parser.add_argument('-o','--outfile',help='output LDML file')
    args = parser.parse_args()
    if not args.ssf:
        _run()

    if args.ldml:
        ldml = Ldml(args.ldml)
    else:
        ldml = Ldml(None)
    if args.ssf:
        loadssf(ldml, args.ssf)
    if args.lds:
        import ducet
        ducetDict = ducet.readDucet()
        loadlds(ldml, args.lds, ducetDict)
    if args.outfile:
        outf = open(args.outfile, 'rb')
    else:
        outf = sys.stdout
    ldml.serialize_xml(outf.write)

