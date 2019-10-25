
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

    def test_parse_basic_attribute(self):
        screen = self.parseFile("std-R3-5-ID_ctrl.adl")
        self.assertEqual(len(screen.widgets), 25)
        # TODO: where is data from basic attribute, line 708
        # goes into contents, but what widget?
        # Why is it given multiple times at the file level?  Error?
        # There's channel content in some of these blocks.

    def test_parse_composite(self):
        screen = self.parseFile("ADBase-R3-3-1.adl")
        self.assertEqual(len(screen.widgets), 10)

        w = screen.widgets[1]
        self.assertEqual(w.symbol, "composite")
        self.assertEqual(w.line_offset, 101)
        self.assertEqual(w.geometry.x, 6)
        self.assertEqual(w.geometry.y, 35)
        self.assertEqual(w.geometry.width, 350)
        self.assertEqual(w.geometry.height, 340)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 2)
        self.assertIn("composite file", w.contents)
        self.assertEqual(w.contents["composite file"], 'ADSetup.adl')
        self.assertIn("composite name", w.contents)
        self.assertEqual(w.contents["composite name"], '')

    def test_parse_dynamic_attribute(self):
        screen = self.parseFile("std-R3-5-ID_ctrl.adl")
        self.assertEqual(len(screen.widgets), 25)
        # TODO: where is data from dynamic attribute, line 687

    def test_parse_message_button(self):
        screen = self.parseFile("std-R3-5-ID_ctrl.adl")
        self.assertEqual(len(screen.widgets), 25)

        w = screen.widgets[3]
        self.assertEqual(w.symbol, "message button")
        self.assertEqual(w.line_offset, 434)
        self.assertEqual(w.geometry.x, 150)
        self.assertEqual(w.geometry.y, 220)
        self.assertEqual(w.geometry.width, 140)
        self.assertEqual(w.geometry.height, 40)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 4)
        self.assertIn("clrmod", w.contents)
        self.assertEqual(w.contents["clrmod"], "static")
        self.assertIn("press_msg", w.contents)
        self.assertEqual(w.contents["press_msg"], "1")
        self.assertIn("release_msg", w.contents)
        self.assertEqual(w.contents["release_msg"], "")
        self.assertIn("control", w.contents)
        control = w.contents["control"]
        self.assertIsInstance(control, dict)
        self.assertEqual(len(control), 1)
        self.assertIn("ctrl", control)
        self.assertEqual(control["ctrl"], 'ID$(xx):UN:stopSQ.PROC')
        self.assertEqual(w.title, "Stop ")

    def test_parse_rectangle(self):
        screen = self.parseFile("ADBase-R3-3-1.adl")
        self.assertEqual(len(screen.widgets), 10)

        w = screen.widgets[0]
        self.assertEqual(w.symbol, "rectangle")
        self.assertEqual(w.line_offset, 90)
        self.assertEqual(w.geometry.x, 0)
        self.assertEqual(w.geometry.y, 4)
        self.assertEqual(w.geometry.width, 715)
        self.assertEqual(w.geometry.height, 25)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 1)
        self.assertIn("basic attribute", w.contents)
        self.assertEqual(len(w.contents["basic attribute"]), 0)

    def test_parse_related_display(self):
        screen = self.parseFile("std-R3-5-ID_ctrl.adl")
        self.assertEqual(len(screen.widgets), 25)

        w = screen.widgets[13]
        self.assertEqual(w.symbol, "related display")
        self.assertEqual(w.line_offset, 611)
        self.assertEqual(w.geometry.x, 119)
        self.assertEqual(w.geometry.y, 285)
        self.assertEqual(w.geometry.width, 18)
        self.assertEqual(w.geometry.height, 18)
        self.assertIsInstance(w.displays, list)
        self.assertEqual(len(w.displays), 8)
        display = w.displays[0]
        self.assertIsInstance(display, dict)
        self.assertIn("args", display)
        self.assertEqual(display["args"], "xx=$(xx)")
        self.assertIn("label", display)
        self.assertEqual(display["label"], "Taper Control")
        self.assertIn("name", display)
        self.assertEqual(display["name"], "ID_taper_ctrl.adl")

    def test_parse_text(self):
        screen = self.parseFile("ADBase-R3-3-1.adl")
        self.assertEqual(len(screen.widgets), 10)

        w = screen.widgets[9]
        self.assertEqual(w.symbol, "text")
        self.assertEqual(w.line_offset, 181)
        self.assertEqual(w.geometry.x, 0)
        self.assertEqual(w.geometry.y, 5)
        self.assertEqual(w.geometry.width, 715)
        self.assertEqual(w.geometry.height, 25)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 2)
        self.assertIn("align", w.contents)
        self.assertEqual(w.contents["align"], 'horiz. centered')
        self.assertIn("basic attribute", w.contents)
        self.assertEqual(len(w.contents["basic attribute"]), 0)
        self.assertEqual(w.title, "Area Detector Control - $(P)$(R)")

    def test_parse_text_entry(self):
        screen = self.parseFile("std-R3-5-ID_ctrl.adl")
        self.assertEqual(len(screen.widgets), 25)

        w = screen.widgets[8]
        self.assertEqual(w.symbol, "text entry")
        self.assertEqual(w.line_offset, 531)
        self.assertEqual(w.geometry.x, 54)
        self.assertEqual(w.geometry.y, 114)
        self.assertEqual(w.geometry.width, 120)
        self.assertEqual(w.geometry.height, 38)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 3)
        self.assertIn("format", w.contents)
        self.assertEqual(w.contents["format"], "decimal")
        self.assertIn("clrmod", w.contents)
        self.assertEqual(w.contents["clrmod"], "static")
        self.assertIn("control", w.contents)
        control = w.contents["control"]
        self.assertIsInstance(control, dict)
        self.assertEqual(len(control), 1)
        self.assertIn("ctrl", control)
        self.assertEqual(control["ctrl"], "ID$(xx):UN:setavgAI.VAL")

    def test_parse_text_update(self):
        screen = self.parseFile("newDisplay.adl")
        self.assertEqual(len(screen.widgets), 1)

        w = screen.widgets[0]
        self.assertEqual(w.symbol, "text update")
        self.assertEqual(w.line_offset, 90)
        self.assertEqual(w.geometry.x, 40)
        self.assertEqual(w.geometry.y, 46)
        self.assertEqual(w.geometry.width, 195)
        self.assertEqual(w.geometry.height, 31)
        self.assertIsInstance(w.contents, dict)
        self.assertEqual(len(w.contents), 2)
        self.assertIn("limits", w.contents)
        self.assertEqual(w.contents["limits"], "")
        self.assertIn("monitor", w.contents)
        mon = w.contents["monitor"]
        self.assertIsInstance(mon, dict)
        self.assertEqual(len(mon), 1)
        self.assertIn("chan", mon)
        self.assertEqual(mon["chan"], "$(P)")


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
