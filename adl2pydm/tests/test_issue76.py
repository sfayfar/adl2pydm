"""
MEDM text widget with non-utf8 text.

- screen: non_utf8.adl
- one instances: 'utf-8' codec can't decode byte 0xb0 in position 980: invalid start byte

Should warn on this and substitute smoething (perhaps whitespace).
"""

import os
import pytest

from xml.etree import ElementTree

from . import _core
from ._core import tempdir


TEST_ADL_FILE = "non_utf8.adl"


#@pytest.mark.parametrize("key", "text text_1 text_2".split())
def test_issue76_fixed(tempdir):
    assert os.path.exists(tempdir)
    assert os.path.exists(os.path.join(_core.MEDM_SCREEN_DIR, TEST_ADL_FILE))

    uiname = _core.convertAdlFile(TEST_ADL_FILE, tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)  # fails if could not read
