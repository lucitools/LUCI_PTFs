import arcpy
import os
import sys

import LUCI_PTFs.lib.log as log
import LUCI_PTFs.lib.common as common
import LUCI_PTFs.lib.progress as progress
import LUCI_PTFs.solo.soil_param as SoilParam

from LUCI_PTFs.lib.refresh_modules import refresh_modules
refresh_modules([log, common, SoilParam])

def function(params):

    try:
        pText = common.paramsAsText(params)

        # Get inputs
        runSystemChecks = common.strToBool(pText[1])
        outputFolder = pText[2]
        inputShapefile = pText[3]
        PTFChoice = common.strToBool(pText[4])
        PTF = pText[5]
        VGChoice = common.strToBool(pText[6])
        VG = pText[7]
        VGPressures = pText[8]
        MVGChoice =  common.strToBool(pText[9])
        MVG = pText[10]
        carbonContent = pText[11]
        carbonConFactor = pText[12]

        # Rerun parameter may not present when tool run as part of a batch run tool. If it is not, set rerun to False.
        try:
            rerun = common.strToBool(pText[13])
        except IndexError:
            rerun = False
        except Exception:
            raise

        # Create output folder
        if not os.path.exists(outputFolder):
            os.mkdir(outputFolder)

        # System checks and setup
        if runSystemChecks:
            common.runSystemChecks(outputFolder, rerun)

        # Set up logging output to file
        log.setupLogging(outputFolder)

        # Set up progress log file
        progress.initProgress(outputFolder, rerun)

        # Write input params to XML
        common.writeParamsToXML(params, outputFolder)

        if PTFChoice == True and VGChoice == False:
            log.info('Soil water content will be calculated using a PTF')

        elif PTFChoice == False and VGChoice == True:
            log.info('Soil water content will be calculated using the van Genuchten model')

        elif PTFChoice == False and VGChoice == False:
            log.error('Method for soil water content not chosen')
            log.error('Please tick box to choose either PTF method or van Genuchten method')
            sys.exit()

        elif PTFChoice == True and VGChoice == True:
            log.error('Both PTF and van Genuchten methods chosen')
            log.error('Please only pick one or the other')
            sys.exit()

        # Set option of PTF
        if PTF == 'Nguyen et al. (2014)':
            PTFOption = 'Nguyen_2014'

        elif PTF == 'Adhikary et al. (2008)':
            PTFOption = 'Adhikary_2014'

        elif PTF == 'Rawls et al. (1982)':
            PTFOption = 'Rawls_1982'

        elif PTF == 'Saxton et al. (1986)':
            PTFOption = 'Saxton_1986'

        elif PTF == 'Hall et al. (1977) topsoil':
            PTFOption = 'Hall_1977_top'

        elif PTF == 'Hall et al. (1977) subsoil':
            PTFOption = 'Hall_1977_sub'

        elif PTF == 'Gupta and Larson (1979)':
            PTFOption = 'GuptaLarson_1979'

        elif PTF == 'Batjes (1996)':
            PTFOption = 'Batjes_1996'

        elif PTF == 'Saxton and Rawls (2006)':
            PTFOption = 'SaxtonRawls_2006'

        elif PTF == 'Pidgeon (1972)':
            PTFOption = 'Pidgeon_1972'

        elif PTF == 'Lal (1978)':
            PTFOption = 'Lal_1978'

        elif PTF == 'Aina and Periaswamy (1985)':
            PTFOption = 'AinaPeriaswamy_1985'

        elif PTF == 'Manrique and Jones (1991)':
            PTFOption = 'ManriqueJones_1991'

        elif PTF == 'van Den Berg et al. (1997)':
            PTFOption = 'vanDenBerg_1997'

        elif PTF == 'Tomasella and Hodnett (1998)':
            PTFOption = 'TomasellaHodnett_1998'

        elif PTF == 'Reichert et al. (2009) - Sand, silt, clay, OM, BD':
            PTFOption = 'Reichert_2009_OM'

        elif PTF == 'Reichert et al. (2009) - Sand, silt, clay, BD':
            PTFOption = 'Reichert_2009'

        elif PTF == 'Botula Manyala (2013)':
            PTFOption = 'Botula_2013'

        elif PTF == 'Shwetha and Varija (2013)':
            PTFOption = 'ShwethaVarija_2013'

        elif PTF == 'Dashtaki et al. (2010)':
            PTFOption = 'Dashtaki_2010'

        elif PTF == 'Santra et al. (2018)':
            PTFOption = 'Santra_2018'

        else:
            log.error('Invalid PTF option')
            sys.exit()

        if VG == "Wosten et al. (1999) topsoil":
            VGOption = "Wosten_1999_top"

        elif VG == "Wosten et al. (1999) subsoil":
            VGOption = "Wosten_1999_sub"

        elif VG == "Vereecken et al. (1989)":
            VGOption = "Vereecken_1989"

        elif VG == "Zacharias and Wessolek (2007)":
            VGOption = "ZachariasWessolek_2007"

        elif VG == "Weynants et al. (2009)":
            VGOption = "Weynants_2009"

        elif VG == "Dashtaki et al. (2010)":
            VGOption = 'Dashtaki_2010'

        elif VG == "Hodnett and Tomasella (2002)":
            VGOption = 'HodnettTomasella_2002'

        else:
            log.error('Invalid PTF option')
            sys.exit()

        # Set Mualem-Van Genuchten choice
        if MVG == "Wosten et al. (1999) topsoil":
            MVGOption = "Wosten_1999_top"

        elif MVG == "Wosten et al. (1999) subsoil":
            MVGOption = "Wosten_1999_sub"

        elif MVG == 'Weynants et al. (2009)':
            MVGOption = 'Weynants_2009'

        else:
            log.error('Invalid Mualem-Van Genuchten option')
            sys.exit()

        # Set carbon content choice
        if carbonContent == 'Organic carbon':
            carbContent = 'OC'

        elif carbonContent == 'Organic matter':
            carbContent = 'OM'

        else:
            log.error('Invalid carbon content option')
            sys.exit()

        # Unpack 'VG pressure heads' parameter
        if VGPressures is None:
            VGPressArray = []
        else:
            VGPressArray = VGPressures.split(' ')

        # Call soil parameterisation function
        SoilParam.function(outputFolder, inputShapefile, PTFChoice, PTFOption,
                           VGChoice, VGOption, VGPressArray, MVGChoice, MVGOption,
                           carbContent, carbonConFactor, rerun)

        # Loading shapefile automatically
        soilParamOut = os.path.join(outputFolder, "soilParam.shp")
        arcpy.SetParameter(14, soilParamOut)

        log.info("Soil parameterisation operations completed successfully")

    except Exception:
        log.exception("Soil parameterisation tool failed")
        raise
