# -*- coding: utf-8 -*-
import arcpy
import os
import sys

import configuration
try:
    reload(configuration)  # Python 2.7
except NameError:
    try:
        import importlib # Python 3.4
        importlib.reload(configuration)
    except Exception:
    	arcpy.AddError('Could not load configuration module')
    	sys.exit()

# Load and refresh the refresh_modules module
from LUCI_PTFs.lib.external.six.moves import reload_module
import LUCI_PTFs.lib.refresh_modules as refresh_modules
reload_module(refresh_modules)
from LUCI_PTFs.lib.refresh_modules import refresh_modules

import LUCI_PTFs.lib.input_validation as input_validation
refresh_modules(input_validation)

import LUCI_PTFs.tool_classes.c_SoilParam as c_SoilParam
refresh_modules(c_SoilParam)
SoilParam = c_SoilParam.SoilParam

import LUCI_PTFs.tool_classes.c_SoilMoisture as c_SoilMoisture
refresh_modules(c_SoilMoisture)
SoilMoisture = c_SoilMoisture.SoilMoisture

import LUCI_PTFs.tool_classes.c_CalcKsat as c_CalcKsat
refresh_modules(c_CalcKsat)
CalcKsat = c_CalcKsat.CalcKsat

import LUCI_PTFs.tool_classes.c_BrooksCorey as c_BrooksCorey
refresh_modules(c_BrooksCorey)
BrooksCorey = c_BrooksCorey.BrooksCorey

import LUCI_PTFs.tool_classes.c_CalcVG as c_CalcVG
refresh_modules(c_CalcVG)
calcVG_PTFs = c_CalcVG.calcVG_PTFs

import LUCI_PTFs.tool_classes.c_CalcPointPTFs as c_CalcPointPTFs
refresh_modules(c_CalcPointPTFs)
calcPoint_PTFs = c_CalcPointPTFs.calcPoint_PTFs

##########################
### Toolbox definition ###
##########################

class Toolbox(object):

    def __init__(self):
        self.label = u'LUCI PTF v1.0'
        self.alias = u'LUCI_PTF'
        # self.tools = [SoilMoisture, CalcKsat, BrooksCorey, calcVG_PTFs, calcPoint_PTFs]
        self.tools = [calcVG_PTFs, calcPoint_PTFs, CalcKsat, BrooksCorey]
