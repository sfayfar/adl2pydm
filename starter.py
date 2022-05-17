#!/usr/bin/env python

"Used by developer to debug."

import pathlib
import sys

_path = pathlib.Path(__file__).parent
sys.path.append(str(_path + "."))
from adl2pydm import cli

TEST_ADL = "Oxford_CS800_hourplot.adl"

sys.argv.append(str(_path + "adl2pydm" + "tests" + "medm" + TEST_ADL))

cli.main()
