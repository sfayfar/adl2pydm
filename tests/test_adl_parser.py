
"""
simple unit tests for this package
"""

import logging
import os
import sys
import unittest

# turn off logging output
logging.basicConfig(level=logging.CRITICAL)

_test_path = os.path.dirname(__file__)
_path = os.path.join(_test_path, '..', 'src')
if _path not in sys.path:
    sys.path.insert(0, _path)

from adl2pydm import adl_parser


class Test_Files(unittest.TestCase):

    test_files = [
        "newDisplay.adl",                  # simple display
        "xxx-R5-8-4.adl",                  # related display
        "xxx-R6-0.adl",
        # "base-3.15.5-caServerApp-test.adl"  #  FIXME: needs more work here (unusual structure, possibly stress test):  # info[, "<<color rules>>", "<<color map>>"
        "calc-3-4-2-1-FuncGen_full.adl",   # strip chart
        "calc-R3-7-1-FuncGen_full.adl",    # strip chart
        "calc-R3-7-userCalcMeter.adl",     # meter
        "mca-R7-7-mca.adl",                # bar
        "motorx-R6-10-1.adl",
        "motorx_all-R6-10-1.adl",
        "optics-R2-13-1-CoarseFineMotorShow.adl",  # indicator
        "optics-R2-13-1-kohzuGraphic.adl", # image
        "optics-R2-13-1-pf4more.adl",      # byte
        "optics-R2-13-xiahsc.adl",         # valuator
        "sampleWheel.adl",                 # image
        "scanDetPlot-R2-11-1.adl",         # cartesian plot, strip
        "sscan-R2-11-1-scanAux.adl",       # shell command
        "std-R3-5-ID_ctrl.adl",            # param
        "wheel_switch.adl",                # wheel switch
        # "beamHistory_full-R3-5.adl", # dl_color -- this .adl has content errors
        "ADBase-R3-3-1.adl",               # composite
        "simDetector-R3-3-31.adl",
        ]

    def setUp(self):
        self.path = os.path.abspath(os.path.dirname(adl_parser.__file__))
        self.medm_path = os.path.join(self.path, "screens", "medm")
    
    # def tearDown(self):
    #     pass

    def parseFile(self, short_name):
        full_name = os.path.join(self.medm_path, short_name)
        
        screen = adl_parser.MedmMainWidget()
        buf = screen.getAdlLines(full_name)
        screen.parseAdlBuffer(buf)
        return screen

    def assertEqualDictKeyValue(self, dictionary, key, value):
        self.assertIsInstance(dictionary, dict)
        self.assertIn(key, dictionary)
        self.assertEqual(dictionary[key], value)

    def assertEqualGeometry(self, parent, x, y, w, h):
        self.assertHasAttribute(parent, "geometry")
        geom = parent.geometry
        self.assertEqual(geom.x, x)
        self.assertEqual(geom.y, y)
        self.assertEqual(geom.width, w)
        self.assertEqual(geom.height, h)

    def assertEqualPoint(self, point, x, y):
        self.assertIsInstance(point, adl_parser.Point)
        self.assertEqual(point.x, x)
        self.assertEqual(point.y, y)

    def assertEqualTitle(self, parent, title):
        self.assertHasAttribute(parent, "title")
        self.assertEqual(parent.title, title)

    def assertHasAttribute(self, parent, attr_name):
        self.assertTrue(hasattr(parent, attr_name))
    
    def pickWidget(self, parent, num_widgets, n, symbol, line_offset):
        self.assertHasAttribute(parent, "widgets")
        self.assertEqual(len(parent.widgets), num_widgets)
        w = parent.widgets[n]
        self.assertEqual(w.symbol, symbol)
        self.assertEqual(w.line_offset, line_offset)
        return w

    # -------------------------------------------------
    
    def test__paths(self):
        self.assertTrue(os.path.exists(self.path))
        self.assertTrue(os.path.exists(self.medm_path))

    def test_adl_parser(self):
        for fname in self.test_files:
            screen = adl_parser.MedmMainWidget()
            self.assertEqual(screen.line_offset, 1)

            full_name = os.path.join(self.medm_path, fname)
            self.assertTrue(os.path.exists(full_name))

            buf = screen.getAdlLines(full_name)
            # any useful MEDM file has more than 10 lines
            self.assertGreater(len(buf), 10)

            screen.parseAdlBuffer(buf)
            self.assertGreater(len(screen.widgets), 0)

    # -------------------------------------------------

    def test_parse_arc(self):
        screen = self.parseFile("sampleWheel.adl")
        w = self.pickWidget(screen, 197, 2, "arc", 111)

        self.assertEqualGeometry(w, 436, 158, 40, 40)
        self.assertEqualTitle(w, None)
        self.assertTrue(hasattr(w, "contents"))
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 4)
        self.assertEqualDictKeyValue(w.contents, "begin", "0")
        self.assertEqualDictKeyValue(w.contents, "path", "23040")
        self.assertIn("basic attribute", w.contents)
        attr = w.contents["basic attribute"]
        self.assertIsInstance(attr, dict)
        self.assertEqual(len(attr), 2)
        self.assertEqualDictKeyValue(attr, "fill", "outline")
        self.assertEqualDictKeyValue(attr, "width", "5")
        self.assertIn("dynamic attribute", w.contents)
        attr = w.contents["dynamic attribute"]
        self.assertIsInstance(attr, dict)
        self.assertEqual(len(attr), 3)
        self.assertEqualDictKeyValue(attr, "calc", "A=3")
        self.assertEqualDictKeyValue(attr, "chan", "$(P)sample")
        self.assertEqualDictKeyValue(attr, "vis", "calc")

    # bar
    # byte
    # cartesian plot

    def test_parse_choice_button(self):
        screen = self.parseFile("motorx-R6-10-1.adl")
        w = self.pickWidget(screen, 31, 30, "choice button", 568)
        
        self.assertEqualGeometry(w, 45, 137, 71, 20)
        self.assertEqualTitle(w, None)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 2)
        self.assertEqualDictKeyValue(w.contents, "stacking", "column")
        self.assertIn("control", w.contents)
        control = w.contents["control"]
        self.assertEqual(len(control), 1)
        self.assertEqualDictKeyValue(control, "chan", "$(P)$(M).SET")

    def test_parse_composite(self):
        screen = self.parseFile("ADBase-R3-3-1.adl")
        w = self.pickWidget(screen, 10, 1, "composite", 101)
        
        self.assertEqualGeometry(w, 6, 35, 350, 340)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 2)
        self.assertEqualDictKeyValue(w.contents, "composite file", "ADSetup.adl")
        self.assertEqualDictKeyValue(w.contents, "composite name", "")

    # TODO: embedded display : no example in synApps

    def test_parse_image(self):
        screen = self.parseFile("sampleWheel.adl")
        w = self.pickWidget(screen, 197, 1, "image", 101)
        
        self.assertEqualGeometry(w, 0, 20, 500, 500)
        self.assertEqualTitle(w, None)
        self.assertTrue(hasattr(w, "contents"))
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 2)
        self.assertEqualDictKeyValue(w.contents, "image name", "sampleWheel.gif")
        self.assertEqualDictKeyValue(w.contents, "type", "gif")

    # indicator
    # menu

    def test_parse_message_button(self):
        screen = self.parseFile("std-R3-5-ID_ctrl.adl")
        w = self.pickWidget(screen, 25, 3, "message button", 434)
        
        self.assertEqualGeometry(w, 150, 220, 140, 40)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 4)
        self.assertEqualDictKeyValue(w.contents, "clrmod", "static")
        self.assertEqualDictKeyValue(w.contents, "press_msg", "1")
        self.assertEqualDictKeyValue(w.contents, "release_msg", "")
        self.assertIn("control", w.contents)
        control = w.contents["control"]
        self.assertIsInstance(control, dict)
        self.assertEqual(len(control), 1)
        self.assertEqualDictKeyValue(control, "ctrl", "ID$(xx):UN:stopSQ.PROC")
        self.assertEqualTitle(w, "Stop ")

    # meter
    # oval
    # polygon - calc-R3-7-1-FuncGen_full.adl

    def test_parse_polyline(self):
        screen = self.parseFile("calc-R3-7-1-FuncGen_full.adl")
        w = self.pickWidget(screen, 38, 18, "composite", 337)
        w = self.pickWidget(w, 2, 0, "polyline", 337)
        
        self.assertEqualGeometry(w, 120, 178, 142, 2)
        self.assertEqualTitle(w, None)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 1)
        self.assertIn("basic attribute", w.contents)
        attr = w.contents["basic attribute"]
        self.assertEqualDictKeyValue(attr, "width", "2")
        self.assertHasAttribute(w, "points")
        self.assertEqual(len(w.points), 2)
        self.assertEqualPoint(w.points[0], 121, 179)
        self.assertEqualPoint(w.points[1], 261, 179)

    def test_parse_rectangle(self):
        screen = self.parseFile("ADBase-R3-3-1.adl")
        w = self.pickWidget(screen, 10, 0, "rectangle", 90)
        
        self.assertEqualGeometry(w, 0, 4, 715, 25)
        self.assertEqualTitle(w, None)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 1)
        self.assertIn("basic attribute", w.contents)
        attr = w.contents["basic attribute"]
        self.assertEqual(len(attr), 0)

    def test_parse_related_display(self):
        screen = self.parseFile("std-R3-5-ID_ctrl.adl")
        w = self.pickWidget(screen, 25, 13, "related display", 611)
        
        self.assertEqualGeometry(w, 119, 285, 18, 18)
        self.assertEqualTitle(w, None)
        self.assertIsInstance(w.displays, list)
        self.assertEqual(len(w.displays), 8)
        display = w.displays[0]
        self.assertIsInstance(display, dict)
        self.assertEqualDictKeyValue(display, "args", "xx=$(xx)")
        self.assertEqualDictKeyValue(display, "label", "Taper Control")
        self.assertEqualDictKeyValue(display, "name", "ID_taper_ctrl.adl")

    def test_parse_shell_command(self):
        screen = self.parseFile("sscan-R2-11-1-scanAux.adl")
        w = self.pickWidget(screen, 66, 42, "shell command", 725)
        
        self.assertEqualGeometry(w, 350, 239, 20, 20)
        self.assertEqualTitle(w, None)
        self.assertHasAttribute(w, "contents")
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 0)
        self.assertHasAttribute(w, "commands")
        self.assertIsInstance(w.commands, list)
        self.assertEqual(len(w.commands), 1)
        cmd = w.commands[0]
        self.assertIsInstance(cmd, dict)
        self.assertEqual(len(cmd), 2)
        self.assertEqualDictKeyValue(cmd, "label", "Help")
        self.assertEqualDictKeyValue(cmd, "name", "medm_help.sh &T")

    def test_parse_strip_chart(self):
        screen = self.parseFile("calc-R3-7-1-FuncGen_full.adl")
        # this widget is in a composite
        w = self.pickWidget(screen, 38, 32, "composite", 614)
        w = self.pickWidget(w, 1, 0, "strip chart", 614)
        
        self.assertEqualGeometry(w, 0, 260, 450, 170)
        self.assertEqualTitle(w, None)
        self.assertHasAttribute(w, "contents")
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 2)
        self.assertEqualDictKeyValue(w.contents, "period", "1.000000")
        self.assertEqualDictKeyValue(w.contents, "units", "minute")

    def test_parse_text(self):
        screen = self.parseFile("ADBase-R3-3-1.adl")
        w = self.pickWidget(screen, 10, 9, "text", 181)
        
        self.assertEqualGeometry(w, 0, 5, 715, 25)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 2)
        self.assertEqualDictKeyValue(w.contents, "align", "horiz. centered")
        self.assertIn("basic attribute", w.contents)
        attr = w.contents["basic attribute"]
        self.assertEqual(len(attr), 0)
        self.assertEqualTitle(w, "Area Detector Control - $(P)$(R)")

    def test_parse_text_entry(self):
        screen = self.parseFile("std-R3-5-ID_ctrl.adl")
        w = self.pickWidget(screen, 25, 8, "text entry", 531)
        
        self.assertEqualGeometry(w, 54, 114, 120, 38)
        self.assertEqualTitle(w, None)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 3)
        self.assertEqualDictKeyValue(w.contents, "format", "decimal")
        self.assertEqualDictKeyValue(w.contents, "clrmod", "static")
        self.assertIn("control", w.contents)
        control = w.contents["control"]
        self.assertIsInstance(control, dict)
        self.assertEqual(len(control), 1)
        self.assertEqualDictKeyValue(control, "ctrl", "ID$(xx):UN:setavgAI.VAL")

    def test_parse_text_update(self):
        screen = self.parseFile("newDisplay.adl")
        w = self.pickWidget(screen, 1, 0, "text update", 90)
        
        self.assertEqualGeometry(w, 40, 46, 195, 31)
        self.assertEqualTitle(w, None)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 2)
        self.assertEqualDictKeyValue(w.contents, "limits", "")
        self.assertIn("monitor", w.contents)
        mon = w.contents["monitor"]
        self.assertIsInstance(mon, dict)
        self.assertEqual(len(mon), 1)
        self.assertEqualDictKeyValue(mon, "chan", "$(P)")

    def test_parse_valuator(self):
        screen = self.parseFile("optics-R2-13-xiahsc.adl")
        w = self.pickWidget(screen, 55, 8, "valuator", 201)
        
        self.assertEqualGeometry(w, 52, 247, 100, 20)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 2)
        self.assertEqualDictKeyValue(w.contents, "dPrecision", "0.010000")
        self.assertIn("control", w.contents)
        control = w.contents["control"]
        self.assertEqual(len(control), 1)
        self.assertEqualDictKeyValue(control, "chan", "$(P)$(HSC)l")
        self.assertEqualTitle(w, "no decorations")

    def test_parse_wheel_switch(self):
        screen = self.parseFile("wheel_switch.adl")
        w = self.pickWidget(screen, 1, 0, "wheel switch", 90)
        
        self.assertEqualGeometry(w, 48, 29, 144, 48)
        self.assertEqualTitle(w, None)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 2)
        self.assertEqualDictKeyValue(w.contents, "limits", "")
        control = w.contents["control"]
        self.assertEqual(len(control), 1)
        self.assertEqualDictKeyValue(control, "chan", "$(P)$(M)")


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_Files,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
