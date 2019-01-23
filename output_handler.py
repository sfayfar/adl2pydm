
"""
write the screen in the new protocol
"""

from collections import namedtuple
import logging
import os
from xml.dom import minidom
from xml.etree import ElementTree


FILE_SUFFIX = ".ui"
QT_STYLESHEET_FILE = "stylesheet.qss"
# the stylesheet should be in one of the directories in PYDM_DISPLAYS_PATH
ENV_PYDM_DISPLAYS_PATH = "PYDM_DISPLAYS_PATH"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
        self.file_suffix = FILE_SUFFIX
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
            z.text = widget.text

        # ElementTree needs help to pretty print
        # (easier in lxml but that's an additional package to add)
        text = ElementTree.tostring(self.root)
        xmlstr = minidom.parseString(text).toprettyxml(indent=" "*2)
        with open(self.outFile, "w") as f:
            f.write(xmlstr)

    def writeProperty(self, parent, name, value, tag="string"):
        prop = self.writeOpenTag(parent, "property", name=name)
        self.writeTaggedString(prop, value, tag)
        return prop
    
    def writeOpenProperty(self, parent, name):
        prop = self.writeOpenTag(parent, "property", name=prop)
        return prop
    
    def writeTaggedString(self, parent, value, tag="string"):
        element = ElementTree.SubElement(parent, tag)
        element.text = value
        return element

    def writeCloseProperty(self):
        pass        # nothing to do

    def writeStyleSheet(self, parent, r, g, b):
        # TODO: needed by PyDM?
        prop = self.writeOpenProperty(parent, name="styleSheet")
        
        fmt = "\n\nQWidget#centralWidget {background: rgba(%d, %d, %d, %d;}\n\n"
        color = fmt % (r, g, b, 255)
        self.writeTaggedString(prop, color)

    def writeOpenTag(self, parent, tag, cls="", name=""):
        if parent is None:
            msg = "writeOpenTag(): parent is None, cannot continue"
            raise ValueError(msg)
        element = ElementTree.SubElement(parent, tag)
        if len(cls) > 0 and len(name)>0:
            element.attrib["class"] = cls
            element.attrib["name"] = name
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


def test1():
    writer = PYDM_Writer(None)
    writer.openFile("test.xml")
    writer.widget_stacking_info.append(Qt_zOrder("widget_0", 2, 1))
    writer.widget_stacking_info.append(Qt_zOrder("widget_1", -3, 1))
    writer.widget_stacking_info.append(Qt_zOrder("widget_2", 2, 1))
    writer.closeFile()


def test2():
    writer = PYDM_Writer(None)
    root = writer.openFile("test.xml")
    writer.writeProperty(root, "example", "text value")
    writer.writeProperty(root, "another_example", "upper", "enum")
    sub = root
    for i in range(4):
        sub = writer.writeOpenTag(sub, "onion")
    writer.closeFile()


# if __name__ == "__main__":
#     test2()
