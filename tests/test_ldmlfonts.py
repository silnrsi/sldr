#!/usr/bin/python3

import sys
import os

try:
    from bin import ldmlfonts
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))
    from bin import ldmlfonts


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


def test_aa():
    assert ldmlfonts.find_fonts('aa')[0] == 'Charis SIL'


def test_aa_arab():
    assert ldmlfonts.find_fonts('aa-Arab')[0] == 'Scheherazade'


def test_cop():
    assert ldmlfonts.find_fonts('cop')[0] == 'NotoSansCoptic'


def test_cop_arab():
    assert ldmlfonts.find_fonts('cop-Arab')[0] == 'Scheherazade'


def test_cop_grek():
    assert ldmlfonts.find_fonts('cop-Grek')[0] == 'Gentium Plus'


def test_el():
    assert ldmlfonts.find_fonts('el')[0] == 'Gentium Plus'


def test_ha():
    assert ldmlfonts.find_fonts('ha')[0] == 'Charis SIL'


def test_ha_arab():
    assert ldmlfonts.find_fonts('ha-Arab')[0] == 'Harmattan'


def test_ha_cm():
    assert ldmlfonts.find_fonts('ha-CM')[0] == 'Harmattan'


def test_ha_sd():
    assert ldmlfonts.find_fonts('ha-SD')[0] == 'Scheherazade'
