import json
import pathlib

from .. import calc2rules


TEST_FILE = "test_calcs.json"


def test_example_calcs():
    path = pathlib.Path(__file__).parent
    test_file = path / TEST_FILE
    assert test_file.exists()

    with open(test_file, "r") as f:
        buf = f.read()

    test_calcs = json.loads(buf)

    for testcase in test_calcs:
        rule = calc2rules.convertCalcToRuleExpression(testcase[0])
        assert rule == testcase[-1], testcase[0]
