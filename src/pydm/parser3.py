#!/usr/bin/env python

"""
read the MEDM .adl file into Python data structures

Parse the file by blocks.
Only rely on packages in the standard Python distribution. 

MEDM's .adl files are divided into a list of blocks where 
each block is structured thus::

    symbol {
        contents
    }

The symbol is given without double quotes if it has not
embedded white space.  Otherwise, double quotes surround the
symbol.

The *contents* are a list of block(s) and assignment(s) or values.
An *assignment* is structured:  ``symbol=value``
A *value* is a number, text surrounded by double quotes, 
or a list of values surrounded by parentheses.

Three special blocks come at the start of the MEDM file: 
file, display, and "color map".  The remaining blocks at 
the main screen level (0) correspond to GUI widgets or, in the case of 
*composite*, a list of widgets that are grouped.

Other blocks are used to provide configuration for their 
parent GUI widget.
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
    "screens/medm/beamHistory_full-R3-5.adl", # this .adl has problems
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


class Block(object):
    """ADL file block structure"""
    
    def __init__(self, start, end, level, symbol):
        self.start = start
        self.end = end
        self.level = level
        self.symbol = symbol
    
    def __str__(self):
        fmt = "Block: %d:%d:%d %s"
        return fmt % (self.level, self.start, self.end, str(self.symbol))


class MedmBaseWidget(object):
    
    def __init__(self):
        self.background_color = None
        self.color = None
        self.geometry = None
    
    def parseAdlBuffer(self, parser, buf):
        text = "".join(buf)
        pass


class MedmMainWidget(MedmBaseWidget):
    
    def __init__(self):
        super(MedmBaseWidget, self).__init__()
        self.adl_filename = "unknown"   # file name given in the file
        self.adl_version = "unknown"    # file version given in the file
        self.color_table = []           # TODO: supply a default color table
        self.widgets = []
    
    def getNamedBlock(self, block_name, blocks):
        """
        """
        block = [b for b in blocks if b.symbol == block_name]
        if len(block) > 0:
            return block[0]

    def locateAssignments(self, buf):
        """
        identify and record the line number of all assignments in the buffer at this nesting level
        """
        assignments = {}
        level = 0
        nesting = level # remember nesting, identify assignments only at THIS level
        for line, text in enumerate(buf):
            p = text.find("=")
            if text.rstrip().endswith(" {"):
                nesting += 1
            elif text.rstrip().endswith("}"):
                nesting -= 1
            elif nesting == level and p > 0:
                key = text[:p].strip()
                value = text[p+1:].strip().strip('"')
                # TODO: look for parentheses
                assignments[key] = value
        return assignments
    
    def locateBlocks(self, buf):
        """
        identify and record the start and end of all blocks at this nesting level in the buffer
        """
        blocks = []
        level = 0
        nesting = level
        for line, text in enumerate(buf):
            if text.rstrip().endswith(" {"):
                if nesting == level:
                    symbol = text.strip()[:-2]
                    block = Block(line, None, nesting, symbol.strip('"'))
                nesting += 1
            elif text.rstrip().endswith("}"):
                nesting -= 1
                if nesting == level:
                    block.end = line
                    blocks.append(block)
        return blocks
    
    def parseAdlFile(self, parser):
        with open(parser.given_filename, "r") as fp:
            buf = fp.readlines()
        
        logger.debug("\n"*2)
        logger.debug(parser.given_filename)
        blocks = self.locateBlocks(buf)
        logger.debug("\n".join(map(str,blocks)))
        
        block = self.getNamedBlock("file", blocks)
        if block is not None:
            self.parseFileBlock(buf[block.start+1:block.end])

        block = self.getNamedBlock("color map", blocks)
        if block is not None:
            self.parseColorMapBlock(buf[block.start+1:block.end])

        block = self.getNamedBlock("display", blocks)
        if block is not None:
            self.parseDisplayBlock(buf[block.start+1:block.end])
         
        for block in blocks:
            if block.symbol in adl_symbols.widgets:
                if block.symbol == "composite":
                    widget = MedmCompositeWidget()
                else:
                    widget = MedmGenericWidget(block.symbol)
                widget.parseAdlBuffer(parser, buf[block.start+1:block.end])
    
    def parseFileBlock(self, buf):
        # TODO: keep original line numbers for debug purposes
        xref = dict(name="adl_filename", version="adl_version")
        assignments = self.locateAssignments(buf)
        for k, sk in xref.items():
            value = assignments.get(k)
            if value is not None:
                self.__setattr__(sk, value)
    
    def parseColorMapBlock(self, buf):
        """read the color_table (clut) from the "color map"""
        # TODO: keep original line numbers for debug purposes
        assignments = self.locateAssignments(buf)   # ignore ncolors=
        blocks = self.locateBlocks(buf)

        block = self.getNamedBlock("colors", blocks)
        if block is not None:
            def _parse_colors_(rgbhex):
                r = int(rgbhex[:2], 16)
                g = int(rgbhex[2:4], 16)
                b = int(rgbhex[4:6], 16)
                return Color(r, g, b)

            text = "".join(buf[block.start+1:block.end])
            clut = list(map(_parse_colors_, text.replace(",", " ").split()))
            self.color_table = clut
        else:
            # dl_color blocks  contain assignments: r, g, b inten
            block = self.getNamedBlock("dl_color", blocks)
            if block is not None:
                clut = []
                for block in blocks:
                    a = self.locateAssignments(buf[block.start+1:block.end])
                    color = Color(a["r"], a["g"], a["b"])   # ignore inten (default = 255)
                    clut.append(color)
                self.color_table = clut
    
    def parseDisplayBlock(self, buf):
        # TODO: keep original line numbers for debug purposes
        assignments = self.locateAssignments(buf)
        blocks = self.locateBlocks(buf)

        # assign certain items in named attributes
        xref = dict(clr="color", bclr="background_color")
        for k, sk in xref.items():
            value = assignments.get(k)
            if value is not None:
                self.__setattr__(sk, self.color_table[int(value)])
                del assignments[k]
        # assign remaining attributes
        for k, value in assignments.items():
            self.__setattr__(k, value)

        block = self.getNamedBlock("object", blocks)
        if block is not None:
            self.geometry = self.parseObjectBlock(buf[block.start+1:block.end])
    
    def parseObjectBlock(self, buf):
        a = self.locateAssignments(buf)
        arr = map(int, (a["x"], a["y"], a["width"], a["height"]))   # convert to int
        return Geometry(*list(arr))


class MedmCompositeWidget(MedmBaseWidget):
    
    def __init__(self):
        super(MedmBaseWidget, self).__init__()
        self.symbol = "composite"
        self.widgets = []


class MedmGenericWidget(MedmBaseWidget):
    
    def __init__(self, symbol):
        super(MedmBaseWidget, self).__init__()
        self.symbol = symbol


class AdlFileParser(object):
    """
    parse the file main blocks, recurse into composites
    """
    
    def __init__(self, given_filename):
        if not os.path.exists(given_filename):
            msg = "Could not find file: " + given_filename
        self.given_filename = given_filename

        self.main = MedmMainWidget()
        self.main.parseAdlFile(self)


if __name__ == "__main__":
    for fname in TEST_FILES:
        screen = AdlFileParser(fname)
    print("done")
