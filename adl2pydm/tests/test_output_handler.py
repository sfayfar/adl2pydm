import os
import pytest

from xml.etree import ElementTree

from . import _core
from ._core import tempdir
from .. import adl_parser



def test_write_widget_text_examples(tempdir):
    testfile = os.path.join(_core.MEDM_SCREEN_DIR, "text_examples.adl")
    assert os.path.exists(testfile)

    uiname = _core.convertAdlFile(testfile, tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    assert len(widgets) == 17

    key = "text_update"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMLabel", key)

    key = "text"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "QLabel", key)
    _core.assertEqualPropertyString(widget, "text", "macro P=${P}")

    key = "text_update"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMLabel", key)
    _core.assertEqualChannel(widget, "ca://${P}")

    # check that widget text will announce widget height
    for widget in widgets[2:]:
        geom = _core.getNamedProperty(widget, "geometry")
        height = None
        for item in geom.iter():
            if item.tag == "height":
                height = item.text
        _core.assertEqualPropertyString(widget, "text", "height: " + height)


def test_write_extends_customwidget(tempdir):
    uiname = _core.convertAdlFile("table_setup_SRI.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)

    root = ElementTree.parse(full_uiname).getroot()
    customwidgets = _core.getSubElement(root, "customwidgets")
    # self.print_xml_children(screen)
    widgets = customwidgets.findall("customwidget")

    customs = [_core.getSubElement(w, "class").text for w in widgets]
    assert "PyDMDrawingPie" in customs
    assert "PyDMDrawingArc" in customs


def test_write_all_example_files_process(tempdir):
    "ensure all example MEDM files are converted to PyDM"
    path = _core.MEDM_SCREEN_DIR
    for adl_file in os.listdir(path):
        if os.path.isfile(os.path.join(path, adl_file)):
            if adl_file.endswith(".adl"):
                uiname = _core.convertAdlFile(adl_file, tempdir)
                full_uiname = os.path.join(tempdir, uiname)
                assert os.path.exists(full_uiname), uiname


def test_write_widget_text(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    assert len(widgets) == 64

    key = "text"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "QLabel", key)
    _core.assertEqualPropertyString(widget, "text", "Test Display")

    for propName in "penStyle penColor penWidth penCapStyle".split():
        _core.assertIsNoneProperty(widget, propName)

    prop = _core.getNamedProperty(widget, "alignment")
    child = _core.getSubElement(prop, "set")
    assert child is not None
    assert child.text == "Qt::AlignCenter"


def test_write_widget_valuator_variations(tempdir):
    uiname = _core.convertAdlFile("slider.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    assert len(widgets) == 1

    key = "valuator"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMSlider", key)
    _core.assertEqualChannel(widget, "ca://sky:userCalc2.A")
    _core.assertEqualPropertyString(widget, "orientation", "Qt::Horizontal")
    _core.assertEqualPropertyNumber(widget, "precision", int(0.1))
    _core.assertEqualPropertyBool(widget, "userDefinedLimits", True)
    _core.assertEqualPropertyDouble(widget, "userMaximum", 10)
    _core.assertEqualPropertyDouble(widget, "userMinimum", -10)
    _core.assertEqualPropertyBool(widget, "showLimitLabels", True)
    _core.assertEqualPropertyBool(widget, "showValueLabel", True)


def test_write_widget_wheel_switch(tempdir):
    uiname = _core.convertAdlFile("wheel_switch.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    assert len(widgets) == 1

    key = "wheel_switch"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMSpinbox", key)
    _core.assertEqualChannel(widget, "ca://sky:userCalc2.A")
    _core.assertEqualPropertyDouble(widget, "maximum", 10)
    _core.assertEqualPropertyDouble(widget, "minimum", -10)
    _core.assertEqualPropertyBool(widget, "showLimitLabels", True)
    _core.assertEqualPropertyBool(widget, "showValueLabel", False)
    _core.assertEqualPropertyBool(widget, "userDefinedLimits", True)


def test_write_widget_valuator(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    assert len(widgets) == 64

    key = "valuator"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMSlider", key)
    _core.assertEqualChannel(widget, "ca://sky:m1")
    _core.assertEqualPropertyString(widget, "orientation", "Qt::Horizontal")
    # precision must be an integer for the slider widget
    _core.assertEqualPropertyNumber(widget, "precision", 1)
    _core.assertEqualPropertyBool(widget, "showLimitLabels", True)
    _core.assertEqualPropertyBool(widget, "showValueLabel", True)
    # self.assertEqualPropertyBool(widget, "userDefinedLimits", False)
    for propName in """userMaximum
                        userMinimum
                        userDefinedLimits
                        """.split():
        _core.assertIsNoneProperty(widget, propName)

    uiname = _core.convertAdlFile("valuators.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)
    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    assert screen is not None

    # fields:
    # name :
    # 0: orientation
    # 1: showValueLabel
    # 2: showLimitLabels
    # 3: showUnits
    # 4: tickPosition
    # 5: precision
    # 6: foregroundColor
    # 7: backgroundColor
    import collections
    Expectation = collections.namedtuple(
        "Expectations", """
        name
        orientation
        showValueLabel
        showLimitLabels
        showUnits
        tickPosition
        precision
        foregroundColor
        backgroundColor
        """.split()
    )
    expectations = {
        "valuator": [
            "up",
            False,
            True,
            False,
            "NoTicks",
            1,
            (0, 0, 0),
            (187, 187, 187),
        ],
        "valuator_1": [
            "down",
            False,
            True,
            False,
            "NoTicks",
            1,
            (0, 0, 0),
            (187, 187, 187),
        ],
        "valuator_2": [
            "right",
            False,
            True,
            False,
            "NoTicks",
            1,
            (0, 0, 0),
            (187, 187, 187),
        ],
        "valuator_3": [
            "left",
            False,
            True,
            False,
            "NoTicks",
            1,
            (0, 0, 0),
            (187, 187, 187),
        ],
        "valuator_4": [
            "up",
            False,
            True,
            False,
            "NoTicks",
            5,
            (253, 0, 0),
            (0, 216, 0),
        ],
        "valuator_5": [
            "left",
            True,
            True,
            False,
            "NoTicks",
            1,
            (0, 0, 0),
            (187, 187, 187),
        ],
        "valuator_6": [
            "left",
            True,
            True,
            False,
            "NoTicks",
            1,
            (0, 0, 0),
            (187, 187, 187),
        ],
    }
    widgets = screen.findall("widget")
    assert len(widgets) == 8
    for w in widgets:
        if w.attrib["class"] == "PyDMSlider":
            nm = w.attrib["name"]
            assert nm in expectations
            exp = expectations[nm]

            direction = exp[0]
            if direction in ("up", "down"):
                e = "Qt::Vertical"
            else:
                e = "Qt::Horizontal"
            _core.assertEqualPropertyString(w, "orientation", e)
            if direction in ("down", "right"):
                # self.assertEqualPropertyBool(w, "invertedAppearance", True)
                # PyDMSLider does not have this property
                _core.assertIsNoneProperty(w, "invertedAppearance")
            _core.assertEqualPropertyBool(w, "showValueLabel", exp[1])
            _core.assertEqualPropertyBool(w, "showLimitLabels", exp[2])
            _core.assertEqualPropertyBool(w, "showUnits", exp[3])
            if exp[4] is None:
                _core.assertIsNoneProperty(w, "tickPosition")
            else:
                _core.assertEqualPropertyEnum(w, "tickPosition", exp[4])
            if exp[5] is None:
                _core.assertIsNoneProperty(w, "precision")
            else:
                _core.assertEqualPropertyNumber(w, "precision", exp[5])

            c = adl_parser.Color(*exp[6])
            bc = adl_parser.Color(*exp[7])
            expected = (
                f"PyDMSlider#{nm}"
                " {\n"
                f"  color: rgb({c.r}, {c.g}, {c.b});\n"
                f"  background-color: rgb({bc.r}, {bc.g}, {bc.b});\n"
                "  }"
            )
            _core.assertEqualStyleSheet(w, expected)
