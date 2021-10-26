"""
Ensure that troublesome screen files can be processed without error.

- screen: non_utf8.adl
- one instance: 'utf-8' codec can't decode byte 0xb0 in position 980: invalid start byte

- screen: Oxford_CS800_hourplot
- one instance: multiple `display[0]` items caused error
"""

import os
import pytest

from . import _core
from ._core import tempdir


SCREENS = """
    non_utf8.adl
    Oxford_CS800_hourplot.adl
""".split()


@pytest.mark.parametrize("test_adl", SCREENS)
def test_issue76_fixed(test_adl, tempdir):
    assert os.path.exists(tempdir)
    assert os.path.exists(os.path.join(_core.MEDM_SCREEN_DIR, test_adl))

    uiname = _core.convertAdlFile(test_adl, tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)  # fails if could not read
