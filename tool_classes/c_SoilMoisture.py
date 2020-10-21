import arcpy
import configuration
import os
from LUCI_PTFs.lib.refresh_modules import refresh_modules

class SoilMoisture(object):

    class ToolValidator:
        """Class for validating a tool's parameter values and controlling the behavior of the tool's dialog."""
    
        def __init__(self, parameters):
            """Setup the Geoprocessor and the list of tool parameters."""
            self.params = parameters
    
        def initializeParameters(self):
            """Refine the properties of a tool's parameters.
            This method is called when the tool is opened."""
            return
        
        def updateParameters(self):
            """Modify the values and properties of parameters before internal validation is performed.
            This method is called whenever a parameter has been changed."""

            return
    
        def updateMessages(self):
            """Modify the messages created by internal validation for each tool parameter.
            This method is called after internal validation."""

            import LUCI_PTFs.lib.input_validation as input_validation
            refresh_modules(input_validation)

            input_validation.checkFilePaths(self)
            input_validation.checkThresholdValues(self, "SoilMoisture")
    
    def __init__(self):
        self.label = u'Calculate soil moisture at thresholds'
        self.canRunInBackground = False

    def getParameterInfo(self):

        params = []

        # 0 Output__Success
        param = arcpy.Parameter()
        param.name = u'Output__Success'
        param.displayName = u'Output: Success'
        param.parameterType = 'Derived'
        param.direction = 'Output'
        param.datatype = u'Boolean'
        params.append(param)

        # 1 Run_system_checks
        param = arcpy.Parameter()
        param.name = u'Run_system_checks'
        param.displayName = u'Run_system_checks'
        param.parameterType = 'Derived'
        param.direction = 'Output'
        param.datatype = u'Boolean'
        param.value = u'True'
        params.append(param)

        # 2 Output_folder
        param = arcpy.Parameter()
        param.name = u'Output_folder'
        param.displayName = u'Output folder'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Folder'
        params.append(param)

        # 3 Input_shapefile
        param = arcpy.Parameter()
        param.name = u'Input_shapefile'
        param.displayName = u'Input soil shapefile with water content information'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Feature Class'
        params.append(param)

        # 4 Field_FieldCapacity
        param = arcpy.Parameter()
        param.name = u'Field_FieldCapacity'
        param.displayName = u'Field containing water content (vol) for field capacity'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'String'
        params.append(param)

        # 5 Field_PWP
        param = arcpy.Parameter()
        param.name = u'Field_PWP'
        param.displayName = u'Field containing water content (vol) for permanent wilting point'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'String'
        params.append(param)

        # 6 Field_Saturation
        param = arcpy.Parameter()
        param.name = u'Field_Saturation'
        param.displayName = u'Field containing water content (vol) for saturation'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'String'
        params.append(param)

        # 7 Calculate_RAW_choice
        param = arcpy.Parameter()
        param.name = u'Calculate_RAW_choice'
        param.displayName = u'Calculate readily-available water using:'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'String'
        param.value = u'Fraction'
        param.filter.list = [u'Fraction', u'Field containing WC (vol) at critical point']
        params.append(param)

        # 8 RAW_fraction
        param = arcpy.Parameter()
        param.name = u'RAW_fraction'
        param.displayName = u'Readily-available water fraction of plant available water'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Double'
        param.value = u'0.5'
        params.append(param)

        # 9 Field_Critical_Point
        param = arcpy.Parameter()
        param.name = u'Field_Critical_Point'
        param.displayName = u'Field containing water content (vol) for critical point'
        param.parameterType = 'Optional'
        param.direction = 'Input'
        param.datatype = u'String'
        params.append(param)

        # 10 Calculate_mm
        param = arcpy.Parameter()
        param.name = u'Calculate_mm'
        param.displayName = u'Calculate water content (mm) using rooting depth below?'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Boolean'
        param.value = u'False'
        params.append(param)

        # 11 Rooting_depth
        param = arcpy.Parameter()
        param.name = u'Rooting_depth'
        param.displayName = u'Rooting depth'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Double'
        param.value = u'100'
        params.append(param)

        return params

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateParameters()

    def updateMessages(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateMessages()

    def execute(self, parameters, messages):

        import LUCI_PTFs.tools.t_soil_moisture as t_soil_moisture
        refresh_modules(t_soil_moisture)

        t_soil_moisture.function(parameters)
