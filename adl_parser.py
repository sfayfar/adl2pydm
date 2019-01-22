
"""
use the tokenizer to read the MEDM file
"""

from collections import namedtuple
import logging
import token
import tokenize


TEST_FILE = "/usr/local/epics/synApps_5_8/support/xxx-5-8-3/xxxApp/op/adl/xxx.adl"
TEST_FILE = "/home/mintadmin/sandbox/synApps/support/xxx-R6-0/xxxApp/op/adl/xxx.adl"
TEST_FILE = "/usr/local/epics/synApps_5_8/support/motor-6-9/motorApp/op/adl/motorx_all.adl"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


"""a color used in MEDM"""
Color = namedtuple('Color', 'r g b')

"""MEDM's object block contains the widget geometry"""
Geometry = namedtuple('Geometry', 'x y width height')

"""MEDM's key = value assignment"""
Assignment = namedtuple('Assignment', 'key value')


class MedmBlock(object):
    """root object of the .adl file structure : contains Medm_file"""
    
    def __init__(self, nm):
        self.name = nm.strip()
        self.contents = []
    
    def __str__(self, *args, **kwargs):
        return "%s(type=\"%s\")" % (type(self).__name__, self.name)


class MedmWidgetBase(object):
    """contains items common to all MEDM widgets"""
    
    def __init__(self, root, block_type, *args, **kwargs):
        self.root = root
        self.medm_block_type = block_type.strip('"')
        self.color = None
        self.background_color = None
        self.geometry = None
        self.contents = []
        
        msg = "token %d" % root.tokenPos
        msg += " in MEDM block %s " % self.medm_block_type
        logger.debug(msg)
    
    def __str__(self, *args, **kwargs):
        return "%s(type=\"%s\")" % (type(self).__name__, self.medm_block_type)


class MedmGenericWidget(MedmWidgetBase):
    """non-specific entity from MEDM .adl file, see ``medm_block_type``"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.warning("using generic handler for '%s' block" % args[1])


class Medm_file(MedmWidgetBase): pass


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
    
    def __init__(self, filename):
        self.filename = filename
        self.tokens = self.tokenizeFile()
        self.tokenPos = 0
        self.brace_nesting = 0
        self.parenthesis_nesting = 0
        self.block = MedmBlock("")
        self.color_table = None
    
    def parse(self, owner=None, level=0):
        owner = owner or self.block
        while self.tokenPos < self.numTokens:
            tkn = self.getCurrentToken()
            token_type = self.getTokenTypeStr(tkn)

            if tkn.type == token.OP:
                self.adjustLevel(tkn)
            
            if self.brace_nesting == level:
                if tkn.type in (token.NAME, token.STRING):
                    logger.debug(("token #%d : type=%s" % (self.tokenPos, token_type)))
                    if self.isAssignment:
                        self.parseAssignment(owner)
                    elif self.isBlockStart:
                        if tkn.string == "colors":
                            self.parseColors(self)
                        elif tkn.string == "object":
                            self.parseObject(owner)
                        else:
                            block = self.parse_block(self, owner)
                        self.tokenPos += 1
                    else:
                        if tkn.line.find("display[") >= 0:
                            owner.contents.append(self.parse_display_n(self))
                        else:
                            self.print_token(tkn)
            elif self.brace_nesting > level:
                logger.debug(("enter level %d" % self.brace_nesting))
                self.tokenPos += 1
                try:
                    self.parse(block, self.brace_nesting)
                except UnboundLocalError as exc:
                    pass
            else:
                logger.debug(("ended level %d" % level))
                return
            self.tokenPos += 1

        # TODO: look through the widgets and convert:
        #   clr=nn into clr=Color(rgb)
        #   bclr=nn into clr=Color(rgb)
        
    def adjustLevel(self, tkn):
        if tkn.string == "{":
            logger.warning("incrementing self.brace_nesting")
            self.brace_nesting += 1
        elif tkn.string == "}":
            self.brace_nesting -= 1
        elif tkn.string == "(":
            self.parenthesis_nesting += 1
        elif tkn.string == ")":
            self.parenthesis_nesting -= 1

    def getCurrentToken(self, offset=0):
        self.tokenPos += offset
        return self.tokens[self.tokenPos]

    def getTokenSequence(self, start=None, length=2):
        start = start or self.tokenPos
        if start+length >= self.numTokens:
            return []
        return self.tokens[start:start+length]

    def getNextTokenPosByType(self, token_types):
        """return the index of the next token with given type(s)"""
        # make sure token_name is a list
        if not isinstance(token_types, (set, tuple, list)):
            token_types = [token_types]
        
        # look through the remaining tokens for the next occurence
        for offset, tkn in enumerate(self.tokens[self.tokenPos:]):
            if tkn.type in token_types:
                return self.tokenPos + offset       # - 1
        
        raise ValueError("unexpected: failed to find next named token")

    def getTokenTypeStr(self, tkn):
        """return the name of this token"""
        return tokenize.tok_name[tkn.type]
    
    @property
    def isAssignment(self):
        """are we looking at a key=value assignment?"""
        def make_text(tseq):
            return " ".join(map(str, tseq))

        tokens = self.getTokenSequence(length=2)
        if len(tokens) == 2:
            seq = make_text([tok.type for tok in tokens])
            choices = [make_text([t, token.OP]) for t in (token.NAME, token.STRING)]
            if seq in choices:
                return tokens[-1].string.rstrip() == "="
        return False
    
    @property
    def isBlockStart(self):
        """are we looking at an MEDM block starting?:  name {"""
        def make_text(tseq):
            return " ".join(map(str, tseq))

        tokens = self.getTokenSequence(length=2)
        if len(tokens) == 2:
            seq = make_text([tok.type for tok in tokens])
            choices = [make_text([t, token.OP]) for t in (token.NAME, token.STRING)]
            if seq in choices:
                return tokens[-1].string.rstrip() == "{"
        return False
        
    @property
    def numTokens(self):
        return len(self.tokens)
        
    def parseAssignment(self, owner):
        """handle assignment operation"""
        # tokenize splits up some things porrly
        # we'll parse it ourselves here
        line = self.getCurrentToken().line.strip()
        pos = line.find("=")
        key = line[:pos]
        value = line[pos+1:].strip()

        assignment = Assignment(key, value.strip('"'))
        owner.contents.append(assignment)
        logger.debug(("assignment: %s = %s" % (key, str(assignment))))
        
        ePos = self.getNextTokenPosByType((token.NEWLINE, tokenize.NL))
        self.tokenPos = ePos - 1
        
    def parse_block(self, root, owner):
        """handle most blocks"""
        tkn = self.getCurrentToken()

        obj = widget_handlers.get(tkn.string) or MedmGenericWidget
        block = obj(root, tkn.string)
        logger.debug(("created %s(name=\"%s\")" % (block.__class__.__name__, tkn.string)))
        self.brace_nesting += 1
        owner.contents.append(block)
        return block
        
    def parseColors(self, root):
        """handle colors block"""
        text = ""
        for offset, tok in enumerate(self.tokens[self.tokenPos+2:]):
            if tok.string == "}" and tok.type == token.OP:
                break
            else:
                text += tok.string
        
        def _parse_colors_(rgbhex):
            r = int(rgbhex[:2], 16)
            g = int(rgbhex[2:4], 16)
            b = int(rgbhex[4:6], 16)
            return Color(r, g, b)
        
        value = list(map(_parse_colors_, text.rstrip(",").split()))
        logger.debug(("color table: length = %d" % len(value)))
        root.color_table = value

        self.tokenPos += 2 + offset
        
    def parse_display_n(self, root):
        d_name = self.getCurrentToken().line.strip().split()[0]
        owner = MedmGenericWidget(root, d_name)
        logger.debug(("created %s(name=\"%s\")" % (owner.__class__.__name__, d_name)))
        self.tokenPos = self.getNextTokenPosByType(tokenize.NL)
        
        tkn = self.getCurrentToken()
        while tkn.line.strip() != "}":
            self.tokenPos = self.getNextTokenPosByType(token.NAME)
            line = self.getCurrentToken().line.strip()
            pos = line.find("=")
            key = line[:pos]
            value = line[pos+1:].strip()
            assignment = Assignment(key, value.strip())
            owner.contents.append(assignment)
            logger.debug(("assignment: %s = %s" % (key, str(assignment))))

            self.tokenPos = self.getNextTokenPosByType(tokenize.NL)+1
            tkn = self.getCurrentToken()

        return owner


    def parseObject(self, owner):
        """handle object (widget bounding box geometry) block"""
        self.tokenPos += 1
        ref = {}

        for _i in "x y width height".split():
            self.tokenPos = self.getNextTokenPosByType(token.NAME)
            key = self.getCurrentToken().string
            value = self.getCurrentToken(2).string
            ref[key] = value

        owner.geometry = Geometry(ref["x"], ref["y"], ref["width"], ref["height"])
        logger.debug(("geometry: %s" % str(owner.geometry)))
        self.tokenPos = self.getNextTokenPosByType(token.OP)-1

    def print_token(self, tkn):
        logger.debug((
            self.tokenPos, 
            "  "*self.brace_nesting, 
            self.getTokenTypeStr(tkn), 
            tkn.string.rstrip()))

    def tokenizeFile(self):
        """tokenize just one file"""
        with open(self.filename, "rb") as f:
            tokens = tokenize.tokenize(f.readline)
            return list(tokens)


if __name__ == "__main__":
    reader = MEDM_Reader(TEST_FILE)
    reader.parse()
    ttypes = [reader.getTokenTypeStr(tkn) for tkn in reader.tokens]
    print("done")
