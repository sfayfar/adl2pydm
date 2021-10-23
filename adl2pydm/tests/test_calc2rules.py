import json
import os

from .. import calc2rules


TEST_FILE = "test_calcs.json"


def test_example_calcs():
    path = os.path.dirname(__file__)
    test_file = os.path.abspath(os.path.join(path, TEST_FILE))
    assert os.path.exists(test_file)

    with open(test_file, "r") as f:
        buf = f.read()

    test_calcs = json.loads(buf)

    for testcase in test_calcs:
        rule = calc2rules.convertCalcToRuleExpression(testcase[0])
        assert rule == testcase[-1], testcase[0]
