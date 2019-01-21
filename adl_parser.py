
"""
use the tokenizer to read the MEDM file
"""

from collections import namedtuple
import logging
import token
import tokenize


TEST_FILE = "/usr/local/epics/synApps_5_8/support/xxx-5-8-3/xxxApp/op/adl/xxx.adl"
TEST_FILE = "/usr/local/epics/synApps_5_8/support/motor-6-9/motorApp/op/adl/motorx_all.adl"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# a color used in MEDM
Color = namedtuple('Color', 'r g b')

# MEDM's object block contains the widget geometry
Geometry = namedtuple('Geometry', 'x y width height')

# MEDM's key = value assignment
Assignment = namedtuple('Assignment', 'key value')


class MedmBlock(object):
    
    def __init__(self, nm):
        self.name = nm
        self.contents = []
        self.tokens = []


class MedmWidgetBase(object):
    """contains items common to all MEDM widgets"""
    
    def __init__(self, parent, block_type, *args, **kwargs):
        self.parent = parent
        self.medm_block_type = block_type
        self.color = None
        self.geometry = None
        self.contents = []
        
        msg = "token %d" % parent.tokenPos
        msg += " in MEDM block %s " % self.medm_block_type
        logger.debug(msg)


class MedmGenericWidget(MedmWidgetBase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.warning("using generic handler for '%s' block" % args[1])


class Medm_file(MedmWidgetBase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        parent = args[0]


widget_handlers = {
    # MEDM block            adl_parser class
    "basic attribute":      None,
    "children":             None,
    "choice button":        None,
    "color map":            None,
    "composite":            None,
    "control":              None,
    "display":              None,       # display[n] - an oddball
    "dynamic attribute":    None,
    "file":                 Medm_file,
    "limits":               None,
    "menu":                 None,
    "message button":       None,
    "monitor":              None,
    "oval":                 None,
    "points":               None,
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
    
    block_handlers = {
        "object": None,
        "colors": None,
        }
    
    def __init__(self, filename):
        self.filename = filename
        self.tokens = self.tokenizeFile()
        self.tokenPos = 0
        self.brace_nesting = 0
        self.parenthesis_nesting = 0
        self.contents = MedmBlock("")
    
    def parse(self, owner=None, level=0):
        owner = owner or self.contents
        while self.tokenPos < self.numTokens:
            token = self.tokens[self.tokenPos]
            token_name = self.getTokenName(token)

            if token_name == "OP":
                if token.string == "{":
                    logger.warning("incrementing self.brace_nesting")
                    self.brace_nesting += 1
                elif token.string == "}":
                    self.brace_nesting -= 1
                elif token.string == "(":
                    self.parenthesis_nesting += 1
                elif token.string == ")":
                    self.parenthesis_nesting -= 1
            
            if self.brace_nesting == level:
                if token_name in ("NAME STRING".split()):
                    logger.debug(("token #%d : name=%s" % (self.tokenPos, token_name)))
                    if self.isAssignment:
                        self.parseAssignment(owner)
                    elif self.isBlockStart:
                        if token.string == "colors":
                            self.parseColors(owner)
                        else:
                            block = self.parse_block(owner)
                        self.tokenPos += 1

                    else:
                        # TODO: display[n] ends up here, handle it
                        self.print_token(token)

            elif self.brace_nesting > level:
                logger.debug(("enter level %d" % self.brace_nesting))
                self.tokenPos += 1
                self.parse(block, self.brace_nesting)
            else:
                logger.debug(("ended level %d" % level))
                return
            
            self.tokenPos += 1

    def print_token(self, token):
        token_name = self.getTokenName(token)
        logger.debug((
            self.tokenPos, 
            "  "*self.brace_nesting, 
            token_name, 
            token.string.rstrip()))
        
    def getTokenSequence(self, start=None, length=2):
        start = start or self.tokenPos
        if start+length >= self.numTokens:
            return []
        return self.tokens[start:start+length]
        
    @property
    def numTokens(self):
        return len(self.tokens)
    
    @property
    def isAssignment(self):
        """are we looking at a key=value assignment?"""
        tokens = self.getTokenSequence(length=2)
        if len(tokens) == 2:
            tt_seq = " ".join(map(self.getTokenName, tokens))
            if tt_seq in ("NAME OP", "STRING OP"):
                return tokens[-1].string.rstrip() == "="
        return False
    
    @property
    def isBlockStart(self):
        """are we looking at an MEDM block starting?:  name {"""
        tokens = self.getTokenSequence(length=2)
        if len(tokens) == 2:
            tt_seq = " ".join(map(self.getTokenName, tokens))
            if tt_seq in ("NAME OP", "STRING OP"):
                return tokens[-1].string.rstrip() == "{"
        return False

    def getTokenName(self, token):
        """return the name of this token"""
        return tokenize.tok_name[token.type]

    def getNextTokenName(self, token_name):
        """return the index of the next token with given name(s)"""
        # make sure token_name is a list
        if not isinstance(token_name, (set, tuple, list)):
            token_name = [token_name]
        
        # look through the remaining tokens for the next occurence
        for offset, token in enumerate(self.tokens[self.tokenPos:]):
            if self.getTokenName(token) in token_name:
                return self.tokenPos + offset       # - 1
        
        raise ValueError("unexpected: failed to find next named token")
        
    def parseAssignment(self, owner):
        """handle assignment operation"""
        token = self.tokens[self.tokenPos]

        key = token.string
        
        # TODO: is it important to identify if number or string?
        ePos = self.getNextTokenName("NL")
        
        # tokenize splits up some things porrly
        # we'll parse it ourselves here
        pos = token.line.find("=") + 1
        value = token.line[pos:].strip().strip('"')
        
        assignment = Assignment(key, value)
        owner.contents.append(assignment)
        self.tokenPos = ePos
        logger.debug(("assignment: %s = %s" % (key, value)))
        
    def parse_block(self, owner):
        """handle most blocks"""
        token = self.tokens[self.tokenPos]

        obj = widget_handlers.get(token.string) or MedmGenericWidget
        block = obj(self, token.string)
        logger.debug(("created %s(name=\"%s\")" % (block.__class__.__name__, token.string)))
        self.brace_nesting += 1
        owner.contents.append(block)
        return block
        
    def parseColors(self, owner):
        """handle colors block"""
        token = self.tokens[self.tokenPos]

        text = ""
        for offset, tok in enumerate(self.tokens[self.tokenPos+2:]):
            if tok.string == "}" and self.getTokenName(tok) == "OP":
                break
            else:
                text += tok.string
        
        def _parse_colors_(rgbhex):
            r = int(rgbhex[:2], 16)
            g = int(rgbhex[2:4], 16)
            b = int(rgbhex[4:6], 16)
            return Color(r, g, b)
        
        key = token.string
        value = list(map(_parse_colors_, text.rstrip(",").split()))
        assignment = Assignment(token.string, value)
        logger.debug(("assignment: %s = %s" % (key, "length=%d" % len(value))))
        owner.contents.append(assignment)

        self.tokenPos += 2 + offset

    def tokenizeFile(self):
        """tokenize just one file"""
        with open(self.filename, "rb") as f:
            tokens = tokenize.tokenize(f.readline)
            return list(tokens)


if __name__ == "__main__":
    reader = MEDM_Reader(TEST_FILE)
    reader.parse()
    ttypes = [reader.getTokenName(token) for token in reader.tokens]
    print("done")
