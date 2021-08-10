import arcpy
import os
import sys
import csv

from LUCI_PTFs.lib.external import six # Python 2/3 compatibility module
import configuration
import LUCI_PTFs.lib.log as log
import LUCI_PTFs.lib.common as common

from LUCI_PTFs.lib.refresh_modules import refresh_modules
refresh_modules([log, common])

def calcBrooksCoreyFXN(pressure, hb_BC, theta_r, theta_s, lambda_BC):

    # log.info('DEBUG: pressure: ' + str(pressure))
    # log.info('DEBUG: hb_BC: ' + str(hb_BC))
    # log.info('DEBUG: theta_r: ' + str(theta_r))
    # log.info('DEBUG: theta_s: ' + str(theta_s))
    # log.info('DEBUG: lambda_BC: ' + str(lambda_BC))

    bcArray = []

    for i in range(0, len(pressure)):

        pressureVal = pressure[i]

        # Calculate the WC @ pressure using Brooks-Corey
        if pressure[i] < hb_BC:
            # if pressure is less than to hb_BC
            bc_WC = theta_s
            bcArray.append(bc_WC)

        else:
            # if pressure is greater than hb_BC
            # bc_WC = theta_r + (((theta_s - theta_r) * (hb_BC ** lambda_BC)) / (pressure[i] ** lambda_BC))
            
            # if pressure is greater than hb_BC
            # bc_WC = theta_r + ((theta_s - theta_r) * (hb_BC / float(pressureVal)) ** lambda_BC)
            # bc_WC = theta_r + (theta_s - theta_r) * (hb_BC / float(pressureVal) ** lambda_BC)

            bc_WC = theta_r + (theta_s - theta_r) * (hb_BC/ float(pressureVal)) ** lambda_BC

            bcArray.append(bc_WC)

    return bcArray

def writeBCParams(outputShp, warning, WC_res, WC_sat, lambda_BC, hb_BC):

    # Write BC Params to shapefile

    # Add fields
    arcpy.AddField_management(outputShp, "warning", "TEXT")
    arcpy.AddField_management(outputShp, "WC_res", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "WC_sat_BC", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "lambda_BC", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "hb_BC", "DOUBLE", 10, 6)

    outputFields = ["warning", "WC_res", "WC_sat_BC", "lambda_BC", "hb_BC"]

    recordNum = 0
    with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
        for row in cursor:
            row[0] = warning[recordNum]
            row[1] = WC_res[recordNum]
            row[2] = WC_sat[recordNum]
            row[3] = lambda_BC[recordNum]
            row[4] = hb_BC[recordNum]

            cursor.updateRow(row)
            recordNum += 1

def plotBrooksCorey(outputFolder, WC_resArray, WC_satArray, hbArray, lambdaArray, nameArray):
    # Create Brooks-Corey plots
    import matplotlib.pyplot as plt
    import numpy as np

    # Check what unit the user wants to output
    PTFUnit = common.getInputValue(outputFolder, 'Pressure_units_plot')

    ################################
    ### Plot 0: individual plots ###
    ################################

    # Plot 0: pressure on the y-axis and water content on the x-axis
    for i in range(0, len(nameArray)):
        outName = 'bc_' + str(nameArray[i]) + '.png'
        outPath = os.path.join(outputFolder, outName)
        title = 'Brooks-Corey plot for ' + str(nameArray[i])

        # Set pressure vector
        psi_kPa = np.linspace(0.01, 1500.0, 1500)

        # Calculate WC over that pressure vector
        bc_WC = calcBrooksCoreyFXN(psi_kPa, hbArray[i], WC_resArray[i], WC_satArray[i], lambdaArray[i])
        
        ## Figure out what to do about multipliers
        if PTFUnit == 'kPa':
            pressureUnit = 'kPa'
            psi_plot = psi_kPa

        elif PTFUnit == 'cm':
            pressureUnit = 'cm'
            psi_plot = 10.0 * psi_kPa

        elif PTFUnit == 'm':
            pressureUnit = 'm'
            psi_plot = 0.1 * psi_kPa

        # Convert psi_plot to negative for plotting
        psi_neg = -1.0 * psi_plot

        plt.plot(psi_neg, bc_WC, label=str(nameArray[i]))        
        plt.xscale('symlog')
        plt.legend(loc="best")
        plt.title(title)
        plt.xlabel('Pressure (' + str(pressureUnit) + ')')
        plt.ylabel('Volumetric water content')
        plt.savefig(outPath, transparent=False)
        plt.close()
        log.info('Plot created for soil ' + str(nameArray[i]))