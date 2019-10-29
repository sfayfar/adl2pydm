
"""
simple unit tests for this package
"""

import logging
import os
import shutil
import sys
import tempfile
import unittest

# turn off logging output
logging.basicConfig(level=logging.CRITICAL)

_test_path = os.path.dirname(__file__)
_path = os.path.join(_test_path, '..', 'src')
if _path not in sys.path:
    sys.path.insert(0, _path)

from adl2pydm import cli, output_handler


class TestOutputHandler(unittest.TestCase):

    # these files both reader AND writer
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
        self.tempdir = tempfile.mkdtemp()
    
    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)
    
    def convertAdlFile(self, adlname):
        path = os.path.abspath(os.path.dirname(output_handler.__file__))
        self.assertTrue(os.path.exists(path))

        medm_path = os.path.join(path, "screens", "medm")
        self.assertTrue(os.path.exists(medm_path))

        full_name = os.path.join(medm_path, adlname)
        self.assertTrue(os.path.exists(full_name))

        sys.argv = [sys.argv[0], "-d", self.tempdir, full_name]
        cli.main()

        base = os.path.splitext(os.path.basename(full_name))[0]
        uiname = base + output_handler.SCREEN_FILE_EXTENSION

        return uiname

    def test_write_pydm_widget_rectangle(self):
        uiname = self.convertAdlFile("ADBase-R3-3-1.adl")
        self.assertTrue(os.path.exists(os.path.join(self.tempdir, uiname)))


class Test_PYDM_Writer_Support(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
    
    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_zorder(self):
        fname = os.path.join(self.tempdir, "test.xml")
        writer = output_handler.PYDM_Writer(None)
        writer.openFile(fname)
        specs = [
            # order     vis text
            ("widget_0", 2, "first"),
            ("widget_4", 0, "last"),
            ("widget_1", -3, 3),
            ("widget_2", 2, 4)
        ]
        for args in specs:
            writer.widget_stacking_info.append(
                output_handler.Qt_zOrder(*args))
        writer.closeFile()
        self.assertTrue(os.path.exists(fname))

        with open(fname, "r") as fp:
            buf = fp.readlines()
        expected = (
            '<?xml version="1.0" ?>',
            '<ui version="4.0">',
            '  <zorder>first</zorder>',
            '  <zorder>3</zorder>',
            '  <zorder>4</zorder>',
            '  <zorder>last</zorder>',
            '</ui>',
        )
        self.assertEqual(len(buf), len(expected))
        for idx in range(len(buf)):
            self.assertEqual(buf[idx].rstrip(), expected[idx])


    def test_xml_subelements(self):
        fname = os.path.join(self.tempdir, "test.xml")
        writer = output_handler.PYDM_Writer(None)
        writer.openFile(fname)
        root = writer.root
        writer.writeProperty(root, "example", "text value")
        writer.writeProperty(root, "another_example", "upper", "enum")
        sub = root
        for tag in "banana banana banana orange".split():
            sub = writer.writeOpenTag(sub, tag)
        writer.closeFile()
        self.assertTrue(os.path.exists(fname))

        with open(fname, "r") as fp:
            buf = fp.readlines()
        expected = (
            '<?xml version="1.0" ?>',
            '<ui version="4.0">',
            '  <property name="example">',
            '    <string>text value</string>',
            '  </property>',
            '  <property name="another_example">',
            '    <enum>upper</enum>',
            '  </property>',
            '  <banana>',
            '    <banana>',
            '      <banana>',
            '        <orange/>',
            '      </banana>',
            '    </banana>',
            '  </banana>',
            '</ui>',
            )
        self.assertEqual(len(buf), len(expected))

    # def test_testDisplay_adl(self):
    #     medm_path = os.path.join(os.path.dirname(__file__), "medm")
    #     self.assertTrue(os.path.exists(medm_path))

    #     full_name = os.path.join(medm_path, "testDisplay.adl")
    #     self.assertTrue(os.path.exists(full_name))

    #     sys.argv = [sys.argv[0], "-d", self.tempdir, full_name]
    #     cli.main()

    #     base = os.path.splitext(os.path.basename(full_name))[0]
    #     uiname = base + output_handler.SCREEN_FILE_EXTENSION

    #     return uiname


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_PYDM_Writer_Support,
        TestOutputHandler,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
