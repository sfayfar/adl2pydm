"""
Ensure that troublesome screen files can be processed without error.

- screen: non_utf8.adl
- one instance: 'utf-8' codec can't decode byte 0xb0 in position 980: invalid start byte

- screen: Oxford_CS800_hourplot
- one instance: multiple `display[0]` items caused error
"""

import pathlib
import pytest

from . import _core
from ._core import tempdir


SCREENS = """
    non_utf8.adl
    Oxford_CS800_hourplot.adl
""".split()


@pytest.mark.parametrize("test_adl", SCREENS)
def test_issue76_fixed(test_adl, tempdir):
    assert pathlib.Path(tempdir).exists()
    assert (_core.MEDM_SCREEN_DIR / test_adl).exists()

    uiname = _core.convertAdlFile(test_adl, tempdir)
    assert (pathlib.Path(tempdir) / uiname).exists()  # fails if could not read
