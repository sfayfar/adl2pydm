import os
import sys

from . import _core
from ._core import tempdir
from .. import cli
from .. import output_handler


def test_file_conversion(tempdir):
    medm_path = _core.MEDM_SCREEN_DIR
    assert os.path.exists(_core.MEDM_SCREEN_DIR)

    full_name = os.path.join(medm_path, "testDisplay.adl")
    assert os.path.exists(full_name)

    sys.argv = [sys.argv[0], "-d", tempdir, full_name]
    cli.main()

    base = os.path.splitext(os.path.basename(full_name))[0]
    uiname = base + output_handler.SCREEN_FILE_EXTENSION

    assert os.path.exists(os.path.join(tempdir, uiname))
