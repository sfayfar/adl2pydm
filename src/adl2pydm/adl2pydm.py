#!/usr/bin/env python

"""
convert MEDM .adl screen file(s) to PyDM .ui format

Only rely on packages in this project or from the standard Python distribution. 
"""

from collections import namedtuple
import logging
import os

from adl_parser import MedmMainWidget
import adl_symbols
from output_handler import PYDM_Writer


OUTPUT_PATH = "screens/pydm"
SCREEN_FILE_EXTENSION = ".ui"
TEST_FILES = [
    "screens/medm/newDisplay.adl",                  # simple display
    "screens/medm/xxx-R5-8-4.adl",                  # related display
    "screens/medm/xxx-R6-0.adl",
    # FIXME: needs more work here (unusual structure, possibly stress test):  "screens/medm/base-3.15.5-caServerApp-test.adl",# info[, "<<color rules>>", "<<color map>>"
    "screens/medm/calc-3-4-2-1-FuncGen_full.adl",   # strip chart
    "screens/medm/calc-R3-7-1-FuncGen_full.adl",    # strip chart
    "screens/medm/calc-R3-7-userCalcMeter.adl",     # meter
    "screens/medm/mca-R7-7-mca.adl",                # bar
    "screens/medm/motorx-R6-10-1.adl",
    "screens/medm/motorx_all-R6-10-1.adl",
    "screens/medm/optics-R2-13-1-CoarseFineMotorShow.adl",  # indicator
    "screens/medm/optics-R2-13-1-kohzuGraphic.adl", # image
    "screens/medm/optics-R2-13-1-pf4more.adl",      # byte
    "screens/medm/optics-R2-13-xiahsc.adl",         # valuator
    "screens/medm/scanDetPlot-R2-11-1.adl",         # cartesian plot, strip
    "screens/medm/sscan-R2-11-1-scanAux.adl",       # shell command
    "screens/medm/std-R3-5-ID_ctrl.adl",            # param
    # "screens/medm/beamHistory_full-R3-5.adl", # dl_color -- this .adl has content errors
    "screens/medm/ADBase-R3-3-1.adl",               # composite
    "screens/medm/simDetector-R3-3-31.adl",
    ]

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
# replace with .pydm_symbols.pydm_custom_widgets

PYDM_CUSTOM_WIDGETS = [
    CustomWidget("PyDMFrame", "QFrame", "pydm.widgets.frame"),
    CustomWidget("PyDMLabel",    "QLabel",    "pydm.widgets.label"),
    CustomWidget("PyDMEmbeddedDisplay", "QFrame", "pydm.widgets.embedded_display"),
    CustomWidget("PyDMLineEdit", "QLineEdit", "pydm.widgets.line_edit"),
    CustomWidget("PyDMImageView", "QWidget", "pydm.widgets.image"),
    CustomWidget("PyDMRelatedDisplayButton", "QPushButton", "pydm.widgets.related_display_button"),
    ]


unique_widget_names = {}    # will not work right when second file is processed!


def getUniqueName(suggestion):
    unique = suggestion
    
    if unique in unique_widget_names:
        knowns = unique_widget_names[suggestion]
        unique = "%s_%d" % (suggestion, len(knowns))
        if unique in unique_widget_names:
            msg = "trouble getting a unique name from " + suggestion
            msg += "\n  complicated:\n%s" % str(unique_widget_names)
            raise ValueError(msg)
    else:
        unique = suggestion
        unique_widget_names[suggestion] = []

    # add this one to the list
    unique_widget_names[suggestion].append(unique)
    
    return unique


def write_block(writer, parent, block):
    nm = getUniqueName(block.symbol.replace(" ", "_"))
    widget_info = adl_symbols.widgets.get(block.symbol)
    # TODO: generalize
    if block.symbol == "text update":
        cls = widget_info["pydm_widget"]
        qw = writer.writeOpenTag(parent, "widget", cls=cls, name=nm)

        pv = None
        for k in ("chan", "rdbk"):
            if k in block.contents["monitor"]:
                pv = block.contents["monitor"][k]
        if pv is not None:
            pv = pv.replace("(", "{").replace(")", "}")

        write_geometry(writer, qw, block.geometry)
        write_colors(writer, qw, block)
        write_tooltip(writer, qw, "PV: " + pv)
        writer.writeProperty(qw, "readOnly", "true", tag="bool")
        write_channel(writer, qw, pv)

    elif block.symbol == "related display":
        cls = widget_info["pydm_widget"]
        qw = writer.writeOpenTag(parent, "widget", cls=cls, name=nm)
        
        text = block.title or nm
        showIcon = not text.startswith("-")
        text = text.lstrip("-")

        write_geometry(writer, qw, block.geometry)
        write_colors(writer, qw, block)
        write_tooltip(writer, qw, text)
        writer.writeProperty(qw, "text", text, tag="string")
        if not showIcon:
            writer.writeProperty(qw, "showIcon", "false", tag="bool", stdset="0")

    else:
        cls = "PyDMFrame"     # generic placeholder now
        qw = writer.writeOpenTag(parent, "widget", cls=cls, name=nm)
        write_geometry(writer, qw, block.geometry)
        write_colors(writer, qw, block)
        write_tooltip(writer, qw, "TBA widget: " + nm)
        # what styling is effective?
        #writer.writeProperty(qw, "frameShape", "QFrame::StyledPanel", tag="enum")
        #writer.writeProperty(qw, "frameShadow", "QFrame::Raised", tag="enum")
        #writer.writeProperty(qw, "lineWidth", "2", tag="number")
        #writer.writeProperty(qw, "midLineWidth", "2", tag="number")


def write_channel(writer, parent, channel):
    propty = writer.writeOpenProperty(parent, "channel", stdset="0")
    # stdset=0 signals this attribute is from PyDM, not Qt widget
    writer.writeTaggedString(propty, value="ca://" + channel)


def write_colors(writer, parent, block):
    clr = block.color
    bclr = block.background_color
    style = ""
    style += "%s#%s {\n" % (parent.attrib["class"], parent.attrib["name"])
    fmt = "  %s: rgb(%d, %d, %d);\n"
    if clr is not None:
        style += fmt % ("color", clr.r, clr.g, clr.b)
    if bclr is not None:
        style += fmt % ("background-color", bclr.r, bclr.g, bclr.b)
    style += "  }"

    if clr is not None or bclr is not None:
        propty = writer.writeOpenProperty(parent, "styleSheet")
        ss = writer.writeOpenTag(propty, "string", notr="true")
        ss.text = style


def write_customwidgets(writer, parent, customwidgets):
    cw_set = writer.writeOpenTag(parent, "customwidgets")
    for item in customwidgets:
        cw = writer.writeOpenTag(cw_set, "customwidget")
        writer.writeTaggedString(cw, "class", item.cls)
        writer.writeTaggedString(cw, "extends", item.extends)
        writer.writeTaggedString(cw, "header", item.header)


def write_geometry(writer, parent, geom):
    propty = writer.writeOpenProperty(parent, "geometry")
    rect = writer.writeOpenTag(propty, "rect")
    if str(geom.x) == "-":
        _debug_ = True
    writer.writeTaggedString(rect, "x", str(geom.x))
    writer.writeTaggedString(rect, "y", str(geom.y))
    writer.writeTaggedString(rect, "width", str(geom.width))
    writer.writeTaggedString(rect, "height", str(geom.height))


def write_tooltip(writer, parent, tip):
    propty = writer.writeOpenProperty(parent, "toolTip")
    writer.writeTaggedString(propty, value=tip)


def write_pydm_ui(screen):
    title = screen.title or os.path.split(os.path.splitext(screen.given_filename)[0])[-1]
    ui_filename = os.path.join(OUTPUT_PATH, title + SCREEN_FILE_EXTENSION)
    writer = PYDM_Writer(None)
    root = writer.openFile(ui_filename)
    logging.info("writing screen file: " + ui_filename)
    writer.writeTaggedString(root, "class", title)
    form = writer.writeOpenTag(root, "widget", cls="QWidget", name="screen")
    
    write_geometry(writer, form, screen.geometry)
    write_colors(writer, form, screen)

    propty = writer.writeOpenProperty(form, "windowTitle")
    writer.writeTaggedString(propty, value=title)

    for widget in screen.widgets:
        # TODO: handle "widget" if it describes a screen component (#6)
        write_block(writer, form, widget)
    
    # TODO: write widget <zorder/> elements here (#7)

    # TODO: need to define ONLY for the widgets actually used (#4)
    write_customwidgets(writer, root, PYDM_CUSTOM_WIDGETS)

    # TODO: write .ui file <resources/> elements here (#9)
    # TODO: write .ui file <connections/> elements here (#10)

    writer.closeFile()


def main(adl_filename):
    reader = MedmMainWidget(adl_filename)
    buf = reader.getAdlLines(adl_filename)
    reader.parseAdlBuffer(buf)
    write_pydm_ui(reader)       # refactor into a class


if __name__ == "__main__":
    for fname in TEST_FILES:
        main(fname)
    print("done")
