
"""
use the tokenizer to read the MEDM file
"""

import token
import tokenize
import pyRestTable


TEST_FILE = "/usr/local/epics/synApps_5_8/support/xxx-5-8-3/xxxApp/op/adl/xxx.adl"


class MedmBlock(object):
    
    def __init__(self, nm):
        self.name = nm
        self.contents = []
        self.tokens = []


class MedmColor(object):
    """mEDM' widget color"""
    
    def __init__(self, r, g, b, intensity=255):
        self.r = r
        self.g = g
        self.b = b
        self.intensity = intensity


class MedmGeometry(object):
    """mEDM's object block contains the widget geometry"""
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class MedmWidgetBase(object):
    """contains items common to all MEDM widgets"""
    
    def __init__(self):
        self.color = None
        self.geometry = None
        self.contents = []


class MEDM_Reader(object):
    """
    read (and parse) entire MEDM .adl file
    """
    
    def __init__(self, filename):
        self.filename = filename
        self.tokens = self.tokenizeFile()
        self.tokenPos = 0
        self.brace_nesting = 0
        self.contents = MedmBlock("")
    
    def parse(self, level=0):
        for token in self.tokens:
            token_name = self.getTokenName(token)
            if token_name == "OP" and token.string == "{":
                self.brace_nesting += 1
            elif token_name == "OP" and token.string == "}":
                self.brace_nesting -= 1
            
            if self.brace_nesting == level and token_name in ("NAME STRING".split()):
                # token_name == "NAME"
                print("  "*self.brace_nesting, token_name, token.string)
                block = MedmBlock(token.string)
                self.contents.contents.append(block)
        
    def getTokenName(self, token):
        return tokenize.tok_name[token.type]

    def tokenizeFile(self):
        '''
        tokenize just one file
        '''
        with open(self.filename, "rb") as f:
            tokens = tokenize.tokenize(f.readline)
            return list(tokens)


if __name__ == "__main__":
    reader = MEDM_Reader(TEST_FILE)
    reader.parse()
    print("done")
