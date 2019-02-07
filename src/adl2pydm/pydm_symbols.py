
"""
describe the various symbols used in PyDM screen files
"""


"""
describes the PyDM connection to Qt

example:

    "cls",       "PyDMLineEdit"
    "extends",   "QLineEdit"
    "header",    "pydm.widgets.line_edit"

"""

CustomWidget = namedtuple('CustomWidget', 'cls extends header')

pydm_custom_widgets = dict(
    PyDMTabWidget = CustomWidget("PyDMTabWidget", "QTabWidget", "pydm.widgets.tab_bar"),
    PyDMLabel = CustomWidget("PyDMLabel", "QLabel", "pydm.widgets.label"),
    PyDMTimePlot = CustomWidget("PyDMTimePlot", "QGraphicsView", "pydm.widgets.timeplot"),
    PyDMWaveformPlot = CustomWidget("PyDMWaveformPlot", "QGraphicsView", "pydm.widgets.waveformplot"),
    PyDMScatterPlot = CustomWidget("PyDMScatterPlot", "QGraphicsView", "pydm.widgets.scatterplot"),
    PyDMByteIndicator = CustomWidget("PyDMByteIndicator", "QWidget", "pydm.widgets.byte"),
    PyDMCheckbox = CustomWidget("PyDMCheckbox", "QCheckBox", "pydm.widgets.checkbox"),
    PyDMDrawingArc = CustomWidget("PyDMDrawingArc", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingChord = CustomWidget("PyDMDrawingChord", "PyDMDrawingArc", "pydm.widgets.drawing"),
    PyDMDrawingCircle = CustomWidget("PyDMDrawingCircle", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingEllipse = CustomWidget("PyDMDrawingEllipse", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingImage = CustomWidget("PyDMDrawingImage", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingLine = CustomWidget("PyDMDrawingLine", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingPie = CustomWidget("PyDMDrawingPie", "PyDMDrawingArc", "pydm.widgets.drawing"),
    PyDMDrawingRectangle = CustomWidget("PyDMDrawingRectangle", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingTriangle = CustomWidget("PyDMDrawingTriangle", "QWidget", "pydm.widgets.drawing"),
    PyDMDrawingPolygon = CustomWidget("PyDMDrawingPolygon", "QWidget", "pydm.widgets.drawing"),
    PyDMEmbeddedDisplay = CustomWidget("PyDMEmbeddedDisplay", "QFrame", "pydm.widgets.embedded_display"),
    PyDMEnumButton = CustomWidget("PyDMEnumButton", "QWidget", "pydm.widgets.enum_button"),
    PyDMEnumComboBox = CustomWidget("PyDMEnumComboBox", "QComboBox", "pydm.widgets.enum_combo_box"),
    PyDMFrame = CustomWidget("PyDMFrame", "QFrame", "pydm.widgets.frame"),
    PyDMImageView = CustomWidget("PyDMImageView", "QWidget", "pydm.widgets.image"),
    PyDMLineEdit = CustomWidget("PyDMLineEdit", "QLineEdit", "pydm.widgets.line_edit"),
    PyDMLogDisplay = CustomWidget("PyDMLogDisplay", "QWidget", "pydm.widgets.logdisplay"),
    PyDMPushButton = CustomWidget("PyDMPushButton", "QPushButton", "pydm.widgets.pushbutton"),
    PyDMRelatedDisplayButton = CustomWidget("PyDMRelatedDisplayButton", "QPushButton", "pydm.widgets.related_display_button"),
    PyDMShellCommand = CustomWidget("PyDMShellCommand", "QPushButton", "pydm.widgets.shell_command"),
    PyDMSlider = CustomWidget("PyDMSlider", "QFrame", "pydm.widgets.slider"),
    PyDMSpinbox = CustomWidget("PyDMSpinbox", "QDoubleSpinBox", "pydm.widgets.spinbox"),
    PyDMScaleIndicator = CustomWidget("PyDMScaleIndicator", "QFrame", "pydm.widgets.scale"),
    PyDMSymbol = CustomWidget("PyDMSymbol", "QWidget", "pydm.widgets.symbol"),
    PyDMWaveformTable = CustomWidget("PyDMWaveformTable", "QTableWidget", "pydm.widgets.waveformtable"),
)
