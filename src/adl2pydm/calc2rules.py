#!/usr/bin/env python

"""
convert MEDM calc expressions to PyDM rules

see: https://epics.anl.gov/EpicsDocumentation/ExtensionsManuals/MEDM/MEDM.html#CalcExpression
see: https://slaclab.github.io/pydm/widgets/widget_rules/index.html
"""

import io
import logging
import tokenize

logger = logging.getLogger(__file__)


def convertCalcToRuleExpression(medm_calc):
    """
    convert MEDM calc expression to PyDM rules

    Parameters
    ----------
    medm_calc : str
        The expression to convert.

    Returns
    -------
    str
        The converted PyDM rule expression.
    """
    logger.debug(f"MEDM: {medm_calc}")

    medm_calc = medm_calc.replace("#", "!=")
    medm_calc = medm_calc.replace("&&", "&")
    medm_calc = medm_calc.replace("||", "|")

    calc = ""
    with io.StringIO(medm_calc) as f:
        for tok in tokenize.generate_tokens(f.read):
            logger.debug(tok)
            if tok.type == tokenize.NAME:
                if len(tok.string) == 1:
                    idx = "ABCDEFGHIJKL".index(tok.string.upper())
                    if idx > 3:
                        # TODO: consider handling these less common cases
                        raise ValueError(
                            f"unhandled complexity in MEDM calc '{medm_calc}''"
                            f" uses special variable {tok.string}"
                            )
                    calc += f"ch[{idx}]"
                else:
                    # probably a math expression
                    # TODO: need a mapping?
                    # we have these imports available:
                    #     from math import *
                    #     import numpy as np
                    calc += tok.string.lower()  # simply
            elif tok.type == tokenize.ERRORTOKEN:
                op = tok.string
                if op == "!":
                    op = " not "
                calc += op
            elif tok.type == tokenize.OP:
                calc += {
                    "=": "==",
                    "|": " or ",
                    "&": " and ",
                }.get(tok.string, tok.string)
            elif tok.type not in (tokenize.NEWLINE, tokenize.ENDMARKER):
                calc += tok.string

    pydm_rule = " ".join(calc.strip().split())  # remove interior extra spaces
    return pydm_rule
