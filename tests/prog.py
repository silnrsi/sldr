import os, json
import requests
import logging, re, unicodedata
from langtag import langtag, lookup
from sldr.utils import find_parents
from argparse import ArgumentParser
from sldr.ldml import Ldml, _alldrafts, getldml


root_sldr = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sldr")
#if this gets moved out of the sldr/tests folder and put somewhere else, need to make sure that this line and possibly the 'filep' variable is changed to reflect how to get back to the sldr folder (the one holding the alphabetical directories)

#theoretically if i wanted to run this on the whole sldr i'd have to do a for loop using the directory and everything in it but that'll get figured out later
#when do that make sure theres a way to skip cldr

parser = ArgumentParser()
parser.add_argument('ldml', help = 'langtag to check, same format as if in one of the tests (no .xml, use \'-\' instead of \'_\', etc.)')
#add argument for searching entire sldr instead of one spec file (might need to make initial ldml optional then)? argument for if you want a range vs one file?
parser.add_argument('-c', '--coverage', choices = ["core", "basic", "both"], default = "both", help = "level of coverage want checking for")
#add argument for filtering categories of basic data
#add argument for if you want it to print out the specific missing things or just the amount missing
#add argument for if you want it to print out specific xml paths for each missing thing or not (if so need to make it somewhat easy to read)
#add argument for filtering entire sldr by region
#add argument for filtering entire sldr by character range (i.e. langtags starting with a - c)
#add argument for filtering entire sldr by script
#add argument for only printing files missing beyond a certain percentage of data
#add argument for only printing files missing a specific category of data
args = vars(parser.parse_args())
print(args)

tag = args.setdefault('ldml')
filep = os.path.join(root_sldr, tag[0], tag.replace("-", "_")+".xml")
#see under 'root_sldr' about needing to change if this file is moved
if os.path.exists(filep):
    ldml = Ldml(filep)


filename = os.path.basename(ldml.fname)    # get filename for reference
lang = ldml.root.find('.//identity/language').get('type')
i = ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.namespaces.items()})
script = i.get("script")
territory = i.get("defaultRegion")
# bug: if script or defaultRegion is not in SIL identity block, error happens. Is this an issue where data needs to be in ID block or an issue where test should work around this scenario?

corereqs = {
    "characters/exemplarCharacters": "Main Exemplar Characters", 
    "characters/exemplarCharacters[@type='auxiliary']": "Auxiliary Exemplar Characters", 
    "characters/exemplarCharacters[@type='punctuation']": "Punctuation Exemplar Characters",
    "characters/exemplarCharacters[@type='numbers']": "Numbers Exemplar Characters",
}
coremissing = {}

# might break this list into separate lists per cateogry and just tell the parser to go through all of them if the user doesn't want to filter
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
#for categories of basic data:
ldnpatternsmissing = {}
ldnvocabmissing = {}
delimmissing = {}
datesmonthsmissing = {}
datesweekmissing = {}
datesperiodsmissing = {}
datespatternsmissing = {}
timezonesmissing = {}
numbersmissing = {}

coverage = args.setdefault('coverage')

if coverage == "core" or "both":
    for r in corereqs.keys():
        req = ldml.root.find(r)
        if req is None:
            coremissing[r]=corereqs.get(r)
    c_missingcount = len(coremissing)
    if c_missingcount != 0 and coverage == "core": 
        print(filename + " is missing " + str(c_missingcount) + " Core Requirement(s): " + str(list(coremissing.values())))  

if coverage == "basic" or "both":
    for r in basicreqs.keys():
        req = ldml.root.find(r)
        if req is None:
            basicmissing[r] = basicreqs.get(r)
            # the below is sorting results in case you only want specific categories of missing data. 
            # no way to actually access them atm in the parser and will probs need to be moved into a separate if statement or something
            # keeping them here for now so that i don't loose track of them
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
    # depending on how I end up handling the categories of data element, the counters below might not be necessary
    # could be narrowed to a function saying "count the list that we are using right now" or something like that
    # also these variable names are getting a bit ridiculous but i'll fix them later when I feel more confident that I'll remember what each one does
    b_missingldnvcount = len(ldnvocabmissing)
    b_missingdelimcount = len(delimmissing)
    b_missingmonthcount = len(datesmonthsmissing)
    b_missingweekcount = len(datesweekmissing)
    b_missingperiodcount = len(datesperiodsmissing)
    b_missingdatepcount = len(datespatternsmissing)
    b_missingtzcount = len(timezonesmissing)
    b_missingnumberscount = len(numbersmissing)

    if b_missingcount != 0 and coverage == "basic": 
        print(filename + " is missing " + str(b_missingcount) + " Basic Requirement(s): " + str(list(basicmissing.values())))

if coverage == "both" and (c_missingcount or b_missingcount) != 0:
    print(filename + " is missing " + str(c_missingcount) + " Core Requirement(s) and " + str(b_missingcount) + " Basic Requirement(s).")
    if c_missingcount != 0:
        print("Missing Core: " + str(list(coremissing.values())))
    if b_missingcount != 0:
        print("Missing Basic: "+ str(list(basicmissing.values())))
        # dont forget to incorporate categories here too.