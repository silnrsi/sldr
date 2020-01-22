#!/usr/bin/python3

import sys
import os

try:
    from bin import ldmlfonts
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))
    from wstools import ldmlfonts


def test_arabic_africa():
    ldmlfonts.read_font_data('Script2Font.csv')
    assert ldmlfonts.suggestions['Arab_NG'][0] == 'Harmattan'


def test_arabic_asia():
    ldmlfonts.read_font_data('Script2Font.csv')
    assert ldmlfonts.suggestions['Arab_PK'][0] == 'Awami Nastaliq'


def test_arabic():
    ldmlfonts.read_font_data('Script2Font.csv')
    assert ldmlfonts.suggestions['Arab'][0] == 'Scheherazade'


def test_coptic():
    ldmlfonts.read_font_data('Script2Font.csv')
    assert ldmlfonts.suggestions['Copt'][1] == 'Sophia Nubian'
