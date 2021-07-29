'''
Function to calculate van Genuchten parameters and SMRC
'''

import sys
import os
import arcpy
import LUCI_PTFs.lib.log as log
import LUCI_PTFs.lib.common as common
import LUCI_PTFs.lib.vanGenuchten as vanGenuchten
import LUCI_PTFs.lib.vg_PTFs as vg_PTFs
import LUCI_PTFs.lib.checks_PTFs as checks_PTFs
from LUCI_PTFs.lib.external import six # Python 2/3 compatibility module

from LUCI_PTFs.lib.refresh_modules import refresh_modules
refresh_modules([log, common, vanGenuchten, vg_PTFs, checks_PTFs])

def function(outputFolder, inputShp, VGOption, MVGChoice, fieldFC, fieldSIC, fieldPWP, carbContent, carbonConFactor):

    try:
        # Set temporary variables
        prefix = os.path.join(arcpy.env.scratchGDB, "soil_")

        # Check the fields at important thresholds
        fcArray, sicArray, pwpArray = checks_PTFs.pressureFields(outputFolder, inputShp, fieldFC, fieldSIC, fieldPWP)

        # Set output filename
        outputShp = os.path.join(outputFolder, "soil_vg.shp")

        # Copy the input shapefile to the output folder
        arcpy.CopyFeatures_management(inputShp, outputShp)

        # Write values for FC, SIC, and PWP to output shapefile
        common.writeFields(outputShp, ["fc_kPa", "sic_kPa", "pwp_kPa"])

        recordNum = 0
        with arcpy.da.UpdateCursor(outputShp, ["fc_kPa", "sic_kPa", "pwp_kPa"]) as cursor:
            for row in cursor:
                row[0] = fcArray[recordNum]
                row[1] = sicArray[recordNum]
                row[2] = pwpArray[recordNum]

                cursor.updateRow(row)
                recordNum += 1

        log.info("Pressure values at important thresholds written to output shapefile")

        ##############################################
        ### Calculate the van Genuchten parameters ###
        ##############################################

        # Get the nameArray
        nameArray = []
        with arcpy.da.SearchCursor(outputShp, "LUCIname") as searchCursor:
            for row in searchCursor:
                name = row[0]

                nameArray.append(name)

        # Initialise the van Genuchten parameter arrays
        # All VG PTFs should return these arrays        
        WC_residualArray = []
        WC_satArray = []
        alpha_VGArray = []
        n_VGArray = []
        m_VGArray = []

        # Call VG PTF here depending on VGOption
        if str(VGOption[0:11]) == "Wosten_1999":
            # Has option to calculate Mualem-van Genuchten
            WC_residualArray, WC_satArray, alpha_VGArray, n_VGArray, m_VGArray, l_MvGArray, K_satArray = vg_PTFs.Wosten_1999(outputShp, VGOption, carbonConFactor, carbContent, MVGChoice)

        elif VGOption == "Vereecken_1989":
            WC_residualArray, WC_satArray, alpha_VGArray, n_VGArray, m_VGArray = vg_PTFs.Vereecken_1989(outputShp, VGOption, carbonConFactor, carbContent)

        elif VGOption == "ZachariasWessolek_2007":
            WC_residualArray, WC_satArray, alpha_VGArray, n_VGArray, m_VGArray = vg_PTFs.ZachariasWessolek_2007(outputShp, VGOption, carbonConFactor, carbContent)
        
        elif VGOption == "Weynants_2009":
            # Has option to calculate Mualem-van Genuchten
            WC_residualArray, WC_satArray, alpha_VGArray, n_VGArray, m_VGArray, l_MvGArray, K_satArray = vg_PTFs.Weynants_2009(outputShp, VGOption, carbonConFactor, carbContent, MVGChoice)

        elif VGOption == "Dashtaki_2010_vg":
            WC_residualArray, WC_satArray, alpha_VGArray, n_VGArray, m_VGArray = vg_PTFs.Dashtaki_2010(outputShp, VGOption, carbonConFactor, carbContent)

        elif VGOption == "HodnettTomasella_2002":
            WC_residualArray, WC_satArray, alpha_VGArray, n_VGArray, m_VGArray = vg_PTFs.HodnettTomasella_2002(outputShp, VGOption, carbonConFactor, carbContent)

        else:
            log.error("Van Genuchten option not recognised: " + str(VGOption))
            sys.exit()
 
        # Write VG parameter results to output shapefile
        vanGenuchten.writeVGParams(outputShp, WC_residualArray, WC_satArray, alpha_VGArray, n_VGArray, m_VGArray)

        # Plot VG parameters
        vanGenuchten.plotVG(outputFolder, WC_residualArray,
                            WC_satArray, alpha_VGArray, n_VGArray,
                            m_VGArray, nameArray, fcArray, sicArray, pwpArray)

        # Initialise water content arrays
        wc_satCalc = []
        wc_fcCalc = []
        wc_sicCalc = []
        wc_pwpCalc = []

        wc_DW = []
        wc_RAW = []
        wc_NRAW = []
        wc_PAW = []

        for i in range(0, len(nameArray)):
            wc_sat = vanGenuchten.calcVGfxn(0, WC_residualArray[i], WC_satArray[i], alpha_VGArray[i], n_VGArray[i], m_VGArray[i])
            wc_fc = vanGenuchten.calcVGfxn(fcArray[i], WC_residualArray[i], WC_satArray[i], alpha_VGArray[i], n_VGArray[i], m_VGArray[i])
            wc_sic = vanGenuchten.calcVGfxn(sicArray[i], WC_residualArray[i], WC_satArray[i], alpha_VGArray[i], n_VGArray[i], m_VGArray[i])
            wc_pwp = vanGenuchten.calcVGfxn(pwpArray[i], WC_residualArray[i], WC_satArray[i], alpha_VGArray[i], n_VGArray[i], m_VGArray[i])

            drainWater = wc_sat - wc_fc
            readilyAvailWater = wc_fc - wc_sic
            notRAW = wc_sic - wc_pwp
            PAW = wc_fc - wc_pwp

            checks_PTFs.checkNegValue("Drainable water", drainWater, nameArray[i])
            checks_PTFs.checkNegValue("Readily available water", readilyAvailWater, nameArray[i])
            checks_PTFs.checkNegValue("Not readily available water", notRAW, nameArray[i])
            checks_PTFs.checkNegValue("Not readily available water", PAW, nameArray[i])

            wc_satCalc.append(wc_sat)
            wc_fcCalc.append(wc_fc)
            wc_sicCalc.append(wc_sic)
            wc_pwpCalc.append(wc_pwp)
            wc_DW.append(drainWater)
            wc_RAW.append(readilyAvailWater)
            wc_NRAW.append(notRAW)
            wc_PAW.append(PAW)

        # Save to shapefile
        wcFields = ["wc_satCalc", "wc_fcCalc", "wc_sicCalc", "wc_pwpCalc", "wc_DW", "wc_RAW", "wc_NRAW", "wc_PAW"]
        common.writeFields(outputShp, wcFields)

        recordNum = 0
        with arcpy.da.UpdateCursor(outputShp, wcFields) as cursor:
            for row in cursor:
                row[0] = wc_satCalc[recordNum]
                row[1] = wc_fcCalc[recordNum]
                row[2] = wc_sicCalc[recordNum]
                row[3] = wc_pwpCalc[recordNum]
                row[4] = wc_DW[recordNum]
                row[5] = wc_RAW[recordNum]
                row[6] = wc_NRAW[recordNum]
                row[7] = wc_PAW[recordNum]

                cursor.updateRow(row)
                recordNum += 1

        log.info('Water contents for critical thresholds written to output shapefile')

        if MVGChoice == True:
            if VGOption in ["Wosten_1999_top", "Wosten_1999_top", "Weynants_2009"]:
                # Allow for calculation of MVG
                log.info("Calculating and plotting MVG")

                # Write l_MvGArray to outputShp
                arcpy.AddField_management(outputShp, "l_MvG", "DOUBLE", 10, 6)

                recordNum = 0
                with arcpy.da.UpdateCursor(outputShp, "l_MvG") as cursor:
                    for row in cursor:
                        row[0] = l_MvGArray[recordNum]

                        cursor.updateRow(row)
                        recordNum += 1

                # Plot MVG
                vanGenuchten.plotMVG(outputFolder, K_satArray, alpha_VGArray, n_VGArray, m_VGArray, l_MvGArray, WC_satArray, WC_residualArray, nameArray)

            else:
                log.error("Selected PTF does not calculate Mualem-van Genuchten parameters")
                log.error("Please select a different PTF")
                sys.exit()

    except Exception:
        arcpy.AddError("van Genuchten function failed")
        raise

    finally:
        # Remove feature layers from memory
        try:
            for lyr in common.listFeatureLayers(locals()):
                arcpy.Delete_management(locals()[lyr])
                exec(lyr + ' = None') in locals()
        except Exception:
            pass