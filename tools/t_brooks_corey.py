import arcpy
import os

import LUCI_PTFs.lib.log as log
import LUCI_PTFs.lib.common as common
import LUCI_PTFs.lib.progress as progress
import LUCI_PTFs.solo.brooks_corey as brooks_corey

from LUCI_PTFs.lib.refresh_modules import refresh_modules
refresh_modules([log, common, brooks_corey])

def function(params):

    try:
        pText = common.paramsAsText(params)

        # Get inputs
        runSystemChecks = common.strToBool(pText[1])
        outputFolder = pText[2]
        inputShapefile = pText[3]
        PTFChoice = pText[4]

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

        if PTFChoice == 'Cosby et al. (1984) - Silt and Clay':
            PTFOption = 'Cosby_1984_SC'

        elif PTFChoice == 'Cosby et al. (1984) - Sand, Silt and Clay':
            PTFOption = 'Cosby_1984_SSC'

        elif PTFChoice == 'Rawls and Brakensiek (1985)':
            PTFOption = 'RawlsBrakensiek_1985'

        elif PTFChoice == 'Campbell and Shiozava (1992)':
            PTFOption = 'CampbellShiozava_1992'

        elif PTFChoice == 'Saxton et al. (1986)':
            PTFOption = 'Saxton_1986'

        else:
            log.error('Choice for readily-available water calculation not recognised')
            sys.exit()

        brooks_corey.function(outputFolder, inputShapefile, PTFOption)

        # Set output filename for display
        BCOut = os.path.join(outputFolder, "BrooksCorey.shp")
        arcpy.SetParameter(5, BCOut)

        log.info("Brooks-Corey operations completed successfully")

    except Exception:
        log.exception("Brooks-Corey tool failed")
        raise
