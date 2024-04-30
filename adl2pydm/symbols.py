"""
symbols used in GUI screen translation

describe the various symbols used in:

* MEDM's .adl files (from the source code)
* PyDM screen files

from the spreadsheet: ref/"MEDM object names.xlsx"
"""

from collections import namedtuple

PyDM_CustomWidget = namedtuple("PyDM_CustomWidget", "cls extends header")


# adl_blocks = {
#     "<<basic attribute>>" : dict(type=""),
#     "<<color map>>" : dict(type=""),
#     "<<color rules>>" : dict(type=""),
#     "attr" : dict(type="nested"),
#     "basic attribute" : dict(type="static"),
#     "children" : dict(type=""),
#     "color map" : dict(type="static"),
#     "colors" : dict(type=""),
#     "control" : dict(type="nested"),
#     "display" : dict(type="static"),
#     "dl_color" : dict(type="nested"),
#     "dl_color_rule" : dict(type=""),
#     "dynamic attribute" : dict(type="static"),
#     "falling line" : dict(type="static"),
#     "file" : dict(type="static"),
#     "limits" : dict(type=""),
#     "mod" : dict(type=""),
#     "monitor" : dict(type="nested"),
#     "object" : dict(type="nested"),
#     "param" : dict(type=""),
#     "plotcom" : dict(type="nested"),
#     "points" : dict(type=""),
#     "rising line" : dict(type="static"),
#     "x_axis" : dict(type=""),
#     "y1_axis" : dict(type=""),
#     "y2_axis" : dict(type=""),
#     }


# adl_block_lists = {     # key starts the line
#     "command[" : dict(type="nested"),
#     "display[" : dict(type="nested"),
#     "info[" : dict(type="nested"),
#     "pen[" : dict(type="nested"),
#     "rulechan[" : dict(type="nested"),  # in monitor block
#     "trace[" : dict(type="nested"),
#     }


adl_widgets = {
    "arc": dict(type="static", pydm_widget="PyDMDrawingPie"),
    "bar": dict(type="monitor", pydm_widget="PyDMScaleIndicator"),
    "byte": dict(type="monitor", pydm_widget="PyDMByteIndicator"),
    "cartesian plot": dict(type="monitor", pydm_widget="PyDMWaveformPlot"),
    "choice button": dict(type="controller", pydm_widget="PyDMEnumButton"),
    "composite": dict(type="static", pydm_widget="PyDMFrame"),
    # "composite": dict(type="static", pydm_widget="PyDMAbsoluteGeometry"),
    "embedded display": dict(type="static", pydm_widget="PyDMEmbeddedDisplay"),
    "image": dict(type="monitor", pydm_widget="PyDMDrawingImage"),
    "indicator": dict(type="monitor", pydm_widget="PyDMScaleIndicator"),
    "menu": dict(type="controller", pydm_widget="PyDMEnumComboBox"),
    "message button": dict(type="controller", pydm_widget="PyDMPushButton"),
    "meter": dict(type="monitor", pydm_widget="PyDMScaleIndicator"),
    "oval": dict(type="static", pydm_widget="PyDMDrawingEllipse"),
    "polygon": dict(type="static", pydm_widget="PyDMDrawingIrregularPolygon"),
    "polyline": dict(type="static", pydm_widget="PyDMDrawingPolyline"),
    "rectangle": dict(type="static", pydm_widget="PyDMDrawingRectangle"),
    "related display": dict(type="static", pydm_widget="PyDMRelatedDisplayButton"),
    "shell command": dict(type="static", pydm_widget="PyDMShellCommand"),
    "strip chart": dict(type="monitor", pydm_widget="PyDMTimePlot"),
    "text": dict(type="static", pydm_widget="PyDMLabel"),
    "text entry": dict(type="controller", pydm_widget="PyDMLineEdit"),
    "text update": dict(type="monitor", pydm_widget="PyDMLabel"),
    "valuator": dict(type="controller", pydm_widget="PyDMSlider"),
    "wheel switch": dict(type="controller", pydm_widget="PyDMSpinbox"),
}


"""
describes the PyDM connection to Qt

example:

    "cls",       "PyDMLineEdit"
    "extends",   "QLineEdit"
    "header",    "pydm.widgets.line_edit"

"""

pydm_widgets = dict(
    # PyDMAbsoluteGeometry=PyDM_CustomWidget("PyDMAbsoluteGeometry", "QWidget", "pydm.widgets.absolute_geometry"),
    PyDMTabWidget=PyDM_CustomWidget("PyDMTabWidget", "QTabWidget", "pydm.widgets.tab_bar"),
    PyDMLabel=PyDM_CustomWidget("PyDMLabel", "QLabel", "pydm.widgets.label"),
    PyDMTimePlot=PyDM_CustomWidget("PyDMTimePlot", "QGraphicsView", "pydm.widgets.timeplot"),
    PyDMWaveformPlot=PyDM_CustomWidget("PyDMWaveformPlot", "QGraphicsView", "pydm.widgets.waveformplot"),
    PyDMScatterPlot=PyDM_CustomWidget("PyDMScatterPlot", "QGraphicsView", "pydm.widgets.scatterplot"),
    PyDMByteIndicator=PyDM_CustomWidget("PyDMByteIndicator", "QWidget", "pydm.widgets.byte"),
    PyDMCheckbox=PyDM_CustomWidget("PyDMCheckbox", "QCheckBox", "pydm.widgets.checkbox"),
    PyDMDrawingArc=PyDM_CustomWidget("PyDMDrawingArc", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingChord=PyDM_CustomWidget("PyDMDrawingChord", "PyDMDrawingArc", "pydm.widgets.drawing"),
    PyDMDrawingCircle=PyDM_CustomWidget("PyDMDrawingCircle", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingEllipse=PyDM_CustomWidget("PyDMDrawingEllipse", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingImage=PyDM_CustomWidget("PyDMDrawingImage", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingLine=PyDM_CustomWidget("PyDMDrawingLine", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingPie=PyDM_CustomWidget("PyDMDrawingPie", "PyDMDrawingArc", "pydm.widgets.drawing"),
    PyDMDrawingRectangle=PyDM_CustomWidget("PyDMDrawingRectangle", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingTriangle=PyDM_CustomWidget("PyDMDrawingTriangle", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingPolygon=PyDM_CustomWidget("PyDMDrawingPolygon", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingPolyline=PyDM_CustomWidget("PyDMDrawingPolyline", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingIrregularPolygon=PyDM_CustomWidget(
        "PyDMDrawingIrregularPolygon", "QWidget", "pydm.widgets.drawing"
    ),
    PyDMEmbeddedDisplay=PyDM_CustomWidget("PyDMEmbeddedDisplay", "QFrame", "pydm.widgets.embedded_display"),
    PyDMEnumButton=PyDM_CustomWidget("PyDMEnumButton", "QWidget", "pydm.widgets.enum_button"),
    PyDMEnumComboBox=PyDM_CustomWidget("PyDMEnumComboBox", "QComboBox", "pydm.widgets.enum_combo_box"),
    PyDMFrame=PyDM_CustomWidget("PyDMFrame", "QFrame", "pydm.widgets.frame"),
    PyDMImageView=PyDM_CustomWidget("PyDMImageView", "QWidget", "pydm.widgets.image"),
    PyDMLineEdit=PyDM_CustomWidget("PyDMLineEdit", "QLineEdit", "pydm.widgets.line_edit"),
    PyDMLogDisplay=PyDM_CustomWidget("PyDMLogDisplay", "QWidget", "pydm.widgets.logdisplay"),
    PyDMPushButton=PyDM_CustomWidget("PyDMPushButton", "QPushButton", "pydm.widgets.pushbutton"),
    PyDMRelatedDisplayButton=PyDM_CustomWidget(
        "PyDMRelatedDisplayButton", "QPushButton", "pydm.widgets.related_display_button"
    ),
    PyDMShellCommand=PyDM_CustomWidget("PyDMShellCommand", "QPushButton", "pydm.widgets.shell_command"),
    PyDMSlider=PyDM_CustomWidget("PyDMSlider", "QFrame", "pydm.widgets.slider"),
    PyDMSpinbox=PyDM_CustomWidget("PyDMSpinbox", "QDoubleSpinBox", "pydm.widgets.spinbox"),
    PyDMScaleIndicator=PyDM_CustomWidget("PyDMScaleIndicator", "QFrame", "pydm.widgets.scale"),
    PyDMSymbol=PyDM_CustomWidget("PyDMSymbol", "QWidget", "pydm.widgets.symbol"),
    PyDMWaveformTable=PyDM_CustomWidget("PyDMWaveformTable", "QTableWidget", "pydm.widgets.waveformtable"),
)
