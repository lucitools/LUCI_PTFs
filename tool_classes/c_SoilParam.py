import arcpy
import configuration
import os
from LUCI_PTFs.lib.refresh_modules import refresh_modules

class SoilParam(object):

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

            # Populate converstion factor automatically when either OM or OC is chosen has been chosen
            CarbParamNo = None
            ConvFactorParamNo = None
            for i in range(0, len(self.params)):
                if self.params[i].name == 'Carbon_content':
                    CarbParamNo = i
                if self.params[i].name == 'Conversion_factor':
                    ConvFactorParamNo = i

            CarbPairs = [('Organic carbon', 1.724),
                         ('Organic matter', 0.58)]

            if CarbParamNo is not None and ConvFactorParamNo is not None:
                # If this is the most recently changed param ...
                if not self.params[CarbParamNo].hasBeenValidated:

                    # Update the linking code with the correct value
                    for CarbPair in CarbPairs:
                        if self.params[CarbParamNo].valueAsText == CarbPair[0]:
                            self.params[ConvFactorParamNo].value = CarbPair[1]
            
            # Populate pressures
            vgChoiceNo = None
            vgPressuresNo = None
            for i in range(0, len(self.params)):
                if self.params[i].name == 'VG_of_choice':
                    vgChoiceNo = i
                if self.params[i].name == 'Pressure_heads_VG':
                    vgPressuresNo = i

            vgPairs = [('Wosten et al. (1999) topsoil', '10 30 100 330 1000 2000 10000 15000'),
                       ('Wosten et al. (1999) subsoil', '10 30 100 330 1000 2000 10000 15000'),
                       ('Vereecken et al. (1989)', '10 30 100 330 1000 2000 10000 15000'),
                       ('Zacharias and Wessolek (2007)', '1 3 10 33 100 200 1000 1500')]

            if vgChoiceNo is not None and vgPressuresNo is not None:
                # If this is the most recently changed param ...
                if not self.params[vgChoiceNo].hasBeenValidated:

                    # Update the linking code with the correct value
                    for vgPair in vgPairs:
                        if self.params[vgChoiceNo].valueAsText == vgPair[0]:
                            self.params[vgPressuresNo].value = vgPair[1]            

            input_validation.checkFilePaths(self)
    
    def __init__(self):
        self.label = u'LUCI soil parameterisation'
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

        # 4 Calculate_PTF
        param = arcpy.Parameter()
        param.name = u'Calculate_PTF'
        param.displayName = u'Estimate soil moisture content using point-PTFs'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Boolean'
        param.value = u'True'
        params.append(param)

        # 5 PTF_of_choice
        param = arcpy.Parameter()
        param.name = u'PTF_of_choice'
        param.displayName = u'PTFs of choice'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'String'
        param.value = u'Nguyen et al. (2014)'
        param.filter.list = [u'Nguyen et al. (2014)', u'Adhikary et al. (2008)',
                             u'Rawls et al. (1982)', u'Saxton et al. (1986)',
                             u'Hall et al. (1977) topsoil', u'Hall et al. (1977) subsoil', u'Gupta and Larson (1979)',
                             u'Batjes (1996)', u'Saxton and Rawls (2006)',
                             u'Pidgeon (1972)', u'Lal (1978)', u'Aina and Periaswamy (1985)',
                             u'Manrique and Jones (1991)', u'van Den Berg et al. (1997)',
                             u'Tomasella and Hodnett (1998)', u'Reichert et al. (2009) - Sand, silt, clay, OM, BD',
                             u'Reichert et al. (2009) - Sand, silt, clay, BD', u'Botula Manyala (2013)',
                             u'Shwetha and Varija (2013)', u'Dashtaki et al. (2010)',
                             u'Santra et al. (2018)']
        params.append(param)

        # 6 Calculate_VG
        param = arcpy.Parameter()
        param.name = u'Calculate_VG'
        param.displayName = u'Estimate soil moisture content and generate soil moisture retention curve using PTFs for van Genuchten model'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Boolean'
        param.value = u'False'
        params.append(param)

        # 7 VG_of_choice
        param = arcpy.Parameter()
        param.name = u'VG_of_choice'
        param.displayName = u'PTFs of choice for van Genuchten model'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'String'
        param.value = u'Wosten et al. (1999) topsoil'
        param.filter.list = [u'Wosten et al. (1999) topsoil', u'Wosten et al. (1999) subsoil',
                             u'Vereecken et al. (1989)', u'Zacharias and Wessolek (2007)',
                             u'Weynants et al. (2009)',
                             u'Dashtaki et al. (2010)', u'Hodnett and Tomasella (2002)']
        params.append(param)

        # 8 Pressure_heads_VG
        param = arcpy.Parameter()
        param.name = u'Pressure_heads_VG'
        param.displayName = u'Specify pressures to calculate water content using van Genuchten (space delimited)'
        param.parameterType = 'Optional'
        param.direction = 'Input'
        param.datatype = u'String'
        param.value = u'1 3 10 33 100 200 1000 1500'
        params.append(param)

        # 9 Calculate_MVG
        param = arcpy.Parameter()
        param.name = u'Calculate_MVG'
        param.displayName = u'Estimate unsaturated hydraulic conductivity and generate hydraulic conductivity curve using PTFs for Mualem van Genuchten model'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Boolean'
        param.value = u'False'
        params.append(param)

        # 10 MVG_of_choice
        param = arcpy.Parameter()
        param.name = u'MVG_of_choice'
        param.displayName = u'Estimate Mualem van Genuchten model parameters'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'String'
        param.value = u'Wosten et al. (1999) topsoil'
        param.filter.list = [u'Wosten et al. (1999) topsoil', u'Wosten et al. (1999) subsoil',
                             u'Weynants et al. (2009)']
        params.append(param)

        # 11 Carbon_content
        param = arcpy.Parameter()
        param.name = u'Carbon_content'
        param.displayName = u'Carbon: Does your dataset contain organic carbon or organic matter?'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'String'
        param.value = u'Organic carbon'
        param.filter.list = [u'Organic carbon', u'Organic matter']
        params.append(param)

        # 12 Conversion_factor
        param = arcpy.Parameter()
        param.name = u'Conversion_factor'
        param.displayName = u'Carbon: enter a conversion factor'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Double'
        param.value = u'1.724'
        params.append(param)

        # 13 Rerun_tool
        param = arcpy.Parameter()
        param.name = u'Rerun_tool'
        param.displayName = u'Rerun tool (will continue previous run from the point where any errors occurred)'
        param.parameterType = 'Required'
        param.direction = 'Input'
        param.datatype = u'Boolean'
        param.value = u'False'
        params.append(param)

        # 14 Output_Layer_SoilParam
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

        import LUCI_PTFs.tools.t_soil_param as t_soil_param
        refresh_modules(t_soil_param)

        t_soil_param.function(parameters)
