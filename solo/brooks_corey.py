import configuration
import arcpy
import math
import os
import sys
import LUCI_PTFs.lib.log as log
import LUCI_PTFs.lib.common as common
import LUCI_PTFs.lib.thresholds as thresholds
import LUCI_PTFs.lib.brooksCorey as brooksCorey
from LUCI_PTFs.lib.external import six # Python 2/3 compatibility module

from LUCI_PTFs.lib.refresh_modules import refresh_modules
refresh_modules([log, common, thresholds, brooksCorey])

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

def function(outputFolder, inputShp, PTFOption):

    try:
        # Set temporary variables
        prefix = os.path.join(arcpy.env.scratchGDB, "bc_")

        tempSoils = prefix + "tempSoils"

        # Set output filename
        outputShp = os.path.join(outputFolder, "BrooksCorey.shp")

        # Copy the input shapefile to the output folder
        arcpy.CopyFeatures_management(inputShp, outputShp)

        if PTFOption == "Cosby_1984_SC":

            # Check for required fields
            reqFields = ["OBJECTID", "Silt", "Clay", "LUCIname"]
            checkInputFields(reqFields, inputShp)

            # Retrieve info from input
            record = []
            siltPerc = []
            clayPerc = []
            nameArray = []

            with arcpy.da.SearchCursor(inputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    silt = row[1]
                    clay = row[2]
                    name = row[3]

                    record.append(objectID)
                    siltPerc.append(silt)
                    clayPerc.append(clay)
                    nameArray.append(name)

            WC_resArray = []
            WC_satArray = []
            lambdaArray = []
            hbArray = []

            for x in range(0, len(record)):
                # Calculate values
                WC_res = 0
                WC_sat = (8.23 - (0.0805 * clayPerc[x]) - (0.0070 * siltPerc[x])) / 10.0
                lambda_BC = 1.0 / (0.92 + (0.0492 * clayPerc[x]) + (0.0144 * siltPerc[x]))
                hb_BC = 10.0 ** (0.72 + (0.0012 * clayPerc[x]) - (0.0026 * siltPerc[x]))

                # Append to arrays
                WC_resArray.append(WC_res)
                WC_satArray.append(WC_sat)
                lambdaArray.append(lambda_BC)
                hbArray.append(hb_BC)

            # Write results back to shapefile
            arcpy.AddField_management(outputShp, "WC_res", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "WC_sat", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "lambda", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "hb", "DOUBLE", 10, 6)

            outputFields = ["WC_res", "WC_sat", "lambda", "hb"]
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = WC_resArray[recordNum]
                    row[1] = WC_satArray[recordNum]
                    row[2] = lambdaArray[recordNum]
                    row[3] = hbArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

            log.info("Results written to the output shapefile inside the output folder")

            # Create plots
            brooksCorey.plotBrooksCorey(outputFolder, record, WC_resArray, WC_satArray, hbArray, lambdaArray, nameArray)

        elif PTFOption == "Cosby_1984_SSC":

            # Check for required fields
            reqFields = ["OBJECTID", "Sand", "Silt", "Clay"]
            checkInputFields(reqFields, inputShp)

            # Retrieve info from input
            record = []
            sandPerc = []
            siltPerc = []
            clayPerc = []

            with arcpy.da.SearchCursor(inputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    sand = row[1]
                    silt = row[2]
                    clay = row[3]

                    record.append(objectID)
                    sandPerc.append(sand)
                    siltPerc.append(silt)
                    clayPerc.append(clay)

            WC_resArray = []
            WC_satArray = []
            lambdaArray = []
            hbArray = []

            for x in range(0, len(record)):
                # Calculate values
                WC_res = 0
                WC_sat = (50.5 - (0.037 * clayPerc[x]) - (0.142 * sandPerc[x])) / 100.0
                lambda_BC = 1.0 / (3.10 + (0.157 * clayPerc[x]) - (0.003 * sandPerc[x]))
                hb_BC = 10.0 ** (1.54 - (0.0095 * sandPerc[x]) + (0.0063 * siltPerc[x]))

                # Append to arrays
                WC_resArray.append(WC_res)
                WC_satArray.append(WC_sat)
                lambdaArray.append(lambda_BC)
                hbArray.append(hb_BC)

            # Write results back to shapefile
            arcpy.AddField_management(outputShp, "WC_res", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "WC_sat", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "lambda", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "hb", "DOUBLE", 10, 6)

            outputFields = ["WC_res", "WC_sat", "lambda", "hb"]
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = WC_resArray[recordNum]
                    row[1] = WC_satArray[recordNum]
                    row[2] = lambdaArray[recordNum]
                    row[3] = hbArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

        elif PTFOption == "RawlsBrakensiek_1985":

            # Check for required fields
            reqFields = ["OBJECTID", "Sand", "Clay", "WC_sat"]
            checkInputFields(reqFields, inputShp)

            # Retrieve info from input
            record = []
            sandPerc = []            
            clayPerc = []
            WC_satArray = []

            with arcpy.da.SearchCursor(inputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    sand = row[1]                    
                    clay = row[2]
                    WCsat = row[3]

                    record.append(objectID)
                    sandPerc.append(sand)
                    clayPerc.append(clay)
                    WC_satArray.append(WCsat)

            WC_resArray = []            
            hbArray = []
            lambdaArray = []

            for x in range(0, len(record)):

                # Calculate values
                WC_residual = -0.0182482 + (0.00087269 * sandPerc[x]) + (0.00513488 * clayPerc[x]) + (0.02939286 * WC_satArray[x]) - (0.00015395 * clayPerc[x]**2) - (0.0010827 * sandPerc[x] * WC_satArray[x]) - (0.00018233 * clayPerc[x]**2 * WC_satArray[x]**2) + (0.00030703 * clayPerc[x]**2 * WC_satArray[x]) - (0.0023584 * WC_satArray[x]**2 * clayPerc[x])
                hb_BC = math.exp(5.3396738 + (0.1845038 * clayPerc[x]) - (2.48394546 * WC_satArray[x]) - (0.00213853 * clayPerc[x]**2) - (0.04356349 * sandPerc[x] * WC_satArray[x]) - (0.61745089 * clayPerc[x] * WC_satArray[x]) + (0.00143598 * sandPerc[x]**2 * WC_satArray[x]**2) - (0.00855375 * clayPerc[x]**2 * WC_satArray[x]**2) - (0.00001282 * sandPerc[x]**2 * clayPerc[x]) + (0.00895359 * clayPerc[x]**2 * WC_satArray[x]) - (0.00072472 * sandPerc[x]**2 * WC_satArray[x]) + (0.0000054 * clayPerc[x]**2 * sandPerc[x]) + (0.50028060 * WC_satArray[x]**2 * clayPerc[x]))
                lambda_BC = math.exp(-0.7842831 + (0.0177544 * sandPerc[x]) - (1.062498 * WC_satArray[x]) - (0.00005304 * sandPerc[x]**2) - (0.00273493* clayPerc[x]**2) + (1.11134946 * WC_satArray[x]**2) - (0.03088295 * sandPerc[x] * WC_satArray[x])  + (0.00026587 * sandPerc[x]**2 * WC_satArray[x]**2)  - (0.00610522 * clayPerc[x]**2 * WC_satArray[x]**2)  - (0.00000235 * sandPerc[x]**2 * clayPerc[x]) + (0.00798746 * clayPerc[x]**2 * WC_satArray[x]) - (0.00674491 * WC_satArray[x]**2 * clayPerc[x]))

                WC_resArray.append(WC_residual)                
                hbArray.append(hb_BC)
                lambdaArray.append(lambda_BC)

            # Write results back to shapefile
            arcpy.AddField_management(outputShp, "WC_res", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "hb", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "lambda", "DOUBLE", 10, 6)
            
            outputFields = ["WC_sat", "lambda", "hb"]
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = WC_satArray[recordNum]
                    row[1] = lambdaArray[recordNum]
                    row[2] = hbArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

        elif PTFOption == "CampbellShiozava_1992":

            # Check for required fields
            reqFields = ["OBJECTID", "Silt", "Clay", "BD"]
            checkInputFields(reqFields, inputShp)

            # Retrieve info from input
            record = []
            siltPerc = []
            clayPerc = []
            BDg_cm3 = []

            with arcpy.da.SearchCursor(inputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    silt = row[1]
                    clay = row[2]
                    BD = row[3]

                    record.append(objectID)
                    siltPerc.append(silt)
                    clayPerc.append(clay)
                    BDg_cm3.append(BD)

            WC_resArray = []
            dg_CSArray = []
            Sg_CSArray = []
            hes_CSArray = []
            b_CSArray = []
            hbArray = []
            lambdaArray = []

            for x in range(0, len(record)):
                # Calculate values
                WC_residual = 0
                dg_CS = math.exp(-0.80 - (0.0317 * siltPerc[x]) - (0.0761 * clayPerc[x]))
                Sg_CS = (math.exp((0.133 * siltPerc[x]) + (0.477 * clayPerc[x]) - ((math.log(dg_CS))**2)))**0.5
                hes_CS = 0.05/float((math.sqrt(dg_CS)))
                b_CS = (-20.0 * (-hes_CS)) + (0.2 * Sg_CS)
                hb_BC = 100.0 * (hes_CS * ((BDg_cm3[x] / 1.3) ** (0.67* b_CS)))
                lambda_BC = 1.0 /float(b_CS)

                WC_resArray.append(WC_residual)
                dg_CSArray.append(dg_CS)
                Sg_CSArray.append(Sg_CS)
                hes_CSArray.append(hes_CS)
                b_CSArray.append(b_CS)
                hbArray.append(hb_BC)
                lambdaArray.append(lambda_BC)

            # Write results back to shapefile
            arcpy.AddField_management(outputShp, "WC_res", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "dg_CS", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "Sg_CS", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "hes_CS", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "b_CS", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "hb", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "lambda", "DOUBLE", 10, 6)

            outputFields = ["WC_res", "dg_CS", "Sg_CS", "hes_CS", "b_CS", "hb", "lambda"]
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = WC_resArray[recordNum]
                    row[1] = dg_CSArray[recordNum]
                    row[2] = Sg_CSArray[recordNum]
                    row[3] = hes_CSArray[recordNum]
                    row[4] = b_CSArray[recordNum]
                    row[5] = hbArray[recordNum]
                    row[6] = lambdaArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

        elif PTFOption == "Saxton_1986":
            # Check for required fields
            reqFields = ["OBJECTID", "Sand", "Clay", "WC_sat"]
            checkInputFields(reqFields, inputShp)

            # Retrieve info from input
            record = []
            sandPerc = []
            clayPerc = []
            WC_satArray = []

            with arcpy.da.SearchCursor(inputShp, reqFields) as searchCursor:
                for row in searchCursor:
                    objectID = row[0]
                    sand = row[1]
                    clay = row[2]
                    WCsat = row[3]

                    record.append(objectID)
                    sandPerc.append(sand)                    
                    clayPerc.append(clay)
                    WC_satArray.append(WCsat)

            WC_resArray = []
            A_Array = []
            B_Array = []
            hbArray = []
            lambdaArray = []

            for x in range(0, len(record)):
                # Calculate values
                WC_residual = 0
                A_Saxton = 100 * math.exp(-4.396 - (0.0715 * clayPerc[x])- (0.000488 * sandPerc[x]**2) - (0.00004285 * sandPerc[x]**2 * clayPerc[x])) 
                B_Saxton = -3.140 - (0.00222 * clayPerc[x]**2) - (0.00003484 * sandPerc[x]**2 * clayPerc[x])
                hb_BC = 10.0 * A_Saxton * (WC_satArray[x]** B_Saxton)  
                lambda_BC = -1.0 / float(B_Saxton)

                WC_resArray.append(WC_residual)
                A_Array.append(A_Saxton)
                B_Array.append(B_Saxton)
                hbArray.append(hb_BC)
                lambdaArray.append(lambda_BC)

            # Write results back to shapefile
            arcpy.AddField_management(outputShp, "WC_res", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "A_Saxton", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "B_Saxton", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "hb", "DOUBLE", 10, 6)
            arcpy.AddField_management(outputShp, "lambda", "DOUBLE", 10, 6)
            
            outputFields = ["WC_res", "A_Saxton", "B_Saxton", "hb", "lambda"]
            recordNum = 0
            with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
                for row in cursor:
                    row[0] = WC_resArray[recordNum]
                    row[1] = A_Array[recordNum]
                    row[2] = B_Array[recordNum]
                    row[3] = hbArray[recordNum]
                    row[4] = lambdaArray[recordNum]

                    cursor.updateRow(row)
                    recordNum += 1

        else:
            log.error('Invalid PTF option selected')
            sys.exit()

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

def Saxton_1986(outputFolder, outputShp):

    log.info('Calculating water content at points using Saxton et al. (1986)')

    PTFInfo = PTFdatabase.checkPTF("Saxton_1986")
    PTFType = PTFInfo.PTFType
    PTFPressures = PTFInfo.PTFPressures
    PTFFields = PTFInfo.PTFFields

    # Returns these arrays
    warningArray = []
    WC_0kPaArray = []
    WC_10kPaArray = []
    WC_33kPaArray = []
    WC_100kPaArray = []
    WC_200kPaArray = []
    WC_400kPaArray = []
    WC_1500kPaArray = []
    K_satArray = []

    # Get OID field
    OIDField = common.getOIDField(outputShp)

    # Requirements: sand, clay
    reqFields = [OIDField, "Sand", "Clay"]
    checks_PTFs.checkInputFields(reqFields, outputShp)

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

    for x in range(0, len(record)):

        warningFlag = checks_PTFs.checkValue("Sand", sandPerc[x], record[x])
        warningFlag = checks_PTFs.checkValue("Clay", clayPerc[x], record[x])
        warningArray.append(warningFlag)
        
        # Calculate water content using Saxton et. al (1986) m3m-3
        WC_0kPa  = 0.332 - (7.251 * 10**(-4) * sandPerc[x]) + (0.1276 * math.log(clayPerc[x], 10.0))

        A = math.exp(-4.396 - (0.0715 * clayPerc[x]) - (4.88 * 10**(-4) * sandPerc[x]**2) - (4.285 * 10**(-5) * sandPerc[x]**2 * clayPerc[x])) * 100
        B = - 3.14 - 2.22 * 10**(-3) * clayPerc[x]**2 - (3.484 * 10**(-5) * sandPerc[x]**2 * clayPerc[x])

        WC_10kPa = math.exp((2.302 - math.log(A)) / float(B))                    
        WC_33kPa = math.exp((math.log(33.0) - math.log(A)) / float(B))
        WC_100kPa = math.exp((math.log(100.0) - math.log(A)) / float(B))
        WC_200kPa = math.exp((math.log(200.0) - math.log(A)) / float(B))
        WC_400kPa = math.exp((math.log(400.0) - math.log(A)) / float(B))
        WC_1500kPa = math.exp((math.log(1500.0)-  math.log(A)) / float(B))

        K_sat = 10.0008 * (math.exp (12.012 - (0.0755 * sandPerc[x]) + ((- 3.895 + (0.03671 * sandPerc[x]) - (0.1103 * clayPerc[x]) + (8.7546 * 10**(-4) * clayPerc[x]**2))/(0.332 - (7.251 * 10**(-4) * sandPerc[x]) + (0.1276 * math.log(clayPerc[x], 10.0))))))

        outValues = [WC_10kPa, WC_33kPa, WC_100kPa, WC_200kPa, WC_400kPa, WC_1500kPa]
        checks_PTFs.checkNegOutput(outValues, x)

        WC_0kPaArray.append(WC_0kPa)
        WC_10kPaArray.append(WC_10kPa)
        WC_33kPaArray.append(WC_33kPa)
        WC_100kPaArray.append(WC_100kPa)
        WC_200kPaArray.append(WC_200kPa)
        WC_400kPaArray.append(WC_400kPa)
        WC_1500kPaArray.append(WC_1500kPa)
        K_satArray.append(K_sat)

    # Write K_sat to shapefile
    arcpy.AddField_management(outputShp, "K_sat", "DOUBLE", 10, 6)

    recordNum = 0
    with arcpy.da.UpdateCursor(outputShp, "K_sat") as cursor:
        for row in cursor:
            row[0] = K_satArray[recordNum]

            cursor.updateRow(row)
            recordNum += 1

    # Write fields to output shapefile
    common.writeFields(outputShp, PTFFields)

    recordNum = 0
    with arcpy.da.UpdateCursor(outputShp, PTFFields) as cursor:
        for row in cursor:
            row[0] = warningArray[recordNum]
            row[1] = WC_0kPaArray[recordNum]
            row[2] = WC_10kPaArray[recordNum]
            row[3] = WC_33kPaArray[recordNum]
            row[4] = WC_100kPaArray[recordNum]
            row[5] = WC_200kPaArray[recordNum]
            row[6] = WC_400kPaArray[recordNum]
            row[7] = WC_1500kPaArray[recordNum]

            cursor.updateRow(row)
            recordNum += 1

    log.info("Results written to the output shapefile inside the output folder")

    results = []
    results.append(warningArray)
    results.append(WC_0kPaArray)
    results.append(WC_10kPaArray)
    results.append(WC_33kPaArray)
    results.append(WC_100kPaArray)
    results.append(WC_200kPaArray)
    results.append(WC_400kPaArray)
    results.append(WC_1500kPaArray)

    return results
