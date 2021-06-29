import arcpy
import os
import sys

import LUCI_PTFs.lib.log as log
import LUCI_PTFs.lib.common as common
import LUCI_PTFs.lib.progress as progress
import LUCI_PTFs.solo.calc_ksat as CalcKsat

from LUCI_PTFs.lib.refresh_modules import refresh_modules
refresh_modules([log, common, CalcKsat])

def function(params):

    try:
        pText = common.paramsAsText(params)

        # Get inputs
        runSystemChecks = common.strToBool(pText[1])
        outputFolder = pText[2]
        inputShapefile = pText[3]

        # Get equation of choice
        Ksat = pText[4]

        # Retrieve required fields
        fieldFC = pText[5] # field capacity
        fieldSat = pText[6] # saturation

        carbonContent = pText[7]
        carbonConFactor = pText[8]

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

        # Set saturated hydraulic conductivity option
        if Ksat == 'Cosby et al. (1984)':
            KsatOption = 'Cosby_1984'

        elif Ksat == 'Puckett et al. (1985)':
            KsatOption = 'Puckett_1985'

        elif Ksat == 'Jabro (1992)':
            KsatOption = 'Jabro_1992'

        elif Ksat == 'Campbell and Shiozawa (1994)':
            KsatOption = 'CampbellShiozawa_1994'

        elif Ksat == 'Ferrer Julia et al. (2004) - Sand':
            KsatOption = 'FerrerJulia_2004_1'

        elif Ksat == 'Ferrer Julia et al. (2004) - Sand, clay, OM':
            KsatOption = 'FerrerJulia_2004_2'

        elif Ksat == 'Ahuja et al. (1989)':
            KsatOption = 'Ahuja_1989'

            if fieldFC == '' or fieldFC is None:
                log.error('Field name containing WC at field capacity must be specified')
                sys.exit()

            elif fieldSat == '' or fieldSat is None:
                log.error('Field name containing WC at saturation must be specified')
                sys.exit()

            else:
                log.info('Ahuja et al. (1989) will use input water content at field capacity and saturation')

        elif Ksat == 'Minasny and McBratney (2000)':
            KsatOption = 'MinasnyMcBratney_2000'

            if fieldFC == '' or fieldFC is None:
                log.error('Field name containing WC at field capacity must be specified')
                sys.exit()

            elif fieldSat == '' or fieldSat is None:
                log.error('Field name containing WC at saturation must be specified')
                sys.exit()

            else:
                log.info('Minasny and McBratney (2000) will use input water content at field capacity and saturation')

        elif Ksat == 'Brakensiek et al. (1984)':
            KsatOption = 'Brakensiek_1984'

            if fieldSat == '' or fieldSat is None:
                log.error('Field name containing WC at saturation must be specified')
                sys.exit()

            else:
                log.info('Brakensiek et al. (1984) will use input water content at saturation')

        else:
            log.error('Invalid Ksat option')
            sys.exit()

        # Set carbon content choice
        if carbonContent == 'Organic carbon':
            carbContent = 'OC'

        elif carbonContent == 'Organic matter':
            carbContent = 'OM'

        else:
            log.error('Invalid carbon content option')
            sys.exit()

        CalcKsat.function(outputFolder, inputShapefile, KsatOption, fieldFC, fieldSat,
                          carbContent, carbonConFactor)

        # Set output filename for display
        KsatOut = os.path.join(outputFolder, "Ksat.shp")
        arcpy.SetParameter(9, KsatOut)

        log.info("Saturated hydraulic conductivity operations completed successfully")

    except Exception:
        log.exception("Saturated hydraulic conductivity tool failed")
        raise
