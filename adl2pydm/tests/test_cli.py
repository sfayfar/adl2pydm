import os
import pytest
import sys

from ._core import tempdir
from .. import cli
from .. import output_handler

from . import _core

# test ALL files (screens and other) in MEDM test screen directory
TEST_FILE_LIST = list(os.listdir(_core.MEDM_SCREEN_DIR))


@pytest.mark.parametrize("screen_file", TEST_FILE_LIST)
def test_acreen_files_can_convert(screen_file, tempdir):
    assert isinstance(screen_file, str)

    if not screen_file.lower().endswith(".adl"):
        return
    full_name = os.path.join(_core.MEDM_SCREEN_DIR, screen_file)
    assert os.path.exists(full_name), full_name

    sys.argv = [sys.argv[0], "-d", tempdir, full_name]
    cli.main()

    uiname = os.path.splitext(screen_file)[0]
    uiname += output_handler.SCREEN_FILE_EXTENSION
    assert os.path.exists(os.path.join(tempdir, uiname))
