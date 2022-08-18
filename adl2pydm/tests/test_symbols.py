import pytest

from .. import symbols


@pytest.mark.parametrize(
    "widget_set, length",
    [
        [symbols.adl_widgets, 24],
        [symbols.pydm_widgets, 35],
    ],
)
def test_symbols_dict(widget_set, length):
    assert isinstance(widget_set, dict)
    assert len(widget_set) == length


def test_symbols_adl_widgets():
    for k, w in symbols.adl_widgets.items():
        assert isinstance(w, dict)
        assert len(w) == 2
    # "arc" : dict(type="static", pydm_widget="PyDMDrawingArc"),
    w = symbols.adl_widgets["arc"]
    assert w["type"] == "static"
    assert w["pydm_widget"] == "PyDMDrawingPie"
    assert w["type"] == "static"


def test_symbols_pydm_widgets():
    for k, w in symbols.pydm_widgets.items():
        assert isinstance(w, symbols.PyDM_CustomWidget)
        assert len(w) == 3
        # PyDMLabel = PyDM_CustomWidget("PyDMLabel", "QLabel", "pydm.widgets.label"),
    w = symbols.pydm_widgets["PyDMLabel"]
    assert w.cls == "PyDMLabel"
    assert w.extends == "QLabel"
    assert w.header == "pydm.widgets.label"
