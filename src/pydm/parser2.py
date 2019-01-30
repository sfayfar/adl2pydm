
"""
read the MEDM .adl file into Python data structures

Parse the file line-by-line. (simpler analysis than the tokenize package)
Only rely on packages in the standard Python distribution. 
"""

from collections import defaultdict, namedtuple
import logging
import os

import adl_symbols


TEST_FILES = [
    "screens/medm/xxx-R5-8-4.adl",
    "screens/medm/xxx-R6-0.adl",
    "screens/medm/motorx-R6-10-1.adl",
    "screens/medm/motorx_all-R6-10-1.adl",
    "screens/medm/scanDetPlot-R2-11-1.adl",
    # "screens/medm/beamHistory_full-R3-5.adl", # this .adl has problems
    "screens/medm/ADBase-R3-3-1.adl",
    "screens/medm/simDetector-R3-3-31.adl",
    ]

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


"""a color used in MEDM"""
Color = namedtuple('Color', 'r g b')

"""MEDM's object block contains the widget geometry"""
Geometry = namedtuple('Geometry', 'x y width height')

"""MEDM's points item: points = [Point]"""
Point = namedtuple('Point', 'x y')


class MEDM_Widget(object):
    """
    describe one widget in the .adl file
    """
    
    def __init__(self, widget_type, adl_file, line, *args, **kwargs):
        self.medm_widget = widget_type
        self.adl_file_name = adl_file
        self.starting_line = line
        self.geometry = Geometry(0, 0, 0, 0)
        self.color = Color(0, 0, 0)
        self.background_color = Color(0, 0, 0)
    
    def __str__(self, *args, **kwargs):
        return "%s(type=\"%s\", line=%d, adl_file=\"%s\")" % (
            type(self).__name__, 
            self.medm_widget,
            self.starting_line,
            self.adl_file_name,
            )


class MEDM_CompositeWidget(MEDM_Widget):
    """
    container for a grouped list of widgets
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets = []


class AdlFile(object):
    """
    describes the root of the .adl file
    """
    
    def __init__(self, filename):
        self.filename = filename    # name given to this code (not the name *in* the file)
        self.color_map = []
        self.attr = {}
        self.nesting = 0
        self.widgets = []

    def parse(self, owner=None, level=0):
        owner = owner or self

        object_catalog = defaultdict(int)
        var_catalog = defaultdict(int)

        with open(self.filename, "r") as fp:
            buf = fp.readlines()
            line = 0
            while line < len(buf):
                text = buf[line].rstrip()
                if text.endswith("{"):
                    self.nesting += 1
                    key = text[:-1].strip().lstrip('"').rstrip('"')
                    if key in adl_symbols.widgets:
                        if key == "composite":
                            widget = MEDM_CompositeWidget(key, self.filename, line)
                            # TODO: self.parse(widget, level +1)
                        else:
                            widget = MEDM_Widget(key, self.filename, line)
                        owner.widgets.append(widget)
                        logging.debug("%d : %s  - widget (nesting=%d)" % (line, key, self.nesting))
                    elif key in adl_symbols.blocks:
                        object_catalog[key] += 1
                        logging.debug("%d : %s  - open block (nesting=%d)" % (line, key, self.nesting))
                    else:
                        key_start = key.split("[")[0] + "["
                        if key_start in adl_symbols.block_lists:
                            object_catalog[key] += 1
                            logging.debug("%d : %s  - open block list (nesting=%d)" % (line, key, self.nesting))
                        else:
                            msg = "%d : %s  - not recognized (nesting=%d)" % (line, key, self.nesting)
                            logger.warn(msg)
                            raise RuntimeError(msg)
    
                elif text.endswith("}"):
                    logging.debug("%d : close block (nesting=%d)" % (line, self.nesting))
                    self.nesting -= 1
    
                elif text.endswith(","):
                    logging.debug("%d : list (color map color)" % line)
    
                elif text.endswith(")") and text.lstrip().startswith("("):
                    logging.debug("%d : tuple" % line)
    
                elif text.find("=") >= 0:
                    logging.debug("%d : assignment" % line)
                    text = text.strip()
                    key = text[:text.find("=")].lstrip('"').rstrip('"')
                    var_catalog[key] += 1
    
                elif len(text.strip()) == 0:
                    logging.debug("%d : empty" % line)
    
                else:
                    logging.debug("%d : unrecognized: |%s|" % (line, text))

                line += 1
    
        # TODO: refactor from MEDM into some standard forms
        #     convert from colors index to Color() objects
        #     object geometry
        #     visibility
        #     other attributes

        for catalog in (object_catalog, var_catalog):
            logger.debug("#"*40)
            for k, v in sorted(catalog.items()):
                logger.debug("%d\t%s" % (v, k))


class MedmWidget(object):
    """
    """
    
    def __init__(self, parent, widget_type):
        self.parent = parent
        self.widget_type = widget_type.strip()
        self.background_color = None
        self.color = None
        self.geometry = None
        self.attr = {}
    
    def __str__(self, *args, **kwargs):
        return "%s(type=\"%s\")" % (type(self).__name__, self.widget_type)


class MedmCompositeWidget(object):
    """
    """
    widgets = []


if __name__ == "__main__":
    for fname in TEST_FILES:
        adl = AdlFile(fname)
        adl.parse()
    print("done")
