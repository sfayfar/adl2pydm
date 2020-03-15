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
                idx = "ABCDEFGHIJKL".index(tok.string.upper())
                if idx > 3:
                    raise ValueError(
                        f"MEDM calc {medm_calc}"
                        f" uses special variable {tok.string}"
                        " -- adl2pydm does not yet handle this calculation"
                        )
                calc += f"ch[{idx}]"
            elif tok.type == tokenize.ERRORTOKEN:
                op = tok.string
                if op == "!":
                    op = " not "
                calc += op
            elif tok.type == tokenize.OP:
                op = tok.string
                if op == "=":
                    op = "=="
                elif op == "|":
                    op = " or "
                elif op == "&":
                    op = " and "
                calc += op
            elif tok.type not in (tokenize.NEWLINE, tokenize.ENDMARKER):
                calc += tok.string

    pydm_rule = " ".join(calc.strip().split())
    return pydm_rule
