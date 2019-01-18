
"""
convert one or more MEDM .adl file(s) to PYDM's .ui format

adapted from caQtDM's adl2ui
"""

import binascii
from enum import Enum
import json
import os
from scipy.stats._discrete_distns import geom


TEST_ADL_FILE = "/usr/local/epics/synApps_5_8/support/xxx-5-8-3/xxxApp/op/adl/xxx.adl"


# enums
T_WORD, T_EQUAL, T_QUOTE, T_LEFT_BRACE, T_RIGHT_BRACE, T_EOF = range(6)

NEUTRAL, INQUOTE, INWORD, INMACRO = range(4)

LONGSTRING              = 4096
MAX_ASCII               =   80   # max size of many asci strings
MAX_TOKEN_LENGTH        =  256   # max size of strings in adl
MAX_PENS                =    8   # max # of pens on strip chart
MAX_TRACES              =    8   # max # of traces on cart. plot
MAX_FILE_CHARS          =  256   # max # of chars in filename
MAX_CALC_RECORDS        =    4   # max # of records for calc
MAX_CALC_INPUTS         =   12   # max # of inputs for calc
DL_MAX_COLORS           =   65   # max # of colors for display
DL_COLORS_COLUMN_SIZE   =    5   # # of colors in each column
EOF_CHAR                = ""     # end of file character


class DisplayObject(object):
    """
    """
    
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = x
        self.y = y
        self.width = w
        self.height = h


class DisplayInfo(object):
    """
    """

    buffer = None
    pos = 0
    versionNumber = None
    drawingAreaBackgroundColor = None
    drawingAreaForegroundColor = None
    dlColormap = None
    nameValueTable = None
    numNameValues = None


class DlColormapEntry:
    
    def __init__(self, r=0, g=0, b=0, inten=0):
        self.r = r
        self.g = g
        self.b = b
        self.inten = inten


class DlColormap:
    
    default_cmap = [
        # r,  g,   b,   inten
        [ 255, 255, 255, 255, ],
        [ 236, 236, 236, 0, ],
        [ 218, 218, 218, 0, ],
        [ 200, 200, 200, 0, ],
        [ 187, 187, 187, 0, ],
        [ 174, 174, 174, 0, ],
        [ 158, 158, 158, 0, ],
        [ 145, 145, 145, 0, ],
        [ 133, 133, 133, 0, ],
        [ 120, 120, 120, 0, ],
        [ 105, 105, 105, 0, ],
        [ 90, 90, 90, 0, ],
        [ 70, 70, 70, 0, ],
        [ 45, 45, 45, 0, ],
        [ 0, 0, 0, 0, ],
        [ 0, 216, 0, 0, ],
        [ 30, 187, 0, 0, ],
        [ 51, 153, 0, 0, ],
        [ 45, 127, 0, 0, ],
        [ 33, 108, 0, 0, ],
        [ 253, 0, 0, 0, ],
        [ 222, 19, 9, 0, ],
        [ 190, 25, 11, 0, ],
        [ 160, 18, 7, 0, ],
        [ 130, 4, 0, 0, ],
        [ 88, 147, 255, 0, ],
        [ 89, 126, 225, 0, ],
        [ 75, 110, 199, 0, ],
        [ 58, 94, 171, 0, ],
        [ 39, 84, 141, 0, ],
        [ 251, 243, 74, 0, ],
        [ 249, 218, 60, 0, ],
        [ 238, 182, 43, 0, ],
        [ 225, 144, 21, 0, ],
        [ 205, 97, 0, 0, ],
        [ 255, 176, 255, 0, ],
        [ 214, 127, 226, 0, ],
        [ 174, 78, 188, 0, ],
        [ 139, 26, 150, 0, ],
        [ 97, 10, 117, 0, ],
        [ 164, 170, 255, 0, ],
        [ 135, 147, 226, 0, ],
        [ 106, 115, 193, 0, ],
        [ 77, 82, 164, 0, ],
        [ 52, 51, 134, 0, ],
        [ 199, 187, 109, 0, ],
        [ 183, 157, 92, 0, ],
        [ 164, 126, 60, 0, ],
        [ 125, 86, 39, 0, ],
        [ 88, 52, 15, 0, ],
        [ 153, 255, 255, 0, ],
        [ 115, 223, 255, 0, ],
        [ 78, 165, 249, 0, ],
        [ 42, 99, 228, 0, ],
        [ 10, 0, 184, 0, ],
        [ 235, 241, 181, 0, ],
        [ 212, 219, 157, 0, ],
        [ 187, 193, 135, 0, ],
        [ 166, 164, 98, 0, ],
        [ 139, 130, 57, 0, ],
        [ 115, 255, 107, 0, ],
        [ 82, 218, 59, 0, ],
        [ 60, 180, 32, 0, ],
        [ 40, 147, 21, 0, ],
        [ 26, 115, 9, 0, ],
    ]
    
    def __init__(self):
        self.dl_color = [DlColormapEntry(r, g, b, inten) for r, g, b, inten in self.default_cmap]
    
    @property
    def ncolors(self):
        return len(self.dl_color)
    
    def clear(self):
        self.dl_color = []
    
    def append(self, entry):
        self.dl_color.append(entry)


class DlDisplay:
    dlobject = None
    clr, bclr = 0, 0
    cmap = ""


class FrameOffset(object):
    """
    """
    
    def __init__(self, x=0, y=0, w=0, h=0):
        self.frameX = x
        self.frameY = y
        self.frameWidth = w
        self.frameHeight = h


def lookupNameValue(nameValueTable, name):
    return nameValueTable.get(name)

    
def getToken(displayInfo):
    """
    """
    state = NEUTRAL
    savedState = NEUTRAL
    word = ""
    macro = ""

    while displayInfo.pos < len(displayInfo.buffer):
        c = displayInfo.buffer[displayInfo.pos]
        displayInfo.pos += 1
        if state == NEUTRAL:
            v = {"=": T_EQUAL, "{": T_LEFT_BRACE, "}": T_RIGHT_BRACE}.get(c)
            if v is not None:
                return v, word
            elif c == '"' :
                state = INQUOTE
            elif c in " \t\r\n":
                pass
            elif c in "(,)":
                word += c
                return T_WORD, word
            else:
                state = INWORD
                word += c

        elif state == INQUOTE:
            if c == '"':
                return T_WORD, word
            word += c

        elif state == INMACRO:
            if c == ")":
                value = lookupNameValue(displayInfo.nameValueTable, macro)
                if value is not None:
                    word += value
                else:
                    value += "$(%s)" % macro
                    state = savedState

            else:
                macro += c

        elif state == INWORD:
            if c in " \r\n\t=(,)\"":
                displayInfo.pos -= 1
                return T_WORD, word
            else:
                word += c
    
    return T_EOF, word


def parseFile(displayInfo):
    """
    parse the file block
    """
    nestingLevel = 0

    while True:
        tokenType, token = getToken(displayInfo)

        if tokenType == T_WORD:
            if token == "name":
                getToken(displayInfo)
                getToken(displayInfo)
        
            elif token == "version":
                getToken(displayInfo)
                getToken(displayInfo)
        
        elif tokenType == T_EQUAL:
            pass
        
        elif tokenType == T_LEFT_BRACE:
            nestingLevel += 1
        
        elif tokenType == T_RIGHT_BRACE:
            nestingLevel -= 1
        
        else:
            pass

        if tokenType in (T_RIGHT_BRACE, T_EOF) or nestingLevel == 0:
            break


def parseDisplay(displayInfo):
    """
    parse the display block
    """
    nestingLevel = 0
    display_object = DisplayObject()
    cmap = ""

    offset = FrameOffset()
    
    while True:
        tokenType, token = getToken(displayInfo)

        if tokenType == T_WORD:
            if token == "object":
                parseObject(displayInfo, display_object)
                writeRectangleDimensions(display_object, offset, "", True);
                pass
        
            elif token == "grid":
                parseGrid(displayInfo)
        
            elif token == "cmap":
                # Parse separate display list to get and use that colormap
                getToken(displayInfo)
                token = getToken(displayInfo)[1]
                if len(token) > 0:
                    cmap = token
        
            elif token == "bclr":
                getToken(displayInfo)
                token = getToken(displayInfo)[1]
                displayInfo.drawingAreaBackgroundColor = int(token) % DL_MAX_COLORS
        
            elif token == "clr":
                getToken(displayInfo)
                token = getToken(displayInfo)[1]
                displayInfo.drawingAreaForegroundColor = int(token) % DL_MAX_COLORS
        
            elif token == "gridSpacing":
                getToken(displayInfo)
                getToken(displayInfo)
        
            elif token == "gridOn":
                getToken(displayInfo)
                getToken(displayInfo)
        
            elif token == "snapToGrid":
                getToken(displayInfo)
                getToken(displayInfo)
        
        elif tokenType == T_EQUAL:
            pass
        
        elif tokenType == T_LEFT_BRACE:
            nestingLevel += 1
        
        elif tokenType == T_RIGHT_BRACE:
            nestingLevel -= 1
        
        else:
            pass

        if tokenType in (T_RIGHT_BRACE, T_EOF) or nestingLevel == 0:
            break
    
    return None


def parseGrid(displayInfo):
    """
    parse MEDM grid structure
    """
    nestingLevel = 0

    while True:
        tokenType, token = getToken(displayInfo)

        if tokenType == T_WORD:
            if token == "gridSpacing":
                getToken(displayInfo)
                getToken(displayInfo)
        
            elif token == "gridOn":
                getToken(displayInfo)
                getToken(displayInfo)
        
            elif token == "snapToGrid":
                getToken(displayInfo)
                getToken(displayInfo)
        
        elif tokenType == T_EQUAL:
            pass
        
        elif tokenType == T_LEFT_BRACE:
            nestingLevel += 1
        
        elif tokenType == T_RIGHT_BRACE:
            nestingLevel -= 1
        
        else:
            pass

        if tokenType in (T_RIGHT_BRACE, T_EOF) or nestingLevel == 0:
            break


def parseObject(displayInfo, dlobject):
    """
    parse MEDM object structure
    """
    nestingLevel = 0

    while True:
        tokenType, token = getToken(displayInfo)
        if tokenType == T_WORD:
            if token == "x":
                getToken(displayInfo)
                token = getToken(displayInfo)[1]
                dlobject.x = int(token)
        
            elif token == "y":
                getToken(displayInfo)
                token = getToken(displayInfo)[1]
                dlobject.y = int(token)
        
            elif token == "width":
                getToken(displayInfo)
                token = getToken(displayInfo)[1]
                dlobject.width = min(1, int(token))     # avoid zero-thickness line
        
            elif token == "height":
                getToken(displayInfo)
                token = getToken(displayInfo)[1]
                dlobject.height = min(1, int(token))    # avoid zero-thickness line
        
        elif tokenType == T_LEFT_BRACE:
            nestingLevel += 1
        
        elif tokenType == T_RIGHT_BRACE:
            nestingLevel -= 1
        
        else:
            pass

        if tokenType in (T_RIGHT_BRACE, T_EOF) or nestingLevel == 0:
            break


def parseColormap(displayInfo):
    """
    parse MEDM colormap structure
    """
    nestingLevel = 0
    counter = 0
    savedBufferPos = displayInfo.pos
    
    dlColormap = createDlColormap(displayInfo)
    if dlColormap is None:
        return None
    dlColormap.clear()        # prepare for cmap from .adl file
 
    while True:
        tokenType, token = getToken(displayInfo)
        if tokenType == T_WORD:
            if token == "ncolors":
                getToken(displayInfo)
                token = getToken(displayInfo)[1]
                ncolors = int(token)
                if ncolors > DL_MAX_COLORS:
                    msg = """
                    Maximum # of colors in colormap exceeded.
                    Continuing with truncated color space.
                    (You may want to change the colors of some objects.)
                    """
                    print(msg)
            elif token == "dl_color":
                # continue parsing but ignore "excess" colormap entries
                entry = parseOldDlColor(displayInfo)
                if dl_color.ncolors < DL_MAX_COLORS:
                    dl_color.append(entry)
            elif token == "colors":
                dlColormap.dl_color = parseDlColor(displayInfo)
        
        elif tokenType == T_EQUAL:
            pass
        
        elif tokenType == T_LEFT_BRACE:
            nestingLevel += 1
        
        elif tokenType == T_RIGHT_BRACE:
            nestingLevel -= 1
 
        if tokenType in (T_RIGHT_BRACE, T_EOF) or nestingLevel == 0:
            break
        
    # restore previous file buffer position
    displayInfo.pos = savedBufferPos
    
    return dlColormap


def parseOldDlColor(displayInfo):
    nestingLevel = 0
    r, g, b, inten = 0, 0, 0, 0
 
    while True:
        tokenType, token = getToken(displayInfo)
        if tokenType == T_WORD:
            if token == "r":
                getToken(displayInfo)
                token = getToken(displayInfo)[1]
                r = int(token)
        
            elif token == "g":
                getToken(displayInfo)
                token = getToken(displayInfo)[1]
                g = int(token)
        
            elif token == "b":
                getToken(displayInfo)
                token = getToken(displayInfo)[1]
                b = int(token)
        
            elif token == "inten":
                getToken(displayInfo)
                token = getToken(displayInfo)[1]
                inten = int(token)
        
        elif tokenType == T_EQUAL:
            pass
        
        elif tokenType == T_LEFT_BRACE:
            nestingLevel += 1
        
        elif tokenType == T_RIGHT_BRACE:
            nestingLevel -= 1
 
        if tokenType in (T_RIGHT_BRACE, T_EOF) or nestingLevel == 0:
            break
    
    return DlColormapEntry(r, g, b, inten)


def parseDlColor(displayInfo):
    nestingLevel = 0
    r, g, b, inten = 0, 0, 0, 0
    
    #    (MDA) have to be sneaky for these colormap parsing routines: 
    #    since possibly external colormap, save and restore * external file
    #    ptr in displayInfo so that getToken() * works with displayInfo and
    #    not the displayInfo.pos directly
    savedBufferPos = displayInfo.pos

    dlColormap = createDlColormap(displayInfo)
    if dlColormap is None:
        return None
    dlColormap.clear()        # prepare for cmap from .adl file
 
    while True:
        tokenType, token = getToken(displayInfo)
        if tokenType == T_WORD:
            color = binascii.unhexlify(token)
            if dlColormap.ncolors < DL_MAX_COLORS:
                r = color[0]
                g = color[1]
                b = color[2]
                dlColormap.append(DlColormapEntry(r, g, b))
            getToken(displayInfo)
        
        elif tokenType == T_EQUAL:
            pass
        
        elif tokenType == T_LEFT_BRACE:
            nestingLevel += 1
        
        elif tokenType == T_RIGHT_BRACE:
            nestingLevel -= 1
 
        if tokenType in (T_RIGHT_BRACE, T_EOF) or nestingLevel == 0:
            break
    
    displayInfo.pos = savedBufferPos


def correctOffset(dlobject, offset):
    w = dlobject.width
    h = dlobject.height

    x = dlobject.x
    if offset.frameX != 0:
        x -= offset.frameX

    y = dlobject.y
    if offset.frameY != 0:
        y -= offset.frameY

    return x, y, w, h


def createDlColormap(displayInfo):
    return DlColormap()


def writeRectangleDimensions(dlobject, offset, widget, correct):
    # TODO:
    print("must write method: writeRectangleDimensions()")
    
    x=offset.frameX 
    y=offset.frameY
    w=offset.frameWidth
    h=offset.frameHeight
    
    if correct:
        x, y, w, h = correctOffset(dlobject, offset)

    if widget == "caFrame":     # add two pixels for frames
        w += 2
        h += 2
        
    rect = dict(x=x, y=y, width=w, height=h)
    geometry = dict(rect=rect)
    property = dict(geometry=geometry)
    
    print(json.dumps(property))
    return geometry


def convert_one_file(inputFile):
    if not os.path.exists(inputFile):
        msg = "file does not exist: " + inputFile
        raise ValueError(msg)

    with open(inputFile, "r") as fp:
        cdi = DisplayInfo()
        cdi.buffer = fp.read()

    # first block: file
    tokenType, word = getToken(cdi)
    if tokenType is not T_WORD or word != "file":
        msg = "Invalid .adl file (First block is not file block) file: " + inputFile
        raise ValueError(msg)
    parseFile(cdi)

    # second block: file
    tokenType, word = getToken(cdi)
    if tokenType is not T_WORD or word != "display":
        msg = "Invalid .adl file (Second block is not display block) file: " + inputFile
        raise ValueError(msg)
    parseDisplay(cdi)

    # Read the colormap if there.  Will also create cdi->dlColormap.
    tokenType, word = getToken(cdi)
    if tokenType is T_WORD and word in ("color map", "<<color map>>"):
        cdi.dlColormap = parseColormap(cdi)
        if not cdi.dlColormap:                              # FIXME:
            msg = "Invalid .adl file (Cannot parse colormap) file: " + inputFile
            raise ValueError(msg)
        tokenType, token = getToken(cdi)
        
    # TODO: more work to finish this


def main():
    print("adl2pydm")
    convert_one_file(TEST_ADL_FILE)
    print("done")


if __name__ == "__main__":
    main()
