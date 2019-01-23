
"""
convert MEDM .adl screen file(s) to PyDM .ui format
"""

from collections import namedtuple
import logging

from adl_parser import MEDM_Reader
from output_handler import PYDM_Writer


TEST_FILE = "/usr/local/epics/synApps_5_8/support/xxx-5-8-3/xxxApp/op/adl/xxx.adl"
TEST_FILE = "/home/mintadmin/sandbox/synApps/support/xxx-R6-0/xxxApp/op/adl/xxx.adl"
TEST_FILE = "/usr/local/epics/synApps_5_8/support/motor-6-9/motorApp/op/adl/motorx_all.adl"
TEST_FILE = "/home/mintadmin/sandbox/screens/pydm/newDisplay.adl"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


"""
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Form</class>
 <widget class="QWidget" name="Form">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>400</width>
    <height>300</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Form</string>
  </property>
  <widget class="PyDMLineEdit" name="PyDMLineEdit">
   <property name="geometry">
    <rect>
     <x>40</x>
     <y>40</y>
     <width>127</width>
     <height>21</height>
    </rect>
   </property>
   <property name="toolTip">
    <string/>
   </property>
   <property name="channel" stdset="0">
    <string>prj:m1.VAL</string>
   </property>
  </widget>
 </widget>
 <customwidgets>
  <customwidget>
   <class>PyDMLineEdit</class>
   <extends>QLineEdit</extends>
   <header>pydm.widgets.line_edit</header>
  </customwidget>
 </customwidgets>
 <resources/>
 <connections/>
</ui>
"""

"""
describes the PyDM connection to Qt

example:

    "cls",       "PyDMLineEdit"
    "extends",   "QLineEdit"
    "header",    "pydm.widgets.line_edit"

"""
CustomWidget = namedtuple('CustomWidget', 'cls extends header')

# TODO: build this from only the widgets in use
# TODO: where is this information available?
PYDM_CUSTOM_WIDGETS = [
    CustomWidget("PyDMLineEdit", "QLineEdit", "pydm.widgets.line_edit"),
    CustomWidget("PyDMLabel",    "QLabel",    "pydm.widgets.label"),
    CustomWidget("PyDMEmbeddedDisplay", "QFrame", "pydm.widgets.embedded_display"),
    # not in MEDM : CustomWidget("PyDMImageView", "QWidget", "pydm.widgets.image"),
    CustomWidget("PyDMRelatedDisplayButton", "QPushButton", "pydm.widgets.related_display_button"),
    ]


def write_channel(writer, parent, channel):
    propty = writer.writeOpenProperty(parent, "channel")
    propty.attrib["stdset"] = "0"      # TODO: what does this mean?
    writer.writeTaggedString(propty, value="ca://" + channel)


def write_customwidgets(writer, parent, customwidgets):
    cw_set = writer.writeOpenTag(parent, "customwidgets")
    for item in customwidgets:
        cw = writer.writeOpenTag(cw_set, "customwidget")
        writer.writeTaggedString(cw, "class", item.cls)
        writer.writeTaggedString(cw, "extends", item.extends)
        writer.writeTaggedString(cw, "header", item.header)


def write_geometry(writer, parent, x, y, width, height):
    propty = writer.writeOpenProperty(parent, "geometry")
    rect = writer.writeOpenTag(propty, "rect")
    writer.writeTaggedString(rect, "x", str(x))
    writer.writeTaggedString(rect, "y", str(y))
    writer.writeTaggedString(rect, "width", str(width))
    writer.writeTaggedString(rect, "height", str(height))


def write_tooltip(writer, parent, tip):
    propty = writer.writeOpenProperty(parent, "toolTip")
    writer.writeTaggedString(propty, value=tip)


def write_pydm_ui(ui_filename):
    writer = PYDM_Writer(None)
    root = writer.openFile(ui_filename)
    writer.writeTaggedString(root, "class", "Form")
    form = writer.writeOpenTag(root, "widget", cls="QWidget", name="Form")

    write_geometry(writer, form, 0, 0, 400, 300)

    propty = writer.writeOpenProperty(form, "windowTitle")
    writer.writeTaggedString(propty, value="Form")

    qw = writer.writeOpenTag(form, "widget", cls="PyDMLineEdit", name="PyDMLineEdit")
    write_geometry(writer, qw, 40, 40, 127, 21)
    write_tooltip(writer, qw, "")
    write_channel(writer, qw, "prj:m1.VAL")
    
    write_customwidgets(writer, root, PYDM_CUSTOM_WIDGETS)

    writer.closeFile()


def main(adl_filename):
    reader = MEDM_Reader(TEST_FILE)
    reader.parse()
    write_pydm_ui("test.xml")


if __name__ == "__main__":
    main(TEST_FILE)
