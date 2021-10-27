import os
import pytest

from xml.etree import ElementTree

from . import _core
from ._core import tempdir
from .. import adl_parser
from .. import output_handler


@pytest.mark.parametrize("test_file", _core.ALL_EXAMPLE_FILES)
def test_write_all_example_files_process(test_file, tempdir):
    "ensure all example MEDM files are converted to PyDM"
    path = _core.MEDM_SCREEN_DIR
    if os.path.isfile(os.path.join(path, test_file)):
        if test_file.endswith(".adl"):
            uiname = _core.convertAdlFile(test_file, tempdir)
            full_uiname = os.path.join(tempdir, uiname)
            assert os.path.exists(full_uiname), uiname


def test_write_extends_customwidget(tempdir):
    uiname = _core.convertAdlFile("table_setup_SRI.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)

    root = ElementTree.parse(full_uiname).getroot()
    customwidgets = _core.getSubElement(root, "customwidgets")
    widgets = customwidgets.findall("customwidget")

    customs = [_core.getSubElement(w, "class").text for w in widgets]
    assert "PyDMDrawingPie" in customs
    assert "PyDMDrawingArc" in customs


def test_write_widget_arc(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 64)

    key = "arc"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMDrawingPie", key)
    _core.assertEqualPenStyle(widget, "Qt::SolidLine")
    _core.assertIsNoneProperty(widget, "startAngle")  # default: 0
    _core.assertEqualPropertyDouble(widget, "spanAngle", -320)
    _core.assertEqualBrush(widget, "SolidPattern", 251, 243, 74)


def test_write_widget_bar(tempdir):
    uiname = _core.convertAdlFile("bar_monitor.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")

    # name
    # orientation
    # barIndicator
    # showValue
    # showTicks
    # showLimits
    # indicatorColor
    # backgroundColor
    expectations = {
        "bar": ["left", True, False, False, False, (253, 0, 0), (187, 187, 187)],
        "bar_1": ["left", True, False, False, False, (253, 0, 0), (187, 187, 187)],
        "bar_2": ["left", True, True, True, False, (253, 0, 0), (187, 187, 187)],
        "bar_3": ["up", True, False, False, False, (253, 0, 0), (187, 187, 187)],
        "bar_4": ["down", True, False, False, False, (253, 0, 0), (187, 187, 187)],
        "bar_5": ["right", True, False, False, False, (253, 0, 0), (187, 187, 187)],
        "bar_6": ["right", True, False, False, False, (253, 0, 0), (187, 187, 187)],
    }
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 22)
    for w in widgets:
        if w.attrib["class"] == "PyDMScaleIndicator":
            nm = w.attrib["name"]
            _core.assertIn(nm, expectations)
            exp = expectations[nm]

            direction = exp[0]
            if direction in ("up", "down"):
                e = "Qt::Vertical"
            else:
                e = "Qt::Horizontal"
            _core.assertEqualPropertyString(w, "orientation", e)
            if direction in ("down", "right"):
                _core.assertEqualPropertyBool(w, "invertedAppearance", True)
            _core.assertEqualPropertyBool(w, "barIndicator", exp[1])
            _core.assertEqualPropertyBool(w, "showValue", exp[2])
            _core.assertEqualPropertyBool(w, "showTicks", exp[3])
            _core.assertEqualPropertyBool(w, "showLimits", exp[4])

            prop = _core.getNamedProperty(w, "indicatorColor")
            _core.assertPropertyColor(prop, *exp[5])
            prop = _core.getNamedProperty(w, "backgroundColor")
            _core.assertPropertyColor(prop, *exp[6])
        if w.attrib["class"] == "PyDMSlider":
            nm = w.attrib["name"]
            _core.assertEqual(nm, "valuator")
            # _core.assertEqualPropertyBool(w, "showValueLabel", False)
            # _core.assertEqualPropertyBool(w, "showLimitLabels", False)


def test_write_widget_byte(tempdir):
    uiname = _core.convertAdlFile("byte-monitor.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 4)

    key = "byte"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMByteIndicator", key)
    _core.assertEqualChannel(widget, "ca://sky:interp_mode")

    prop = _core.getNamedProperty(widget, "onColor")
    _core.assertPropertyColor(prop, 0, 0, 0)
    prop = _core.getNamedProperty(widget, "offColor")
    _core.assertPropertyColor(prop, 187, 187, 187)
    _core.assertEqualPropertyString(widget, "orientation", "Qt::Horizontal")
    _core.assertEqualPropertyBool(widget, "showLabels", False)
    _core.assertEqualPropertyBool(widget, "bigEndian", False)
    _core.assertEqualPropertyNumber(widget, "numBits", 4)

    key = "byte_1"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMByteIndicator", key)
    _core.assertEqualChannel(widget, "ca://sky:interp_mode")

    prop = _core.getNamedProperty(widget, "onColor")
    _core.assertPropertyColor(prop, 0, 0, 0)
    prop = _core.getNamedProperty(widget, "offColor")
    _core.assertPropertyColor(prop, 187, 187, 187)
    _core.assertEqualPropertyString(widget, "orientation", "Qt::Horizontal")
    _core.assertEqualPropertyBool(widget, "showLabels", False)
    _core.assertEqualPropertyBool(widget, "bigEndian", True)
    _core.assertEqualPropertyNumber(widget, "numBits", 4)

    key = "byte_2"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMByteIndicator", key)
    _core.assertEqualChannel(widget, "ca://sky:interp_mode")

    prop = _core.getNamedProperty(widget, "onColor")
    _core.assertPropertyColor(prop, 0, 0, 0)
    prop = _core.getNamedProperty(widget, "offColor")
    _core.assertPropertyColor(prop, 187, 187, 187)
    _core.assertEqualPropertyString(widget, "orientation", "Qt::Vertical")
    _core.assertEqualPropertyBool(widget, "showLabels", False)
    _core.assertEqualPropertyBool(widget, "bigEndian", False)
    _core.assertEqualPropertyNumber(widget, "numBits", 4)

    key = "byte_3"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMByteIndicator", key)
    _core.assertEqualChannel(widget, "ca://sky:interp_mode")

    prop = _core.getNamedProperty(widget, "onColor")
    _core.assertPropertyColor(prop, 0, 0, 0)
    prop = _core.getNamedProperty(widget, "offColor")
    _core.assertPropertyColor(prop, 187, 187, 187)
    _core.assertEqualPropertyString(widget, "orientation", "Qt::Vertical")
    _core.assertEqualPropertyBool(widget, "showLabels", False)
    _core.assertEqualPropertyBool(widget, "bigEndian", True)
    _core.assertEqualPropertyNumber(widget, "numBits", 4)


def test_write_widget_cartesian_plot(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 64)

    key = "cartesian_plot"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMWaveformPlot", key)
    _core.assertEqualTitle(widget, "Calibration Curve (S1A:H1)")
    _core.assertEqualPropertyStringlist(widget, "xLabels", ["Magnetic Field",])
    _core.assertEqualPropertyStringlist(widget, "yLabels", ["Current",])

    prop = _core.getNamedProperty(widget, "curves")
    stringlist = _core.getSubElement(prop, "stringlist")
    _core.assertEqual(len(stringlist), 1)
    trace = output_handler.jsonDecode(stringlist[0].text)
    expected = dict(
        name="curve 1",
        x_channel="ca://Xorbit:S1A:H1:CurrentAI.BARR",
        y_channel="ca://Xorbit:S1A:H1:CurrentAI.IARR",
        color="#000000",
        lineStyle=1,
        lineWidth=1,
        block_size=8,
        redraw_mode=2,
        symbolSize=10,
    )
    _core.assertDictEqual(trace, expected)


def test_write_widget_choice_button(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 64)

    key = "choice_button"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMEnumButton", key)
    _core.assertEqualChannel(widget, "ca://sky:m1.SCAN")


def test_write_widget_composite(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 64)

    key = "composite"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMFrame", key)
    _core.assertEqual(len(widget), 6)


def test_write_widget_embedded_display(tempdir):
    # Actually. MEDM writes as a composite
    # but we redirect (in the output_handler module)
    # that to be an "embedded display".
    uiname = _core.convertAdlFile("configMenu.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 19)

    key = "composite"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMEmbeddedDisplay", key)
    _core.assertEqual(len(widget), 4)
    _core.assertEqualPropertyString(widget, "filename", "configMenuHead_bare.ui")
    _core.assertEqualPropertyString(widget, "macros", "P=${P},CONFIG=${CONFIG}")


def test_write_widget_image(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 64)

    key = "image"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMDrawingImage", key)
    _core.assertEqualPropertyString(widget, "filename", "apple.gif")


def test_write_widget_indicator(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 64)

    key = "indicator"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMScaleIndicator", key)

    _core.assertEqualChannel(widget, "ca://sky:m1.RBV")

    key = "meter"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMScaleIndicator", key)

    _core.assertEqualChannel(widget, "ca://sky:m1.RBV")

    # meter widget has no title
    _core.assertEqualTitle(widget, None)

    _core.assertEqualPropertyBool(widget, "limitsFromChannel", False)

    # if not found, then gets default value in PyDM
    for item in "userUpperLimit userLowerLimit".split():
        prop = _core.getNamedProperty(widget, item)
        _core.assertIsNone(prop, item)


def test_write_widget_menu(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 64)

    key = "menu"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMEnumComboBox", key)
    _core.assertEqualChannel(widget, "ca://sky:m1.SPMG")


def test_write_widget_message_button(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 64)

    key = "message_button"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMPushButton", "message_button")
    _core.assertEqualPropertyString(widget, "text", "sky:m1 to zero")
    _core.assertEqualPropertyString(widget, "toolTip", "sky:m1")
    _core.assertEqualChannel(widget, "ca://sky:m1")
    _core.assertEqualPropertyString(widget, "pressValue", "0.00")


def test_write_widget_meter(tempdir):
    uiname = _core.convertAdlFile("meter.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 1)

    key = "meter"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMScaleIndicator", key)
    _core.assertEqualTitle(widget, None)  # meter widget has no title
    _core.assertEqualPropertyBool(widget, "limitsFromChannel", False)
    _core.assertEqualPropertyDouble(widget, "userUpperLimit", 10)
    _core.assertEqualPropertyDouble(widget, "userLowerLimit", -10)


def test_write_widget_oval(tempdir):
    uiname = _core.convertAdlFile("bar_monitor.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")

    # brush (color)
    # brush (brushstyle)
    # penStyle
    # penCapStyle
    # penWidth
    expectations = {
        "oval": [(0, 0, 0), "SolidPattern", "Qt::SolidLine", "Qt::FlatCap", 0],
        "oval_1": [(0, 0, 0), "NoBrush", "Qt::SolidLine", "Qt::FlatCap", 0],
        "oval_2": [(0, 0, 0), "NoBrush", "Qt::DashLine", "Qt::FlatCap", 0],
        "oval_3": [(253, 0, 0), "SolidPattern", "Qt::SolidLine", "Qt::FlatCap", 0],
        "oval_4": [(253, 0, 0), "NoBrush", "Qt::SolidLine", "Qt::FlatCap", 4],
        "oval_5": [(253, 0, 0), "NoBrush", "Qt::DashLine", "Qt::FlatCap", 0],
        "oval_6": [(253, 0, 0), "SolidPattern", "Qt::SolidLine", "Qt::FlatCap", 0],
        "oval_7": [(0, 0, 0), "SolidPattern", "Qt::SolidLine", "Qt::FlatCap", 0],
    }
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 22)
    for w in widgets:
        if w.attrib["class"] == "PyDMDrawingEllipse":
            nm = w.attrib["name"]
            _core.assertIn(nm, expectations)
            exp = expectations[nm]

            brushProp = _core.getNamedProperty(w, "brush")
            _core.assertIsNotNone(brushProp, nm)
            brush = brushProp.find("brush")
            _core.assertIsNotNone(brush, nm)
            brushstyle = brush.attrib.get("brushstyle")
            _core.assertEqual(brushstyle, exp[1])
            color = brush.find("color")
            _core.assertColor(color, *exp[0])

            penColor = _core.getNamedProperty(w, "penColor")
            _core.assertPropertyColor(penColor, *exp[0])
            _core.assertEqualPropertyEnum(w, "penStyle", exp[2])
            if exp[4] == 0:
                _core.assertIsNone(_core.getNamedProperty(w, "penWidth"))
            else:
                _core.assertEqualPropertyDouble(w, "penWidth", exp[4])

            if nm == "oval_6":
                expected = {
                    "name": "visibility",
                    "property": "Visible",
                    "channels": [{"channel": "ca://demo:bar_RBV", "trigger": True, "use_enum": False}],
                    "expression": "ch[0]>128",
                }
                _core.assertEqualRules(w, expected)
            elif nm == "oval_7":
                expected = {
                    "name": "visibility",
                    "property": "Visible",
                    "channels": [{"channel": "ca://demo:bar", "trigger": True, "use_enum": False}],
                    "expression": "ch[0]==0",
                }
                _core.assertEqualRules(w, expected)


def test_write_widget_polygon(tempdir):
    uiname = _core.convertAdlFile("polygons.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    _core.assertIsNotNone(screen, full_uiname)
    # TODO: complete


def test_write_widget_polyline(tempdir):
    uiname = _core.convertAdlFile("polyline.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 1)

    key = "polyline"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMDrawingPolyline", key)

    prop = _core.getNamedProperty(widget, "points")
    stringlist = _core.getSubElement(prop, "stringlist")
    _core.assertEqual(len(stringlist), 6)
    strings = stringlist.findall("string")
    _core.assertEqual(len(strings), 6)
    _core.assertEqual(strings[0].text, "-2, -2")
    _core.assertEqual(strings[1].text, "55, -2")
    _core.assertEqual(strings[2].text, "-2, 55")
    _core.assertEqual(strings[3].text, "55, 55")
    _core.assertEqual(strings[4].text, "-2, -2")
    _core.assertEqual(strings[5].text, "-2, 6")
    _core.assertEqualPenWidth(widget, 4)
    _core.assertEqualPenCapStyle(widget, "Qt::FlatCap")


def test_write_widget_polyline_with_rules(tempdir):
    uiname = _core.convertAdlFile("polyline-arrow.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 1)

    key = "polyline"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMDrawingPolyline", key)

    _core.assertEqualChannel(widget, "ca://PYDM:visible")
    expected = {
        "name": "visibility",
        "property": "Visible",
        "channels": [{"channel": "ca://PYDM:visible", "trigger": True, "use_enum": False}],
        "expression": "ch[0]!=0",
    }
    _core.assertEqualRules(widget, expected)


def test_write_widget_rectangle(tempdir):
    """
    also test the full file structure
    """
    uiname = _core.convertAdlFile("rectangle.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    # five rectangle widgets
    tree = ElementTree.parse(full_uiname)
    root = tree.getroot()
    _core.assertEqual(root.tag, "ui")
    _core.assertEqual(len(root), 3)

    screen = _core.getSubElement(root, "widget")
    _core.assertEqualClassName(screen, "QWidget", "screen")
    properties = screen.findall("property")
    _core.assertEqual(len(properties), 3)
    _core.assertEqualGeometry(screen, 96, 57, 142, 182)
    expected = (
        "QWidget#screen {\n"
        "  color: rgb(0, 0, 0);\n"
        "  background-color: rgb(133, 133, 133);\n"
        "  }"
    )
    _core.assertEqualStyleSheet(screen, expected)

    prop = _core.getNamedProperty(screen, "windowTitle")
    _core.assertExpectedAttrib(prop, name="windowTitle")
    _core.assertEqualStringChild(prop, "rectangle")

    children = screen.findall("widget")
    _core.assertEqual(len(children), 5)

    key = "rectangle"
    rect = children[0]
    _core.assertEqualClassName(rect, "PyDMDrawingRectangle", key)
    _core.assertEqualGeometry(rect, 10, 15, 113, 35)
    _core.assertEqualToolTip(rect, key)

    key = "rectangle_1"
    rect = children[1]
    _core.assertEqualClassName(rect, "PyDMDrawingRectangle", key)
    _core.assertEqualGeometry(rect, 10, 53, 113, 35)
    _core.assertEqualToolTip(rect, key)
    properties = rect.findall("property")
    _core.assertEqual(len(properties), 7)
    _core.assertEqualBrush(rect, "NoBrush", 253, 0, 0)
    _core.assertEqualPenStyle(rect, "Qt::SolidLine")
    _core.assertEqualPenColor(rect, 253, 0, 0)
    _core.assertEqualPenWidth(rect, 1)
    _core.assertEqualPenCapStyle(rect, "Qt::FlatCap")

    key = "rectangle_2"
    rect = children[2]
    _core.assertEqualClassName(rect, "PyDMDrawingRectangle", key)
    _core.assertEqualGeometry(rect, 10, 92, 113, 35)
    _core.assertEqualToolTip(rect, key)
    properties = rect.findall("property")
    _core.assertEqual(len(properties), 7)
    _core.assertEqualBrush(rect, "NoBrush", 249, 218, 60)
    _core.assertEqualPenStyle(rect, "Qt::DashLine")
    _core.assertEqualPenColor(rect, 249, 218, 60)
    _core.assertEqualPenWidth(rect, 1)
    _core.assertEqualPenCapStyle(rect, "Qt::FlatCap")

    key = "rectangle_3"
    rect = children[3]
    _core.assertEqualClassName(rect, "PyDMDrawingRectangle", key)
    _core.assertEqualGeometry(rect, 10, 130, 113, 36)
    _core.assertEqualToolTip(rect, key)
    properties = rect.findall("property")
    _core.assertEqual(len(properties), 8)
    _core.assertEqualBrush(rect, "NoBrush", 115, 255, 107)
    _core.assertEqualPenStyle(rect, "Qt::SolidLine")
    _core.assertEqualPenColor(rect, 115, 255, 107)
    _core.assertEqualPenWidth(rect, 6)
    _core.assertEqualPenCapStyle(rect, "Qt::FlatCap")

    prop = _core.getNamedProperty(rect, "rules")
    _core.assertExpectedAttrib(prop, stdset="0")
    child = _core.getSubElement(prop, "string")
    rules = output_handler.jsonDecode(child.text)
    _core.assertEqual(len(rules), 1)
    expected = {
        "name": "visibility",
        "property": "Visible",
        "channels": [
            {"channel": "ca://${P}alldone", "trigger": True, "use_enum": False}
        ],
        "expression": "ch[0]==0",
    }
    _core.assertExpectedDictInRef(rules[0], **expected)

    key = "rectangle_4"
    rect = children[4]
    _core.assertEqualClassName(rect, "PyDMDrawingRectangle", key)
    _core.assertEqualGeometry(rect, 20, 138, 93, 20)
    _core.assertEqualToolTip(rect, key)
    properties = rect.findall("property")
    _core.assertEqual(len(properties), 8)
    _core.assertEqualBrush(rect, "SolidPattern", 115, 223, 255)
    _core.assertEqualPenStyle(rect, "Qt::SolidLine")
    _core.assertEqualPenColor(rect, 115, 223, 255)
    _core.assertEqualPenWidth(rect, 0)
    _core.assertEqualPenCapStyle(rect, "Qt::FlatCap")

    expected = {
        "name": "visibility",
        "property": "Visible",
        "channels": [
            {"channel": "ca://${P}${M}.RBV", "trigger": True, "use_enum": False},
            {"channel": "ca://${P}${M}.VAL", "trigger": True, "use_enum": False},
        ],
        "expression": "ch[0]==ch[1]",
    }
    _core.assertEqualRules(rect, expected)


def test_write_widget_related_display(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 64)

    key = "related_display"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMRelatedDisplayButton", key)

    tips = screen.findall("toolTip")
    _core.assertEqual(len(tips), 0, "no tooltip if no title")
    text = _core.getNamedProperty(widget, "text")
    _core.assertIsNone(text)

    expected = (
        f"PyDMRelatedDisplayButton#{key}"
        " {\n"
        "  color: rgb(0, 0, 0);\n"
        "  background-color: rgb(115, 223, 255);\n"
        "  }"
    )
    _core.assertEqualStyleSheet(widget, expected)

    _core.assertEqualPropertyBool(widget, "openInNewWindow", True)
    _core.assertEqualPropertyBool(widget, "showIcon", True)

    prop = _core.getNamedProperty(widget, "filenames")
    stringlist = prop.find("stringlist")
    _core.assertEqual(len(stringlist), 1)
    _core.assertEqualStringChild(stringlist, "junk.ui")

    prop = _core.getNamedProperty(widget, "titles")
    stringlist = prop.find("stringlist")
    _core.assertEqual(len(stringlist), 1)
    _core.assertEqualStringChild(stringlist, "Another Junk")

    prop = _core.getNamedProperty(widget, "macros")
    stringlist = prop.find("stringlist")
    _core.assertEqual(len(stringlist), 1)
    child = stringlist.find("string")
    _core.assertIsNone(child.text)


def test_write_widget_strip_chart_axis_labels(tempdir):
    uiname = _core.convertAdlFile("strip.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 1)

    key = "strip_chart"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMTimePlot", key)
    _core.assertEqualTitle(widget, "chart title text")
    _core.assertEqualPropertyString(widget, "xLabels", "x axis text")
    _core.assertEqualPropertyString(widget, "yLabels", "y axis text")


def test_write_widget_shell_command(tempdir):
    uiname = _core.convertAdlFile("test_shell_command.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    _core.assertTrue(os.path.exists(full_uiname))

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    _core.assertEqual(len(widgets), 1)

    key = "shell_command"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMShellCommand", key)
    _core.assertEqualPropertyString(widget, "text", "shell commands")
    _core.assertEqualPropertyBool(widget, "showIcon", False)
    _core.assertEqualPropertyBool(widget, "allowMultipleExecutions", True)

    prop = _core.getNamedProperty(widget, "titles")
    stringlist = _core.getSubElement(prop, "stringlist")
    _core.assertEqual(len(stringlist), 4)
    titles = [t.text for t in stringlist]
    expected = [
        "Eyes",
        "System Load",
        "Command with Arguments",
        "Command with Arguments",
    ]
    _core.assertEqual(titles, expected)

    prop = _core.getNamedProperty(widget, "commands")
    stringlist = _core.getSubElement(prop, "stringlist")
    _core.assertEqual(len(stringlist), 4)
    commands = [t.text for t in stringlist]
    expected = [
        "xeyes",
        "xload",
        "pvview sky:UPTIME",
        "pvview sky:datetime",
    ]
    _core.assertEqual(commands, expected)


def test_write_widget_strip_chart(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    assert len(widgets) == 64

    key = "strip_chart"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMTimePlot", key)

    _core.assertEqualTitle(widget, "Horizontal Correctors")

    prop = _core.getNamedProperty(widget, "curves")
    stringlist = _core.getSubElement(prop, "stringlist")
    assert len(stringlist) == 3
    trace = output_handler.jsonDecode(stringlist[0].text)
    expected = {
        "color": "#cd6100",
        "lineStyle": 1,
        "lineWidth": 1,
        "channel": "ca://sky:m1",
        "name": "sky:m1",
    }
    _core.assertDictEqual(trace, expected)
    trace = output_handler.jsonDecode(stringlist[1].text)
    expected = {
        "color": "#610a75",
        "lineStyle": 1,
        "lineWidth": 1,
        "channel": "ca://Xorbit:S1A:H2:CurrentAO",
        "name": "Xorbit:S1A:H2:CurrentAO",
    }
    _core.assertDictEqual(trace, expected)
    trace = output_handler.jsonDecode(stringlist[2].text)
    expected = {
        "color": "#4ea5f9",
        "lineStyle": 1,
        "lineWidth": 1,
        "channel": "ca://Xorbit:S1A:H3:CurrentAO",
        "name": "Xorbit:S1A:H3:CurrentAO",
    }
    _core.assertDictEqual(trace, expected)


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


def test_write_widget_text_entry(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    assert len(widgets) == 64

    key = "text_entry"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMLineEdit", key)

    for propName in "penStyle penColor penWidth penCapStyle".split():
        _core.assertIsNoneProperty(widget, propName)

    _core.assertEqualChannel(widget, "ca://sky:m1")


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


def test_write_widget_text_update(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    assert len(widgets) == 64

    key = "text_update"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "PyDMLabel", key)
    expected = (
        f"PyDMLabel#{key}"
        " {\n"
        f"  color: rgb(88, 147, 255);\n"
        f"  background-color: rgb(236, 236, 236);\n"
        "  }"
    )
    _core.assertEqualStyleSheet(widget, expected)

    _core.assertEqualChannel(widget, "ca://sky:m1.RBV")

    for propName in "penStyle penColor penWidth penCapStyle".split():
        _core.assertIsNoneProperty(widget, propName)

    prop = _core.getNamedProperty(widget, "textInteractionFlags")
    child = _core.getSubElement(prop, "set")
    assert child is not None
    assert (
        child.text == "Qt::TextSelectableByKeyboard|Qt::TextSelectableByMouse"
    )


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
    # _core.assertEqualPropertyBool(widget, "userDefinedLimits", False)
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
                # _core.assertEqualPropertyBool(w, "invertedAppearance", True)
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


def test_zorder(tempdir):
    fname = os.path.join(tempdir, "test.xml")
    writer = output_handler.PYDM_Writer(None)
    writer.openFile(fname)
    specs = [
        # order     vis text
        ("widget_0", 2, "first"),
        ("widget_4", 0, "last"),
        ("widget_1", -3, 3),
        ("widget_2", 2, 4),
    ]
    for args in specs:
        writer.widget_stacking_info.append(output_handler.Qt_zOrder(*args))
    writer.closeFile()
    _core.assertTrue(os.path.exists(fname))

    with open(fname, "r") as fp:
        buf = fp.readlines()
    expected = (
        '<?xml version="1.0" ?>',
        '<ui version="4.0">',
        "  <zorder>first</zorder>",
        "  <zorder>3</zorder>",
        "  <zorder>4</zorder>",
        "  <zorder>last</zorder>",
        "</ui>",
    )
    _core.assertEqual(len(buf), len(expected))
    for idx in range(len(buf)):
        _core.assertEqual(buf[idx].rstrip(), expected[idx])


def test_xml_subelements(tempdir):
    fname = os.path.join(tempdir, "test.xml")
    writer = output_handler.PYDM_Writer(None)
    writer.openFile(fname)
    root = writer.root
    writer.writeProperty(root, "example", "text value")
    writer.writeProperty(root, "another_example", "upper", "enum")
    sub = root
    for tag in "banana banana banana orange".split():
        sub = writer.writeOpenTag(sub, tag)
    writer.closeFile()
    _core.assertTrue(os.path.exists(fname))

    with open(fname, "r") as fp:
        buf = fp.readlines()
    expected = (
        '<?xml version="1.0" ?>',
        '<ui version="4.0">',
        '  <property name="example">',
        "    <string>text value</string>",
        "  </property>",
        '  <property name="another_example">',
        "    <enum>upper</enum>",
        "  </property>",
        "  <banana>",
        "    <banana>",
        "      <banana>",
        "        <orange/>",
        "      </banana>",
        "    </banana>",
        "  </banana>",
        "</ui>",
    )
    _core.assertEqual(len(buf), len(expected))
