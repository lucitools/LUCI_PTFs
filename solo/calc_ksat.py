import configuration
import arcpy
import math
import os
import sys
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

def function(outputFolder, inputShp, KsatOption, fieldFC, fieldSat, carbContent, carbonConFactor):

    try:
        # Set temporary variables
        prefix = os.path.join(arcpy.env.scratchGDB, "moist_")

        # Set output filename
        outputShp = os.path.join(outputFolder, "Ksat.shp")

        # Copy the input shapefile to the output folder
        arcpy.CopyFeatures_management(inputShp, outputShp)

        if KsatOption == 'Cosby_1984':

            log.info("Calculating saturated hydraulic conductivity using Cosby et al. (1984)")

            # Requirements: sand and clay                    
            reqFields = ["OBJECTID", "Sand", "Clay"]
            checkInputFields(reqFields, outputShp)

            # Retrieve info from input
            record = []
            sandPerc = []
            clayPerc = []

            with arcpy.da.SearchCursor(outputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    sand = row[1]
                    clay = row[2]

                    record.append(objectID)
                    sandPerc.append(sand)
                    clayPerc.append(clay)

            warningArray = []
            K_satArray = []

            for x in range(0, len(record)):
                # Data checks
                warningFlag = thresholds.checkValue("Sand", sandPerc[x], record[x])
                warningFlag = thresholds.checkValue("Clay", clayPerc[x], record[x])
                warningArray.append(warningFlag)

                K_sat = 25.4 * 10**(-0.6 + (0.0126 * sandPerc[x]) - (0.0064 * clayPerc[x]))

                K_satArray.append(K_sat)

            # Write results back to the shapefile
            # Add fields
            arcpy.AddField_management(outputShp, "warning", "TEXT")
            arcpy.AddField_management(outputShp, "K_sat", "DOUBLE", 10, 6)

            outputFields = ["warning", "K_sat"]
            
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = warningArray[recordNum]
                    row[1] = K_satArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

            log.info("Results written to the output shapefile inside the output folder")

        elif KsatOption == 'Puckett_1985':
            # Requirements: clay

            log.info("Calculating saturated hydraulic conductivity using Puckett et al. (1985)")

            reqFields = ["OBJECTID", "Clay"]
            checkInputFields(reqFields, outputShp)

            # Retrieve info from input
            record = []
            clayPerc = []

            with arcpy.da.SearchCursor(outputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    clay = row[1]

                    record.append(objectID)
                    clayPerc.append(clay)

            warningArray = []
            K_satArray = []

            for x in range(0, len(record)):
                # Data checks
                warningFlag = thresholds.checkValue("Clay", clayPerc[x], record[x])
                warningArray.append(warningFlag)

                K_sat = 156.96 * math.exp(-0.1975 * clayPerc[x])
                
                K_satArray.append(K_sat)

            # Write results back to the shapefile
            # Add fields
            arcpy.AddField_management(outputShp, "warning", "TEXT")
            arcpy.AddField_management(outputShp, "K_sat", "DOUBLE", 10, 6)

            outputFields = ["warning", "K_sat"]
            
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = warningArray[recordNum]
                    row[1] = K_satArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

            log.info("Results written to the output shapefile inside the output folder")

        elif KsatOption == "Jabro_1992":
            log.info("Calculating saturated hydraulic conductivity using Jabro (1992)")

            # Requirements: silt, clay, BD
            reqFields = ["OBJECTID", "Silt", "Clay", "BD"]
            checkInputFields(reqFields, outputShp)

            # Retrieve info from input
            record = []
            siltPerc = []
            clayPerc = []
            BDg_cm3 = []

            with arcpy.da.SearchCursor(outputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    silt = row[1]
                    clay = row[2]
                    BD = row[3]

                    record.append(objectID)
                    siltPerc.append(silt)
                    clayPerc.append(clay)
                    BDg_cm3.append(BD)

            warningArray = []
            K_satArray = []

            for x in range(0, len(record)):
                # Data checks
                warningFlag = thresholds.checkValue("Silt", siltPerc[x], record[x])
                warningFlag = thresholds.checkValue("Clay", clayPerc[x], record[x])
                warningFlag = thresholds.checkValue("Bulk density", BDg_cm3[x], record[x])
                warningArray.append(warningFlag)

                K_sat = 10**(9.56 - (0.81 * math.log(siltPerc[x], 10.0)) - (1.09 * math.log(clayPerc[x], 10.0)) - (4.64 * BDg_cm3[x])) * (10.0 / 24.0)

                K_satArray.append(K_sat)

            # Write results back to the shapefile
            # Add fields
            arcpy.AddField_management(outputShp, "warning", "TEXT")
            arcpy.AddField_management(outputShp, "K_sat", "DOUBLE", 10, 6)

            outputFields = ["warning", "K_sat"]
            
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = warningArray[recordNum]
                    row[1] = K_satArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

            log.info("Results written to the output shapefile inside the output folder")

        elif KsatOption == "CampbellShiozawa_1994":
            log.info("Calculating saturated hydraulic conductivity using Campbell and Shiozawa (1994)")

            # Requirements: silt, clay
            reqFields = ["OBJECTID", "Silt", "Clay"]
            checkInputFields(reqFields, outputShp)

            # Retrieve info from input
            record = []
            siltPerc = []
            clayPerc = []

            with arcpy.da.SearchCursor(outputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    silt = row[1]
                    clay = row[2]

                    record.append(objectID)
                    siltPerc.append(silt)
                    clayPerc.append(clay)

            warningArray = []
            K_satArray = []

            for x in range(0, len(record)):
                # Data checks
                warningFlag = thresholds.checkValue("Silt", siltPerc[x], record[x])
                warningFlag = thresholds.checkValue("Clay", clayPerc[x], record[x])
                warningArray.append(warningFlag)

                K_sat = 54.0 * math.exp((- 0.07 * siltPerc[x]) - (0.167 * clayPerc[x]))

                K_satArray.append(K_sat)

            # Write results back to the shapefile
            # Add fields
            arcpy.AddField_management(outputShp, "warning", "TEXT")
            arcpy.AddField_management(outputShp, "K_sat", "DOUBLE", 10, 6)

            outputFields = ["warning", "K_sat"]
            
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = warningArray[recordNum]
                    row[1] = K_satArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

            log.info("Results written to the output shapefile inside the output folder")

        elif KsatOption == "FerrerJulia_2004_1":
            log.info("Calculating saturated hydraulic conductivity using Ferrer Julia et al. (2004) using sand")

            # Requirements: sand
            reqFields = ["OBJECTID", "Sand"]
            checkInputFields(reqFields, outputShp)

            # Retrieve info from input
            record = []
            sandPerc = []

            with arcpy.da.SearchCursor(outputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    sand = row[1]

                    record.append(objectID)
                    sandPerc.append(sand)

            warningArray = []
            K_satArray = []

            for x in range(0, len(record)):
                # Data checks
                warningFlag = thresholds.checkValue("Sand", sandPerc[x], record[x])
                warningArray.append(warningFlag)

                K_sat = 0.920 * math.exp(0.0491 * sandPerc[x])
                
                K_satArray.append(K_sat)

            # Write results back to the shapefile
            # Add fields
            arcpy.AddField_management(outputShp, "warning", "TEXT")
            arcpy.AddField_management(outputShp, "K_sat", "DOUBLE", 10, 6)

            outputFields = ["warning", "K_sat"]
            
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = warningArray[recordNum]
                    row[1] = K_satArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

            log.info("Results written to the output shapefile inside the output folder")

        elif KsatOption == "FerrerJulia_2004_2":
            log.info("Calculating saturated hydraulic conductivity using Ferrer Julia et al. (2004) using sand, clay, and organic matter")

            # Requirements: sand, clay, OM, BD
            if carbContent == 'OC':
                reqFields = ["OBJECTID", "Sand", "Clay", "OC", "BD"]
                carbonConFactor = 1.724

            elif carbContent == 'OM':
                reqFields = ["OBJECTID", "Sand", "Clay", "OM", "BD"]
                carbonConFactor = 1.0
                
            checkInputFields(reqFields, outputShp)

            # Retrieve info from input
            record = []
            sandPerc = []
            clayPerc = []
            carbPerc = []
            BDg_cm3 = []

            with arcpy.da.SearchCursor(outputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    sand = row[1]
                    clay = row[2]
                    carbon = row[3]
                    BD = row[4]

                    record.append(objectID)
                    sandPerc.append(sand)
                    clayPerc.append(clay)
                    carbPerc.append(carbon)
                    BDg_cm3.append(BD)

            warningArray = []
            K_satArray = []

            for x in range(0, len(record)):
                # Data checks
                warningFlag = thresholds.checkCarbon(carbPerc[x], carbContent, record[x])
                warningFlag = thresholds.checkValue("Sand", sandPerc[x], record[x])
                warningFlag = thresholds.checkValue("Clay", clayPerc[x], record[x])
                warningFlag = thresholds.checkValue("Bulk density", BDg_cm3[x], record[x])
                warningArray.append(warningFlag)

                K_sat = - 4.994 + (0.56728 * sandPerc[x]) - (0.131 * clayPerc[x]) - (0.0127 * carbPerc[x]*float(carbonConFactor))

                K_satArray.append(K_sat)

            # Write results back to the shapefile
            # Add fields
            arcpy.AddField_management(outputShp, "warning", "TEXT")
            arcpy.AddField_management(outputShp, "K_sat", "DOUBLE", 10, 6)

            outputFields = ["warning", "K_sat"]
            
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = warningArray[recordNum]
                    row[1] = K_satArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

            log.info("Results written to the output shapefile inside the output folder")

        elif KsatOption == "Ahuja_1989":
            log.info("Calculating saturated hydraulic conductivity using Ahuja et al. (1989)")

            # Requirements: WC @ Sat and WC @ FC
            
            reqFields = ["OBJECTID", fieldSat, fieldFC]
            checkInputFields(reqFields, outputShp)

            # Retrieve info from input
            record = []
            WC_satArray = []
            WC_FCArray = []

            with arcpy.da.SearchCursor(outputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    WC_sat = row[1]
                    WC_FC = row[2]

                    record.append(objectID)
                    WC_satArray.append(WC_sat)
                    WC_FCArray.append(WC_FC)

            K_satArray = []

            for x in range(0, len(record)):
                Eff_porosity = WC_satArray[x] - WC_FCArray[x]
                K_sat = 7645.0 * Eff_porosity **3.288
                
                K_satArray.append(K_sat)

            # Write results back to the shapefile
            # Add fields
            arcpy.AddField_management(outputShp, "K_sat", "DOUBLE", 10, 6)

            outputFields = ["K_sat"]
            
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = K_satArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

            log.info("Results written to the output shapefile inside the output folder")

        elif KsatOption == "MinasnyMcBratney_2000":
            log.info("Calculating saturated hydraulic conductivity using Minasny and McBratney (2000)")

            # Requirements: WC @ sat and WC @ FC
            
            reqFields = ["OBJECTID", fieldSat, fieldFC]
            checkInputFields(reqFields, outputShp)

            # Retrieve info from input
            record = []
            WC_satArray = []
            WC_FCArray = []

            with arcpy.da.SearchCursor(outputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    WC_sat = row[1]
                    WC_FC = row[2]

                    record.append(objectID)
                    WC_satArray.append(WC_sat)
                    WC_FCArray.append(WC_FC)

            K_satArray = []

            for x in range(0, len(record)):
                Eff_porosity = WC_satArray[x] - WC_FCArray[x]
                K_sat = 23190.55 * Eff_porosity ** 3.66

                K_satArray.append(K_sat)

            # Write results back to the shapefile
            # Add fields
            arcpy.AddField_management(outputShp, "K_sat", "DOUBLE", 10, 6)

            outputFields = ["K_sat"]
            
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = K_satArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

            log.info("Results written to the output shapefile inside the output folder")

        elif KsatOption == "Brakensiek_1984":
            log.info("Calculating saturated hydraulic conductivity using Brakensiek et al. (1984)")

            # Requirements: Clay, sand, WC @ sat
            
            reqFields = ["OBJECTID", "Sand", "Clay", fieldSat]
            checkInputFields(reqFields, outputShp)

            # Retrieve info from input
            record = []
            sandPerc = []
            clayPerc = []
            WC_satArray = []

            with arcpy.da.SearchCursor(outputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    sand = row[1]
                    clay = row[2]
                    WC_sat = row[3]

                    record.append(objectID)
                    sandPerc.append(sand)
                    clayPerc.append(clay)
                    WC_satArray.append(WC_sat)

            warningArray = []
            K_satArray = []

            for x in range(0, len(record)):
                # Data checks
                warningFlag = thresholds.checkValue("Sand", sandPerc[x], record[x])
                warningFlag = thresholds.checkValue("Clay", clayPerc[x], record[x])

                warningArray.append(warningFlag)

                K_sat = 10 * math.exp((19.52348 * WC_satArray[x]) - 8.96847 - (0.028212 * clayPerc[x]) + (0.00018107 * sandPerc[x]**2) - (0.0094125 * clayPerc[x]**2) - (8.395215 * WC_satArray[x]**2) + (0.077718 * sandPerc[x] * WC_satArray[x]) - (0.00298 * sandPerc[x]**2 * WC_satArray[x]**2) - (0.019492 * clayPerc[x]**2 * WC_satArray[x]**2) + (0.0000173 * sandPerc[x]**2 * clayPerc[x]) + (0.02733 * clayPerc[x]**2 * WC_satArray[x]) + (0.001434 * sandPerc[x]**2 * WC_satArray[x]) - (0.0000035 * clayPerc[x]**2 * sandPerc[x]))

                K_satArray.append(K_sat)

            # Write results back to the shapefile
            # Add fields
            arcpy.AddField_management(outputShp, "warning", "TEXT")
            arcpy.AddField_management(outputShp, "K_sat", "DOUBLE", 10, 6)

            outputFields = ["warning", "K_sat"]
            
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = warningArray[recordNum]
                    row[1] = K_satArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

            log.info("Results written to the output shapefile inside the output folder")

        else:
            log.error('Ksat option not recognised')
            log.error('Please choose a Ksat option from the drop down menu')
            sys.exit()

    except Exception:
        arcpy.AddError("Saturated hydraulic conductivity function failed")
        raise

    finally:
        # Remove feature layers from memory
        try:
            for lyr in common.listFeatureLayers(locals()):
                arcpy.Delete_management(locals()[lyr])
                exec(lyr + ' = None') in locals()
        except Exception:
            pass
