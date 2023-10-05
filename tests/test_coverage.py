import os, json
import requests
import logging, os, re, unicodedata
from langtag import langtag, lookup
from sldr.utils import find_parents
from argparse import ArgumentParser


def iscldr(ldml):
    i = ldml.ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.ldml.namespaces.items()})
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

def test_core(ldml):
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    corereqs = {
        "characters/exemplarCharacters": "Main Exemplar Characters", 
        "characters/exemplarCharacters[@type='auxiliary']": "Auxiliary Exemplar Characters", 
        "characters/exemplarCharacters[@type='punctuation']": "Punctuation Exemplar Characters",
        "characters/exemplarCharacters[@type='numbers']": "Numbers Exemplar Characters",
    }
    coremissing = {}
    for r in corereqs.keys():
        req = ldml.ldml.root.find(r)
        if req is None:
            coremissing[r]=corereqs.get(r)
    c_missingcount = len(coremissing)
    if c_missingcount == 0: 
        return
    assert False, filename + " is missing " + str(c_missingcount) + " Core Requirement(s): " + str(list(coremissing.values()))    

def test_basic(ldml):
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    lang = ldml.ldml.root.find('.//identity/language').get('type')
    i = ldml.ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.ldml.namespaces.items()})
    script = i.get("script")
    territory = i.get("defaultRegion")
    # bug: if script or defaultRegion is not in SIL identity block, error happens. Is this an issue where data needs to be in ID block or an issue where test should work around this scenario?
    basicreqs = {
        # Locale Names: Patterns
        "localeDisplayNames/localeDisplayPattern/localePattern": "Locale Display Names Pattern",
        "localeDisplayNames/localeDisplayPattern/localeSeparator": "Locale Display Names Separator",
        # Locale Names: Vocab
        "localeDisplayNames/languages/language[@type='" + lang + "']": "Locale Display Names Autonym",
        "localeDisplayNames/languages/language[@type='en']": "Locale Display Names English",
        "localeDisplayNames/scripts/script[@type='"+ script + "']": "Locale Display Names Default Script",
        "localeDisplayNames/territories/territory[@type='" + territory + "']": "Locale Display Names Default Region", 
        "localeDisplayNames/measurementSystemNames/measurementSystemName[@type='metric']": "Measurement System Names Metric", 
        "localeDisplayNames/measurementSystemNames/measurementSystemName[@type='UK']": "Measurement System Names UK",
        "localeDisplayNames/measurementSystemNames/measurementSystemName[@type='US']": "Measurement System Names US",
        "localeDisplayNames/codePatterns/codePattern[@type='language']": "Locale Display Names Language Code Pattern",
        "localeDisplayNames/codePatterns/codePattern[@type='script']": "Locale Display Names Script Code Pattern",
        "localeDisplayNames/codePatterns/codePattern[@type='territory']": "Locale Display Names Territory Pattern",
        # Delimiters
        "delimiters/quotationStart": "Quotation Start Delimiters",
        "delimiters/quotationEnd": "Quotation End Delimiters",
        "delimiters/alternateQuotationStart": "Alt Quotation Start Delimiters", 
        "delimiters/alternateQuotationEnd": "Alt Quotation End Delimiters", 
        # Dates: Months Vocab
        "dates/calendars/calendar[@type='gregorian']/months/monthContext[@type='format']/monthWidth[@type='wide']/month[@type='1']": "Gregorian Month 1 Wide Name",
        "dates/calendars/calendar[@type='gregorian']/months/monthContext[@type='format']/monthWidth[@type='wide']/month[@type='2']": "Gregorian Month 2 Wide Name", 
        "dates/calendars/calendar[@type='gregorian']/months/monthContext[@type='format']/monthWidth[@type='wide']/month[@type='3']": "Gregorian Month 3 Wide Name",
        "dates/calendars/calendar[@type='gregorian']/months/monthContext[@type='format']/monthWidth[@type='wide']/month[@type='4']": "Gregorian Month 4 Wide Name",
        "dates/calendars/calendar[@type='gregorian']/months/monthContext[@type='format']/monthWidth[@type='wide']/month[@type='5']": "Gregorian Month 5 Wide Name",
        "dates/calendars/calendar[@type='gregorian']/months/monthContext[@type='format']/monthWidth[@type='wide']/month[@type='6']": "Gregorian Month 6 Wide Name",
        "dates/calendars/calendar[@type='gregorian']/months/monthContext[@type='format']/monthWidth[@type='wide']/month[@type='7']": "Gregorian Month 7 Wide Name",
        "dates/calendars/calendar[@type='gregorian']/months/monthContext[@type='format']/monthWidth[@type='wide']/month[@type='8']": "Gregorian Month 8 Wide Name",
        "dates/calendars/calendar[@type='gregorian']/months/monthContext[@type='format']/monthWidth[@type='wide']/month[@type='9']": "Gregorian Month 9 Wide Name",
        "dates/calendars/calendar[@type='gregorian']/months/monthContext[@type='format']/monthWidth[@type='wide']/month[@type='10']": "Gregorian Month 10 Wide Name", 
        "dates/calendars/calendar[@type='gregorian']/months/monthContext[@type='format']/monthWidth[@type='wide']/month[@type='11']": "Gregorian Month 11 Wide Name",
        "dates/calendars/calendar[@type='gregorian']/months/monthContext[@type='format']/monthWidth[@type='wide']/month[@type='12']": "Gregorian Month 12 Wide Name",
        # Dates: Week Vocab
        "dates/calendars/calendar[@type='gregorian']/days/dayContext[@type='format']/dayWidth[@type='wide']/day[@type='sun']": "Gregorian Sunday Wide Name",
        "dates/calendars/calendar[@type='gregorian']/days/dayContext[@type='format']/dayWidth[@type='wide']/day[@type='mon']": "Gregorian Monday Wide Name",
        "dates/calendars/calendar[@type='gregorian']/days/dayContext[@type='format']/dayWidth[@type='wide']/day[@type='tue']": "Gregorian Tuesday Wide Name",
        "dates/calendars/calendar[@type='gregorian']/days/dayContext[@type='format']/dayWidth[@type='wide']/day[@type='wed']": "Gregorian Wednesday Wide Name",
        "dates/calendars/calendar[@type='gregorian']/days/dayContext[@type='format']/dayWidth[@type='wide']/day[@type='thu']": "Gregorian Thursday Wide Name",
        "dates/calendars/calendar[@type='gregorian']/days/dayContext[@type='format']/dayWidth[@type='wide']/day[@type='fri']": "Gregorian Friday Wide Name",
        "dates/calendars/calendar[@type='gregorian']/days/dayContext[@type='format']/dayWidth[@type='wide']/day[@type='sat']": "Gregorian Saturday Wide Name",
        # Dates: Period Vocab
        "dates/calendars/calendar[@type='gregorian']/dayPeriods/dayPeriodContext[@type='format']/dayPeriodWidth[@type='wide']/dayPeriod[@type='am']": "Gregorian AM Wide Name",
        "dates/calendars/calendar[@type='gregorian']/dayPeriods/dayPeriodContext[@type='format']/dayPeriodWidth[@type='wide']/dayPeriod[@type='pm']": "Gregorian PM Wide Name",
        # Dates: Patterns
        "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='Hm']": "Gregorian Date/Time Format Hm",
        "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='hm']": "Gregorian Date/Time Format hm",
        "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='Hms']": "Gregorian Date/Time Format Hms",
        "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='hms']": "Gregorian Date/Time Format hms",
        "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='Hmsv']": "Gregorian Date/Time Format Hmsv", 
        "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='hmsv']": "Gregorian Date/Time Format hmsv",
        "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='yMd']": "Gregorian Date/Time Format yMd",
        "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='yMMMd']": "Gregorian Date/Time Format yMMMd",
        "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/intervalFormats/intervalFormatFallback": "Gregorian Date/Time Interval Format Fallback",
        # Time Zones
        "dates/timeZoneNames/hourFormat": "Time Zone Hour Format",
        "dates/timeZoneNames/gmtFormat": "Time Zone gmtFormat",
        "dates/timeZoneNames/gmtZeroFormat": "Time Zone gmtZero Format",
        "dates/timeZoneNames/regionFormat": "Time Zone Default Region Format",
        "dates/timeZoneNames/regionFormat[@type='daylight']": "Time Zone Daylight Time Region Format",
        "dates/timeZoneNames/regionFormat[@type='standard']": "Time Zone Standard Time Region Format",
        "dates/timeZoneNames/fallbackFormat": "Time Zone Fallback Format",
        "dates/timeZoneNames/metazone[@type='GMT']/long/standard": "Time Zone GMT Long Name",
        # Numbers
        "numbers/defaultNumberingSystem": "Default Numbering System",
        "numbers/otherNumberingSystems/native": "Other Native Numbering Systems",        
        "numbers/symbols[@numberSystem='latn']/decimal": "Latin Numbers Decimal Symbol",
        "numbers/symbols[@numberSystem='latn']/group": "Latin Numbers Group Symbol",
        "numbers/symbols[@numberSystem='latn']/percentSign": "Latin Numbers Percent Sign Symbol",
        "numbers/symbols[@numberSystem='latn']/plusSign": "Latin Numbers Plus Sign Symbol",
        "numbers/symbols[@numberSystem='latn']/minusSign": "Latin Numbers Minus Sign Symbol",
        "numbers/decimalFormats[@numberSystem='latn']/decimalFormatLength/decimalFormat/pattern": "Latin Numbers Decimal/Group Format Pattern",
        "numbers/scientificFormats[@numberSystem='latn']/scientificFormatLength/scientificFormat/pattern": "Latin Numbers Scientific Format Pattern",
        "numbers/percentFormats[@numberSystem='latn']/percentFormatLength/percentFormat/pattern": "Latin Numbers Percent Format Pattern",
        "numbers/currencyFormats[@numberSystem='latn']/currencyFormatLength/currencyFormat/pattern": "Latin Numbers Currency Format Pattern"
    }
    basicmissing = {}
    ldnpatternsmissing = {}
    ldnvocabmissing = {}
    delimmissing = {}
    datesmonthsmissing = {}
    datesweekmissing = {}
    datesperiodsmissing = {}
    datespatternsmissing = {}
    timezonesmissing = {}
    numbersmissing = {}
    for r in basicreqs.keys():
        req = ldml.ldml.root.find(r)
        if req is None:
            basicmissing[r] = basicreqs.get(r)
            # the below is sorting results in case you only want specific types of missing data
            if r.startswith("localeDisplayNames/localeDisplayPattern/"):
                ldnpatternsmissing[r] = basicreqs.get(r)
            elif r.startswith("localeDisplayNames"):
                ldnvocabmissing[r] = basicreqs.get(r)
            elif r.startswith("delimiters"):
                delimmissing[r] = basicreqs.get(r)
            elif r.startswith("dates/calendars/calendar[@type='gregorian']/months/"):
                datesmonthsmissing[r] = basicreqs.get(r)
            elif r.startswith("dates/calendars/calendar[@type='gregorian']/days/"):
                datesweekmissing[r] = basicreqs.get(r)
            elif r.startswith("dates/calendars/calendar[@type='gregorian']/dayPeriods/"):
                datesperiodsmissing[r] = basicreqs.get(r)
            elif r.startswith("dates/calendars/calendar[@type='gregorian']/dateTimeFormats/"):
                datespatternsmissing[r] = basicreqs.get(r)
            elif r.startswith("dates/timeZoneNames/"):
                timezonesmissing[r] = basicreqs.get(r)
            elif r.startswith("numbers/"):
                numbersmissing[r] = basicreqs.get(r)
    b_missingcount = len(basicmissing)
    # the below probs dont all need their own variables, but rather something like 'given the argument for specific types of data, count this one' or something
    b_missingldnpcount = len(ldnpatternsmissing)
    b_missingldnvcount = len(ldnvocabmissing)
    b_missingdelimcount = len(delimmissing)
    b_missingmonthcount = len(datesmonthsmissing)
    b_missingweekcount = len(datesweekmissing)
    b_missingperiodcount = len(datesperiodsmissing)
    b_missingdatepcount = len(datespatternsmissing)
    b_missingtzcount = len(timezonesmissing)
    b_missingnumberscount = len(numbersmissing)
    if b_missingcount == 0: 
        return
    assert False, filename + " is missing " + str(b_missingcount) + " Basic Requirement(s): " + str(list(basicmissing.values()))    


# trying out argument parser and command line stuff
#one for a spec file and one for a range maybe?


def parse_core():
    parser = ArgumentParser()
    parser.add_argument('ldml', help = 'file to check')
    args = vars(parser.parse_args)
    ldml = ldml(args.setdefault('ldml'))
    filename = os.path.basename(ldml.ldml.fname)    # get filename for reference
    corereqs = {
        "characters/exemplarCharacters": "Main Exemplar Characters", 
        "characters/exemplarCharacters[@type='auxiliary']": "Auxiliary Exemplar Characters", 
        "characters/exemplarCharacters[@type='punctuation']": "Punctuation Exemplar Characters",
        "characters/exemplarCharacters[@type='numbers']": "Numbers Exemplar Characters",
    }
    coremissing = {}
    for r in corereqs.keys():
        req = ldml.ldml.root.find(r)
        if req is None:
            coremissing[r]=corereqs.get(r)
    c_missingcount = len(coremissing)
    if c_missingcount == 0: 
        return
    else:
        print(filename + " is missing " + str(c_missingcount) + " Core Requirement(s): " + str(list(coremissing.values())))  