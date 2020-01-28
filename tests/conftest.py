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
def fixdata(pytestconfig):
    return pytestconfig.option.fix

@pytest.fixture(scope="session")
def langid(request):
    return request.param

@pytest.fixture(scope="session")
def ldml(langid):
    ldml = LdmlFile(langid)
    yield ldml
    if ldml.dirty:
        ldml.ldml.normalise()
        ldml.ldml.save_as(ldml.path, topns=False)

@pytest.hookimpl(hookwrapper=True)
def pytest_sessionfinish(session, exitstatus):
    if session.config.option.tbstyle == "auto":
        session.config.option.tbstyle = "no" if len(session.config.option.locale) == 0 else "short"
    yield
    tr = session.config.pluginmanager.get_plugin("terminalreporter")
    reports = tr.getreports("failed")
    summary = {}
    for r in reports:
        mod, f = r.location[2].split("[")
        f = os.path.splitext(os.path.basename(f.rstrip("]")))[0]
        summary.setdefault(mod, []).append(f)
    tr.write_line("")
    for k, v in sorted(summary.items()):
        tr.write_line("{} ({}): {}".format(k, len(v), ", ".join(v)))
    
def getallpaths():
    res = {}
    base = os.path.join(os.path.dirname(__file__), '..', 'sldr')
    for l in os.listdir(base):
        if l.endswith('.xml'):
            res[l[:-4].lower()] = os.path.join(base, l)
        elif os.path.isdir(os.path.join(base, l)):
            for t in os.listdir(os.path.join(base, l)):
                if t.endswith('.xml') and t != "root.xml":
                    res[t[:-4].lower()] = os.path.join(base, l, t)
    return res

def pytest_addoption(parser):
    parser.addoption("-L","--locale", action="append", default=[])
    parser.addoption("-F","--fix", action="store_true", dest="fix", default=[])

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
