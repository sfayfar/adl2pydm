
"""
symbols used in MEDM's .adl files (from the source code)

from the spreadsheet: ref/"MEDM object names.xlsx"
"""


blocks = {
    "<<basic attribute>>" : dict(type=""),
    "<<color map>>" : dict(type=""),
    "<<color rules>>" : dict(type=""),
    "attr" : dict(type="nested"),
    "basic attribute" : dict(type="static"),
    "children" : dict(type=""),
    "color map" : dict(type="static"),
    "colors" : dict(type=""),
    "control" : dict(type="nested"),
    "display" : dict(type="static"),
    "dl_color" : dict(type="nested"),
    "dl_color_rule" : dict(type=""),
    "dynamic attribute" : dict(type="static"),
    "falling line" : dict(type="static"),
    "file" : dict(type="static"),
    "limits" : dict(type=""),
    "mod" : dict(type=""),
    "monitor" : dict(type="nested"),
    "object" : dict(type="nested"),
    "plotcom" : dict(type="nested"),
    "points" : dict(type=""),
    "rising line" : dict(type="static"),
    "x_axis" : dict(type=""),
    "y1_axis" : dict(type=""),
    "y2_axis" : dict(type=""),
    }


block_lists = {     # key starts the line
    "command[" : dict(type="nested"),
    "display[" : dict(type="nested"),
    "info[" : dict(type="nested"),
    "pen[" : dict(type="nested"),
    "trace[" : dict(type="nested"),
    }


widgets = {
    "arc" : dict(type="static", pydm_widget="PyDMDrawingArc"),
    "bar" : dict(type="monitor", pydm_widget=""),
    "byte" : dict(type="monitor", pydm_widget=""),
    "cartesian plot" : dict(type="monitor", pydm_widget="PyDMScatterPlot"),
    "choice button" : dict(type="controller", pydm_widget="?PyDMEnumButton"),
    "composite" : dict(type="static", pydm_widget="PyDMFrame"),
    "embedded display" : dict(type="static", pydm_widget="PyDMEmbeddedDisplay"),
    "image" : dict(type="monitor", pydm_widget="PyDMImageView"),
    "indicator" : dict(type="monitor", pydm_widget=""),
    "menu" : dict(type="controller", pydm_widget="?PyDMEnumButton"),
    "message button" : dict(type="controller", pydm_widget="PyDMPushButton"),
    "meter" : dict(type="monitor", pydm_widget="?PyDMScaleIndicator"),
    "oval" : dict(type="static", pydm_widget="PyDMDrawingEllipse"),
    "param" : dict(type="static", pydm_widget=""),
    "polygon" : dict(type="static", pydm_widget="PyDMDrawingPolygon"),
    "polyline" : dict(type="static", pydm_widget=""),
    "rectangle" : dict(type="static", pydm_widget=""),
    "related display" : dict(type="static", pydm_widget="PyDMRelatedDisplayButton"),
    "shell command" : dict(type="static", pydm_widget="PyDMShellCommand"),
    "strip chart" : dict(type="monitor", pydm_widget="PyDMTimePlot"),
    "text" : dict(type="static", pydm_widget="PyDMLabel"),
    "text entry" : dict(type="controller", pydm_widget="PyDMLineEdit"),
    "text update" : dict(type="monitor", pydm_widget="PyDMLineEdit + readOnly=True"),
    "valuator" : dict(type="controller", pydm_widget=""),
    "wheel switch" : dict(type="controller", pydm_widget=""),
    }
