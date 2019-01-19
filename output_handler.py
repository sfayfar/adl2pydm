
"""
write the screen in the new protocol
"""

import os
from xml.dom import minidom
from xml.etree import ElementTree


FILE_SUFFIX = ".ui"
QT_STYLESHEET_FILE = "stylesheet.qss"
# the stylesheet should be in one of the directories in PYDM_DISPLAYS_PATH
ENV_PYDM_DISPLAYS_PATH = "PYDM_DISPLAYS_PATH"


class Qt_zOrder:
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
    
    Example how the zorder is given in the .ui file:

        <zorder>caRectangle_0</zorder>
        <zorder>caRectangle_1</zorder>
        <zorder>caLabel_0</zorder>
        <zorder>caLabel_1</zorder>
        ...
    """    
    
    def __init__(self, text, order, vis):
        self.order = order  # sorting order
        self.vis = vis      # is this widget visible?
        self.text = text    # the text content


class PYDM_Writer(object):
    """
    write the screen description to a PyDM .ui file
    """

    def __init__(self):
        self.filename = None
        self.path = None
        self.file_suffix = FILE_SUFFIX
        self.stylesheet = None
        self.root = None
        self.outFile = None
        self.widget_stacking_info = []        # stacking order
    
    def openTag(self):
        raise NotImplemented
    
    def openFile(self, outFile):
        """actually, begin to create the .ui file content IN MEMORY"""
        if os.environ.get(ENV_PYDM_DISPLAYS_PATH) is None:
            msg = "Environment variable %s is not defined." % "PYDM_DISPLAYS_PATH"
            print(msg)      # TODO: use logger instead of print()

        sfile = findFile(QT_STYLESHEET_FILE)
        if sfile is None:
            msg = "file not found: " + QT_STYLESHEET_FILE
            print(msg)      # TODO: use logger instead of print()
        else:
            with open(sfile, "r") as fp:
                self.stylesheet = fp.read()
                msg = "Using stylesheet file in .ui files: " + sfile
                msg += "\n  unset %d to not use any stylesheet" % ENV_PYDM_DISPLAYS_PATH
                print(msg)      # TODO: use logger instead of print()
        
        # adl2ui opened outFile here AND started to write XML-like content
        # that is not necessary now
        if os.path.exists(outFile):
            msg = "output file already exists: " + outFile
            print(msg)      # TODO: use logger instead of print()
        self.outFile = outFile
        
        # Qt .ui files are XML, use XMl tools to create the content
        # create the XML file root element
        self.root = ElementTree.Element("ui", attrib=dict(version="4.0"))
        # write the XML to the file in the close() method

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

    def writeProperty(name, type, value): pass
    def writeOpenProperty(name): pass
    def writeTaggedString(type, value): pass
    def writeCloseProperty(): pass
    def writeStyleSheet(r, g, b): pass

    def writeOpenTag(type, cls = "", name = ""): pass
    def writeCloseTag(type): pass
    def test(): pass
    def Init(adlParser): pass
    def writeMessage(mess): pass


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
    writer = PYDM_Writer()
    writer.openFile("test.xml")
    writer.widget_stacking_info.append(Qt_zOrder("widget_0", 2, 1))
    writer.widget_stacking_info.append(Qt_zOrder("widget_1", -3, 1))
    writer.widget_stacking_info.append(Qt_zOrder("widget_2", 2, 1))
    writer.closeFile()


# if __name__ == "__main__":
#     test1()
