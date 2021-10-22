__all__ = """
    MEDM_SCREEN_DIR
    assertEqualClassName
    assertEqualPropertyString
    assertEqualPropertyStringlist
    assertEqualStringChild
    assertExpectedAttrib
    assertExpectedDictInRef
    convertAdlFile
    getNamedProperty
    getNamedWidget
    getSubElement
""".split()

import os
import pytest
import shutil
import sys
import tempfile

from .. import cli
from .. import output_handler


MEDM_SCREEN_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "tests", "medm")


@pytest.fixture(scope="function")
def tempdir():
    path = tempfile.mkdtemp()
    yield path

    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)


def convertAdlFile(adlname, temppath):
    medm_path = MEDM_SCREEN_DIR
    assert os.path.exists(medm_path)

    full_name = os.path.join(medm_path, adlname)
    assert os.path.exists(full_name)

    sys.argv = [sys.argv[0], "-d", temppath, full_name]
    cli.main()

    base = os.path.splitext(os.path.basename(full_name))[0]
    uiname = base + output_handler.SCREEN_FILE_EXTENSION

    return uiname


def getNamedProperty(xmlparent, propName):
    properties = xmlparent.findall("property")
    assert len(properties) > 0
    for prop in properties:
        if prop.attrib["name"] == propName:
            return prop


def getNamedWidget(xmlparent, key):
    for widget in xmlparent.findall("widget"):
        if widget.attrib["name"] == key:
            return widget


def getSubElement(xmlparent, tag):
    assert xmlparent is not None, "parent not found"
    child = xmlparent.find(tag)
    assert child is not None, tag + " subelement expected"
    return child


def assertEqualClassName(parent, cls, nm, doc=None):
    doc = doc or f"widget:{parent.attrib['name']}"
    assertExpectedAttrib(parent, **{"class": cls, "name": nm})


def assertEqualPropertyString(parent, propName, expected):
    doc = f"widget:{parent.attrib['name']}, property:{propName}"
    prop = getNamedProperty(parent, propName)
    assert prop is not None, doc
    assertEqualStringChild(prop, expected, doc)


def assertEqualPropertyStringlist(widget, tag, expected=[]):
    doc = f"widget:{widget.attrib['name']}"
    prop = getNamedProperty(widget, tag)
    stringlist = getSubElement(prop, "stringlist")
    assert len(stringlist) == len(expected)
    for i, string in enumerate(stringlist.findall("string")):
        expect_str = expected[i]
        assert string.text == expect_str


def assertEqualStringChild(parent, text="", doc=None):
    child = getSubElement(parent, "string")
    assert child.text == str(text), doc


def assertExpectedAttrib(parent, doc=None, **kwargs):
    doc = doc or f"element:{parent.tag}"
    assert hasattr(parent, "attrib")
    assertExpectedDictInRef(parent.attrib, **kwargs)


def assertExpectedDictInRef(ref, doc=None, **kwargs):
    assert isinstance(ref, dict), doc
    assert isinstance(kwargs, dict), doc
    for k, v in kwargs.items():
        assert k in ref, f"{doc}, k={k}, v={v}"
        assert v == ref[k], f"{doc}, k={k}, v={v}"
