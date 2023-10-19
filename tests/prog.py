import os, json
import requests
import logging, re, unicodedata
from langtag import langtag, lookup
from sldr.utils import find_parents
from argparse import ArgumentParser
from sldr.ldml import Ldml, _alldrafts, getldml

def resultformatter(str, filter, fulllist, result):
    if filter.index(str) != 0:
        fulllist += "\n"
        if filter.index(str) != (len(filter)-1):
            result += (", ")
        elif len(filter) == 2:
            result += (" and ")
        else:
            result += (", and ")
    return fulllist, result


root_sldr = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sldr")
#if this gets moved out of the sldr/tests folder and put somewhere else, need to make sure that this line and possibly the 'filep' variable is changed to reflect how to get back to the sldr folder (the one holding the alphabetical directories)

#theoretically if i wanted to run this on the whole sldr i'd have to do a for loop using the directory and everything in it but that'll get figured out later
#when do that make sure theres a way to skip cldr? maybe not; there may be remnants of seed data that are lurking from cldr 

parser = ArgumentParser()
parser.add_argument('ldml', help = 'The langtag of the file you are examining. It should be the file name with \'-\' replacing \'_\' and without \'.xml\' at the end. If you are familiar with the pytests used on the SLDR, it is the same format.')
#add argument for searching entire sldr instead of one spec file (might need to make initial ldml optional then)? argument for if you want a range vs one file?
parser.add_argument('-c', '--coverage', choices = ["core", "basic", "both"], default = "both", help = "The CLDR coverage level you are searching for. Options are 'core', 'basic', or the default 'both'.")
#add argument for filtering categories of basic data
parser.add_argument('-f', '--filter', action= 'append', choices = ['ldnp', 'ldnv', 'delim', 'month', 'week', 'ampm', 'dtform', 'tzones', 'num'], help = "Used to filter for specific categories of Basic data. Multiple options can be selected, and each will be displayed individually. Options are 'ldnp' (Locale Display Names Patterns), 'ldnv' (Locale Display Names Vocab), 'delim' (Delimiters), 'month' (Gregorian Wide Months Vocab), 'week' (Gregorian Wide Days of the Week Vocab), 'ampm' (Gregorian Wide Day Period Vocab), 'dtform' (Date/Time Format), 'tzones' (Time Zone Vocab), and 'num' (Numbers). By default, no filtering occurs.")
#this should also allow for multiple choices. should put choices in a list. 
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

coverage = args.setdefault('coverage')
filter_unsorted = args.setdefault('filter')
sorted = ['ldnp', 'ldnv', 'delim', 'month', 'week', 'ampm', 'dtform', 'tzones', 'num']
filter = []
for item in sorted:
    if item in filter_unsorted: 
        filter.append(item)
print(filter)

fulllist = ""
result = filename + " is missing " 

core_reqs = {
    "characters/exemplarCharacters": "Main Exemplar Characters", 
    "characters/exemplarCharacters[@type='auxiliary']": "Auxiliary Exemplar Characters", 
    "characters/exemplarCharacters[@type='punctuation']": "Punctuation Exemplar Characters",
    "characters/exemplarCharacters[@type='numbers']": "Numbers Exemplar Characters",
}
core_msng = {}

# might break this list into separate lists per cateogry and just tell the parser to go through all of them if the user doesn't want to filter
basic_reqs = {
    # Locale Display Names: Locale Display Pattern
    "localeDisplayNames/localeDisplayPattern/localePattern": "Locale Display Names Pattern",
    "localeDisplayNames/localeDisplayPattern/localeSeparator": "Locale Display Names Separator",
    # Locale Display Names: Vocabulary
    "localeDisplayNames/languages/language[@type='" + lang + "']": "Locale Display Names Autonym",
    "localeDisplayNames/languages/language[@type='en']": "Locale Display Names English",
    "localeDisplayNames/scripts/script[@type='"+ script + "']": "Locale Display Names Default Script",
    "localeDisplayNames/territories/territory[@type='" + territory + "']": "Locale Display Names Default Region", 
    "localeDisplayNames/measurementSystemNames/measurementSystemName[@type='metric']": "Measurement System Names Metric", 
    "localeDisplayNames/measurementSystemNames/measurementSystemName[@type='UK']": "Measurement System Names UK",
    "localeDisplayNames/measurementSystemNames/measurementSystemName[@type='US']": "Measurement System Names US",
        # the three below fall under the "vocabulary" category because while they are also patterns they require the word in the language for "Language", "Script", and "Territory"
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
    # Dates: Date/Time Formats
    "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='Hm']": "Gregorian Date/Time Format Hm",
    "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='hm']": "Gregorian Date/Time Format hm",
    "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='Hms']": "Gregorian Date/Time Format Hms",
    "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='hms']": "Gregorian Date/Time Format hms",
    "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='Hmsv']": "Gregorian Date/Time Format Hmsv", 
    "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='hmsv']": "Gregorian Date/Time Format hmsv",
    "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='yMd']": "Gregorian Date/Time Format yMd",
    "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/availableFormats/dateFormatItem[@id='yMMMd']": "Gregorian Date/Time Format yMMMd",
    "dates/calendars/calendar[@type='gregorian']/dateTimeFormats/intervalFormats/intervalFormatFallback": "Gregorian Date/Time Interval Format Fallback",
    # Dates: Time Zones
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
basic_msng = {}
#for categories of basic data:
if filter != None:
    ldnp_msng = {}
    ldnv_msng = {}
    delim_msng = {}
    month_msng = {}
    week_msng = {}
    ampm_msng = {}
    dtform_msng = {}
    tzones_msng = {}
    num_msng = {}

if coverage == "core" or "both":
    for r in core_reqs.keys():
        req = ldml.root.find(r)
        if req is None:
            core_msng[r]=core_reqs.get(r)
    core_msng_count = len(core_msng)
    if core_msng_count != 0 and coverage == "core": 
        print(filename + " is missing " + str(core_msng_count) + " Core Requirement(s): " + str(list(core_msng.values())))  

if coverage == "basic" or "both":
    for r in basic_reqs.keys():
        req = ldml.root.find(r)
        if req is None:
            basic_msng[r] = basic_reqs.get(r)
            # the below is sorting results in case you only want specific categories of missing data. 
            #could we pull all of this out into its own function that we call if filter isnt none instead of having it all here? idk hmm
            if filter != None:
                if r.startswith("localeDisplayNames/localeDisplayPattern/"):
                    if 'ldnp' in filter:
                        ldnp_msng[r] = basic_reqs.get(r)
                elif r.startswith("localeDisplayNames"):
                    if 'ldnv' in filter:
                        ldnv_msng[r] = basic_reqs.get(r)
                elif r.startswith("delimiters"):
                    if 'delim' in filter:
                        delim_msng[r] = basic_reqs.get(r)
                elif r.startswith("dates/calendars/calendar[@type='gregorian']/months/"):
                    if 'month' in filter:
                        month_msng[r] = basic_reqs.get(r)
                elif r.startswith("dates/calendars/calendar[@type='gregorian']/days/"):
                    if 'week' in filter:
                        week_msng[r] = basic_reqs.get(r)
                elif r.startswith("dates/calendars/calendar[@type='gregorian']/dayPeriods/"):
                    if 'ampm' in filter:
                        ampm_msng[r] = basic_reqs.get(r)
                elif r.startswith("dates/calendars/calendar[@type='gregorian']/dateTimeFormats/"):
                    if 'dtform' in filter:
                        dtform_msng[r] = basic_reqs.get(r)
                elif r.startswith("dates/timeZoneNames/"):
                    if 'tzones' in filter:
                        tzones_msng[r] = basic_reqs.get(r)
                elif r.startswith("numbers/"):
                    if 'num' in filter: 
                        num_msng[r] = basic_reqs.get(r)
    basic_msng_count = len(basic_msng)
    # depending on how I end up handling the categories of data element, the counters below might not be necessary
    # could be narrowed to a function saying "count the list that we are using right now" or something like that
    # also these variable names are getting a bit ridiculous but i'll fix them later when I feel more confident that I'll remember what each one does
    if filter != None:
        #theres probs a way to make this a loop or something ugh but for now i just wanna see if it works
        #it works! but it's ugly and i know there's a way to make this a loop or function ugh 
        # for item in filter blah blah blah only hiccup i see off the top of my head is the different variables. wouldn't be an issue if i didn't want to have the option to include as many filters as you want and to list them separate hmmm
        #for abbrv in filter:


        if 'ldnp' in filter:
            ldnp_msng_count = len(ldnp_msng)
            resultformatter('ldnp', filter, fulllist, result)
            fulllist, result = resultformatter('ldnp', filter, fulllist, result)
            result += str(ldnp_msng_count) + " Locale Data Pattern Requirement(s)"
            fulllist += ("Missing Locale Data Patterns: " + str(list(ldnp_msng.values())))
        if 'ldnv' in filter:
            ldnv_msng_count = len(ldnv_msng)
            resultformatter('ldnv', filter, fulllist, result)
            fulllist, result = resultformatter('ldnv', filter, fulllist, result)
            result += (str(ldnv_msng_count) + " Locale Data Vocabulary Requirement(s)") 
            fulllist += ("Missing Locale Data Vocab: " + str(list(ldnv_msng.values())))
        if 'delim' in filter:
            delim_msng_count = len(delim_msng)
            resultformatter('delim', filter, fulllist, result)
            fulllist, result = resultformatter('delim', filter, fulllist, result)
            result += (str(delim_msng_count) + " Delimiter Requirement(s)") 
            fulllist += ("Missing Delimiters: " + str(list(delim_msng.values())))
        if 'month' in filter:
            month_msng_count = len(month_msng)
            resultformatter('month', filter, fulllist, result)
            fulllist, result = resultformatter('month', filter, fulllist, result)
            result += (str(month_msng_count) + " Month Vocabulary Requirement(s)") 
            fulllist += ("Missing Months: " + str(list(month_msng.values())))
        if 'week' in filter:
            week_msng_count = len(week_msng)
            resultformatter('week', filter, fulllist, result)
            fulllist, result = resultformatter('week', filter, fulllist, result)
            result += (str(week_msng_count) + " Days of the Week Vocabulary Requirement(s)") 
            fulllist += ("Missing Days of the Week: " + str(list(week_msng.values())))
        if 'ampm' in filter:
            ampm_msng_count = len(ampm_msng)
            resultformatter('ampm', filter, fulllist, result)
            fulllist, result = resultformatter('ampm', filter, fulllist, result)
            result += (str(ampm_msng_count) + " Day Period Vocabulary Requirement(s)") 
            fulllist += ("Missing Day Period: " + str(list(ampm_msng.values())))
        if 'dtform' in filter:
            dtform_msng_count = len(dtform_msng)
            resultformatter('dtform', filter, fulllist, result)
            fulllist, result = resultformatter('dtform', filter, fulllist, result)
            result += (str(dtform_msng_count) + " Date/Time Format Requirement(s)") 
            fulllist += ("Missing Date/Time Format: " + str(list(dtform_msng.values())))
        if 'tzones' in filter:
            tzones_msng_count = len(tzones_msng)
            resultformatter('tzones', filter, fulllist, result)
            fulllist, result = resultformatter('tzones', filter, fulllist, result)
            result += (str(tzones_msng_count) + " Time Zones Vocabulary Requirement(s)") 
            fulllist += ("Missing Time Zones: " + str(list(tzones_msng.values())))
        if 'num' in filter:
            num_msng_count = len(num_msng)
            resultformatter('num', filter, fulllist, result)
            fulllist, result = resultformatter('num', filter, fulllist, result)
            result += (str(num_msng_count) + " Numbers Requirement(s)")
            fulllist += ("Missing Numbers: " + str(list(num_msng.values())))

        print(result)
        print(fulllist)

    if basic_msng_count != 0 and coverage == "basic" and filter is None: 
        print(filename + " is missing " + str(basic_msng_count) + " Basic Requirement(s): " + str(list(basic_msng.values())))

if coverage == "both" and (core_msng_count or basic_msng_count) != 0:
    print(filename + " is missing " + str(core_msng_count) + " Core Requirement(s) and " + str(basic_msng_count) + " Basic Requirement(s).")
    if core_msng_count != 0:
        print("Missing Core: " + str(list(core_msng.values())))
    if basic_msng_count != 0:
        print("Missing Basic: "+ str(list(basic_msng.values())))
        # dont forget to incorporate categories here too.