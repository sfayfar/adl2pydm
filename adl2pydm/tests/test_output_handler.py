import os

from xml.etree import ElementTree

from . import _core
from ._core import tempdir


def test_write_all_example_files_process(tempdir):
    "ensure all example MEDM files are converted to PyDM"
    path = _core.MEDM_SCREEN_DIR
    for adl_file in os.listdir(path):
        if os.path.isfile(os.path.join(path, adl_file)):
            if adl_file.endswith(".adl"):
                uiname = _core.convertAdlFile(adl_file, tempdir)
                full_uiname = os.path.join(tempdir, uiname)
                assert os.path.exists(full_uiname), uiname


def test_write_widget_text(tempdir):
    uiname = _core.convertAdlFile("testDisplay.adl", tempdir)
    full_uiname = os.path.join(tempdir, uiname)
    assert os.path.exists(full_uiname)

    root = ElementTree.parse(full_uiname).getroot()
    screen = _core.getSubElement(root, "widget")
    widgets = screen.findall("widget")
    assert len(widgets) == 64

    key = "text"
    widget = _core.getNamedWidget(screen, key)
    _core.assertEqualClassName(widget, "QLabel", key)
    _core.assertEqualPropertyString(widget, "text", "Test Display")

    for propName in "penStyle penColor penWidth penCapStyle".split():
        assert widget is not None, propName

    prop = _core.getNamedProperty(widget, "alignment")
    child = _core.getSubElement(prop, "set")
    assert child is not None
    assert child.text == "Qt::AlignCenter"
