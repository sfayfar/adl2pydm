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
import pydm_symbols


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


class PydmSupport(object):
    """
    """
    
    def __init__(self):
        self.custom_widgets = []
        self.unique_widget_names = {}
    
    def get_unique_widget_name(self, suggestion):
        """
        return a widget name that is not already in use
        
        Qt requires that all widgets have a unique name.
        This algorithm keeps track of all widget names in use 
        (basedon the suggested name) and, if the suggested name
        exists, generates a new name with an index number suffixed.
        """
        unique = suggestion
        
        if unique in self.unique_widget_names:
            knowns = self.unique_widget_names[suggestion]
            unique = "%s_%d" % (suggestion, len(knowns))
            if unique in self.unique_widget_names:
                msg = "trouble getting a unique name from " + suggestion
                msg += "\n  complicated:\n%s" % str(unique_widget_names)
                raise ValueError(msg)
        else:
            unique = suggestion
            self.unique_widget_names[suggestion] = []
    
        # add this one to the list
        self.unique_widget_names[suggestion].append(unique)
        
        return unique
    
    def get_channel(self, contents):
        """return the PV channel described in the MEDM widget"""
        pv = None
        for k in ("chan", "rdbk", "ctrl"):
            if k in contents:
                pv = contents[k]
        if pv is not None:
            pv = pv.replace("(", "{").replace(")", "}")
        return pv
    
    def write_ui(self, screen):
        """main entry point to write the .ui file"""
        title = screen.title or os.path.split(os.path.splitext(screen.given_filename)[0])[-1]
        ui_filename = os.path.join(OUTPUT_PATH, title + SCREEN_FILE_EXTENSION)
        self.writer = PYDM_Writer(None)

        root = self.writer.openFile(ui_filename)
        logging.info("writing screen file: " + ui_filename)
        self.writer.writeTaggedString(root, "class", title)
        form = self.writer.writeOpenTag(root, "widget", cls="QWidget", name="screen")
        
        self.write_geometry(form, screen.geometry)
        self.write_colors(form, screen)
    
        propty = self.writer.writeOpenProperty(form, "windowTitle")
        self.writer.writeTaggedString(propty, value=title)
    
        for widget in screen.widgets:
            # handle "widget" if it is a known screen component
            self.write_block(form, widget)
        
        # TODO: self.write widget <zorder/> elements here (#7)
    
        self.write_customwidgets(root)
    
        # TODO: write .ui file <resources/> elements here (#9)
        # TODO: write .ui file <connections/> elements here (#10)
        
        self.writer.closeFile()

    def write_block(self, parent, block):
        handlers = {
            #"arc" : dict(type="static", pydm_widget="PyDMDrawingArc"),
            #"bar" : dict(type="monitor", pydm_widget="PyDMDrawingRectangle"),
            #"byte" : dict(type="monitor", pydm_widget="PyDMByteIndicator"),
            #"cartesian plot" : dict(type="monitor", pydm_widget="PyDMScatterPlot"),
            #"choice button" : dict(type="controller", pydm_widget="PyDMEnumComboBox"),
            #"composite" : dict(type="static", pydm_widget="PyDMFrame"),
            #"embedded display" : dict(type="static", pydm_widget="PyDMEmbeddedDisplay"),
            "image" : self.write_block_image,
            #"indicator" : dict(type="monitor", pydm_widget="PyDMLineEdit"),
            #"menu" : dict(type="controller", pydm_widget="PyDMEnumButton"),
            "message button" : self.write_block_message_button,
            #"meter" : dict(type="monitor", pydm_widget="PyDMScaleIndicator"),
            #"oval" : dict(type="static", pydm_widget="PyDMDrawingEllipse"),
            #"polygon" : dict(type="static", pydm_widget="PyDMDrawingPolygon"),
            #"polyline" : dict(type="static", pydm_widget="PyDMDrawingPolygon"),
            #"rectangle" : dict(type="static", pydm_widget="PyDMDrawingRectangle"),
            "related display" : self.write_block_related_display,
            #"shell command" : dict(type="static", pydm_widget="PyDMShellCommand"),
            #"strip chart" : dict(type="monitor", pydm_widget="PyDMTimePlot"),
            "text" : self.write_block_text,
            "text entry" : self.write_block_text_entry,
            "text update" : self.write_block_text_update,
            #"valuator" : dict(type="controller", pydm_widget="PyDMLineEdit"),
            #"wheel switch" : dict(type="controller", pydm_widget="PyDMSpinbox"),
            }

        nm = self.get_unique_widget_name(block.symbol.replace(" ", "_"))
        widget_info = adl_symbols.widgets.get(block.symbol)
        if widget_info is not None:
            cls = widget_info["pydm_widget"]
            if cls not in self.custom_widgets:
                self.custom_widgets.append(cls)
        
        handler = handlers.get(block.symbol, self.write_block_default)
        handler(parent, block, nm, widget_info)
        
    def write_block_default(self, parent, block, nm, widget_info):
        cls = "PyDMFrame"     # generic placeholder now
        cls = widget_info["pydm_widget"]
        qw = self.writer.writeOpenTag(parent, "widget", cls=cls, name=nm)
        self.write_geometry(qw, block.geometry)
        self.write_colors(qw, block)
        self.write_tooltip(qw, "TBA widget: " + nm)
        # what styling is effective?
        #self.writer.writeProperty(qw, "frameShape", "QFrame::StyledPanel", tag="enum")
        #self.writer.writeProperty(qw, "frameShadow", "QFrame::Raised", tag="enum")
        #self.writer.writeProperty(qw, "lineWidth", "2", tag="number")
        #self.writer.writeProperty(qw, "midLineWidth", "2", tag="number")
    
    def write_block_image(self, parent, block, nm, widget_info):
        cls = widget_info["pydm_widget"]
        qw = self.writer.writeOpenTag(parent, "widget", cls=cls, name=nm)

        image_name = block.contents.get("image name")
        if image_name is None:
            pass
        
        self.writer.writeProperty(qw, "filename", image_name, tag="string", stdset="0")

        self.write_geometry(qw, block.geometry)
        self.write_colors(qw, block)
        self.write_tooltip(qw, nm)
        
    def write_block_message_button(self, parent, block, nm, widget_info):
        cls = widget_info["pydm_widget"]
        qw = self.writer.writeOpenTag(parent, "widget", cls=cls, name=nm)

        pv = self.get_channel(block.contents["control"])
        
        self.writer.writeProperty(qw, "text", block.title, tag="string")

        self.write_geometry(qw, block.geometry)
        self.write_colors(qw, block)
        self.write_tooltip(qw, nm)
        self.write_channel(qw, pv)  # TODO:block.contents["press_msg"]
    
    def write_block_related_display(self, parent, block, nm, widget_info):
        cls = widget_info["pydm_widget"]
        qw = self.writer.writeOpenTag(parent, "widget", cls=cls, name=nm)
        
        text = block.title or nm
        showIcon = not text.startswith("-")
        text = text.lstrip("-")

        self.write_geometry(qw, block.geometry)
        self.write_colors(qw, block)
        self.write_tooltip(qw, text)
        self.writer.writeProperty(qw, "text", text, tag="string")
        if not showIcon:
            self.writer.writeProperty(qw, "showIcon", "false", tag="bool", stdset="0")
    
    def write_block_text(self, parent, block, nm, widget_info):
        cls = widget_info["pydm_widget"]
        qw = self.writer.writeOpenTag(parent, "widget", cls=cls, name=nm)

        # block.contents["align"] = horiz. right
        
        self.writer.writeProperty(qw, "text", block.title, tag="string")

        self.write_geometry(qw, block.geometry)
        self.write_colors(qw, block)
        self.write_tooltip(qw, nm)
    
    def write_block_text_entry(self, parent, block, nm, widget_info):
        cls = widget_info["pydm_widget"]
        qw = self.writer.writeOpenTag(parent, "widget", cls=cls, name=nm)

        pv = self.get_channel(block.contents["control"])    # TODO: format = string | compact

        self.write_geometry(qw, block.geometry)
        self.write_colors(qw, block)
        self.write_tooltip(qw, "PV: " + pv)
        self.write_channel(qw, pv)
    
    def write_block_text_update(self, parent, block, nm, widget_info):
        cls = widget_info["pydm_widget"]
        qw = self.writer.writeOpenTag(parent, "widget", cls=cls, name=nm)

        pv = self.get_channel(block.contents["monitor"])

        self.write_geometry(qw, block.geometry)
        self.write_colors(qw, block)
        self.write_tooltip(qw, "PV: " + pv)
        self.writer.writeProperty(qw, "readOnly", "true", tag="bool")
        self.write_channel(qw, pv)
    
    def write_channel(self, parent, channel):
        propty = self.writer.writeOpenProperty(parent, "channel", stdset="0")
        # stdset=0 signals this attribute is from PyDM, not Qt widget
        self.writer.writeTaggedString(propty, value="ca://" + channel)
    
    
    def write_colors(self, parent, block):
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
            propty = self.writer.writeOpenProperty(parent, "styleSheet")
            ss = self.writer.writeOpenTag(propty, "string", notr="true")
            ss.text = style
    
    
    def write_customwidgets(self, parent):
        cw_set = self.writer.writeOpenTag(parent, "customwidgets")
        for widget in self.custom_widgets:
            item = pydm_symbols.pydm_custom_widgets.get(widget)
            if item is None:
                continue
            cw = self.writer.writeOpenTag(cw_set, "customwidget")
            self.writer.writeTaggedString(cw, "class", item.cls)
            self.writer.writeTaggedString(cw, "extends", item.extends)
            self.writer.writeTaggedString(cw, "header", item.header)
    
    
    def write_geometry(self, parent, geom):
        propty = self.writer.writeOpenProperty(parent, "geometry")
        rect = self.writer.writeOpenTag(propty, "rect")
        if str(geom.x) == "-":
            _debug_ = True
        self.writer.writeTaggedString(rect, "x", str(geom.x))
        self.writer.writeTaggedString(rect, "y", str(geom.y))
        self.writer.writeTaggedString(rect, "width", str(geom.width))
        self.writer.writeTaggedString(rect, "height", str(geom.height))

    def write_tooltip(self, parent, tip):
        propty = self.writer.writeOpenProperty(parent, "toolTip")
        self.writer.writeTaggedString(propty, value=tip)
    


def main(adl_filename):
    screen = MedmMainWidget(adl_filename)
    buf = screen.getAdlLines(adl_filename)
    screen.parseAdlBuffer(buf)
    
    writer = PydmSupport()
    writer.write_ui(screen)


if __name__ == "__main__":
    for fname in TEST_FILES:
        main(fname)
    print("done")
