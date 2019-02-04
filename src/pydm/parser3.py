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
A *value* is a number, text suorrounded by double quotes, 
or list of values surrounded by parentheses.

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


class MedmMainWidget(MedmBaseWidget):
    
    def __init__(self):
        super().__init__()
        self.adl_filename = "unknown"    # file name given in the file
        self.adl_version = "unknown"     # file version given in the file
        self.widgets = []
    
    def parseFileBlock(self, buf):
        # TODO: keep original line numbers for debug purposes
        for line, text in enumerate(buf):
            text = text.strip()
            p = text.find("=")
            if p > 0:
                key = text[:p]
                value = text[p+1:]
                if key == "name":
                    self.adl_filename = text[p+1:].strip('"')
                elif key == "version":
                    self.adl_version = text[p+1:]

class MedmCompositeWidget(MedmBaseWidget):
    
    def __init__(self):
        super().__init__()
        self.symbol = "composite"
        self.widgets = []


class MedmGenericWidget(MedmBaseWidget):
    
    def __init__(self, symbol):
        super().__init__()
        self.symbol = symbol


class AdlFileParser(object):
    """
    parse the file main blocks, recurse into composites
    """
    
    def __init__(self, given_filename):
        if not os.path.exists(given_filename):
            msg = "Could not find file: " + given_filename
        self.given_filename = given_filename

        with open(self.given_filename, "r") as fp:
            buf = fp.readlines()
        
        logger.debug("\n"*2)
        logger.debug(self.given_filename)
        blocks = self.locateBlocks(buf, 0)
        logger.debug("\n".join(map(str,blocks)))
        
        self.main = MedmMainWidget()

        block = [b for b in blocks if b.symbol == "file"]
        if len(block) > 0:
            block = block[0]
            self.main.parseFileBlock(buf[block.start+1:block.end])

        block = [b for b in blocks if b.symbol == "display"]
        if len(block) > 0:
            block = block[0]
            # self.main.parseDisplayBlock(buf[block.start+1:block.end])

        block = [b for b in blocks if b.symbol == "color map"]
        if len(block) > 0:
            block = block[0]
            # self.main.parseColorMapBlock(buf[block.start+1:block.end])
#         
#         for block in blocks:
#             pass        # TODO: parse the widgets
    
    def locateBlocks(self, buf, level):
        """
        identify and record the start and end of all blocks at this nesting level in the buffer
        """
        blocks = []
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


if __name__ == "__main__":
    for fname in TEST_FILES:
        screen = AdlFileParser(fname)
    print("done")
