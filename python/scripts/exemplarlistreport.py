from xml.etree import ElementTree as et
import os, sys

def reportfordir(path):
    """
    Usage: python3 exemplarlistreport.py directorypath
    """
    print("Report for " + path)
    try: 
        for file in sorted(os.listdir(path)):
            cf = os.path.join(path, file)
            print("\n" + file)
            r = et.parse(cf).getroot()
            e = set(r.findall(".//exemplarCharacters[@draft='generated']"))
            if len(e) == 0:
                print("No generated exemplar lists found")
                continue
            d = set(r.findall(".//exemplarCharacters[@draft='generated'][@type]"))
            m = list(e-d)
            if len(m) == 0:
                print("No generated main exemplar list found")
                continue
            else:
                print("Generated main exemplar list: " + m[0].text)
            a = r.findall(".//exemplarCharacters[@draft='generated'][@type='auxiliary']")
            if len(a) == 0:
                print("No generated auxiliary list found")
            else:
                print("Generated auxiliary exemplar list: " + a[0].text)
    except OSError:
        print("Directory not found or empty")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        reportfordir(sys.argv[1])
    else:
        print(reportfordir.__doc__)
