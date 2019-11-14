
"""
write the screen in the new XML protocol

Only rely on packages in the standard Python distribution. (rules out lxml)
"""

from collections import namedtuple
import json
import logging
import os
from xml.dom import minidom
from xml.etree import ElementTree

from . import symbols


QT_STYLESHEET_FILE = "stylesheet.qss"
# the stylesheet should be in one of the directories in PYDM_DISPLAYS_PATH
ENV_PYDM_DISPLAYS_PATH = "PYDM_DISPLAYS_PATH"
SCREEN_FILE_EXTENSION = ".ui"

logger = logging.getLogger(__name__)


def jsonDecode(src):
    "reads rules json text from .ui file"
    return json.loads(src)


def jsonEncode(rules):
    "writes rules as json text for .ui file"
    return json.dumps(rules)


def convertMacros(macros):
    """
    convert $(P)$(M) to ${P}${M}
    """
    return macros.replace("(", "{").replace(")", "}")


def replaceExtension(filename):
    """
    convert filename.adl to filename.ui
    """
    return os.path.splitext(filename)[0] + SCREEN_FILE_EXTENSION


def convertDynamicAttribute_to_Rules(attr):
    """
    interpret MEDM's "dynamic attribute" into PyDM's "rules"

    note difference in macro expression:

    ====  ======
    tool  macro
    ====  ======
    MEDM  `$(P)`
    PyDM  `${P}`
    ====  ======
    """
    rule = dict(name="rule_0", property="Visible")
    channels = []
    for nm in "chan chanB chanC chanD".split():
        if nm not in attr:
            break
        pv = convertMacros(attr[nm])
        channels.append(dict(channel=pv, trigger=len(pv)>0))

    calc = attr.get("calc")
    visibility_calc = {
        "if zero": " == 0",
        "if not zero": " != 0",
        "calc": calc
    }[attr.get("vis", "if not zero")]
    if len(channels) > 0:
        rule["channels"] = channels
        if calc is None:
            calc = "ch[0]" + visibility_calc
    
    # edit the calc expression for known changes
    # FIXME: misses calc="a==0", algorithm needs improvement
    exchanges = {
        "A": "ch[0]",
        "B": "ch[1]",
        "C": "ch[2]",
        "D": "ch[3]",
        "#": "!=",
        "||": "|"
        }
    for k, v in exchanges.items():
        calc = calc.replace(k, v)

    rule["expression"] = calc

    return [rule]


class Widget2Pydm(object):
    """
    convert screen to PyDM structure and write the '.ui' file
    
    NOTES

    describes the PyDM connection to Qt

    example:

        "cls",       "PyDMLineEdit"
        "extends",   "QLineEdit"
        "header",    "pydm.widgets.line_edit"

    """
    
    def __init__(self):
        self.custom_widgets = []
        self.unique_widget_names = {}
        self.pydm_widget_handlers = {
            "arc" : self.write_block_arc,
            #"bar" : dict(type="monitor", pydm_widget="PyDMDrawingRectangle"),
            "byte" : self.write_block_byte_indicator,
            "cartesian plot" : self.write_block_cartesian_plot,
            "choice button" : self.write_block_choice_button,
            "composite" : self.write_block_composite,
            "embedded display" : self.write_block_embedded_display,
            "image" : self.write_block_image,
            "indicator" : self.write_block_indicator,
            "menu" : self.write_block_menu,
            "message button" : self.write_block_message_button,
            "meter" : self.write_block_meter,
            #"oval" : dict(type="static", pydm_widget="PyDMDrawingEllipse"),
            #"polygon" : dict(type="static", pydm_widget="PyDMDrawingPolygon"),
            "polyline" : self.write_block_polyline,
            "rectangle" : self.write_block_rectangle,
            "related display" : self.write_block_related_display,
            "shell command" : self.write_block_shell_command,
            "strip chart" : self.write_block_strip_chart,
            "text" : self.write_block_text,
            "text entry" : self.write_block_text_entry,
            "text update" : self.write_block_text_update,
            "valuator" : self.write_block_valuator,
            "wheel switch" : self.write_block_wheel_switch,
            }
    
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
            pv = convertMacros(pv)
        return pv

    def processDynamicAttributeAsRules(self, widget, block):
        attr = block.contents.get("dynamic attribute", {})
        if len(attr) > 0:
            # see: http://slaclab.github.io/pydm/widgets/widget_rules/index.html
            rules = convertDynamicAttribute_to_Rules(attr)
            json_rules = jsonEncode(rules)
            self.writer.writeProperty(widget, "rules", json_rules, stdset="0")
        
    def write_basic_attribute(self, parent, block, nm, qw):
        attr = block.contents.get("basic attribute")
        if attr is None:
            return
        propty = self.writer.writeOpenProperty(qw, "brush", stdset="0")
        fill = dict(
            solid = "SolidPattern", 
            outline = "NoBrush")[attr.get("fill", "solid")]
        brush = self.writer.writeOpenTag(propty, "brush", brushstyle=fill)
        self.write_color_element(brush, block.color, alpha="255")

        propty = self.writer.writeOpenProperty(qw, "penStyle", stdset="0")
        pen = dict(
            solid = "Qt::SolidLine",
            dash = "Qt::DashLine"
        )[attr.get("style", "solid")]
        self.writer.writeTaggedString(propty, "enum", pen)

        propty = self.writer.writeOpenProperty(qw, "penColor", stdset="0")
        self.write_color_element(propty, block.color)

        propty = self.writer.writeOpenProperty(qw, "penWidth", stdset="0")
        width = attr.get("width", 0)
        if fill == "NoBrush":
            width = max(1, float(width))   # make sure the outline is seen
        self.writer.writeTaggedString(propty, "double", str(width))

        block.color = None

    def write_block(self, parent, block):
        nm = self.get_unique_widget_name(block.symbol.replace(" ", "_"))

        if (block.symbol == "composite" 
                and len(block.widgets) == 0 
                and "composite file" in block.contents):
            block.symbol = "embedded display"

        widget_info = symbols.adl_widgets.get(block.symbol)
        if widget_info is not None:
            cls = widget_info["pydm_widget"]
            if cls not in self.custom_widgets:
                self.custom_widgets.append(cls)

        handler = self.pydm_widget_handlers.get(block.symbol, self.write_block_default)
        cls = widget_info["pydm_widget"]
        # if block.symbol.find("chart") >= 0:
        #     _z = 2
        # TODO: PyDMDrawingMMM (Line, Polygon, Oval, ...) need more decisions here 
        qw = self.writer.writeOpenTag(parent, "widget", cls=cls, name=nm)
        self.write_geometry(qw, block.geometry)
        # self.write_colors_style(qw, block)
        logger.debug("(#%d) %s: %s" % (block.line_offset, block.symbol, nm))
        handler(parent, block, nm, qw)

    def write_color_element(self, xml_element, color, **kwargs):
        if color is not None:
            item = self.writer.writeOpenTag(xml_element, "color", **kwargs)
            self.writer.writeTaggedString(item, "red", str(color.r))
            self.writer.writeTaggedString(item, "green", str(color.g))
            self.writer.writeTaggedString(item, "blue", str(color.b))
        
    def write_dynamic_attribute(self, parent, block, nm, qw):
        attr = block.contents.get("dynamic attribute")
        if attr is None:
            return
        self.processDynamicAttributeAsRules(qw, block)
    
    def write_ui(self, screen, output_path):
        """main entry point to write the .ui file"""
        title = screen.title or os.path.split(os.path.splitext(screen.given_filename)[0])[-1]
        ui_filename = os.path.join(output_path, title + SCREEN_FILE_EXTENSION)
        self.writer = PYDM_Writer(None)

        root = self.writer.openFile(ui_filename)
        logging.info("writing screen file: " + ui_filename)
        self.writer.writeTaggedString(root, "class", title)
        form = self.writer.writeOpenTag(root, "widget", cls="QWidget", name="screen")
        
        self.write_geometry(form, screen.geometry)
        self.write_colors_style(form, screen)
    
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
    
    def writePropertyBoolean(self, widget, tag, value, **kwargs):
        self.writer.writeProperty(widget, tag, str(value).lower(), tag="bool", **kwargs)
    
    def writePropertyTextAlignment(self, widget, attr):
        align =  {
            "horiz. left": "Qt::AlignLeading|Qt::AlignLeft|Qt::AlignVCenter",
            "horiz. centered" : "Qt::AlignCenter",
            "horiz. right" : "Qt::AlignRight|Qt::AlignTrailing|Qt::AlignVCenter",
            "justify" : "Qt::AlignJustify|Qt::AlignVCenter",
        }[attr.get("align", "horiz. left")]
        self.writer.writeProperty(widget, "alignment", align, tag="set")
    
    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
        
    def write_block_default(self, parent, block, nm, qw):
        self.write_tooltip(qw, "TBA widget: " + nm)
        self.write_basic_attribute(parent, block, nm, qw)
        self.write_dynamic_attribute(parent, block, nm, qw)
        # what styling is effective?
        #self.writer.writeProperty(qw, "frameShape", "QFrame::StyledPanel", tag="enum")
        #self.writer.writeProperty(qw, "frameShadow", "QFrame::Raised", tag="enum")
        #self.writer.writeProperty(qw, "lineWidth", "2", tag="number")
        #self.writer.writeProperty(qw, "midLineWidth", "2", tag="number")

    def write_block_arc(self, parent, block, nm, qw):
        self.write_basic_attribute(parent, block, nm, qw)
        self.write_dynamic_attribute(parent, block, nm, qw)

        beginAngle = block.contents.get("beginAngle", 0)
        pathAngle = block.contents.get("pathAngle", 0)

        if beginAngle != 0:
            self.writer.writeProperty(
                qw, 
                "startAngle", 
                str(beginAngle),
                tag="double", 
                stdset="0")
        if pathAngle != 0:
            self.writer.writeProperty(
                qw, 
                "spanAngle", 
                str(-pathAngle),
                tag="double", 
                stdset="0")

    def write_block_byte_indicator(self, parent, block, nm, qw):
        direction = block.contents.get("direction", "right")
        ebit = int(block.contents.get("ebit", 0))
        sbit = int(block.contents.get("sbit", 0))
        numBits = 1 + max(ebit, sbit) - min(ebit, sbit)
        if numBits < 1:
            wmsg = "number of bits = %d" % numBits
            logger.warning(wmsg)

        self.write_tooltip(qw, nm)
        pv = self.get_channel(block.contents["monitor"])
        self.write_channel(qw, pv)

        color = self.writer.writeOpenProperty(qw, "onColor", stdset="0")
        self.write_color_element(color, block.color)
        color = self.writer.writeOpenProperty(qw, "offColor", stdset="0")
        self.write_color_element(color, block.background_color)
        block.color = None
        block.background_color = None

        orientation = {"right": "Qt::Horizontal", "down": "Qt::Vertical"}[direction]
        self.writer.writeProperty(qw, "orientation", orientation, stdset="0")
        self.writePropertyBoolean(qw, "showLabels", False, stdset="0")
        self.writePropertyBoolean(qw, "bigEndian", sbit < ebit, stdset="0")
        self.writer.writeProperty(qw, "numBits", numBits, tag="number", stdset="0")
        
    def write_block_choice_button(self, parent, block, nm, qw):
        pv = self.get_channel(block.contents["control"])
        self.write_tooltip(qw, pv)
        self.write_channel(qw, pv)
        self.write_colors_style(qw, block)
        
    def write_block_cartesian_plot(self, parent, block, nm, qw):
        """
        Could be either PyDMWaveformPlot or PyDMScatterPlot
        """
        logger.debug("line %d in file: %s" % (block.line_offset, block.main.given_filename))
        logger.debug("contents:\n" + json.dumps(block.contents, indent=2))
        self.write_tooltip(qw, nm)
        self.writer.writeProperty(qw, "title", block.title, stdset="0")

        if len(block.contents["traces"]) > 0:
            prop = self.writer.writeOpenProperty(qw, "curves", stdset="0")
            stringlist = self.writer.writeOpenTag(prop, "stringlist")

            # count: n where plot last n pts or plot n pts & stop
            count = block.contents.get("count")
            if count is not None:
                count = int(count)

            text = block.contents.get("xlabel")
            if text is not None:
                self.writer.writeProperty(qw, "xLabels", text)
            text = block.contents.get("ylabel")
            if text is not None:
                self.writer.writeProperty(qw, "yLabels", text)

            for v in block.contents["traces"]:
                c = v["color"]
                trace = dict(
                    color = "#%02x%02x%02x" % (c.r, c.g, c.b),
                    lineStyle = 1,          # NoLine Solid Dash Dot DashDot DashDotDot
                    # "lineWidth": 1,       # TODO:
                    # "symbol": null,       # TODO:
                    # "symbolSize": 10,     # TODO:
                    # "redraw_mode": 2      # TODO:
                )
                names = []
                if "xdata" in v:
                    trace["x_channel"] = "ca://" + v["xdata"]
                    names.append("x=" + v["xdata"])
                if "ydata" in v:
                    trace["y_channel"] = "ca://" + v["ydata"]
                    names.append("y=" + v["ydata"])
                trace["name"] = ", ".join(names)

                if block.contents["style"] == "point":
                    trace["symbol"] = 1  # Circle
                    trace["symbolSize"] = 10
                elif block.contents["style"] == "line":
                    trace["lineStyle"] = 1  # Solid
                elif block.contents["style"] == "fill-under":
                    # TODO: improve?  fill-under not available in PyDM
                    trace["lineStyle"] = 1  # Solid
                
                if count is not None:
                    trace["block_size"] = count

                # x_axis y1_axis y2_axis: might have rangeStyle="auto-scale"
                for item in "x_axis y1_axis y2_axis".split():
                    if item in block.contents:
                        # TODO:
                        logger.warning("block.contents['%s'] not handled" % item)
                self.writeStringText(stringlist, text=jsonEncode(trace))

    def write_block_composite(self, parent, block, nm, qw):
        # self.write_tooltip(qw, nm)
        self.write_dynamic_attribute(parent, block, nm, qw)
        for widget in block.widgets:
            self.write_block(qw, widget)

    def write_block_embedded_display(self, parent, block, nm, qw):
        self.write_tooltip(qw, nm)
        # has block.contents["composite file"] and block.contents["composite name"]
        # Note: composite file is a list delimited by ";"
        filelist = block.contents["composite file"].split(";")
        macros = None
        if len(filelist) != 1:
            if len(filelist) < 1:
                emsg = "'composite file' list was empty"
                emsg += " (file: %s, line %d)" % (block.main.given_filename, block.line_offset)
                logger.error(emsg)
                return
            elif len(filelist) == 2:
                macros = convertMacros(filelist[1])
            else:
                emsg = "Rendering only first file from 'composite file'"
                emsg += "=%s" % block.contents["composite file"]
                emsg += " (file: %s, line %d)" % (block.main.given_filename, block.line_offset)
                logger.warning(emsg)
        filename = replaceExtension(filelist[0])
        self.writer.writeProperty(qw, "filename", filename, stdset="0")
        if macros is not None:
            macros = convertMacros(macros)
            self.writer.writeProperty(qw, "macros", convertMacros(macros), stdset="0")
    
    def write_block_image(self, parent, block, nm, qw):
        image_name = block.contents.get("image name")
        self.writer.writeProperty(qw, "filename", image_name, tag="string", stdset="0")
        self.write_dynamic_attribute(parent, block, nm, qw)
        self.write_tooltip(qw, nm)
        
    def write_block_indicator(self, parent, block, nm, qw):
        """
        Also known as an Indicator.  
        The scale monitor has attributes:
        
        * Object (X Position, Y Position, Width, Height)
        * Monitor (Readback Channel, Foreground, Background)
        * Limits (Low Limit, High Limit, Precision)
        * Label
        * Direction
        * Color Mode
        
        The Scale Monitor displays the value of the process variable on a scale.  
        The limits of the scale are the HOPR and LOPR values for the record 
        associated with the process variable by default but may be set via 
        the PV Limits Dialog Box.

        The Meter has attributes:
        
        * Object (X Position, Y Position, Width, Height)
        * Monitor (Readback Channel, Foreground, Background)
        * Limits (Low Limit, High Limit, Precision)
        * Label
        * Color Mode
        
        It displays the value of the process variable on a meter with a dial.
        """
        pv = self.get_channel(block.contents["monitor"])
        self.write_tooltip(qw, pv)
        self.write_channel(qw, pv)

        precision = block.contents.get("precision")        # TODO: needs an example from .adl
        if precision is not None:
            logger.warning("precision needs an example .adl file")

        if (
            block.contents.get("hoprSrc") == "default"
            or 
            block.contents.get("loprSrc") == "default"
        ):
            self.writePropertyBoolean(qw, "limitsFromChannel", False, stdset="0")
            self.writer.writeProperty(
                qw, 
                "userUpperLimit", 
                block.contents.get("hoprDefault", str(0.0)), 
                tag="double", 
                stdset="0")
            self.writer.writeProperty(
                qw, 
                "userLowerLimit", 
                block.contents.get("loprDefault", str(0.0)), 
                tag="double", 
                stdset="0")
        
    def write_block_menu(self, parent, block, nm, qw):
        pv = self.get_channel(block.contents["control"])
        self.write_channel(qw, pv)
        self.write_tooltip(qw, pv)
        self.write_colors_style(qw, block)
        
    def write_block_message_button(self, parent, block, nm, qw):
        pv = self.get_channel(block.contents["control"])
        self.writer.writeProperty(qw, "text", block.title, tag="string")
        self.write_tooltip(qw, pv)
        self.write_channel(qw, pv)  
        msg = block.contents.get("press_msg")
        if msg is not None:
            self.writer.writeProperty(qw, "pressValue", msg, stdset="0")
        self.write_colors_style(qw, block)
        
    def write_block_meter(self, parent, block, nm, qw):
        # handle same as indicator since PyDM does not have a meter widget
        self.write_block_indicator(parent, block, nm, qw)
        
    def write_block_polyline(self, parent, block, nm, qw):
        # TODO: PyDM widget choice needs help here
        # this gets interesting because of the number points required for each PyDMDrawingMMM widget
        self.write_tooltip(qw, nm)

    def write_block_rectangle(self, parent, block, nm, qw):
        self.write_basic_attribute(parent, block, nm, qw)
        self.write_dynamic_attribute(parent, block, nm, qw)
        self.write_tooltip(qw, nm)

    def write_block_related_display(self, parent, block, nm, qw):
        text = block.title or nm
        showIcon = not text.startswith("-")
        text = text.lstrip("-")
        self.write_tooltip(qw, text)
        self.writer.writeProperty(qw, "text", text, tag="string")
        if not showIcon:
            self.writePropertyBoolean(qw, "showIcon", False, stdset="0")
        self.write_colors_style(qw, block)
        if hasattr(block, "displays"):
            displays = {
                "titles" : [d.get("label", "") for d in block.displays],
                "filenames" : [replaceExtension(d.get("name", "")) for d in block.displays],
                "macros" : [convertMacros(d.get("args", "")) for d in block.displays]
            }
            for tag, items in displays.items():
                prop = self.writer.writeOpenProperty(qw, tag, stdset="0")
                stringlist = self.writer.writeOpenTag(prop, "stringlist")
                for v in items:
                    self.writeStringText(stringlist, text=v)

        # # TODO: conditional
        # self.writePropertyBoolean(qw, "showIcon", True)
        # self.writePropertyBoolean(qw, "openInNewWindow", True)
    
    def write_block_shell_command(self, parent, block, nm, qw):
        self.write_tooltip(qw, nm)
        # TODO: block.commands is a list
        
    def write_block_strip_chart(self, parent, block, nm, qw):
        self.write_tooltip(qw, nm)
        self.writer.writeProperty(qw, "title", block.title, stdset="0")
        if "period" in block.contents:
            logger.warning("block.contents['%s'] not handled" % "period")
            # TODO: block.contents["period"]
            # The period is the time between updates (s)

        if len(block.contents["pens"]) > 0:
            text = block.contents.get("xlabel")
            if text is not None:
                self.writer.writeProperty(qw, "xLabels", text)
            text = block.contents.get("ylabel")
            if text is not None:
                self.writer.writeProperty(qw, "yLabels", text)

            prop = self.writer.writeOpenProperty(qw, "curves", stdset="0")
            stringlist = self.writer.writeOpenTag(prop, "stringlist")
            for v in block.contents["pens"]:
                c = v["color"]
                trace = dict(
                    color = "#%02x%02x%02x" % (c.r, c.g, c.b),
                    # MEDM only supports Solid line with color, width=1
                    lineStyle = 1,          # NoLine Solid Dash Dot DashDot DashDotDot
                    lineWidth = 1,
                )
                if "chan" in v:
                    trace["channel"] = "ca://" + v["chan"]
                    trace["name"] = v["chan"]

                self.writeStringText(stringlist, text=jsonEncode(trace))

    def write_block_text(self, parent, block, nm, qw):
        text = block.title
        if block.title is not None:
            text = convertMacros(block.title)
        self.writer.writeProperty(qw, "text", text, tag="string")
        self.write_basic_attribute(parent, block, nm, qw)
        self.write_dynamic_attribute(parent, block, nm, qw)
        self.write_tooltip(qw, nm)
        self.writePropertyTextAlignment(qw, block.contents)
    
    def write_block_text_entry(self, parent, block, nm, qw):
        pv = self.get_channel(block.contents["control"])    # TODO: format = string | compact
        self.write_channel(qw, pv)
        self.write_tooltip(qw, pv)
        self.write_colors_style(qw, block)
    
    def write_block_text_update(self, parent, block, nm, qw):
        pv = self.get_channel(block.contents["monitor"])
        self.write_tooltip(qw, "PV: " + pv)
        self.writePropertyTextAlignment(qw, block.contents)
        self.writer.writeProperty(
            qw, 
            "textInteractionFlags", 
            "Qt::TextSelectableByKeyboard|Qt::TextSelectableByMouse",
            tag="set")
        self.write_channel(qw, pv)
        self.write_colors_style(qw, block)
        
    def write_block_valuator(self, parent, block, nm, qw):
        pv = self.get_channel(block.contents["control"])
        self.write_channel(qw, pv)
        self.write_tooltip(qw, pv)
        item = "dPrecision"
        if item in block.contents:
            logger.warning("block.contents['%s'] not handled" % item)
        # TODO:

    def write_block_wheel_switch(self, parent, block, nm, qw):
        pv = self.get_channel(block.contents["control"])
        self.write_channel(qw, pv)
        self.write_tooltip(qw, pv)

    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

    def write_channel(self, parent, channel):
        logger.debug("PV channel: " + channel)
        propty = self.writer.writeOpenProperty(parent, "channel", stdset="0")
        # stdset=0 signals this attribute is from PyDM, not Qt widget
        self.writer.writeTaggedString(
            propty, 
            value="ca://" + convertMacros(channel))
    
    def write_colors_style(self, parent, block):
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
            item = symbols.pydm_widgets.get(widget)
            if item is None:
                continue
            cw = self.writer.writeOpenTag(cw_set, "customwidget")
            self.writer.writeTaggedString(cw, "class", item.cls)
            self.writer.writeTaggedString(cw, "extends", item.extends)
            self.writer.writeTaggedString(cw, "header", item.header)
    
    def write_geometry(self, parent, geom):
        propty = self.writer.writeOpenProperty(parent, "geometry")
        rect = self.writer.writeOpenTag(propty, "rect")
        # if str(geom.x) == "-":
        #     _debug_ = True
        self.writer.writeTaggedString(rect, "x", str(geom.x))
        self.writer.writeTaggedString(rect, "y", str(geom.y))
        self.writer.writeTaggedString(rect, "width", str(geom.width))
        self.writer.writeTaggedString(rect, "height", str(geom.height))

    def writeStringText(self, parent, tag="string", text=""):
        s = self.writer.writeOpenTag(parent, tag)
        s.text = text
        return s
        
    def write_tooltip(self, parent, tip):
        propty = self.writer.writeOpenProperty(parent, "toolTip")
        self.writer.writeTaggedString(propty, value=tip)


"""
control the stacking order of Qt widgets - important!

Sets the stacking order of sibling items. 
By default the stacking order is 0.

* Items with a higher stacking value are drawn
    on top of siblings with a lower stacking order. 
* Items with the same stacking value are drawn 
    bottom up in the order they appear. 
* Items with a negative stacking value are drawn 
    under their parent's content.
    
PARAMS

order (int) :
    sorting order

vis (int) :
    is this widget visible?

text (str) :
    the text content

Example how the zorder is given in the .ui file:

    <zorder>caRectangle_0</zorder>
    <zorder>caRectangle_1</zorder>
    <zorder>caLabel_0</zorder>
    <zorder>caLabel_1</zorder>
    ...
"""    
Qt_zOrder = namedtuple('Qt_zOrder', 'order vis text')


class PYDM_Writer(object):
    """
    write the screen description to a PyDM .ui file
    """

    def __init__(self, adlParser):
        self.adlParser = adlParser
        self.filename = None
        self.path = None
        self.file_suffix = SCREEN_FILE_EXTENSION
        self.stylesheet = None
        self.root = None
        self.outFile = None
        self.widget_stacking_info = []        # stacking order
    
    def openFile(self, outFile):
        """actually, begin to create the .ui file content IN MEMORY"""
        if os.environ.get(ENV_PYDM_DISPLAYS_PATH) is None:
            msg = "Environment variable %s is not defined." % "PYDM_DISPLAYS_PATH"
            logger.info(msg)

        sfile = findFile(QT_STYLESHEET_FILE)
        if sfile is None:
            msg = "file not found: " + QT_STYLESHEET_FILE
            logger.info(msg)
        else:
            with open(sfile, "r") as fp:
                self.stylesheet = fp.read()
                msg = "Using stylesheet file in .ui files: " + sfile
                msg += "\n  unset %d to not use any stylesheet" % ENV_PYDM_DISPLAYS_PATH
                logger.info(msg)
        
        # adl2ui opened outFile here AND started to write XML-like content
        # that is not necessary now
        if os.path.exists(outFile):
            msg = "output file already exists: " + outFile
            logger.info(msg)
        self.outFile = outFile
        
        # Qt .ui files are XML, use XMl tools to create the content
        # create the XML file root element
        self.root = ElementTree.Element("ui", attrib=dict(version="4.0"))
        # write the XML to the file in the close() method
        
        return self.root

    def closeFile(self):
        """finally, write .ui file (XML content)"""
        
        def sorter(widget):
            return widget.order
            
        # sort widgets by the order we had when parsing
        for widget in sorted(self.widget_stacking_info, key=sorter):
            z = ElementTree.SubElement(self.root, "zorder")
            # TODO: what about "vis" field?
            z.text = str(widget.text)

        # ElementTree needs help to pretty print
        # (easier in lxml but that's an additional package to add)
        text = ElementTree.tostring(self.root)
        xmlstr = minidom.parseString(text).toprettyxml(indent=" "*2)
        with open(self.outFile, "w") as f:
            f.write(xmlstr)

    def writeProperty(self, parent, name, value, tag="string", **kwargs):
        prop = self.writeOpenTag(parent, "property", name=name)
        self.writeTaggedString(prop, tag, value)
        for k, v in kwargs.items():
            prop.attrib[k] = v
        return prop
    
    def writeOpenProperty(self, parent, name, **kwargs):
        prop = self.writeOpenTag(parent, "property", name=name)
        for k, v in kwargs.items():
            prop.attrib[k] = v
        return prop
    
    def writeTaggedString(self, parent, tag="string", value=None):
        element = ElementTree.SubElement(parent, tag)
        if value is not None:
            element.text = str(value)
        return element

    def writeCloseProperty(self):
        pass        # nothing to do

    # def writeStyleSheet(self, parent, r, g, b):
    #     # TODO: needed by PyDM?
    #     prop = self.writeOpenProperty(parent, name="styleSheet")
    #     
    #     fmt = "\n\nQWidget#centralWidget {background: rgba(%d, %d, %d, %d;}\n\n"
    #     color = fmt % (r, g, b, 255)
    #     self.writeTaggedString(prop, value=color)

    def writeOpenTag(self, parent, tag, cls="", name="", **kwargs):
        if parent is None:
            msg = "writeOpenTag(): parent is None, cannot continue"
            raise ValueError(msg)
        element = ElementTree.SubElement(parent, tag)
        if len(cls) > 0:
            element.attrib["class"] = cls
        if len(name) > 0:
            element.attrib["name"] = name
        for k, v in kwargs.items():
            element.attrib[k] = v
        return element

    def writeCloseTag(self, tag):
        pass        # nothing to do

    def writeMessage(self, mess):
        pass        # nothing to do


def findFile(fname):
    """look for file in PYDM_DISPLAYS_PATH"""
    if fname is None or len(fname) == 0:
        return None
    
    if os.name =="nt":
        delimiter = ";"
    else:
        delimiter = ":"

    path = os.environ.get(ENV_PYDM_DISPLAYS_PATH)
    if path is None:
        paths = [os.getcwd()]      # safe choice that becomes redundant
    else:
        paths = path.split(delimiter)

    if os.path.exists(fname):
        # found it in current directory
        return fname
    
    for path in paths:
        path_fname = os.path.join(path, fname)
        if os.path.exists(path_fname):
            # found it in the DISPLAYS path
            return path_fname

    return None
