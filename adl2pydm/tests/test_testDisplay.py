import pathlib
import sys

from . import _core
from ._core import tempdir
from .. import cli
from .. import output_handler


def test_file_conversion(tempdir):
    medm_path = _core.MEDM_SCREEN_DIR
    assert _core.MEDM_SCREEN_DIR.exists()

    full_name = medm_path / "testDisplay.adl"
    assert full_name.exists()

    sys.argv = [sys.argv[0], "-d", tempdir, str(full_name)]
    cli.main()

    uiname = full_name.stem + output_handler.SCREEN_FILE_EXTENSION

    assert (pathlib.Path(tempdir) / uiname).exists()
