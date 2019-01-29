
"""
read the MEDM .adl file into Python data structures

Parse the file line-by-line. (simpler analysis than the tokenize package)
Only rely on packages in the standard Python distribution. 
"""

from collections import defaultdict, namedtuple
import logging
import os


TEST_FILES = [
    "screens/medm/xxx-R5-8-4.adl",
    "screens/medm/xxx-R6-0.adl",
    "screens/medm/motorx-R6-10-1.adl",
    "screens/medm/motorx_all-R6-10-1.adl",
    "screens/medm/scanDetPlot-R2-11-1.adl",
    "screens/medm/beamHistory_full-R3-5.adl",
    ]

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


"""a color used in MEDM"""
Color = namedtuple('Color', 'r g b')

"""MEDM's object block contains the widget geometry"""
Geometry = namedtuple('Geometry', 'x y width height')

"""MEDM's points item: points = [Point]"""
Point = namedtuple('Point', 'x y')


ATTRIBUTE_BLOCK_NAMES = [
    "basic attribute",      #
    "color map",            # color table
    "colors",               # color specification
    "control",              # PV and visibility of control (rw) widget
    "display",              # parameters of main window
    "dynamic attribute",    # calculated widget visibility
    "file",                 # designer's file name and version
    "limits",               #
    "monitor",              # PV and visibility of monitor (ro) widget
    "object",               # geometry
    "points",               # widget vertices
    ]


class AdlFile(object):
    """
    """
    
    def __init__(self, filename):
        self.filename = filename    # name given to this code (not the name *in* the file)
        self.color_map = []
        self.attr = {}
        self.nesting = 0

    def parse(self, owner=None, level=0):
        owner = owner or self

        object_catalog = defaultdict(int)
        var_catalog = defaultdict(int)

        with open(self.filename, "r") as fp:
            for line, text in enumerate(fp.readlines()):
                text = text.rstrip()
                if text.endswith("{"):
                    self.nesting += 1
                    key = text[:-1].strip().lstrip('"').rstrip('"')
                    if key not in ATTRIBUTE_BLOCK_NAMES:
                        object_catalog[key] += 1
                    is_attr = str(key in ATTRIBUTE_BLOCK_NAMES)
                    logging.debug("%d : %s  - open block (nesting=%d attribute=%s)" % (line, key, self.nesting, is_attr))
    
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
    adl = AdlFile(TEST_FILES[0])
    adl.parse()
    print("done")
