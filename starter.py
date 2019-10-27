#!/usr/bin/env python

import os
import sys

_path = os.path.dirname(__file__)
sys.path.append(os.path.join(_path, "src"))
from adl2pydm import cli

cli.main()
