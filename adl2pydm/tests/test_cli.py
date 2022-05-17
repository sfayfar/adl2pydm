import pathlib
import pytest
import sys

from ._core import tempdir
from .. import cli
from .. import output_handler

from . import _core


@pytest.mark.parametrize("screen_file", _core.ALL_EXAMPLE_FILES)
def test_screen_files_can_convert(screen_file, tempdir):
    """Test ALL files (screens and other) in MEDM test screen directory."""
    assert isinstance(screen_file, str)

    if not screen_file.lower().endswith(".adl"):
        return
    full_name = _core.MEDM_SCREEN_DIR / screen_file
    assert full_name.exists(), full_name

    sys.argv = [sys.argv[0], "-d", tempdir, str(full_name)]
    cli.main()

    uiname = full_name.stem + output_handler.SCREEN_FILE_EXTENSION
    assert (pathlib.Path(tempdir) / uiname).exists()
