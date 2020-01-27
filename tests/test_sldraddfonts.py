#!/usr/bin/python3

import sys
import os

try:
    from bin import sldraddfonts
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bin')))
    from bin import sldraddfonts


def setup_module():
    sldraddfonts.read_font_data('Script2Font.csv')


def test_arabic_africa():
    assert sldraddfonts.suggestions['Arab_NG'][0] == 'Harmattan'


def test_arabic_asia():
    assert sldraddfonts.suggestions['Arab_PK'][0] == 'Awami Nastaliq'


def test_arabic():
    assert sldraddfonts.suggestions['Arab'][0] == 'Scheherazade'


def test_coptic():
    assert sldraddfonts.suggestions['Copt'][1] == 'Sophia Nubian'


def test_aa():
    assert sldraddfonts.find_fonts('aa')[0] == 'Charis SIL'


def test_aa_arab():
    assert sldraddfonts.find_fonts('aa-Arab')[0] == 'Scheherazade'


def test_cop():
    assert sldraddfonts.find_fonts('cop')[0] == 'NotoSansCoptic'


def test_cop_arab():
    assert sldraddfonts.find_fonts('cop-Arab')[0] == 'Scheherazade'


def test_cop_grek():
    assert sldraddfonts.find_fonts('cop-Grek')[0] == 'Gentium Plus'


def test_el():
    assert sldraddfonts.find_fonts('el')[0] == 'Gentium Plus'


def test_ha():
    assert sldraddfonts.find_fonts('ha')[0] == 'Charis SIL'


def test_ha_arab():
    assert sldraddfonts.find_fonts('ha-Arab')[0] == 'Harmattan'


def test_ha_cm():
    assert sldraddfonts.find_fonts('ha-CM')[0] == 'Harmattan'


def test_ha_sd():
    assert sldraddfonts.find_fonts('ha-SD')[0] == 'Scheherazade'
