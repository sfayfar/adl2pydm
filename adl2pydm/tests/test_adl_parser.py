import os
import pytest

from . import _core
from ._core import tempdir
from .. import adl_parser


def parseFile(short_name):
    full_name = os.path.join(_core.MEDM_SCREEN_DIR, short_name)

    screen = adl_parser.MedmMainWidget()
    buf = screen.getAdlLines(full_name)
    screen.parseAdlBuffer(buf)
    return screen


def assertEqualDictKeyValue(dictionary, key, value):
    _core.assertIsInstance(dictionary, dict)
    _core.assertIn(key, dictionary)
    _core.assertEqual(dictionary[key], value)


def assertEqualGeometry(parent, x, y, w, h):
    assertHasAttribute(parent, "geometry")
    geom = parent.geometry
    _core.assertEqual(geom.x, x)
    _core.assertEqual(geom.y, y)
    _core.assertEqual(geom.width, w)
    _core.assertEqual(geom.height, h)


def assertEqualPoint( point, x, y):
    _core.assertIsInstance(point, adl_parser.Point)
    _core.assertEqual(point.x, x)
    _core.assertEqual(point.y, y)


def assertEqualTitle(parent, title):
    assertHasAttribute(parent, "title")
    _core.assertEqual(parent.title, title)


def assertHasAttribute(parent, attr_name):
    _core.assertTrue(hasattr(parent, attr_name))


@pytest.mark.parametrize("test_file", _core.ALL_EXAMPLE_FILES)
def test_adl_parser(test_file):
    assert isinstance(test_file, str)
    if not test_file.endswith(".adl"):
        return

    screen = adl_parser.MedmMainWidget()
    _core.assertEqual(screen.line_offset, 1)

    full_name = os.path.join(_core.MEDM_SCREEN_DIR, test_file)
    _core.assertTrue(os.path.exists(full_name))

    buf = screen.getAdlLines(full_name)
    # any useful MEDM file has more than 10 lines
    _core.assertGreater(len(buf), 10)

    screen.parseAdlBuffer(buf)
    _core.assertGreater(len(screen.widgets), 0)

# -------------------------------------------------

def test_parse_medm_file_std():
    screen = parseFile("std-R3-5-ID_ctrl.adl")

    assertEqualGeometry(screen, 10, 10, 290, 310)
    _core.assertEqualColor(screen.color, 0, 0, 0)
    _core.assertEqualColor(screen.background_color, 212, 219, 157)
    _core.assertEqual(
        screen.adl_filename, "/home/oxygen16/MOHAN/user_adl/ID_ctrl.adl"
    )
    _core.assertEqual(screen.adl_version, "020199")
    _core.assertEqual(screen.cmap, "")
    _core.assertEqual(len(screen.color_table), 65)
    _core.assertEqualColor(screen.color_table[0], 255, 255, 255)
    _core.assertEqualColor(screen.color_table[1], 236, 236, 236)
    _core.assertEqualColor(screen.color_table[25], 88, 147, 255)
    _core.assertEqualColor(screen.color_table[-1], 26, 115, 9)
    _core.assertEqual(screen.line_offset, 1)
    _core.assertEqual(screen.symbol, None)
    assertEqualTitle(screen, None)


def test_parse_medm_file_beamHistory_full():
    screen = parseFile("beamHistory_full-R3-5.adl")

    assertEqualGeometry(screen, 10, 10, 500, 650)
    _core.assertEqualColor(screen.color, 0, 0, 0)
    _core.assertEqualColor(screen.background_color, 212, 219, 157)
    _core.assertEqual(
        screen.adl_filename, "/net/epics/xfd/WWW/xfd/operations/SR_Status.adl"
    )
    _core.assertEqual(screen.adl_version, "020199")
    _core.assertEqual(screen.cmap, "")
    _core.assertEqual(len(screen.color_table), 65)
    _core.assertEqualColor(screen.color_table[0], 255, 255, 255)
    _core.assertEqualColor(screen.color_table[1], 236, 236, 236)
    _core.assertEqualColor(screen.color_table[25], 88, 147, 255)
    _core.assertEqualColor(screen.color_table[-1], 26, 115, 9)
    _core.assertEqual(screen.line_offset, 1)
    _core.assertEqual(screen.symbol, None)
    assertEqualTitle(screen, None)


def test_parse_medm_widget_arc():
    screen = parseFile("sampleWheel.adl")
    w = _core.pickWidget(screen, 197, 2, "arc", 111)

    assertEqualGeometry(w, 436, 158, 40, 40)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 0, 216, 0)
    _core.assertEqualColor(w.background_color, None)

    _core.assertTrue(hasattr(w, "contents"))
    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 4)
    assertEqualDictKeyValue(w.contents, "beginAngle", 0.0)
    assertEqualDictKeyValue(w.contents, "pathAngle", 360.0)

    _core.assertIn("basic attribute", w.contents)
    attr = w.contents["basic attribute"]
    _core.assertIsInstance(attr, dict)
    _core.assertEqual(len(attr), 2)
    assertEqualDictKeyValue(attr, "fill", "outline")
    assertEqualDictKeyValue(attr, "width", "5")

    _core.assertIn("dynamic attribute", w.contents)
    attr = w.contents["dynamic attribute"]
    _core.assertIsInstance(attr, dict)
    _core.assertEqual(len(attr), 3)
    assertEqualDictKeyValue(attr, "calc", "A=3")
    assertEqualDictKeyValue(attr, "chan", "$(P)sample")
    assertEqualDictKeyValue(attr, "vis", "calc")


def test_parse_medm_widget_bar():
    screen = parseFile("mca-R7-7-mca.adl")
    w = _core.pickWidget(screen, 86, 84, "bar", 1779)

    assertEqualGeometry(w, 6, 217, 60, 16)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 255, 255, 255)
    _core.assertEqualColor(w.background_color, 0, 0, 0)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 3)
    assertEqualDictKeyValue(w.contents, "clrmod", "alarm")
    assertEqualDictKeyValue(w.contents, "limits", "")
    _core.assertIn("monitor", w.contents)
    monitor = w.contents["monitor"]
    _core.assertEqual(len(monitor), 1)
    assertEqualDictKeyValue(monitor, "chan", "$(P)$(M).IDTIM")

def test_parse_medm_widget_byte():
    screen = parseFile("optics-R2-13-1-pf4more.adl")
    w = _core.pickWidget(screen, 79, 41, "byte", 754)

    assertEqualGeometry(w, 166, 224, 10, 336)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 139, 26, 150)
    _core.assertEqualColor(w.background_color, 218, 218, 218)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 4)
    assertEqualDictKeyValue(w.contents, "direction", "down")
    assertEqualDictKeyValue(w.contents, "ebit", "15")
    assertEqualDictKeyValue(w.contents, "sbit", "0")
    _core.assertIn("monitor", w.contents)
    monitor = w.contents["monitor"]
    _core.assertEqual(len(monitor), 1)
    assertEqualDictKeyValue(monitor, "chan", "$(P)$(H)bitFlag$(A)")

def test_parse_medm_widget_byte_additional():
    # see: https://github.com/BCDA-APS/adl2pydm/issues/32
    screen = parseFile("byte-monitor.adl")
    w = _core.pickWidget(screen, 4, 0, "byte", 90)
    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 2)
    _core.assertNotIn("direction", w.contents)
    _core.assertNotIn("ebit", w.contents)
    assertEqualDictKeyValue(w.contents, "sbit", "3")

    w = _core.pickWidget(screen, 4, 1, "byte", 104)
    assertEqualDictKeyValue(w.contents, "ebit", "3")
    assertEqualDictKeyValue(w.contents, "sbit", "0")

    w = _core.pickWidget(screen, 4, 2, "byte", 119)
    assertEqualDictKeyValue(w.contents, "direction", "down")
    _core.assertNotIn("ebit", w.contents)
    assertEqualDictKeyValue(w.contents, "sbit", "3")

    w = _core.pickWidget(screen, 4, 3, "byte", 134)
    assertEqualDictKeyValue(w.contents, "direction", "down")
    assertEqualDictKeyValue(w.contents, "ebit", "3")
    assertEqualDictKeyValue(w.contents, "sbit", "0")

def test_parse_medm_widget_cartesian_plot():
    screen = parseFile("beamHistory_full-R3-5.adl")
    w = _core.pickWidget(screen, 47, 13, "cartesian plot", 551)

    assertEqualGeometry(w, 11, 281, 480, 200)
    assertEqualTitle(w, "")
    _core.assertEqualColor(w.color, 10, 0, 184)
    _core.assertEqualColor(w.background_color, 218, 218, 218)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 13)
    assertEqualDictKeyValue(w.contents, "count", "1")
    assertEqualDictKeyValue(w.contents, "erase", "")
    assertEqualDictKeyValue(w.contents, "eraseMode", "if not zero")
    assertEqualDictKeyValue(w.contents, "erase_oldest", "plot last n pts")
    assertEqualDictKeyValue(w.contents, "style", "fill-under")
    assertEqualDictKeyValue(w.contents, "trigger", "")
    assertEqualDictKeyValue(w.contents, "xlabel", "History (Hours)")
    assertEqualDictKeyValue(w.contents, "ylabel", "Current")

    symbol = "x_axis"
    _core.assertIn(symbol, w.contents)
    axis = w.contents[symbol]
    _core.assertEqual(len(axis), 4)
    assertEqualDictKeyValue(axis, "axisStyle", "linear")
    assertEqualDictKeyValue(axis, "maxRange", "1.000000")
    assertEqualDictKeyValue(axis, "minRange", "0.000000")
    assertEqualDictKeyValue(axis, "rangeStyle", "auto-scale")

    symbol = "y1_axis"
    _core.assertIn(symbol, w.contents)
    axis = w.contents[symbol]
    _core.assertEqual(len(axis), 4)
    assertEqualDictKeyValue(axis, "axisStyle", "linear")
    assertEqualDictKeyValue(axis, "maxRange", "1.000000")
    assertEqualDictKeyValue(axis, "minRange", "0.000000")
    assertEqualDictKeyValue(axis, "rangeStyle", "auto-scale")

    symbol = "y2_axis"
    _core.assertIn(symbol, w.contents)
    axis = w.contents[symbol]
    _core.assertEqual(len(axis), 4)
    assertEqualDictKeyValue(axis, "axisStyle", "linear")
    assertEqualDictKeyValue(axis, "maxRange", "1.000000")
    assertEqualDictKeyValue(axis, "minRange", "0.000000")
    assertEqualDictKeyValue(axis, "rangeStyle", "from channel")

    _core.assertIn("traces", w.contents)
    traces = w.contents["traces"]
    _core.assertIsInstance(traces, list)
    _core.assertEqual(len(traces), 8)
    for item, trace in enumerate(traces):
        _core.assertEqual(len(trace), 3)
        _core.assertIn("color", trace)
        if item == 0:
            xdata = "S:SRtimeCP"
            ydata = "S:SRcurrentCP"
            r, g, b = 42, 99, 228
        else:
            xdata = ""
            ydata = ""
            r, g, b = 0, 0, 0
        assertEqualDictKeyValue(trace, "xdata", xdata)
        assertEqualDictKeyValue(trace, "ydata", ydata)
        _core.assertEqualColor(trace["color"], r, g, b)


def test_parse_medm_widget_choice_button():
    screen = parseFile("motorx-R6-10-1.adl")
    w = _core.pickWidget(screen, 31, 30, "choice button", 568)

    assertEqualGeometry(w, 45, 137, 71, 20)
    assertEqualTitle(w, None)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 2)
    assertEqualDictKeyValue(w.contents, "stacking", "column")

    _core.assertIn("control", w.contents)
    control = w.contents["control"]
    _core.assertEqual(len(control), 1)
    assertEqualDictKeyValue(control, "chan", "$(P)$(M).SET")


def test_parse_medm_widget_composite():
    screen = parseFile("ADBase-R3-3-1.adl")
    w = _core.pickWidget(screen, 10, 1, "composite", 101)

    assertEqualGeometry(w, 6, 35, 350, 340)
    _core.assertEqualColor(w.color, None)
    _core.assertEqualColor(w.background_color, None)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 2)
    assertEqualDictKeyValue(w.contents, "composite file", "ADSetup.adl")
    assertEqualDictKeyValue(w.contents, "composite name", "")


# TODO: embedded display : no example in synApps


def test_parse_medm_widget_image():
    screen = parseFile("sampleWheel.adl")
    w = _core.pickWidget(screen, 197, 1, "image", 101)

    assertEqualGeometry(w, 0, 20, 500, 500)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, None)
    _core.assertEqualColor(w.background_color, None)

    _core.assertTrue(hasattr(w, "contents"))
    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 2)
    assertEqualDictKeyValue(w.contents, "image name", "sampleWheel.gif")
    assertEqualDictKeyValue(w.contents, "type", "gif")

def test_parse_medm_widget_indicator():
    screen = parseFile("optics-R2-13-1-CoarseFineMotorShow.adl")
    w = _core.pickWidget(screen, 12, 5, "indicator", 156)

    assertEqualGeometry(w, 178, 52, 250, 25)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 0, 0, 0)
    _core.assertEqualColor(w.background_color, 115, 223, 255)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 3)

    # assertEqualDictKeyValue(w.contents, "beginAngle", 0.0)
    # assertEqualDictKeyValue(w.contents, "pathAngle", 360.0)
    _core.assertIn("monitor", w.contents)
    monitor = w.contents["monitor"]
    _core.assertEqual(len(monitor), 1)
    assertEqualDictKeyValue(monitor, "chan", "$(PM)$(CM).RBV")

def test_parse_medm_widget_menu():
    screen = parseFile("motorx_all-R6-10-1.adl")
    w = _core.pickWidget(screen, 175, 23, "composite", 417)
    w = _core.pickWidget(w, 2, 0, "menu", 417)

    assertEqualGeometry(w, 186, 232, 100, 18)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 0, 0, 0)
    _core.assertEqualColor(w.background_color, 115, 223, 255)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 1)

    _core.assertIn("control", w.contents)
    control = w.contents["control"]
    _core.assertIsInstance(control, dict)
    _core.assertEqual(len(control), 1)
    assertEqualDictKeyValue(control, "chan", "$(P)$(M).FOFF")

def test_parse_medm_widget_message_button():
    screen = parseFile("std-R3-5-ID_ctrl.adl")
    w = _core.pickWidget(screen, 25, 3, "message button", 434)

    assertEqualGeometry(w, 150, 220, 140, 40)
    assertEqualTitle(w, "Stop ")
    _core.assertEqualColor(w.color, 253, 0, 0)
    _core.assertEqualColor(w.background_color, 160, 18, 7)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 5)
    assertEqualDictKeyValue(w.contents, "clrmod", "static")
    assertEqualDictKeyValue(w.contents, "press_msg", "1")
    assertEqualDictKeyValue(w.contents, "release_msg", "")

    _core.assertIn("control", w.contents)
    control = w.contents["control"]
    _core.assertIsInstance(control, dict)
    _core.assertEqual(len(control), 1)
    assertEqualDictKeyValue(control, "ctrl", "ID$(xx):UN:stopSQ.PROC")

def test_parse_medm_widget_meter():
    screen = parseFile("calc-R3-7-userCalcMeter.adl")
    w = _core.pickWidget(screen, 6, 0, "meter", 87)

    assertEqualGeometry(w, 0, 38, 200, 150)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 0, 0, 0)
    _core.assertEqualColor(w.background_color, 218, 218, 218)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 1)
    _core.assertIn("monitor", w.contents)
    monitor = w.contents["monitor"]
    _core.assertEqual(len(monitor), 1)
    assertEqualDictKeyValue(monitor, "chan", "$(P)$(C).VAL")

def test_parse_medm_widget_oval():
    screen = parseFile("motorx_all-R6-10-1.adl")
    w = _core.pickWidget(screen, 175, 60, "oval", 993)

    assertEqualGeometry(w, 290, 132, 21, 21)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 253, 0, 0)
    _core.assertEqualColor(w.background_color, None)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 2)
    _core.assertIn("basic attribute", w.contents)
    attr = w.contents["basic attribute"]
    _core.assertIsInstance(attr, dict)
    _core.assertEqual(len(attr), 0)
    _core.assertIn("dynamic attribute", w.contents)
    attr = w.contents["dynamic attribute"]
    _core.assertIsInstance(attr, dict)
    _core.assertEqual(len(attr), 2)
    assertEqualDictKeyValue(attr, "chan", "$(P)$(M).LLS")
    assertEqualDictKeyValue(attr, "vis", "if not zero")

def test_parse_medm_widget_polygon():
    screen = parseFile("calc-R3-7-1-FuncGen_full.adl")
    w = _core.pickWidget(screen, 38, 18, "composite", 337)
    w = _core.pickWidget(w, 2, 1, "polygon", 353)

    assertEqualGeometry(w, 260, 174, 10, 10)
    assertEqualTitle(w, None)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 1)
    _core.assertIn("basic attribute", w.contents)
    attr = w.contents["basic attribute"]
    _core.assertIsInstance(attr, dict)
    _core.assertEqual(len(attr), 0)

    _core.assertHasAttribute(w, "points")
    _core.assertEqual(len(w.points), 4)
    assertEqualPoint(w.points[0], 260, 174)
    assertEqualPoint(w.points[1], 270, 178)
    assertEqualPoint(w.points[2], 260, 184)
    assertEqualPoint(w.points[3], 260, 174)

def test_parse_medm_widget_polyline():
    screen = parseFile("calc-R3-7-1-FuncGen_full.adl")
    w = _core.pickWidget(screen, 38, 18, "composite", 337)
    w = _core.pickWidget(w, 2, 0, "polyline", 337)

    assertEqualGeometry(w, 120, 178, 142, 2)
    assertEqualTitle(w, None)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 1)
    _core.assertIn("basic attribute", w.contents)
    attr = w.contents["basic attribute"]
    _core.assertIsInstance(attr, dict)
    _core.assertEqual(len(attr), 1)
    assertEqualDictKeyValue(attr, "width", "2")

    _core.assertHasAttribute(w, "points")
    _core.assertEqual(len(w.points), 2)
    assertEqualPoint(w.points[0], 121, 179)
    assertEqualPoint(w.points[1], 261, 179)

def test_parse_medm_widget_rectangle():
    screen = parseFile("ADBase-R3-3-1.adl")
    w = _core.pickWidget(screen, 10, 0, "rectangle", 90)

    assertEqualGeometry(w, 0, 4, 715, 25)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 218, 218, 218)
    _core.assertEqualColor(w.background_color, None)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 1)
    _core.assertIn("basic attribute", w.contents)
    attr = w.contents["basic attribute"]
    _core.assertEqual(len(attr), 0)

def test_parse_medm_widget_related_display():
    screen = parseFile("std-R3-5-ID_ctrl.adl")
    w = _core.pickWidget(screen, 25, 13, "related display", 611)

    assertEqualGeometry(w, 119, 285, 18, 18)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 88, 52, 15)
    _core.assertEqualColor(w.background_color, 115, 223, 255)

    _core.assertIsInstance(w.displays, list)
    _core.assertEqual(len(w.displays), 8)
    display = w.displays[0]
    _core.assertIsInstance(display, dict)
    assertEqualDictKeyValue(display, "args", "xx=$(xx)")
    assertEqualDictKeyValue(display, "label", "Taper Control")
    assertEqualDictKeyValue(display, "name", "ID_taper_ctrl.adl")

def test_parse_medm_widget_shell_command():
    screen = parseFile("sscan-R2-11-1-scanAux.adl")
    w = _core.pickWidget(screen, 66, 42, "shell command", 725)

    assertEqualGeometry(w, 350, 239, 20, 20)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 0, 0, 0)
    _core.assertEqualColor(w.background_color, 251, 243, 74)

    _core.assertHasAttribute(w, "contents")
    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 0)

    _core.assertHasAttribute(w, "commands")
    _core.assertIsInstance(w.commands, list)
    _core.assertEqual(len(w.commands), 1)
    cmd = w.commands[0]
    _core.assertIsInstance(cmd, dict)
    _core.assertEqual(len(cmd), 2)
    assertEqualDictKeyValue(cmd, "label", "Help")
    assertEqualDictKeyValue(cmd, "name", "medm_help.sh &T")

def test_parse_medm_widget_strip_chart():
    screen = parseFile("calc-R3-7-1-FuncGen_full.adl")
    # this widget is in a composite
    w = _core.pickWidget(screen, 38, 32, "composite", 614)
    w = _core.pickWidget(w, 1, 0, "strip chart", 614)

    assertEqualGeometry(w, 0, 260, 450, 170)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 0, 0, 0)
    _core.assertEqualColor(w.background_color, 255, 255, 255)

    _core.assertHasAttribute(w, "contents")
    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 3)
    assertEqualDictKeyValue(w.contents, "period", "1.000000")
    assertEqualDictKeyValue(w.contents, "units", "minute")
    pens = w.contents.get("pens")
    _core.assertIsNotNone(pens)
    _core.assertEqual(len(pens), 2)
    _core.assertEqual(pens[0]["chan"], "$(P)$(Q):Output")
    _core.assertEqual(pens[1]["chan"], "$(P)$(Q):Readback")
    _core.assertEqualColor(pens[0]["color"], 0, 0, 0)
    _core.assertEqualColor(pens[1]["color"], 253, 0, 0)

def test_parse_medm_widget_text():
    screen = parseFile("ADBase-R3-3-1.adl")
    w = _core.pickWidget(screen, 10, 9, "text", 181)

    assertEqualGeometry(w, 0, 5, 715, 25)
    assertEqualTitle(w, "Area Detector Control - $(P)$(R)")
    _core.assertEqualColor(w.color, 10, 0, 184)
    _core.assertEqualColor(w.background_color, None)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 2)
    assertEqualDictKeyValue(w.contents, "align", "horiz. centered")
    _core.assertIn("basic attribute", w.contents)
    attr = w.contents["basic attribute"]
    _core.assertEqual(len(attr), 0)

def test_parse_medm_widget_text_entry():
    screen = parseFile("std-R3-5-ID_ctrl.adl")
    w = _core.pickWidget(screen, 25, 8, "text entry", 531)

    assertEqualGeometry(w, 54, 114, 120, 38)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 255, 255, 255)
    _core.assertEqualColor(w.background_color, 10, 0, 184)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 3)
    assertEqualDictKeyValue(w.contents, "format", "decimal")
    assertEqualDictKeyValue(w.contents, "clrmod", "static")

    _core.assertIn("control", w.contents)
    control = w.contents["control"]
    _core.assertIsInstance(control, dict)
    _core.assertEqual(len(control), 1)
    assertEqualDictKeyValue(control, "ctrl", "ID$(xx):UN:setavgAI.VAL")

def test_parse_medm_widget_text_update():
    screen = parseFile("text_examples.adl")
    w = _core.pickWidget(screen, 17, 0, "text update", 90)

    assertEqualGeometry(w, 10, 46, 140, 24)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 0, 0, 0)
    _core.assertEqualColor(w.background_color, 187, 187, 187)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 2)
    assertEqualDictKeyValue(w.contents, "limits", "")

    _core.assertIn("monitor", w.contents)
    mon = w.contents["monitor"]
    _core.assertIsInstance(mon, dict)
    _core.assertEqual(len(mon), 1)
    assertEqualDictKeyValue(mon, "chan", "$(P)")

def test_parse_medm_widget_valuator():
    screen = parseFile("optics-R2-13-xiahsc.adl")
    w = _core.pickWidget(screen, 55, 8, "valuator", 201)

    assertEqualGeometry(w, 52, 247, 100, 20)
    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 3)
    assertEqualDictKeyValue(w.contents, "dPrecision", "0.010000")
    _core.assertIn("control", w.contents)
    control = w.contents["control"]
    _core.assertEqual(len(control), 1)
    assertEqualDictKeyValue(control, "chan", "$(P)$(HSC)l")
    assertEqualTitle(w, None)

def test_parse_medm_widget_wheel_switch():
    screen = parseFile("wheel_switch.adl")
    w = _core.pickWidget(screen, 1, 0, "wheel switch", 90)

    assertEqualGeometry(w, 19, 16, 185, 91)
    assertEqualTitle(w, None)
    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 7)
    assertEqualDictKeyValue(w.contents, "hoprSrc", "default")
    assertEqualDictKeyValue(w.contents, "loprSrc", "default")
    assertEqualDictKeyValue(w.contents, "precSrc", "default")
    assertEqualDictKeyValue(w.contents, "hoprDefault", "10")
    assertEqualDictKeyValue(w.contents, "loprDefault", "-10")
    assertEqualDictKeyValue(w.contents, "precDefault", "3")
    control = w.contents["control"]
    _core.assertEqual(len(control), 1)
    assertEqualDictKeyValue(control, "chan", "sky:userCalc2.A")

def test_parse_medm_userArrayCalc():
    screen = parseFile("userArrayCalc.adl")
    w = _core.pickWidget(screen, 88, 24, "text entry", 442)

    assertEqualGeometry(w, 235, 170, 150, 20)
    assertEqualTitle(w, None)
    _core.assertEqualColor(w.color, 0, 0, 0)
    _core.assertEqualColor(w.background_color, 115, 223, 255)

    _core.assertIsInstance(w.contents, dict)
    _core.assertEqual(len(w.contents), 3)
    assertEqualDictKeyValue(w.contents, "format", "string")
    assertEqualDictKeyValue(w.contents, "limits", "")

    _core.assertIn("control", w.contents)
    control = w.contents["control"]
    _core.assertIsInstance(control, dict)
    _core.assertEqual(len(control), 1)
    assertEqualDictKeyValue(control, "chan", "$(P)$(C).AA")
