import unittest
import pytest
import logging, os
from lxml.etree import RelaxNG, parse

@pytest.fixture(scope="session")
def validator(request):
    return RelaxNG(file=os.path.join(os.path.dirname(__file__), '..', 'doc', 'sil.rng'))

def test_validate(ldml, validator):
    xml = parse(ldml.path)
    validator.assertValid(xml)

def test_first(ldml):
    logging.info("Test run ")
    assert 1
