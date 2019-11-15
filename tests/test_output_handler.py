
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

    def getNamedProperty(self, parent, propName):
        properties = parent.findall("property")
        self.assertGreater(len(properties), 0)
        for prop in properties:
            if prop.attrib["name"] == propName:
                return prop

    def getNamedWidget(self, parent, key):
        for widget in parent.findall("widget"):
            if widget.attrib["name"] == key:
                return widget

    def getSubElement(self, parent, tag):
        self.assertIsNotNone(parent, "parent not found")
        child = parent.find(tag)
        self.assertIsNotNone(child, tag + " subelement expected")
        return child

    def print_xml_children(self, parent, tag=None, iter=False):
        if iter:
            for i, child in enumerate(parent.iter(tag)):
                print(i, child.tag, child.attrib)
        else:
            for i, child in enumerate(parent):#  .iter(tag):
                print(i, child.tag, child.attrib)

    def assertEqualBool(self, prop, value):
        child = self.getSubElement(prop, "bool")
        self.assertEqual(child.text, str(value).lower())

    def assertEqualBrush(self, parent, brushstyle, r, g, b):
        prop = self.getNamedProperty(parent, "brush")
        self.assertIsNotNone(prop)
        self.assertExpectedAttrib(prop, stdset="0")
        for item in prop.iter():
            if item.tag == "brush":
                self.assertExpectedAttrib(item, brushstyle=brushstyle)
        self.assertPropertyColor(prop, r, g, b, alpha="255")

    def assertEqualChannel(self, parent, channel):
        self.assertEqualPropertyString(parent, "channel", channel)

    def assertEqualClassName(self, parent, cls, nm):
        self.assertExpectedAttrib(parent, **{"class":cls, "name":nm})

    def assertEqualDouble(self, prop, number):
        self.assertIsNotNone(prop)
        self.assertExpectedAttrib(prop, stdset="0")
        for item in prop.iter():
            if item.tag == "double":
                self.assertEqual(float(item.text), number)

    def assertEqualGeometry(self, parent, x, y, w, h):
        prop = self.getNamedProperty(parent, "geometry")
        self.assertIsNotNone(prop)
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

    def assertEqualNumber(self, prop, number):
        child = self.getSubElement(prop, "number")
        self.assertEqual(float(child.text), float(number))

    def assertEqualPenColor(self, parent, r, g, b):
        prop = self.getNamedProperty(parent, "penColor")
        self.assertIsNotNone(prop)
        self.assertExpectedAttrib(prop, stdset="0")
        self.assertPropertyColor(prop, r, g, b)

    def assertEqualPenStyle(self, parent, value):
        prop = self.getNamedProperty(parent, "penStyle")
        self.assertIsNotNone(prop)
        self.assertExpectedAttrib(prop, stdset="0")
        for item in prop.iter():
            if item.tag == "enum":
                self.assertEqual(item.text, value)

    def assertEqualPenWidth(self, parent, number):
        prop = self.getNamedProperty(parent, "penWidth")
        self.assertEqualDouble(prop, number)

    def assertEqualString(self, parent, text=""):
        child = self.getSubElement(parent, "string")
        self.assertEqual(child.text, str(text))

    def assertEqualTitle(self, parent, title):
        prop = self.getNamedProperty(parent, "title")
        if title is None:
            self.assertIsNone(prop)
        else:
            self.assertIsNotNone(prop)
            self.assertEqualString(prop, title)

    def assertEqualPropertyBool(self, parent, propName, expected):
        prop = self.getNamedProperty(parent, propName)
        self.assertIsNotNone(prop)
        self.assertEqualBool(prop, expected)

    def assertEqualPropertyDouble(self, parent, propName, expected):
        prop = self.getNamedProperty(parent, propName)
        self.assertIsNotNone(prop)
        self.assertEqualDouble(prop, expected)

    def assertEqualPropertyNumber(self, parent, propName, expected):
        prop = self.getNamedProperty(parent, propName)
        self.assertIsNotNone(prop)
        self.assertEqualNumber(prop, expected)

    def assertEqualPropertyString(self, parent, propName, expected):
        prop = self.getNamedProperty(parent, propName)
        self.assertIsNotNone(prop)
        self.assertEqualString(prop, expected)

    def assertEqualStyleSheet(self, parent, expected):
        self.assertEqualPropertyString(parent, "styleSheet", expected)

    def assertEqualToolTip(self, parent, expected):
        self.assertEqualPropertyString(parent, "toolTip", expected)

    def assertExpectedAttrib(self, parent, **kwargs):
        self.assertTrue(hasattr(parent, "attrib"))
        self.assertExpectedDictInRef(parent.attrib, **kwargs)

    def assertExpectedDictInRef(self, ref, **kwargs):
        self.assertIsInstance(ref, dict)
        self.assertIsInstance(kwargs, dict)
        for k, v in kwargs.items():
            self.assertTrue(k in ref)
            self.assertEqual(v, ref[k])

    def assertIsNoneProperty(self, parent, propName):
        prop = self.getNamedProperty(parent, propName)
        self.assertIsNone(prop)

    def assertPropertyColor(self, parent, r, g, b, **kwargs):
        self.assertEqual(parent.tag, "property")
        for item in parent.iter():
            if item.tag == "color":
                self.assertEqual(len(item.attrib), len(kwargs))
                if len(kwargs) > 0:
                    self.assertExpectedAttrib(item, **kwargs)
            elif item.tag == "red":
                self.assertEqual(item.text, str(r))
            elif item.tag == "green":
                self.assertEqual(item.text, str(g))
            elif item.tag == "blue":
                self.assertEqual(item.text, str(b))

    # ----------------------------------------------------------

    def test_write_widget_arc(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "arc"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(
            widget, 
            "PyDMDrawingPie", 
            key)
        # self.print_xml_children(widget)

        self.assertEqualPenStyle(widget, "Qt::SolidLine")
        self.assertIsNoneProperty(widget, "startAngle")   # default: 0
        self.assertEqualPropertyDouble(widget, "spanAngle", -320)
        self.assertEqualBrush(widget, "SolidPattern", 251, 243, 74)

    def test_write_widget_byte(self):
        uiname = self.convertAdlFile("byte-monitor.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen, iter=True)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 4)

        key = "byte"
        widget = self.getNamedWidget(screen, key)
        # self.print_xml_children(widget)
        self.assertEqualClassName(
            widget, 
            "PyDMByteIndicator", 
            key)
        
        self.assertEqualChannel(widget, "ca://sky:interp_mode")

        prop = self.getNamedProperty(widget, "onColor")
        self.assertPropertyColor(prop, 0, 0, 0)
        prop = self.getNamedProperty(widget, "offColor")
        self.assertPropertyColor(prop, 187, 187, 187)
        self.assertEqualPropertyString(widget, "orientation", "Qt::Horizontal")
        self.assertEqualPropertyBool(widget, "showLabels", False)
        self.assertEqualPropertyBool(widget, "bigEndian", False)
        self.assertEqualPropertyNumber(widget, "numBits", 4)

        key = "byte_1"
        widget = self.getNamedWidget(screen, key)
        # self.print_xml_children(widget)
        self.assertEqualClassName(
            widget, 
            "PyDMByteIndicator", 
            key)
        
        self.assertEqualChannel(widget, "ca://sky:interp_mode")

        prop = self.getNamedProperty(widget, "onColor")
        self.assertPropertyColor(prop, 0, 0, 0)
        prop = self.getNamedProperty(widget, "offColor")
        self.assertPropertyColor(prop, 187, 187, 187)
        self.assertEqualPropertyString(widget, "orientation", "Qt::Horizontal")
        self.assertEqualPropertyBool(widget, "showLabels", False)
        self.assertEqualPropertyBool(widget, "bigEndian", True)
        self.assertEqualPropertyNumber(widget, "numBits", 4)

        key = "byte_2"
        widget = self.getNamedWidget(screen, key)
        # self.print_xml_children(widget)
        self.assertEqualClassName(
            widget, 
            "PyDMByteIndicator", 
            key)
        
        self.assertEqualChannel(widget, "ca://sky:interp_mode")

        prop = self.getNamedProperty(widget, "onColor")
        self.assertPropertyColor(prop, 0, 0, 0)
        prop = self.getNamedProperty(widget, "offColor")
        self.assertPropertyColor(prop, 187, 187, 187)
        self.assertEqualPropertyString(widget, "orientation", "Qt::Vertical")
        self.assertEqualPropertyBool(widget, "showLabels", False)
        self.assertEqualPropertyBool(widget, "bigEndian", False)
        self.assertEqualPropertyNumber(widget, "numBits", 4)

        key = "byte_3"
        widget = self.getNamedWidget(screen, key)
        # self.print_xml_children(widget)
        self.assertEqualClassName(
            widget, 
            "PyDMByteIndicator", 
            key)
        
        self.assertEqualChannel(widget, "ca://sky:interp_mode")

        prop = self.getNamedProperty(widget, "onColor")
        self.assertPropertyColor(prop, 0, 0, 0)
        prop = self.getNamedProperty(widget, "offColor")
        self.assertPropertyColor(prop, 187, 187, 187)
        self.assertEqualPropertyString(widget, "orientation", "Qt::Vertical")
        self.assertEqualPropertyBool(widget, "showLabels", False)
        self.assertEqualPropertyBool(widget, "bigEndian", True)
        self.assertEqualPropertyNumber(widget, "numBits", 4)

    def test_write_widget_cartesian_plot(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "cartesian_plot"
        widget = self.getNamedWidget(screen, key)
        # self.print_xml_children(widget)
        self.assertEqualClassName(
            widget, 
            "PyDMScatterPlot", 
            key)

        self.assertEqualTitle(widget, "Calibration Curve (S1A:H1)")
        self.assertEqualPropertyString(widget, "xLabels", "Magnetic Field")
        self.assertEqualPropertyString(widget, "yLabels", "Current")

        prop = self.getNamedProperty(widget, "curves")
        stringlist = self.getSubElement(prop, "stringlist")
        self.assertEqual(len(stringlist), 1)
        trace = output_handler.jsonDecode(stringlist[0].text)
        expected = dict(
                name = "x=%s, y=%s" % (
                    "Xorbit:S1A:H1:CurrentAI.BARR",
                    "Xorbit:S1A:H1:CurrentAI.IARR", 
                    ),
                x_channel = "ca://Xorbit:S1A:H1:CurrentAI.BARR",
                y_channel = "ca://Xorbit:S1A:H1:CurrentAI.IARR",
                color = "#%02x%02x%02x" % (0, 0, 0),
                lineStyle = 1,
                block_size = 8,
            )
        self.assertDictEqual(trace, expected)

    def test_write_widget_choice_button(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "choice_button"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(
            widget, 
            "PyDMEnumComboBox", 
            key)

        self.assertEqualChannel(widget, "ca://Xorbit:S1A:H1:CurrentAO.SCAN")

    def test_write_widget_composite(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "composite"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(widget, "PyDMFrame", key)
        # self.print_xml_children(widget)
        self.assertEqual(len(widget), 6)

    def test_write_widget_embedded_display(self):
        # Actually. MEDM writes as a composite
        # but we redirect (in the output_handler module) 
        # that to be an "embedded display".
        uiname = self.convertAdlFile("configMenu.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 19)

        key = "composite"
        widget = self.getNamedWidget(screen, key)
        # self.print_xml_children(widget)
        self.assertEqualClassName(widget, "PyDMEmbeddedDisplay", key)
        self.assertEqual(len(widget), 4)
        self.assertEqualPropertyString(widget, "filename", "configMenuHead_bare.ui")
        self.assertEqualPropertyString(widget, "macros", "P=${P},CONFIG=${CONFIG}")

    def test_write_widget_image(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "image"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(widget, "PyDMDrawingImage", key)
        # self.print_xml_children(widget)

        self.assertEqualPropertyString(widget, "filename", "apple.gif")

    def test_write_widget_indicator(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "indicator"
        widget = self.getNamedWidget(screen, key)
        # self.print_xml_children(widget)
        self.assertEqualClassName(
            widget, 
            "PyDMScaleIndicator", 
            key)
        
        self.assertEqualChannel(widget, "ca://Xorbit:S1A:H1:CurrentAO")

        key = "meter"
        widget = self.getNamedWidget(screen, key)
        # self.print_xml_children(widget)
        self.assertEqualClassName(
            widget, 
            "PyDMScaleIndicator", 
            key)
        
        self.assertEqualChannel(widget, "ca://Xorbit:S1A:H1:CurrentAO")

        # meter widget has no title
        self.assertEqualTitle(widget, None)

        # if not found, then gets default value in PyDM
        for item in "limitsFromChannel userUpperLimit userLowerLimit".split():
            prop = self.getNamedProperty(widget, item)
            self.assertIsNone(prop, item)

    def test_write_widget_menu(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "menu"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(
            widget, 
            "PyDMEnumButton", 
            key)
        # self.print_xml_children(widget)

        self.assertEqualChannel(widget, "ca://Xorbit:S1A:H1:CurrentAO.SCAN")

    def test_write_widget_message_button(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "message_button"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(widget, "PyDMPushButton", "message_button")
        self.assertEqualPropertyString(widget, "text", "S1A:H1 Reset")
        self.assertEqualPropertyString(widget, "toolTip", "Xorbit:S1A:H1:CurrentAO")
        self.assertEqualChannel(widget, "ca://Xorbit:S1A:H1:CurrentAO")
        self.assertEqualPropertyString(widget, "pressValue", "0.00")

    def test_write_widget_meter(self):
        uiname = self.convertAdlFile("meter.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 1)

        key = "meter"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(widget, "PyDMScaleIndicator", key)
        self.assertEqualTitle(widget, None) # meter widget has no title
        self.assertEqualPropertyBool(widget, "limitsFromChannel", False)
        self.assertEqualPropertyDouble(widget, "userUpperLimit", 10)
        self.assertEqualPropertyDouble(widget, "userLowerLimit", -10)

    def test_write_widget_rectangle(self):
        """
        also test the full file structure
        """
        uiname = self.convertAdlFile("rectangle.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        # five rectangle widgets
        tree = ElementTree.parse(full_uiname)
        root = tree.getroot()
        self.assertEqual(root.tag, "ui")
        self.assertEqual(len(root), 3)

        screen = self.getSubElement(root, "widget")
        self.assertEqualClassName(screen, "QWidget", "screen")
        properties = screen.findall("property")
        self.assertEqual(len(properties), 3)
        self.assertEqualGeometry(screen, 96, 57, 142, 182)
        expected = """QWidget#screen {
  color: rgb(0, 0, 0);
  background-color: rgb(133, 133, 133);
  }"""
        self.assertEqualStyleSheet(screen, expected)

        prop = self.getNamedProperty(screen, "windowTitle")
        self.assertExpectedAttrib(prop, name="windowTitle")
        self.assertEqualString(prop, "rectangle")

        children = screen.findall("widget")
        self.assertEqual(len(children), 5)

        key = "rectangle"
        rect = children[0]
        self.assertEqualClassName(rect, "PyDMDrawingRectangle", key)
        self.assertEqualGeometry(rect, 10, 15, 113, 35)
#         expected = """PyDMDrawingRectangle#%s {
#   color: rgb(0, 0, 0);
#   }""" % key
#         self.assertEqualStyleSheet(rect, expected)
        self.assertEqualToolTip(rect, key)

        key = "rectangle_1"
        rect = children[1]
        self.assertEqualClassName(rect, "PyDMDrawingRectangle", key)
        self.assertEqualGeometry(rect, 10, 53, 113, 35)
        self.assertEqualToolTip(rect, key)
        properties = rect.findall("property")
        self.assertEqual(len(properties), 6)
        self.assertEqualBrush(rect, "NoBrush", 253, 0, 0)
        self.assertEqualPenStyle(rect, "Qt::SolidLine")
        self.assertEqualPenColor(rect, 253, 0, 0)
        self.assertEqualPenWidth(rect, 1)

        key = "rectangle_2"
        rect = children[2]
        self.assertEqualClassName(rect, "PyDMDrawingRectangle", key)
        self.assertEqualGeometry(rect, 10, 92, 113, 35)
        self.assertEqualToolTip(rect, key)
        properties = rect.findall("property")
        self.assertEqual(len(properties), 6)
        self.assertEqualBrush(rect, "NoBrush", 249, 218, 60)
        self.assertEqualPenStyle(rect, "Qt::DashLine")
        self.assertEqualPenColor(rect, 249, 218, 60)
        self.assertEqualPenWidth(rect, 1)

        key = "rectangle_3"
        rect = children[3]
        self.assertEqualClassName(rect, "PyDMDrawingRectangle", key)
        self.assertEqualGeometry(rect, 10, 130, 113, 36)
        self.assertEqualToolTip(rect, key)
        properties = rect.findall("property")
        self.assertEqual(len(properties), 7)
        self.assertEqualBrush(rect, "NoBrush", 115, 255, 107)
        self.assertEqualPenStyle(rect, "Qt::SolidLine")
        self.assertEqualPenColor(rect, 115, 255, 107)
        self.assertEqualPenWidth(rect, 6)

        prop = self.getNamedProperty(rect, "rules")
        self.assertExpectedAttrib(prop, stdset="0")
        child = self.getSubElement(prop, "string")
        rules = output_handler.jsonDecode(child.text)
        self.assertEqual(len(rules), 1)
        expected = {
            'name': 'rule_0', 
            'property': 'Visible', 
            'channels': [
                {'channel': '${P}alldone', 
                 'trigger': True}
                ], 
            'expression': 'ch[0] == 0'
            }
        self.assertExpectedDictInRef(rules[0], **expected)

        key = "rectangle_4"
        rect = children[4]
        self.assertEqualClassName(rect, "PyDMDrawingRectangle", key)
        self.assertEqualGeometry(rect, 20, 138, 93, 20)
        self.assertEqualToolTip(rect, key)
        properties = rect.findall("property")
        self.assertEqual(len(properties), 7)
        self.assertEqualBrush(rect, "SolidPattern", 115, 223, 255)
        self.assertEqualPenStyle(rect, "Qt::SolidLine")
        self.assertEqualPenColor(rect, 115, 223, 255)
        self.assertEqualPenWidth(rect, 0)

        prop = self.getNamedProperty(rect, "rules")
        self.assertExpectedAttrib(prop, stdset="0")
        child = self.getSubElement(prop, "string")
        rules = output_handler.jsonDecode(child.text)
        self.assertEqual(len(rules), 1)
        expected = {
            'name': 'rule_0', 
            'property': 'Visible', 
            'channels': [
                {'channel': '${P}${M}.RBV', 
                 'trigger': True},
                {'channel': '${P}${M}.VAL', 
                 'trigger': True}
                ], 
            'expression': 'ch[0]==ch[1]'
            }
        self.assertExpectedDictInRef(rules[0], **expected)

    def test_write_widget_related_display(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "related_display"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(
            widget, 
            "PyDMRelatedDisplayButton", 
            key)
        # self.print_xml_children(widget)

        self.assertEqualPropertyString(widget, "toolTip", key)
        self.assertEqualPropertyString(widget, "text", key)

        expected = """PyDMRelatedDisplayButton#%s {
  color: rgb(0, 0, 0);
  background-color: rgb(115, 223, 255);
  }""" % key
        self.assertEqualStyleSheet(widget, expected)

        self.assertIsNoneProperty(widget, "openInNewWindow")
        # self.assertEqualPropertyBool(widget, "openInNewWindow", True)
        self.assertEqualPropertyBool(widget, "showIcon", True)

        prop = self.getNamedProperty(widget, "filenames")
        stringlist = prop.find("stringlist")
        self.assertEqual(len(stringlist), 1)
        self.assertEqualString(stringlist, "junk.ui")

        prop = self.getNamedProperty(widget, "titles")
        stringlist = prop.find("stringlist")
        self.assertEqual(len(stringlist), 1)
        self.assertEqualString(stringlist, "Another Junk")

        prop = self.getNamedProperty(widget, "macros")
        stringlist = prop.find("stringlist")
        self.assertEqual(len(stringlist), 1)
        child = stringlist.find("string")
        self.assertIsNone(child.text)

    def test_write_widget_strip_chart_axis_labels(self):
        uiname = self.convertAdlFile("strip.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 1)

        key = "strip_chart"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(
            widget, 
            "PyDMTimePlot", 
            key)

        self.assertEqualTitle(widget, "chart title text")
        self.assertEqualPropertyString(widget, "xLabels", "x axis text")
        self.assertEqualPropertyString(widget, "yLabels", "y axis text")

    def test_write_widget_strip_chart(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "strip_chart"
        widget = self.getNamedWidget(screen, key)
        # self.print_xml_children(widget)
        self.assertEqualClassName(
            widget, 
            "PyDMTimePlot", 
            key)

        self.assertEqualTitle(widget, "Horizontal Correctors")

        prop = self.getNamedProperty(widget, "curves")
        stringlist = self.getSubElement(prop, "stringlist")
        self.assertEqual(len(stringlist), 3)
        trace = output_handler.jsonDecode(stringlist[0].text)
        expected = {
            "color": "#cd6100",
            "lineStyle": 1,
            "lineWidth": 1,
            "channel": "ca://Xorbit:S1A:H1:CurrentAO",
            "name": "Xorbit:S1A:H1:CurrentAO"
            }
        self.assertDictEqual(trace, expected)
        trace = output_handler.jsonDecode(stringlist[1].text)
        expected = {
            "color": "#610a75",
            "lineStyle": 1,
            "lineWidth": 1,
            "channel": "ca://Xorbit:S1A:H2:CurrentAO",
            "name": "Xorbit:S1A:H2:CurrentAO"
            }
        self.assertDictEqual(trace, expected)
        trace = output_handler.jsonDecode(stringlist[2].text)
        expected = {
            "color": "#4ea5f9",
            "lineStyle": 1,
            "lineWidth": 1,
            "channel": "ca://Xorbit:S1A:H3:CurrentAO",
            "name": "Xorbit:S1A:H3:CurrentAO"
            }
        self.assertDictEqual(trace, expected)

    def test_write_widget_text(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "text"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(widget, "PyDMLabel", key)

        self.assertEqualPropertyString(widget, "text", "Test Display")

        prop = self.getNamedProperty(widget, "alignment")
        child = self.getSubElement(prop, "set")
        self.assertIsNotNone(child)
        self.assertEqual(child.text, "Qt::AlignCenter")

    def test_write_widget_text_entry(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "text_entry"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(widget, "PyDMLineEdit", key)
        # self.print_xml_children(widget)

        self.assertEqualChannel(widget, "ca://Xorbit:S1A:H1:CurrentAO")

    def test_write_widget_text_update(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "text_update"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(widget, "PyDMLabel", key)
        expected = """PyDMLabel#%s {
  color: rgb(88, 147, 255);
  background-color: rgb(236, 236, 236);
  }""" % key
        self.assertEqualStyleSheet(widget, expected)

        self.assertEqualChannel(widget, "ca://Xorbit:S1A:H1:CurrentAO")

        prop = self.getNamedProperty(widget, "textInteractionFlags")
        child = self.getSubElement(prop, "set")
        self.assertIsNotNone(child)
        self.assertEqual(
            child.text, 
            "Qt::TextSelectableByKeyboard|Qt::TextSelectableByMouse")

    def test_write_widget_valuator(self):
        uiname = self.convertAdlFile("testDisplay.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 64)

        key = "valuator"
        widget = self.getNamedWidget(screen, key)
        # self.print_xml_children(widget)
        self.assertEqualClassName(
            widget, 
            "PyDMSlider", 
            key)

        self.assertEqualChannel(widget, "ca://Xorbit:S1A:H1:CurrentAO")
        self.assertEqualPropertyString(widget, "orientation", "Qt::Horizontal")
        self.assertEqualPropertyNumber(widget, "precision", 1)
        for propName in """showLimitLabels 
                           showValueLabel 
                           userDefinedLimits
                           userMaximum
                           userMinimum
                           """.split():
            self.assertIsNoneProperty(widget, propName)

    def test_write_widget_valuator_variations(self):
        uiname = self.convertAdlFile("slider.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 1)

        key = "valuator"
        widget = self.getNamedWidget(screen, key)
        # self.print_xml_children(widget)
        self.assertEqualClassName(
            widget, 
            "PyDMSlider", 
            key)

        self.assertEqualChannel(widget, "ca://sky:userCalc2.A")
        self.assertEqualPropertyString(widget, "orientation", "Qt::Horizontal")
        self.assertEqualPropertyNumber(widget, "precision", 0.1)
        # self.print_xml_children(widget)
        self.assertEqualPropertyBool(widget, "userDefinedLimits", True)
        self.assertEqualPropertyDouble(widget, "userMaximum", 10)
        self.assertEqualPropertyDouble(widget, "userMinimum", -10)
        self.assertEqualPropertyBool(widget, "showLimitLabels", True)
        self.assertEqualPropertyBool(widget, "showValueLabel", True)

    def test_write_widget_wheel_switch(self):
        uiname = self.convertAdlFile("wheel_switch.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 1)

        key = "wheel_switch"
        widget = self.getNamedWidget(screen, key)
        # self.print_xml_children(widget)
        self.assertEqualClassName(
            widget, 
            "PyDMSpinbox", 
            key)

        self.assertEqualChannel(widget, "ca://sky:userCalc2.A")
        self.assertEqualPropertyDouble(widget, "maximum", 10)
        self.assertEqualPropertyDouble(widget, "minimum", -10)
        self.assertEqualPropertyBool(widget, "showLimitLabels", True)
        self.assertEqualPropertyBool(widget, "showValueLabel", False)
        self.assertEqualPropertyBool(widget, "userDefinedLimits", True)

    def test_write_widget_text_examples(self):
        uiname = self.convertAdlFile("text_examples.adl")
        full_uiname = os.path.join(self.tempdir, uiname)
        self.assertTrue(os.path.exists(full_uiname))

        root = ElementTree.parse(full_uiname).getroot()
        screen = self.getSubElement(root, "widget")
        # self.print_xml_children(screen)
        widgets = screen.findall("widget")
        self.assertEqual(len(widgets), 17)

        key = "text_update"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(
            widget, 
            "PyDMLabel", 
            key)

        key = "text"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(
            widget, 
            "PyDMLabel", 
            key)

        self.assertEqualPropertyString(widget, "text", "macro P=${P}")

        key = "text_update"
        widget = self.getNamedWidget(screen, key)
        self.assertEqualClassName(
            widget, 
            "PyDMLabel", 
            key)

        self.assertEqualChannel(widget, "ca://${P}")

        # check that widget text will announce widget height
        for widget in widgets[2:]:
            geom = self.getNamedProperty(widget, "geometry")
            height = None
            for item in geom.iter():
                if item.tag == "height":
                    height = item.text
            self.assertEqualPropertyString(widget, "text", "height: " + height)


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
