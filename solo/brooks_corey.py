import configuration
import arcpy
import math
import os
import sys
import LUCI_PTFs.lib.log as log
import LUCI_PTFs.lib.common as common
import LUCI_PTFs.lib.thresholds as thresholds
import LUCI_PTFs.lib.PTFdatabase as PTFdatabase
import LUCI_PTFs.lib.brooksCorey as brooksCorey
import LUCI_PTFs.lib.bc_PTFs as bc_PTFs
from LUCI_PTFs.lib.external import six # Python 2/3 compatibility module

from LUCI_PTFs.lib.refresh_modules import refresh_modules
refresh_modules([log, common, thresholds, PTFdatabase, brooksCorey, bc_PTFs])

def function(outputFolder, inputShp, PTFOption, carbContent, carbonConFactor):

    try:
        # Set temporary variables
        prefix = os.path.join(arcpy.env.scratchGDB, "bc_")

        tempSoils = prefix + "tempSoils"

        # Set output filename
        outputShp = os.path.join(outputFolder, "BrooksCorey.shp")

        # Copy the input shapefile to the output folder
        arcpy.CopyFeatures_management(inputShp, outputShp)

        # Get the nameArray
        nameArray = []
        with arcpy.da.SearchCursor(outputShp, "LUCIname") as searchCursor:
            for row in searchCursor:
                name = row[0]
                nameArray.append(name)

        # PTFs should return: WC_res, WC_sat, lambda_BC, hb_BC

        if PTFOption == "Cosby_1984_SC_BC":
            warning, WC_res, WC_sat, lambda_BC, hb_BC = bc_PTFs.Cosby_1984_SC_BC(outputShp, PTFOption)

        elif PTFOption == "Cosby_1984_SSC_BC":
            warning, WC_res, WC_sat, lambda_BC, hb_BC = bc_PTFs.Cosby_1984_SSC_BC(outputShp, PTFOption)

        elif PTFOption == "RawlsBrakensiek_1985_BC":
            warning, WC_res, WC_sat, lambda_BC, hb_BC = bc_PTFs.RawlsBrakensiek_1985_BC(outputShp, PTFOption)

        elif PTFOption == "CampbellShiozawa_1992_BC":
            warning, WC_res, WC_sat, lambda_BC, hb_BC = bc_PTFs.CampbellShiozawa_1992_BC(outputShp, PTFOption)

        elif PTFOption == "Saxton_1986_BC":
            warning, WC_res, WC_sat, lambda_BC, hb_BC = bc_PTFs.Saxton_1986_BC(outputShp, PTFOption)

        elif PTFOption == "SaxtonRawls_2006_BC":
            warning, WC_res, WC_sat, lambda_BC, hb_BC = bc_PTFs.SaxtonRawls_2006_BC(outputShp, PTFOption, carbonConFactor, carbContent)

        else:
            log.error("Brooks-Corey option not recognised: " + str(PTFOption))
            sys.exit()

        # Write to shapefile
        brooksCorey.writeBCParams(outputShp, warning, WC_res, WC_sat, lambda_BC, hb_BC)

        log.info("Brooks-Corey parameters written to output shapefile")

        '''
        # DEBUG: Printint out water content
        for x in range(0, len(nameArray)):
            log.info("DEBUG: nameArray: " + str(nameArray[x]))

            pressures = [1.0, 3.0, 6.0, 10.0, 20.0, 33.0, 100.0, 1500.0]

            bc_WC = brooksCorey.calcBrooksCoreyFXN(pressures, hb_BC[x], WC_res[x], WC_sat[x], lambda_BC[x])

            log.info("DEBUG: pressures: " + str(pressures))
            log.info("DEBUG: bc_WC: " + str(bc_WC))
        '''
            
        # Create plots
        brooksCorey.plotBrooksCorey(outputFolder, WC_res, WC_sat, hb_BC, lambda_BC, nameArray)

    except Exception:
        arcpy.AddError("Brooks-Corey function failed")
        raise

    finally:
        # Remove feature layers from memory
        try:
            for lyr in common.listFeatureLayers(locals()):
                arcpy.Delete_management(locals()[lyr])
                exec(lyr + ' = None') in locals()
        except Exception:
            pass