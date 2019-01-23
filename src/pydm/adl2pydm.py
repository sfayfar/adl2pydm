
"""
convert MEDM .adl screen file(s) to PyDM .ui format

Only rely on packages in this project or from the standard Python distribution. 
"""

from collections import namedtuple
import logging
import os

from adl_parser import MEDM_Reader
from output_handler import PYDM_Writer


# TEST_FILE = "/usr/local/epics/synApps_5_8/support/xxx-5-8-3/xxxApp/op/adl/xxx.adl"
# TEST_FILE = "/home/mintadmin/sandbox/synApps/support/xxx-R6-0/xxxApp/op/adl/xxx.adl"
# TEST_FILE = "/usr/local/epics/synApps_5_8/support/motor-6-9/motorApp/op/adl/motorx_all.adl"
TEST_FILE = "screens/medm/newDisplay.adl"
OUTPUT_PATH = "screens/pydm"

SCREEN_FILE_EXTENSION = ".ui"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


"""
describes the PyDM connection to Qt

example:

    "cls",       "PyDMLineEdit"
    "extends",   "QLineEdit"
    "header",    "pydm.widgets.line_edit"

"""
CustomWidget = namedtuple('CustomWidget', 'cls extends header')

# TODO: build this from only the widgets in use (#4)
PYDM_CUSTOM_WIDGETS = [
    CustomWidget("PyDMLineEdit", "QLineEdit", "pydm.widgets.line_edit"),
    CustomWidget("PyDMLabel",    "QLabel",    "pydm.widgets.label"),
    CustomWidget("PyDMEmbeddedDisplay", "QFrame", "pydm.widgets.embedded_display"),
    # not in MEDM : CustomWidget("PyDMImageView", "QWidget", "pydm.widgets.image"),
    CustomWidget("PyDMRelatedDisplayButton", "QPushButton", "pydm.widgets.related_display_button"),
    ]


def write_block(writer, parent, block):
    if block.medm_block_type == "text update":
        cls = "PyDMLineEdit"
        nm = cls        # FIXME: must be unique in the file!
        qw = writer.writeOpenTag(parent, "widget", cls=cls, name=nm)
        # pv = "prj:m1.VAL"     # FIXME: get this from block.contents[0].contents[0].chan.value
        pv = block.contents[0].contents[0].value   # FIXME: dynamically
        
        geo = block.geometry

        write_geometry(writer, qw, geo.x, geo.y, geo.width, geo.height)
        write_tooltip(writer, qw, "PV: " + pv)
        propty = writer.writeProperty(qw, "readOnly", "true", tag="bool")
        write_channel(writer, qw, pv)


def write_channel(writer, parent, channel):
    propty = writer.writeOpenProperty(parent, "channel")
    propty.attrib["stdset"] = "0"      # TODO: what does this mean? (#5)
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


def write_pydm_ui(screen):
    title = os.path.split(os.path.splitext(screen.filename)[0])[-1]
    ui_filename = os.path.join(OUTPUT_PATH, title + SCREEN_FILE_EXTENSION)
    writer = PYDM_Writer(None)
    root = writer.openFile(ui_filename)
    logging.info("writing screen file: " + ui_filename)
    writer.writeTaggedString(root, "class", title)
    form = writer.writeOpenTag(root, "widget", cls="QWidget", name="Form")
    
    def getDisplayBlock(base):
        for item in base.contents:
            if hasattr(item, "medm_block_type") and item.medm_block_type == "display": 
                return item
        # failure is not an option
        raise ValueError("Did not find display block")

    display = getDisplayBlock(screen.root)
    geom = display.geometry
    write_geometry(writer, form, geom.x, geom.y, geom.width, geom.height)

    clr = display.color
    bclr = display.background_color
    style = ""
    style += "%s#%s {\n" % (form.attrib["class"], form.attrib["name"])
    style += "  %s: rgb(%d, %d, %d);\n" % ("color", clr.r, clr.g, clr.b)
    style += "  %s: rgb(%d, %d, %d);\n" % ("background-color", bclr.r, bclr.g, bclr.b)
    style += "  }"
    propty = writer.writeOpenProperty(form, "styleSheet")
    ss = writer.writeOpenTag(propty, "string")
    ss.attrib["notr"] = "true"
    ss.text = style

    propty = writer.writeOpenProperty(form, "windowTitle")
    writer.writeTaggedString(propty, value=title)

    screen_blocks = screen.root.contents[3:]    # FIXME: dynamically (#8)
    for block in screen_blocks:
        # TODO: handle "block" if it describes a screen component (#6)
        write_block(writer, form, block)
    
    # TODO: write widget <zorder/> elements here (#7)

    # TODO: need to define ONLY for the widgets actually used (#4)
    write_customwidgets(writer, root, PYDM_CUSTOM_WIDGETS)

    # TODO: write .ui file <resources/> elements here (#9)
    # TODO: write .ui file <connections/> elements here

    writer.closeFile()


def main(adl_filename):
    reader = MEDM_Reader(TEST_FILE)
    reader.parse()
    write_pydm_ui(reader)


if __name__ == "__main__":
    main(TEST_FILE)
