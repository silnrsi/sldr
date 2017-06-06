About the SIL LDML Editor
-------------------------

The [LDML Editor](http://scripts.sil.org/pub/ldmledit/#/loadnsave) is a small web application that allows a user to generate an LDML file without knowing the details of the syntax or the need to type a lot of XML.

# Background

LDML stands for Locale Data Markup Language. It is an XML format that is used specifically by the Common Language Data Repository (CLDR) to provide language documentation for the purposes of software localization. The main syntax is [defined by the Unicode Consortium](http://unicode.org/reports/tr35/). The syntax has been extended with an [SIL namespace](https://docs.google.com/document/d/1H20pFQQsuAoyM0UAygiL_tUL3KuapoMoBbTXRtaT924/edit) to handle details specifically of interest for SIL software. It is mainly these extensions that need to be handled by the LDML Editor, although the app handles some standard parts of the syntax as well.

The editor allows the user to either load and edit an existing LDML or to create a new one. The application currently provides functionality to save the file to the user’s computer; the user is then responsible for submitting it to the appropriate repository. Each LDML file is named and identified by a ISO 639 code (a two-letter [639-1](http://www.loc.gov/standards/iso639-2/php/code_list.php) code if it exists, otherwise a three-letter [639-3](http://www-01.sil.org/iso639-3/codes.asp) code) and possibly a four-letter [ISO 15924](http://unicode.org/iso15924/) script code. It is the responsibility of the user to name their LDML file appropriately.

Each page of the application contains controls for editing various LDML fields. There is some help text on each page, but it is not complete.

# Source Code

The app is written in Angular, Javascript, and Bootstrap. The source code is located here: [https://github.com/silnrsi/sldr/tree/master/editor](https://github.com/silnrsi/sldr/tree/master/editor). Most of the relevant code is located in editor/src/app-ng.

# Status of the application

The app is more or less complete as far as basic functionality. That is, it imports and exports the bits of LDML syntax that we are most interested in.

The main problem is that the UI is clunky and awkward and unattractive. There are also certainly bugs that need to be fixed. It would be good, although not necessary, to have help text on each page

# Bugs

Collation sequences are not stored in the correct format.
