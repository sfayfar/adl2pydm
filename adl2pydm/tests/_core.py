import os
import pytest
import shutil
import sys
import tempfile

from .. import adl_parser
from .. import cli
from .. import output_handler


MEDM_SCREEN_DIR = os.path.join(os.path.dirname(__file__), "medm")
ALL_EXAMPLE_FILES = os.listdir(MEDM_SCREEN_DIR)


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


def getNamedProperty(parent, propName):
    properties = parent.findall("property")
    # assert len(properties) > 0
    for prop in properties:
        if prop.attrib["name"] == propName:
            return prop


def getNamedWidget(parent, key):
    for widget in parent.findall("widget"):
        if widget.attrib["name"] == key:
            return widget


def getSubElement(parent, tag):
    assert parent is not None, "parent not found"
    child = parent.find(tag)
    assert child is not None, tag + " subelement expected"
    return child


def getWidgetsClass(parent, cls):
    widgets = parent.findall("widget")
    findings = [
        w.attrib["class"]
        for w in widgets
        if w.attrib["class"] == cls
    ]
    return findings


def pickWidget(parent, num_widgets, n, symbol, line_offset):
    assertHasAttribute(parent, "widgets")
    assertEqual(len(parent.widgets), num_widgets)
    w = parent.widgets[n]
    assertEqual(w.symbol, symbol)
    assertEqual(w.line_offset, line_offset)
    return w


# custom assertions
# some assertions are for compatibility with code that used unittest

def assertColor(parent, r, g, b, **kwargs):
    for item in parent.iter():
        if item.tag == "red":
            assertEqual(item.text, str(r))
        elif item.tag == "green":
            assertEqual(item.text, str(g))
        elif item.tag == "blue":
            assertEqual(item.text, str(b))


def assertDictEqual(a, b, doc=None):
    assert isinstance(a, dict)
    assert isinstance(b, dict)
    assert dict(a) == dict(b), doc


def assertEqual(a, b, doc=None):
    assert a == b, doc


def assertEqualBool(parent, value, doc=None):
    doc = doc or f"widget:{parent.attrib['name']}"
    child = getSubElement(parent, "bool")
    assert child.text == str(value).lower(), doc


def assertEqualBrush(parent, brushstyle, r, g, b, doc=None):
    doc = doc or f"widget:{parent.attrib['name']}"
    prop = getNamedProperty(parent, "brush")
    assertIsNotNone(prop, doc)
    assertExpectedAttrib(prop, stdset="0", doc=doc)
    for item in prop.iter():
        if item.tag == "brush":
            assertExpectedAttrib(item, brushstyle=brushstyle, doc=doc)
    assertPropertyColor(prop, r, g, b, alpha="255")


def assertEqualChannel(parent, channel, doc=None):
    doc = doc or f"widget:{parent.attrib['name']}"
    assertEqualPropertyString(parent, "channel", channel)


def assertEqualClassName(parent, cls, nm, doc=None):
    doc = doc or f"widget:{parent.attrib['name']}"
    assertExpectedAttrib(parent, **{"class": cls, "name": nm})


def assertEqualColor(color, r=None, g=None, b=None):
    if color is None:
        assertIsNone(r)
        assertIsNone(g)
        assertIsNone(b)
    else:
        assertIsInstance(color, adl_parser.Color)
        assertEqual(color.r, r)
        assertEqual(color.b, b)
        assertEqual(color.g, g)


def assertEqualDouble(parent, expected, doc=None):
    doc = doc or f"widget:{parent.attrib['name']}"
    assert parent is not None
    child = getSubElement(parent, "double")
    assert float(child.text) == float(expected)


def assertEqualEnum(parent, expected, doc=None):
    doc = doc or f"widget:{parent.attrib['name']}"
    assert parent is not None
    child = getSubElement(parent, "enum")
    assert child.text == expected


def assertEqualGeometry(parent, x, y, w, h, doc=None):
    doc = doc or f"widget:{parent.attrib['name']}"
    prop = getNamedProperty(parent, "geometry")
    assertIsNotNone(prop)
    for item in prop.iter():
        if item.tag == "rect":
            assertEqual(len(item), 4)
        elif item.tag == "x":
            assertEqual(item.text, str(x))
        elif item.tag == "y":
            assertEqual(item.text, str(y))
        elif item.tag == "width":
            assertEqual(item.text, str(w))
        elif item.tag == "height":
            assertEqual(item.text, str(h))


def assertEqualNumber(parent, expected, doc=None, dtype=float):
    doc = doc or f"widget:{parent.attrib['name']}, expected:{expected}"
    child = getSubElement(parent, "number")
    assert parent is not None
    assert child.text is not None
    assert expected is not None
    assert dtype(child.text) == dtype(expected), doc


def assertEqualPenColor(parent, r, g, b, doc=None):
    doc = doc or f"widget:{parent.attrib['name']}"
    prop = getNamedProperty(parent, "penColor")
    assertIsNotNone(prop)
    assertExpectedAttrib(prop, stdset="0")
    assertPropertyColor(prop, r, g, b)


def assertEqualPenStyle(parent, value, doc=None):
    doc = doc or f"widget:{parent.attrib['name']}"
    prop = getNamedProperty(parent, "penStyle")
    assertIsNotNone(prop, doc)
    assertExpectedAttrib(prop, stdset="0")
    assertEqualEnum(prop, value)


def assertEqualPenCapStyle(parent, expected, doc=None):
    doc = doc or f"widget:{parent.attrib['name']}"
    assertEqualPropertyEnum(parent, "penCapStyle", expected)


def assertEqualPenWidth(parent, expected, doc=None):
    doc = doc or f"widget:{parent.attrib['name']}"
    assertEqualPropertyDouble(parent, "penWidth", expected)


def assertEqualPropertyBool(parent, propName, expected):
    doc = f"widget:{parent.attrib['name']}, property:{propName}"
    prop = getNamedProperty(parent, propName)
    assert prop is not None, doc
    assertEqualBool(prop, expected, doc)


def assertPropertyColor(parent, r, g, b, **kwargs):
    doc = f"widget:{parent.attrib['name']}"
    assertEqual(parent.tag, "property")
    for item in parent.iter():
        if item.tag == "color":
            assertEqual(len(item.attrib), len(kwargs))
            if len(kwargs) > 0:
                assertExpectedAttrib(item, doc=doc, **kwargs)
            assertColor(item, r, g, b)


def assertEqualPropertyDouble(parent, propName, expected):
    doc = f"widget:{parent.attrib['name']}, property:{propName}"
    prop = getNamedProperty(parent, propName)
    assert prop is not None, doc
    assertEqualDouble(prop, expected, doc)


def assertEqualPropertyEnum(parent, propName, expected):
    doc = f"widget:{parent.attrib['name']}, property:{propName}"
    prop = getNamedProperty(parent, propName)
    assert prop is not None, doc
    assertEqualEnum(prop, expected, doc)


def assertEqualPropertyNumber(parent, propName, expected, dtype=float):
    doc = f"widget:{parent.attrib['name']}, property:{propName}"
    prop = getNamedProperty(parent, propName)
    assert prop is not None, doc
    assertEqualNumber(prop, expected, doc=doc, dtype=dtype)


def assertEqualPropertyString(parent, propName, expected):
    doc = f"widget:{parent.attrib['name']}, property:{propName}"
    prop = getNamedProperty(parent, propName)
    doc += f" property:name:'{prop.attrib['name']}'"
    assert prop is not None, doc
    assert prop.attrib["name"] == propName
    assertEqualStringChild(prop, expected, doc)


def assertEqualPropertyStringlist(widget, tag, expected=[]):
    doc = f"widget:{widget.attrib['name']}"
    prop = getNamedProperty(widget, tag)
    stringlist = getSubElement(prop, "stringlist")
    assert len(stringlist) == len(expected)
    for i, string in enumerate(stringlist.findall("string")):
        expect_str = expected[i]
        assert string.text == expect_str


def assertEqualRules(parent, expected):
    prop = getNamedProperty(parent, "rules")
    assertIsNotNone(prop)
    assertExpectedAttrib(prop, stdset="0")
    child = getSubElement(prop, "string")
    assertIsNotNone(child)
    rules = output_handler.jsonDecode(child.text)
    assertEqual(len(rules), 1)
    assertExpectedDictInRef(rules[0], **expected)


def assertEqualStringChild(parent, text="", doc=None):
    child = getSubElement(parent, "string")
    doc = doc or ""
    doc += f"\nfound:{child.text}\nexpected:{text}"
    assert child.text == str(text), doc


def assertEqualStyleSheet(parent, expected):
    # doc = f"widget:{parent.attrib['name']} tag:{parent.attrib['class']}"
    assertEqualPropertyString(parent, "styleSheet", expected)


def assertEqualTitle(parent, title, doc=None):
    doc = doc or f"widget:{parent.attrib['name']}"
    prop = getNamedProperty(parent, "title")
    if title is None:
        assert prop is None, doc
    else:
        assert prop is not None, doc
        assertEqualStringChild(prop, title, doc)


def assertEqualToolTip(parent, expected):
    # doc = f"widget:{parent.attrib['name']}"
    assertEqualPropertyString(parent, "toolTip", expected)


def assertExpectedAttrib(parent, doc=None, **kwargs):
    doc = doc or f"element:{parent.tag}"
    assert hasattr(parent, "attrib")
    assertExpectedDictInRef(parent.attrib, **kwargs)


def assertExpectedDictInRef(ref, doc=None, **kwargs):
    assert isinstance(ref, dict), doc
    assert isinstance(kwargs, dict), doc
    for k, v in kwargs.items():
        assert k in ref, f"{doc}, k={k}, v={v}"
        assert v == ref[k], f"{doc}, k={k}, v={v}, ref[k]={ref[k]}"


def assertGreater(a, b, doc=None):
    assert a > b, doc


def assertHasAttribute(parent, attr_name):
    assertTrue(hasattr(parent, attr_name))


def assertIsNone(a, doc=None):
    assert a is None, doc


def assertIsNoneProperty(parent, propName):
    doc = f"widget:{parent.attrib['name']}, property:{propName}"
    prop = getNamedProperty(parent, propName)
    assert prop is None, doc


def assertIsNotNone(a, doc=None):
    assert a is not None, doc


def assertIn(a, b, doc=None):
    assert a in b, doc


def assertNotIn(a, b, doc=None):
    assert a not in b, doc


def assertIsInstance(a, b, doc=None):
    assert isinstance(a, b), doc


def assertTrue(a, doc=None):
    assert a, doc
