import arcpy
import configuration
import os
from LUCI_PTFs.lib.refresh_modules import refresh_modules

class BrooksCorey(object):

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
    
    def __init__(self):
        self.label = u'Calculate using Brooks-Corey'
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
        param.displayName = u'Input soil shapefile'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Feature Class'
        params.append(param)

        # 4 PTF_of_choice
        param = arcpy.Parameter()
        param.name = u'PTF_of_choice'
        param.displayName = u'PTFs of choice'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'String'
        param.value = u'Cosby et al. (1984) - Silt and Clay'
        param.filter.list = [u'Cosby et al. (1984) - Silt and Clay',
                             u'Cosby et al. (1984) - Sand, Silt and Clay',
                             u'Rawls and Brakensiek (1985)',
                             u'Campbell and Shiozava (1992)', u'Saxton et al. (1986)']
        params.append(param)

        # 5 Output_Layer_SoilParam
        param = arcpy.Parameter()
        param.name = u'Output_Layer_SoilParam'
        param.displayName = u'Soil'
        param.parameterType = 'Derived'
        param.direction = 'Output'
        param.datatype = u'Feature Layer'
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

        import LUCI_PTFs.tools.t_brooks_corey as t_brooks_corey
        refresh_modules(t_brooks_corey)

        t_brooks_corey.function(parameters)
