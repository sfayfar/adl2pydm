
"""
structures built from MEDM's DISPLAY_LIST.txt file in the source distribution

General rules:  order of things in display list

    + file
    + display
    + attributes and static objects ...
    + dynamic attributes and static objects...
    + monitors
    + controllers
    + plots

"""

static_objects = {
    "file" : [],
    "display" : ["object", "cmap", "clr", "bclr"],
    "color map" : ["ncolors", "dl_color"],
    "basic atribute" : ["attr",],
    "dynamic attribute" : ["attr", "dynattr"],            # not fully implemented
    "rectangle" : ["object"],
    "oval" : ["object"],
    "arc" : ["object", "begin", "path"],
    "text" : ["object", "textix", "align", "format"],
    "falling line" : ["object"],
    "rising line" : ["object"],
    "related display" : ["object", "clr", "bclr"],
}


monitor_objects = {
    "bar" : ["object", "monitor", "label", "clrmod", "direction", "fillmod", "pad"],
    "indicator" : [],                        # not yet implemented
    "meter" : ["object", "monitor", "label", "clrmod", "pad"],
    "strip chart" : [],                        # not fully implemented
    "text update" : ["object", "monitor", "clrmod", "format", "align", "pad"],
}


controller_objects = {
    "choice button" : ["object", "control", "label", "clrmod", "stacking", "pad"],
    # (button == choice button)
    "button" : ["object", "control", "label", "clrmod", "stacking", "pad"],
    "message button" : [],            # not yet implemented
    "menu" : [],                # not yet implemented
    "text entry" : [],           # not yet implemented
    "valuator" : ["object", "control", "label", "clrmod", "direction", "pad"],
}


nested_objects = {
    "dl_color" : ["r", "g", "b", "inten"],
    "object" : ["x", "y", "width", "height"],
    "attr" : ["clr", "style", "fill", "width"],
    "attr" : ["mod", "chan"],
    "dynattr" : ["mod", "chan"],
    "display[i]" : ["label", "name", "args"],
    "monitor" : ["rdbk", "clr", "bclr"],
    "control" : ["ctrl", "clr", "bclr"],
    "plotcom" : [],                # not yet implemented
    "pen" : [],                # not yet implemented
}

other_keywords = [
    "clr",
    "bclr",
    ]

"""
Current State of Affairs
========================
========================

clrmod = {static, alarm, discrete}
   static: color = foreground color
   alarm:  color = alarm color (based on current channel alarm condition)
   discrete: implemented as alarm (so does LANL)

label = {none, outline, limits, channel}
   none: no label
   outline: no label
   limits:  include low and high limits in display
   channel: include low and high limits and channel name
"""


"""
These names were found by searching all .adl files on my workstation 
for lines that end in "{", removing white space indentation, and sorting.

arc
attr
bar
"<<basic attribute>>"
"basic attribute"
byte
"cartesian plot"
children
"choice button"
"<<color map>>"
"color map"
"<<color rules>>"
colors
command[0]
command[2]
command[3]
command[4]
command[5]
command[6]
command[7]
composite
control
display
display[0]
display[1]
display[10]
display[11]
display[12]
display[13]
display[14]
display[15]
display[2]
display[3]
display[4]
display[5]
display[6]
display[7]
display[8]
display[9]
dl_color
dl_color_rule
"dynamic attribute"
file
hildren
image
indicator
"indicator"
info[0]
info[1]
info[10]
info[11]
info[12]
info[13]
info[14]
info[15]
info[2]
info[3]
info[4]
info[5]
info[6]
info[7]
info[8]
info[9]
limits
menu
"message button"
meter
mod
monitor
object
oval
param
pen[0]
pen[1]
pen[2]
pen[3]
pen[4]
plotcom
points
polygon
polyline
rectangle
"related display"
"shell command"
"strip chart"
text
"text"
"text entry"
"text update"
trace[0]
trace[1]
trace[2]
trace[3]
trace[4]
trace[5]
trace[6]
trace[7]
valuator
"valuator"
x_axis
y1_axis
y2_axis
"""
