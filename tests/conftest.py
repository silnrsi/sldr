import pytest
import logging
import sys, os
from palaso.sldr.ldml import Ldml

class LdmlFile(object):
    def __init__(self, path, **kw):
        print("Creating ", path)
        for k, v in kw.items():
            setattr(self, k, v)
        self.path = path
        self.ldml = Ldml(self.path)
        self.dirty = False

@pytest.fixture(scope="session")
def langid(request):
    return request.param

@pytest.fixture(scope="session")
def ldml(langid):
    ldml = LdmlFile(langid)
    yield ldml
    if ldml.dirty:
        ldml.ldml.save_as(ldml.path)

def getallpaths():
    res = {}
    base = os.path.join(os.path.dirname(__file__), '..', 'sldr')
    for l in os.listdir(base):
        if l.endswith('.xml'):
            res[l[:-4].lower()] = os.path.join(base, l)
        elif os.path.isdir(os.path.join(base, l)):
            for t in os.listdir(os.path.join(base, l)):
                if t.endswith('.xml'):
                    res[t[:-4].lower()] = os.path.join(base, l, t)
    return res

def pytest_addoption(parser):
    parser.addoption("-L","--locale", action="append", default=[])

def pytest_generate_tests(metafunc):
    if 'langid' not in metafunc.fixturenames:
        return
    vals = [v.lower().replace("-","_") for v in metafunc.config.getoption('locale')]
    allpaths = getallpaths()
    vals = [allpaths[v] for v in vals if v in allpaths]
    if not len(vals):
        vals = sorted(allpaths.values())
    metafunc.parametrize("langid", vals, indirect=True)

def pytest_configure(config):
    config.option.verbose -= 1              # equivalent to one -q, so can be overridden
    if config.option.tbstyle == "auto":     # equivalent to --tb=short. Use --tb=long to override
        config.option.tbstyle = "short"
