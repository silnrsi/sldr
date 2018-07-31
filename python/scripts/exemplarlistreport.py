from xml.etree import ElementTree as et
import os, sys

def reportfordir(path, reportfilename):
    """
    Usage: python exemplarlistreport.py directorypath reportfile.txt
    """
    with open(reportfilename, mode="w", encoding='utf-8') as ofile:
        chars = ofile.write("Report for " + path)
        try: 
            for file in sorted(os.listdir(path)):
                cf = os.path.join(path, file)
                chars = ofile.write("\n" + file)
                r = et.parse(cf).getroot()
                e = set(r.findall(".//exemplarCharacters[@draft='generated']"))
                if len(e) == 0:
                    chars = ofile.write("\nNo generated exemplar lists found")
                    continue
                d = set(r.findall(".//exemplarCharacters[@draft='generated'][@type]"))
                m = list(e-d)
                if len(m) == 0:
                    chars = ofile.write("\nNo generated main exemplar list found")
                    continue
                else:
                    chars = ofile.write("\nGenerated main exemplar list: " + m[0].text)
                a = r.findall(".//exemplarCharacters[@draft='generated'][@type='auxiliary']")
                if len(a) == 0:
                    chars = ofile.write("\nNo generated auxiliary list found")
                else:
                    chars = ofile.write("\nGenerated auxiliary exemplar list: " + a[0].text)
        except OSError:
            chars = ofile.write("\nDirectory not found or empty")

if __name__ == '__main__':
    if len(sys.argv) > 2:
        reportfordir(sys.argv[1], sys.argv[2])
    else:
        print(reportfordir.__doc__)
