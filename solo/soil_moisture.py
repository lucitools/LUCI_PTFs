import configuration
import arcpy
import math
import os
import LUCI_PTFs.lib.log as log
import LUCI_PTFs.lib.common as common
import LUCI_PTFs.lib.thresholds as thresholds
from LUCI_PTFs.lib.external import six # Python 2/3 compatibility module

from LUCI_PTFs.lib.refresh_modules import refresh_modules
refresh_modules([log, common])

def checkInputFields(inputFields, inputShp):

    log.info('Checking if all required input fields are present in ' + str(inputShp))

    # Checks if the input fields are present in the shapefile
    for param in inputFields:        

        fieldPresent = False
        
        if common.CheckField(inputShp, param):
            fieldPresent = True

        else:
            log.error("Field " + str(param) + " not found in the input shapefile")
            log.error("Please ensure this field present in the input shapefile")
            sys.exit()

def function(outputFolder, inputShp, fieldFC, fieldPWP, fieldSat, RAWoption, RAWfrac, fieldCrit, RDchoice, rootingDepth):

    try:
        # Set temporary variables
        prefix = os.path.join(arcpy.env.scratchGDB, "moist_")

        tempSoils = prefix + "tempSoils"

        # Set output filename
        outputShp = os.path.join(outputFolder, "soilMoisture.shp")

        # Check fields are present in the input shapefile
        reqFields = ['OBJECTID', fieldFC, fieldPWP, fieldSat]

        if RAWoption == 'CriticalPoint':
            reqFields.append(fieldCrit)

        checkInputFields(reqFields, inputShp)

        # Copy the input shapefile to the output folder
        arcpy.CopyFeatures_management(inputShp, tempSoils)

        # Retrieve information from input shapefile
        record = []
        volFC = []
        volPWP = []
        volSat = []
        volCrit = []

        with arcpy.da.SearchCursor(tempSoils, reqFields) as searchCursor:
            for row in searchCursor:
                objectID = row[0]
                WC_FC = row[1]
                WC_PWP = row[2]
                WC_Sat = row[3]

                record.append(objectID)
                volFC.append(WC_FC)
                volPWP.append(WC_PWP)
                volSat.append(WC_Sat)

                if RAWoption == 'CriticalPoint':
                    WC_Crit = row[4]
                    volCrit.append(WC_Crit)

        volPAW = []
        volDW = []
        volTWC = []
        volRAW = []

        mmPAW = []
        mmDW = []
        mmTWC = []
        mmRAW = []

        for x in range(0, len(record)):

            # Calculate PAW
            PAW = volFC[x] - volPWP[x]

            if PAW < 0:
                log.warning('Negative PAW (vol) calculated for record ' + str(record[x]))

            volPAW.append(PAW)

            # Calculate drainable water
            DW = volSat[x] - volFC[x]

            if DW < 0:
                log.warning('Negative drainable water (vol) calculated for record ' + str(record[x]))

            volDW.append(DW)

            # Calculate total water content
            TWC = volSat[x] - volPWP[x]

            if TWC < 0:
                log.warning('Negative total water content (vol) calculated for record ' + str(record[x]))

            volTWC.append(TWC)

            if RAWoption == 'CriticalPoint':
                RAW = volFC[x] - volCrit[x]

                RAWfrac = RAW / float(PAW)

                if frac <= 0.2 or frac >= 0.8:
                    log.warning('Fraction of RAW to PAW is below 0.2 or 0.8')

                volRAW.append(RAW)

            elif RAWoption == 'Fraction':

                RAW = float(RAWfrac) * float(PAW)
                volRAW.append(RAW)

            if RDchoice == True:
                mm_PAW = PAW * float(rootingDepth)
                mm_DW = DW * float(rootingDepth)
                mm_TWC = TWC * float(rootingDepth)
                mm_RAW = RAW * float(rootingDepth)

                mmPAW.append(mm_PAW)
                mmDW.append(mm_DW)
                mmTWC.append(mm_TWC)
                mmRAW.append(mm_RAW)

        outFields = ['volPAW', 'volDW' , 'volTWC', 'volRAW']

        # Write outputs to shapefile
        arcpy.AddField_management(tempSoils, "volPAW", "DOUBLE", 10, 6)
        arcpy.AddField_management(tempSoils, "volDW", "DOUBLE", 10, 6)
        arcpy.AddField_management(tempSoils, "volTWC", "DOUBLE", 10, 6)
        arcpy.AddField_management(tempSoils, "volRAW", "DOUBLE", 10, 6)

        if RDchoice == True:
            arcpy.AddField_management(tempSoils, "mmPAW", "DOUBLE", 10, 6)
            arcpy.AddField_management(tempSoils, "mmDW", "DOUBLE", 10, 6)
            arcpy.AddField_management(tempSoils, "mmTWC", "DOUBLE", 10, 6)
            arcpy.AddField_management(tempSoils, "mmRAW", "DOUBLE", 10, 6)

            outFields.append('mmPAW')
            outFields.append('mmDW')
            outFields.append('mmTWC')
            outFields.append('mmRAW')

        recordNum = 0
        with arcpy.da.UpdateCursor(tempSoils, outFields) as cursor:
            for row in cursor:
                row[0] = volPAW[recordNum]
                row[1] = volDW[recordNum]
                row[2] = volTWC[recordNum]
                row[3] = volRAW[recordNum]

                if RDchoice == True:
                    row[4] = mmPAW[recordNum]
                    row[5] = mmDW[recordNum]
                    row[6] = mmTWC[recordNum]
                    row[7] = mmRAW[recordNum]

                cursor.updateRow(row)
                recordNum += 1

        # Clean fields
        outFields.append('OBJECTID')
        common.CleanFields(tempSoils, outFields)

        arcpy.CopyFeatures_management(tempSoils, outputShp)

    except Exception:
        arcpy.AddError("Soil moisture function failed")
        raise

    finally:
        # Remove feature layers from memory
        try:
            for lyr in common.listFeatureLayers(locals()):
                arcpy.Delete_management(locals()[lyr])
                exec(lyr + ' = None') in locals()
        except Exception:
            pass
