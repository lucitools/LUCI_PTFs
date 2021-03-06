import arcpy
import configuration
import os
from LUCI_PTFs.lib.refresh_modules import refresh_modules

class CalcKsat(object):

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
            input_validation.checkThresholdValues(self, "CalcKsat")
    
    def __init__(self):
        self.label = u'Calculate saturated hydraulic conductivity (Ksat)'
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

        # 4 Ksat_of_choice
        param = arcpy.Parameter()
        param.name = u'Ksat_of_choice'
        param.displayName = u'Select PTF to estimate Ksat'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'String'
        param.value = u'Cosby et al. (1984)'
        param.filter.list = [u'Cosby et al. (1984)', u'Puckett et al. (1985)',
                             u'Jabro (1992)', u'Campbell and Shiozawa (1994)',
                             u'Ferrer Julia et al. (2004) - Sand',
                             u'Ferrer Julia et al. (2004) - Sand, clay, OM',
                             u'Brakensiek et al. (1984)',
                             u'Ahuja et al. (1989)', u'Minasny and McBratney (2000)']
        params.append(param)

        # 5 Field_FieldCapacity
        param = arcpy.Parameter()
        param.name = u'Field_FieldCapacity'
        param.displayName = u'Field containing water content (vol) for field capacity'
        param.parameterType = 'Optional'
        param.direction = 'Input'
        param.datatype = u'String'
        params.append(param)

        # 6 Field_Saturation
        param = arcpy.Parameter()
        param.name = u'Field_Saturation'
        param.displayName = u'Field containing water content (vol) for saturation'
        param.parameterType = 'Optional'
        param.direction = 'Input'
        param.datatype = u'String'
        params.append(param)

        # 7 Carbon_content
        param = arcpy.Parameter()
        param.name = u'Carbon_content'
        param.displayName = u'Carbon: Does your dataset contain organic carbon or organic matter?'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'String'
        param.value = u'Organic carbon'
        param.filter.list = [u'Organic carbon', u'Organic matter']
        params.append(param)

        # 8 Conversion_factor
        param = arcpy.Parameter()
        param.name = u'Conversion_factor'
        param.displayName = u'Carbon: enter a conversion factor'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Double'
        param.value = u'1.724'
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

        import LUCI_PTFs.tools.t_calc_ksat as t_calc_ksat
        refresh_modules(t_calc_ksat)

        t_calc_ksat.function(parameters)
