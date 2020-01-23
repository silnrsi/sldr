#!/usr/bin/python3

import sys
import os

try:
    from bin import ldmlfonts
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))
    from wstools import ldmlfonts


def setup_module():
    ldmlfonts.read_font_data('Script2Font.csv')


def test_arabic_africa():
    assert ldmlfonts.suggestions['Arab_NG'][0] == 'Harmattan'


def test_arabic_asia():
    assert ldmlfonts.suggestions['Arab_PK'][0] == 'Awami Nastaliq'


def test_arabic():
    assert ldmlfonts.suggestions['Arab'][0] == 'Scheherazade'


def test_coptic():
    assert ldmlfonts.suggestions['Copt'][1] == 'Sophia Nubian'


def test_greek():
    assert ldmlfonts.suggestions['Grek'][1] == 'Galatia'
