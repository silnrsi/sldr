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

def calldirect():  #tentative name, making separate method for version referencing missingdata.json until i figure out what overlaps.
    root_sldr = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sldr")
    #if this gets moved out of the sldr/tests folder and put somewhere else, need to make sure that this line and possibly the 'filep' variable is changed to reflect how to get back to the sldr folder (the one holding the alphabetical directories)
    #tbh this is probs gonna end up in sldr tools which is unfortuante bc it means we are out of the repo and need to be able to path our way to wherever other ppl have the repo bleghhhhh

    #theoretically if i wanted to run this on the whole sldr i'd have to do a for loop using the directory and everything in it but that'll get figured out later
    #when do that make sure theres a way to skip cldr? UPDATE maybe dont skip it actually; there may be remnants of seed data that are lurking from cldr 

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


    #how to use for Em ref: python prog.py nga --coverage core 

    tag = args.setdefault('ldml')
    filep = os.path.join(root_sldr, tag[0], tag.replace("-", "_")+".xml")
    #see under 'root_sldr' about needing to change if this file is moved
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
    #currently has a bandaid-fix: checks for script in other part of ID block and, if that isn't there either, outputs a string so it can concatenate later without killing the program. 
    #still needs an exception to actually address what it means if "script" or "territory" == "error" in the approprate spots

    coverage = args.setdefault('coverage')
    filter_unsorted = args.setdefault('filter')
    sorted = ['ldnp', 'ldnv', 'delim', 'month', 'week', 'ampm', 'dtform', 'tzones', 'num']
    filter = []
    if filter_unsorted != None:
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
                # add something that says if script or territory = "error" have a separate warning saying that the sil id block is missing script or territory data and that info relating to this vocab may actually not be missing 
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
            # add something that says if script or territory = "error" have a separate warning saying that the sil id block is missing script or territory data and that info relating to this vocab may actually not be missing 

    if coverage == "both" and (core_msng_count or basic_msng_count) != 0:
        print(filename + " is missing " + str(core_msng_count) + " Core Requirement(s) and " + str(basic_msng_count) + " Basic Requirement(s).")
        if core_msng_count != 0:
            print("Missing Core: " + str(list(core_msng.values())))
        if basic_msng_count != 0:
            print("Missing Basic: "+ str(list(basic_msng.values())))
            # add something that says if script or territory = "error" have a separate warning saying that the sil id block is missing script or territory data and that info relating to this vocab may actually not be missing 

            # dont forget to incorporate categories here too.


            #FOR CODE IMPLIMENT LATER, IF TIME IS 24 HR TIME THEN NO AM PM STUFF NEEDED. ALSO UPPERCASE H IS 24 HR AND THE AMOUNT OF LETTERS HAS TO DO
            #WITH ZERO/NON ZERO BUFFER OR SOMETHING? TEST MIGHT NEED TO BE A BIT MORE FLEXIBLE


#def callmissing():
parser = ArgumentParser()
parser.add_argument('-l', '--langtag', default = None, help = 'The langtag of the file you are examining. It should be the file name with \'-\' replacing \'_\' and without \'.xml\' at the end. If you are familiar with the pytests used on the SLDR, it is the same format.')
    #this needs to be swapped out for the locale range specifier, along with anything referencing it (i.e. 'tag') 
parser.add_argument('-r','--range', default = None, help = "The alphabet range of sldr files you want to search for. Can be a single letter (e.g. 'a', 'b', 'c') or a range of characters as long as they are in order (e.g. 'a-d', 'x-z'). If you know how regexes work, you can also write a regex without the square brackets ([]) such as '^aef' (everything except a, e, or f) or 'arn' (match to a, r, and n specifically).")
    #figure out how to do alphabet ranges without specifically typing in every one
parser.add_argument('-t','--territory', default = None, help = "the territory you want to search in, alt to range, this is a bad help pop up fix later")
#add argument for searching entire sldr instead of one spec file (might need to make initial ldml optional then)? argument for if you want a range vs one file?
parser.add_argument('-s','--script', default = None, help = "the script you want to search in, alt to range, fix help later")
parser.add_argument('-c', '--coverage', choices = ["core", "basic", "both"], default = "both", help = "The CLDR coverage level you are searching for. Options are 'core', 'basic', or the default 'both'.")
#add argument for filtering categories of basic data
parser.add_argument('-f', '--filter', action= 'append', choices = ['ldnp', 'ldnv', 'delim', 'month', 'week', 'ampm', 'dtform', 'tzones', 'num','all'], help = "Used to filter for specific categories of Basic data. Multiple options can be selected, and each will be displayed individually. Options are 'ldnp' (Locale Display Names Patterns), 'ldnv' (Locale Display Names Vocab), 'delim' (Delimiters), 'month' (Gregorian Wide Months Vocab), 'week' (Gregorian Wide Days of the Week Vocab), 'ampm' (Gregorian Wide Day Period Vocab), 'dtform' (Date/Time Format), 'tzones' (Time Zone Vocab), 'num' (Numbers), and 'all' (show all filters). By default, no filtering occurs.")
#this should also allow for multiple choices. should put choices in a list. 
#add argument for if you want it to print out the specific missing things or just the amount missing
#add argument for if you want it to print out specific xml paths for each missing thing or not (if so need to make it somewhat easy to read)
#add argument for only printing files missing beyond a certain percentage of data
#add argument for only printing files missing a specific category of data
args = vars(parser.parse_args())
print(args)

root_sldr = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sldr")
    #if this gets moved out of the sldr/tests folder and put somewhere else, need to make sure that this line and possibly the 'filep' variable is changed to reflect how to get back to the sldr folder (the one holding the alphabetical directories)
    #tbh this is probs gonna end up in sldr tools which is unfortuante bc it means we are out of the repo and need to be able to path our way to wherever other ppl have the repo bleghhhhh

ltag = args.setdefault('langtag')
range = args.setdefault('range')
territory = args.setdefault('territory')
script = args.setdefault('script')
coverage = args.setdefault('coverage')
filter_unsorted = args.setdefault('filter')
sorted = ['ldnp', 'ldnv', 'delim', 'month', 'week', 'ampm', 'dtform', 'tzones', 'num', 'all']
filter = []
if filter_unsorted != None:
    for item in sorted:
        if item in filter_unsorted: 
            filter.append(item)
    print(filter)


missingdata = json.load(open("missingdata.json"))
alldata = {}
for x in missingdata: 
    msng_dict = {
        "core_msng": None,
        "basic_msng": None,
        "ldnp_msng": None,
        "ldnv_msng": None,
        "delim_msng": None,
        "month_msng": None,
        "week_msng": None,
        "ampm_msng": None,
        "tzones_msng": None,
        "num_msng": None,
    }
    print(x.get("filename")) #IT WORKSSSSSS
    if ltag != None and x.get("langtag") != ltag:
        continue
    if range != None:
        print(range)
        if len(range) == 1:
            if x.get("filename")[0] != range:
                if [x.get("filename")[0], range].sort()[0] == range:        #cuts off search after searching all of the files starting with that letter
                    print("out of range")
                    break 
                continue
        elif re.search(("[" + range + "]"), x.get("filename")[0]) == None:
            q = [(x.get("filename")[0]), (range[-1])]
            q.sort()
            if "^" in range:        # allows search to continue until 'z' since a set like [^aef] will match to everything except those three letters
                continue
            else:
                if "-" not in range:    #cuts off search when reaching the possible results matching sets such as [arn] and [a-h]
                    range.sort()        #allows for situations where a set like [arn] is out of order, such as [rna]
                if q[0] == range[-1]:
                    print("out of range")
                    break 
            continue
    if territory != None and x.get("region") != territory:
        continue
    if script != None and x.get("script") != script:
        continue
    if coverage == "core" or "both":
        msng_dict["core_msng"] = x.get("core_msng")
    if coverage == "basic" or "both":
        msng_dict["basic_msng"] = x.get("basic_msng")
    if filter != None:
        if 'ldnp' or 'all' in filter:
            msng_dict["ldnp_msng"] = x.get("ldnp_msng")
        if 'ldnv' or 'all' in filter:
            msng_dict["ldnv_msng"] = x.get("ldnv_msng")
        if 'delim' or 'all' in filter:
            msng_dict["delim_msng"] = x.get("delim_msng")
        if 'month' or 'all' in filter:
            msng_dict["month_msng"] = x.get("month_msng")
        if 'week' or 'all' in filter:
            msng_dict["week_msng"] = x.get("week_msng")
        if 'ampm' or 'all' in filter:
            msng_dict["ampm_msng"] = x.get("ampm_msng")
        if 'tzones' or 'all' in filter:
            msng_dict["tzones_msng"] = x.get("tzones_msng")
        if 'num' or 'all' in filter:
            msng_dict["num_msng"] = x.get("num_msng")
    alldata[x.get("filename")] = msng_dict
        
print(alldata)
print(alldata.keys())
#alldata is a dictionary with the key being a filename and the value being a dictionary containing all of the missing data related to that file. 

# tag = args.setdefault('ldml')
# filep = os.path.join(root_sldr, tag[0], tag.replace("-", "_")+".xml")
#     #see under 'root_sldr' about needing to change if this file is moved
# if os.path.exists(filep):
#     ldml = Ldml(filep)
# filename = os.path.basename(ldml.fname)    # get filename for reference

#if locale element specified (region or script), for x in missingdata with that locale, output contents of that dictionary/list?
    #if filter specified, for x in missingdata, for filter, output the contents of that dictionary/list? 

#tldr order of "filtering out" if statements needs to be: 
    # 1. picking out files to search in missingdata.json (aka locale filters, alphabet ranges, or one specific file)
        # for x in missing data, if [matches filters for the above] (
        # OR better yet, hit continue if it DOESN'T match, filter it out
    # 2. picking out specific missing data to output (core, basic, or subcategories of basic)
        # for [chosen filters], collect list of contents of each
    # 3. Numerical range of how much content is in the chosen outputs (will need to be different per output, calculate later)
        # if len([list of contents of each filter]) is less than or equal to [amount specified (default is max per category)] 
        # output the list of contents of each filter


#how to use for Em ref: python prog.py --langtag nga --coverage both --filter all
