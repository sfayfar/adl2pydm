
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
    
    def test_paths(self):
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

    def test_parse_text_update(self):
        screen = self.parseFile("newDisplay.adl")
        self.assertEqual(len(screen.widgets), 1)

        w = screen.widgets[0]
        self.assertEqual(w.symbol, "text update")
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
