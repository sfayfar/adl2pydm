#!/usr/bin/env python

"""
convert MEDM calc expressions to PyDM rules

see: https://epics.anl.gov/EpicsDocumentation/ExtensionsManuals/MEDM/MEDM.html#CalcExpression
see: https://slaclab.github.io/pydm/widgets/widget_rules/index.html
"""

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
    calc = medm_calc

    # TODO: consider using tokenizer

    # if calc is not None and len(calc) > 0:
    #     logger.info(f"CALC: {calc}")
    # visibility_calc = {
    #     "if zero": " == 0",
    #     "if not zero": " != 0",
    #     "calc": calc
    # }[attr.get("vis", "if not zero")]
    # if len(channels) > 0:
    #     rule["channels"] = channels
    #     if calc is None:
    #         calc = "ch[0]" + visibility_calc
    
    # edit the calc expression for known changes
    # FIXME: misses calc="a==0", algorithm needs improvement
    exchanges = {
        "A": "ch[0]",
        "B": "ch[1]",
        "C": "ch[2]",
        "D": "ch[3]",
        "#": "!=",
        "||": " or "
        }
    for k, v in exchanges.items():
        calc = calc.replace(k, v)

    pydm_rule = calc
    return pydm_rule


def tester():
    import json
    import os
    import pyRestTable

    path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "tests",
            "test_calcs.json",
        )
    )

    with open(path, "r") as f:
        buf = f.read()
    
    test_calcs = json.loads(buf)
    
    tbl = pyRestTable.Table()
    tbl.labels = "MEDM PyDM convertCalcToRule".split()
    for testcase in test_calcs:
        rule = convertCalcToRuleExpression(testcase[0])
        testcase.append(rule)
        tbl.addRow(testcase)
    print(tbl)


if __name__ == "__main__":
    tester()
