#!/bin/bash

#   . env_setup.sh

# conda activate pydm
export PYQTDESIGNERPATH=${HOME}/Documents/projects/BCDA-APS/adl2pydm/pyqtdesignerpath:
export QT_PLUGIN_PATH=${CONDA_PREFIX}/plugins

# the  PYQTDESIGNERPATH directory contains this file:  pydm_designer_plugin.py 
# and that file contains this one line:
#     from pydm.widgets.qtplugins import *

