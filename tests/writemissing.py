import os, json
import requests
import logging, re, unicodedata
from langtag import langtag, lookup
from sldr.utils import find_parents
from argparse import ArgumentParser
from sldr.ldml import Ldml, _alldrafts, getldml

def iscldr(ldml):
    i = ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.namespaces.items()})
    if i is not None and i.get('source', "") == "cldr":
        return True
    return False

root_sldr = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sldr")
#if this gets moved out of the sldr/tests folder and put somewhere else, need to make sure that this line and possibly the 'filep' variable is changed to reflect how to get back to the sldr folder (the one holding the alphabetical directories)

#theoretically if i wanted to run this on the whole sldr i'd have to do a for loop using the directory and everything in it but that'll get figured out later
#when do that make sure theres a way to skip cldr? UPDATE maybe dont skip it actually; there may be remnants of seed data that are lurking from cldr 


#parser = ArgumentParser()
#parser.add_argument('ldml', help = 'The langtag of the file you are examining. It should be the file name with \'-\' replacing \'_\' and without \'.xml\' at the end. If you are familiar with the pytests used on the SLDR, it is the same format.')
#add argument for searching entire sldr instead of one spec file (might need to make initial ldml optional then)? argument for if you want a range vs one file?
#parser.add_argument('-c', '--coverage', choices = ["core", "basic", "both"], default = "both", help = "The CLDR coverage level you are searching for. Options are 'core', 'basic', or the default 'both'.")
#add argument for filtering categories of basic data
#parser.add_argument('-f', '--filter', action= 'append', choices = ['ldnp', 'ldnv', 'delim', 'month', 'week', 'ampm', 'dtform', 'tzones', 'num'], help = "Used to filter for specific categories of Basic data. Multiple options can be selected, and each will be displayed individually. Options are 'ldnp' (Locale Display Names Patterns), 'ldnv' (Locale Display Names Vocab), 'delim' (Delimiters), 'month' (Gregorian Wide Months Vocab), 'week' (Gregorian Wide Days of the Week Vocab), 'ampm' (Gregorian Wide Day Period Vocab), 'dtform' (Date/Time Format), 'tzones' (Time Zone Vocab), and 'num' (Numbers). By default, no filtering occurs.")
#this should also allow for multiple choices. should put choices in a list. 
#add argument for if you want it to print out the specific missing things or just the amount missing
#add argument for if you want it to print out specific xml paths for each missing thing or not (if so need to make it somewhat easy to read)
#add argument for filtering entire sldr by region
#add argument for filtering entire sldr by character range (i.e. langtags starting with a - c)
#add argument for filtering entire sldr by script
#add argument for only printing files missing beyond a certain percentage of data
#add argument for only printing files missing a specific category of data
#args = vars(parser.parse_args())
#print(args)


#get all of the files in the sldr in a big list :) 
filelist = []
for (root, dirs, file) in os.walk(root_sldr):
    for f in file:
        if '.xml' in f:
            filelist.append(f)

jsonoutput = []
#cldr_missing = []

for f in filelist:
    if f == "root.xml" or f == "test.xml":
        continue
    print(f)
    tag = f[:-4].replace("_", "-")
    filep = os.path.join(root_sldr, tag[0], f)
    #file path from root_sldr to the actual file: see under 'root_sldr' about needing to change if this file is moved
    if os.path.exists(filep):
        ldml = Ldml(filep)

    filename = os.path.basename(ldml.fname)    # get filename for reference
    lang = ldml.root.find('.//identity/language').get('type')
    i = ldml.root.find(".//identity/special/sil:identity", {v:k for k,v in ldml.namespaces.items()})
    script = i.get("script")
    if script is None:
        if ldml.root.find('.//identity/script') == None:
            script = "error"
        else:
            script = ldml.root.find('.//identity/script').get('type')
    territory = i.get("defaultRegion")
    if territory is None:
        if ldml.root.find('.//identity/territory') == None:
            territory = "error"
        else:
            territory = ldml.root.find('.//identity/territory').get('type')
    # bug: if script or defaultRegion is not in SIL identity block, error happens. Is this an issue where data needs to be in ID block or an issue where test should work around this scenario?

    core_reqs = {
        "characters/exemplarCharacters": "Main Exemplar Characters", 
        "characters/exemplarCharacters[@type='auxiliary']": "Auxiliary Exemplar Characters", 
        "characters/exemplarCharacters[@type='punctuation']": "Punctuation Exemplar Characters",
        "characters/exemplarCharacters[@type='numbers']": "Numbers Exemplar Characters", 
    }
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
    core_msng = {}
    basic_msng = {}
    #for categories of basic data:
    ldnp_msng = {}
    ldnv_msng = {}
    delim_msng = {}
    month_msng = {}
    week_msng = {}
    ampm_msng = {}
    dtform_msng = {}
    tzones_msng = {}
    num_msng = {}

    for r in core_reqs.keys():
        req = ldml.root.find(r)
        if req is None:
            core_msng[r]=core_reqs.get(r)        

    for r in basic_reqs.keys():
        req = ldml.root.find(r)
        if req is None:
            basic_msng[r] = basic_reqs.get(r)
            # the below is sorting results in case you only want specific categories of missing data. 
            #could we pull all of this out into its own function that we call if filter isnt none instead of having it all here? idk hmm
            if r.startswith("localeDisplayNames/localeDisplayPattern/"):
                ldnp_msng[r] = basic_reqs.get(r)
            elif r.startswith("localeDisplayNames"):
                ldnv_msng[r] = basic_reqs.get(r)
            elif r.startswith("delimiters"):
                delim_msng[r] = basic_reqs.get(r)
            elif r.startswith("dates/calendars/calendar[@type='gregorian']/months/"):
                month_msng[r] = basic_reqs.get(r)
            elif r.startswith("dates/calendars/calendar[@type='gregorian']/days/"):
                week_msng[r] = basic_reqs.get(r)
            elif r.startswith("dates/calendars/calendar[@type='gregorian']/dayPeriods/"):
                ampm_msng[r] = basic_reqs.get(r)
            elif r.startswith("dates/calendars/calendar[@type='gregorian']/dateTimeFormats/"):
                dtform_msng[r] = basic_reqs.get(r)
            elif r.startswith("dates/timeZoneNames/"):
                tzones_msng[r] = basic_reqs.get(r)
            elif r.startswith("numbers/"):
                num_msng[r] = basic_reqs.get(r)
    #cldr stuff
    cldr = iscldr(ldml)
    #blocklist = []
    # if i is not None and i.get('source', "") == "cldr":
    #     for b in ldml.root:
    #         blocklist.append(b.tag)     #gives me list of all the major element blocks, starting with 'identity' 
    # if blocklist == ['identity']:
    #     if len(basic_msng) != 0 or len(core_msng) != 0:
    #         cldr_missing.append(f)
    
    jsonentry = {
        "filename": filename,
        "langtag": tag,
        "cldr": cldr,
        "language": lang,
        "script": script,
        "region": territory,
        "core_msng": core_msng,
        "basic_msng": basic_msng,
        "ldnp_msng": ldnp_msng,
        "ldnv_msng": ldnv_msng,
        "delim_msng": delim_msng,
        "month_msng": month_msng,
        "week_msng": week_msng,
        "ampm_msng": ampm_msng,
        "dtform_msng": dtform_msng,
        "tzones_msng": tzones_msng,
        "num_msng": num_msng,
    }
    jsonoutput.append(jsonentry)

json_object = json.dumps(jsonoutput, indent=4)
with open("missingdata.json", "w") as outfile:
    outfile.write(json_object)

#print(cldr_missing)

#HOW TO MAKE SURE IT DOESN'T OUTPUT FOR INHERITED DATA OR EMPTY REGIONAL FILES HMMM

    #want to structure it sorta like langtags: list of dictionaries? 


#    print(filename + " is missing " + str(basic_msng_count) + " Basic Requirement(s): " + str(list(basic_msng.values())))

#    print(filename + " is missing " + str(core_msng_count) + " Core Requirement(s) and " + str(basic_msng_count) + " Basic Requirement(s).")
#    if core_msng_count != 0:
#        print("Missing Core: " + str(list(core_msng.values())))
#    if basic_msng_count != 0:
#        print("Missing Basic: "+ str(list(basic_msng.values())))
        # dont forget to incorporate categories here too.