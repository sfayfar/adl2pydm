#!/usr/bin/env python

"Used by developer to debug."

import os
import sys

_path = os.path.dirname(__file__)
sys.path.append(os.path.join(_path, "."))
from adl2pydm import cli

sys.argv.append(os.path.join(_path, "adl2pydm", "tests", "medm", "testDisplay.adl"))

cli.main()
