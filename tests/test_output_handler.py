
"""
simple unit tests for this package
"""

import logging
import os
import shutil
import sys
import tempfile
import unittest
from xml.etree import ElementTree

# turn off logging output
logging.basicConfig(level=logging.CRITICAL)

_test_path = os.path.dirname(__file__)
_path = os.path.join(_test_path, '..', 'src')
if _path not in sys.path:
    sys.path.insert(0, _path)

from adl2pydm import cli, output_handler


class TestOutputHandler(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
    
    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)
    
    def convertAdlFile(self, adlname):
        medm_path = os.path.join(os.path.dirname(__file__), "medm")
        self.assertTrue(os.path.exists(medm_path))

        full_name = os.path.join(medm_path, adlname)
        self.assertTrue(os.path.exists(full_name))

        sys.argv = [sys.argv[0], "-d", self.tempdir, full_name]
        cli.main()

        base = os.path.splitext(os.path.basename(full_name))[0]
        uiname = base + output_handler.SCREEN_FILE_EXTENSION

        return uiname

    def print_xml_children(self, parent, tag=None, iter=False):
        if iter:
            for child in parent.iter(tag):
                print(child.tag, child.attrib)
        else:
            for child in parent:#  .iter(tag):
                print(child.tag, child.attrib)

    def assertEqualGeometry(self, parent, x, y, w, h):
        properties = parent.findall("property")
        self.assertGreater(len(properties), 0)
        found = False
        for prop in properties:
            if prop.attrib["name"] == "geometry":
                found = True
                for item in prop.iter():
                    if item.tag == "rect":
                        self.assertEqual(len(item), 4)
                    elif item.tag == "x":
                        self.assertEqual(item.text, str(x))
                    elif item.tag == "y":
                        self.assertEqual(item.text, str(y))
                    elif item.tag == "width":
                        self.assertEqual(item.text, str(w))
                    elif item.tag == "height":
                        self.assertEqual(item.text, str(h))
                break
        self.assertTrue(found, "geometry expected")

    def assertEqualString(self, parent, text=""):
        child = parent.find("string")
        self.assertIsNotNone(child)
        self.assertEqual(child.text, str(text))

    def assertEqualPropertyString(self, parent, propName, expected):
        properties = parent.findall("property")
        self.assertGreater(len(properties), 0)
        found = False
        for prop in properties:
            if prop.attrib["name"] == propName:
                found = True
                self.assertEqualString(prop, expected)
                break
        self.assertTrue(found, f"{propName} expected")

    def assertEqualStyleSheet(self, parent, expected):
        self.assertEqualPropertyString(parent, "styleSheet", expected)

    def assertEqualToolTip(self, parent, expected):
        self.assertEqualPropertyString(parent, "toolTip", expected)

    def test_write_pydm_widget_rectangle(self):
        uiname = self.convertAdlFile("rectangle.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        # five rectangle widgets
        tree = ElementTree.parse(full_uiname)
        root = tree.getroot()
        self.assertEqual(root.tag, "ui")
        self.assertEqual(len(root), 3)

        screen = root.find("widget")
        self.assertIsNotNone(screen)
        self.assertEqual(screen.attrib["class"], "QWidget")
        self.assertEqual(screen.attrib["name"], "screen")
        properties = screen.findall("property")
        self.assertEqual(len(properties), 3)
        self.assertEqualGeometry(screen, 96, 57, 142, 182)
        expected = """QWidget#screen {
  color: rgb(0, 0, 0);
  background-color: rgb(133, 133, 133);
  }"""
        self.assertEqualStyleSheet(screen, expected)
        self.assertEqual(properties[2].attrib["name"], "windowTitle")
        self.assertEqualString(properties[2], "rectangle")

        children = screen.findall("widget")
        self.assertEqual(len(children), 5)

        rect = children[0]
        key = "rectangle"
        self.assertEqual(rect.attrib["class"], "PyDMDrawingRectangle")
        self.assertEqual(rect.attrib["name"], key)
        self.assertEqualGeometry(rect, 10, 15, 113, 35)
        expected = """PyDMDrawingRectangle#%s {
  color: rgb(0, 0, 0);
  }""" % key
        self.assertEqualStyleSheet(rect, expected)
        self.assertEqualToolTip(rect, key)

        rect = children[1]
        key = "rectangle_1"
        self.print_xml_children(rect)
        self.assertEqual(rect.attrib["class"], "PyDMDrawingRectangle")
        self.assertEqual(rect.attrib["name"], key)
        self.assertEqualGeometry(rect, 10, 53, 113, 35)
        expected = """PyDMDrawingRectangle#%s {
  color: rgb(253, 0, 0);
  }""" % key
        self.assertEqualStyleSheet(rect, expected)
        self.assertEqualToolTip(rect, key)
        properties = rect.findall("property")
        self.assertEqual(len(properties), 7)
        # TODO: test more property content
        self.assertEqual(properties[3].attrib["name"], "brush")
        self.assertEqual(properties[4].attrib["name"], "penStyle")
        self.assertEqual(properties[5].attrib["name"], "penColor")
        self.assertEqual(properties[6].attrib["name"], "penWidth")

        rect = children[2]
        key = "rectangle_2"
        properties = rect.findall("property")
        self.assertEqual(rect.attrib["class"], "PyDMDrawingRectangle")
        self.assertEqual(rect.attrib["name"], key)
        self.assertEqualGeometry(rect, 10, 92, 113, 35)
        expected = """PyDMDrawingRectangle#%s {
  color: rgb(249, 218, 60);
  }""" % key
        self.assertEqualStyleSheet(rect, expected)
        self.assertEqualToolTip(rect, key)
        # TODO: more properties

        rect = children[3]
        key = "rectangle_3"
        properties = rect.findall("property")
        self.assertEqual(rect.attrib["class"], "PyDMDrawingRectangle")
        self.assertEqual(rect.attrib["name"], key)
        self.assertEqualGeometry(rect, 10, 130, 113, 36)
        expected = """PyDMDrawingRectangle#%s {
  color: rgb(115, 255, 107);
  }""" % key
        self.assertEqualStyleSheet(rect, expected)
        self.assertEqualToolTip(rect, key)
        # TODO: more properties

        rect = children[4]
        key = "rectangle_4"
        properties = rect.findall("property")
        self.assertEqual(rect.attrib["class"], "PyDMDrawingRectangle")
        self.assertEqual(rect.attrib["name"], key)
        self.assertEqualGeometry(rect, 20, 138, 93, 20)
        expected = """PyDMDrawingRectangle#%s {
  color: rgb(115, 223, 255);
  }""" % key
        self.assertEqualStyleSheet(rect, expected)
        self.assertEqualToolTip(rect, key)
        # TODO: more properties

        # # diagnostics
        # for rect in children:
        #     print("="*20, rect.attrib["name"])
        #     self.print_xml_children(rect, iter=True)
        #     properties = rect.findall("property")
        #     self.assertEqual(rect.attrib["class"], "PyDMDrawingRectangle")


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
