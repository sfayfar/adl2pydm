import os
import pytest

from xml.etree import ElementTree

from . import _core
from ._core import tempdir



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
