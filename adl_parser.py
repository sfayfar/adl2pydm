
"""
use the tokenizer to read the MEDM file
"""

import token
import tokenize
import pyRestTable


TEST_FILE = "/usr/local/epics/synApps_5_8/support/xxx-5-8-3/xxxApp/op/adl/xxx.adl"
TEST_FILE = "/usr/local/epics/synApps_5_8/support/motor-6-9/motorApp/op/adl/motorx_all.adl"


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
    
    def __init__(self, parent, block_type, *args, **kwargs):
        self.parent = parent
        self.medm_block_type = block_type
        self.color = None
        self.geometry = None
        self.contents = []


class MedmGenericWidget(MedmWidgetBase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: use logger instead of print()
        print("NOTE: using generic handler for '%s' block" % args[1])


class Medm_file(MedmWidgetBase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        parent = args[0]
        print("token %d" % parent.tokenPos, " in file block ")


known_handlers = {
    # MEDM block            adl_parser class
    "choice button":        None,
    "color map":            None,
    "composite":            None,
    "display":              None,
    "file":                 Medm_file,
    "message button":       None,
    "oval":                 None,
    "polyline":             None,
    "rectangle":            None,
    "related display":      None,
    "text entry":           None,
    "text":                 None,
    "text update":          None,
    }


class MEDM_Reader(object):
    """
    read (and parse) entire MEDM .adl file
    """
    
    def __init__(self, filename):
        self.filename = filename
        self.tokens = self.tokenizeFile()
        self.tokenPos = 0
        self.brace_nesting = 0
        self.parenthesis_nesting = 0
        self.contents = MedmBlock("")
    
    def parse(self, parent=None, level=0):
        parent = parent or self
        while self.tokenPos < self.numTokens:
            token = self.tokens[self.tokenPos]
            token_name = self.getTokenName(token)

            if token_name == "OP":
                if token.string == "{":
                    self.brace_nesting += 1
                elif token.string == "}":
                    self.brace_nesting -= 1
                elif token.string == "(":
                    self.parenthesis_nesting += 1
                elif token.string == ")":
                    self.parenthesis_nesting -= 1
            
            if self.brace_nesting == level:
                if token_name in ("NAME STRING".split()):
                    obj = known_handlers.get(token.string) or MedmGenericWidget
                    block = obj(self, token.string)
                    self.contents.contents.append(block)
                    self.print_token(token)
            elif self.brace_nesting > level:
                print("enter level %d" % self.brace_nesting)
                self.tokenPos += 1
                self.parse(block, self.brace_nesting)
            else:
                print("ended level %d" % level)
                return
            
            self.tokenPos += 1
        
    def print_token(self, token):
        token_name = self.getTokenName(token)
        print(
            self.tokenPos, 
            "  "*self.brace_nesting, 
            token_name, 
            token.string.rstrip())
        
    @property
    def numTokens(self):
        return len(self.tokens)
    
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
