import os
import pytest
import shutil
import sys
import tempfile

from .. import adl_parser
from .. import cli
from .. import output_handler

MEDM_SCREEN_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "tests", "medm")


@pytest.fixture(scope="function")
def tempdir():
    path = tempfile.mkdtemp()
    yield path

    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)


def convertAdlFile(adlname, temppath):
    medm_path = MEDM_SCREEN_DIR
    assert os.path.exists(medm_path)

    full_name = os.path.join(medm_path, adlname)
    assert os.path.exists(full_name)

    sys.argv = [sys.argv[0], "-d", temppath, full_name]
    cli.main()

    base = os.path.splitext(os.path.basename(full_name))[0]
    uiname = base + output_handler.SCREEN_FILE_EXTENSION

    return uiname


def test_write_all_example_files_process(tempdir):
    "ensure all example MEDM files are converted to PyDM"
    path = MEDM_SCREEN_DIR
    for adl_file in os.listdir(path):
        if (
            os.path.isfile(os.path.join(path, adl_file) )
            and 
            adl_file.endswith(".adl")
        ):
            uiname = convertAdlFile(adl_file, tempdir)
            full_uiname = os.path.join(tempdir, uiname)
            assert os.path.exists(full_uiname), uiname
