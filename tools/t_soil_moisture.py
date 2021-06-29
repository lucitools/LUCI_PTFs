import arcpy
import os

import LUCI_PTFs.lib.log as log
import LUCI_PTFs.lib.common as common
import LUCI_PTFs.lib.progress as progress
import LUCI_PTFs.solo.soil_moisture as SoilMoisture

from LUCI_PTFs.lib.refresh_modules import refresh_modules
refresh_modules([log, common, SoilMoisture])

def function(params):

    try:
        pText = common.paramsAsText(params)

        # Get inputs
        runSystemChecks = common.strToBool(pText[1])
        outputFolder = pText[2]
        inputShapefile = pText[3]

        # Retrieve required fields
        fieldFC = pText[4] # field capacity
        fieldPWP = pText[5] # permanent wilting point
        fieldSat = pText[6] # saturation

        # Retrieve RAW information
        RAWchoice = pText[7]
        RAWfrac = pText[8]
        fieldCrit = pText[9] # critical point for RAW

        # Retrive rooting depth information
        RDchoice = common.strToBool(pText[10])
        rootingDepth = pText[11]

        # Create output folder
        if not os.path.exists(outputFolder):
            os.mkdir(outputFolder)

        # System checks and setup
        if runSystemChecks:
            common.runSystemChecks(outputFolder)

        # Set up logging output to file
        log.setupLogging(outputFolder)

        # Write input params to XML
        common.writeParamsToXML(params, outputFolder)

        if RAWchoice == 'Fraction':
            RAWoption = 'Fraction'

        elif RAWchoice == 'Field containing WC (vol) at critical point':
            RAWoption = 'CriticalPoint'

        else:
            log.error('Choice for readily-available water calculation not recognised')
            sys.exit()

        SoilMoisture.function(outputFolder, inputShapefile,
                              fieldFC, fieldPWP, fieldSat,
                              RAWoption, RAWfrac, fieldCrit,
                              RDchoice, rootingDepth)

        # Set output filename for display
        soilMoistureOut = os.path.join(outputFolder, "soilMoisture.shp")
        arcpy.SetParameter(12, soilMoistureOut)

        log.info("Soil moisture operations completed successfully")

    except Exception:
        log.exception("Soil moisture tool failed")
        raise
