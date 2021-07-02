import arcpy
import os
import sys
import csv

from LUCI_PTFs.lib.external import six # Python 2/3 compatibility module
import configuration
import LUCI_PTFs.lib.log as log

from LUCI_PTFs.lib.refresh_modules import refresh_modules
refresh_modules([log])

def calcVGfxn(pressure, theta_res, theta_sat, alpha, n, m):
    
    # Function to calculate the water content at a given pressure
    # or vector/range of pressures
    # Pressure is normally expected in kPa
    # Unless VG parameters have been derived using moisture content vs pressure data
    # at different units

    vg_WC = theta_res + ((theta_sat - theta_res) / ((1.0 + ((alpha * pressure) ** n))) ** m)
    
    # Return WC    
    return vg_WC

def calcMVGfxn(pressure, K_sat, alpha, n, m, l):

    # Calculate Mualem-van Genuchten

    # Calc Se
    Se_MVG = 1.0 / float((1.0 + (alpha * pressure) ** n) ** m)

    # Calc K_Se
    K_Se_MVG = K_sat * Se_MVG ** l * (1.0 - (1.0 - Se_MVG ** (1.0 / m)) ** m) ** 2.0

    return Se_MVG, K_Se_MVG

def calcKhfxn(pressure, K_sat, alpha, n, m, l):

    # Calculate K(h)
    Kh = K_sat * (((((1.0 + (alpha * pressure)**n)**m) - (alpha * pressure)**(n - 1.0))**2.0) / (((1.0 + (alpha * pressure)**n))**(m * (l + 2.0))))

    return Kh

def calcthetaHKfxn(pressure, WC_res, WC_sat, alpha, n, m, K_sat, l):

    # Calculate thetaH and Ktheta for MVG
    thetaH = calcVGfxn(pressure, WC_res, WC_sat, alpha, n, m)            
    Ktheta = K_sat * (((thetaH - WC_res) / float(WC_sat - WC_res))**l) * (1.0 - (1.0 - ((thetaH - WC_res) / float(WC_sat - WC_res))**(1.0/m))**m)**2.0
            
    return thetaH, Ktheta

def calcVG(WC_residual, WC_sat, alpha_VG, n_VG, m_VG):
    # Calculates soil water content using the van Genuchten equation

    WC_1kPaArray = []
    WC_3kPaArray = []
    WC_10kPaArray = []
    WC_33kPaArray = []
    WC_100kPaArray = []
    WC_200kPaArray = []
    WC_1000kPaArray = []
    WC_1500kPaArray = []

    for x in range(0, len(WC_residual)):
        WC_1kPa = calcVGfxn(1.0, WC_residual[x], WC_sat[x], alpha_VG[x], n_VG[x], m_VG[x])        
        WC_3kPa = calcVGfxn(3.0, WC_residual[x], WC_sat[x], alpha_VG[x], n_VG[x], m_VG[x])
        WC_10kPa = calcVGfxn(10.0, WC_residual[x], WC_sat[x], alpha_VG[x], n_VG[x], m_VG[x])
        WC_33kPa = calcVGfxn(33.0, WC_residual[x], WC_sat[x], alpha_VG[x], n_VG[x], m_VG[x])
        WC_100kPa = calcVGfxn(100.0, WC_residual[x], WC_sat[x], alpha_VG[x], n_VG[x], m_VG[x])
        WC_200kPa = calcVGfxn(200.0, WC_residual[x], WC_sat[x], alpha_VG[x], n_VG[x], m_VG[x])
        WC_1000kPa = calcVGfxn(1000.0, WC_residual[x], WC_sat[x], alpha_VG[x], n_VG[x], m_VG[x])
        WC_1500kPa = calcVGfxn(1500.0, WC_residual[x], WC_sat[x], alpha_VG[x], n_VG[x], m_VG[x])

        WC_1kPaArray.append(WC_1kPa)
        WC_3kPaArray.append(WC_3kPa)
        WC_10kPaArray.append(WC_10kPa)
        WC_33kPaArray.append(WC_33kPa)
        WC_100kPaArray.append(WC_100kPa)
        WC_200kPaArray.append(WC_200kPa)
        WC_1000kPaArray.append(WC_1000kPa)
        WC_1500kPaArray.append(WC_1500kPa)

    return WC_1kPaArray, WC_3kPaArray, WC_10kPaArray, WC_33kPaArray, WC_100kPaArray, WC_200kPaArray, WC_1000kPaArray, WC_1500kPaArray

def writeOutputVG(outputShp, WC_1kPaArray, WC_3kPaArray, WC_10kPaArray, WC_33kPaArray, WC_100kPaArray, WC_200kPaArray, WC_1000kPaArray, WC_1500kPaArray):
    # Write outputs of VG equations to output shapefile

    # Add fields
    arcpy.AddField_management(outputShp, "WC_1kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "WC_3kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "WC_10kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "WC_33kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "WC_100kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "WC_200kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "WC_1000kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "WC_1500kPa", "DOUBLE", 10, 6)

    outputFields = ["WC_1kPa", "WC_3kPa", "WC_10kPa", "WC_33kPa", "WC_100kPa", "WC_200kPa", "WC_1000kPa", "WC_1500kpa"]

    recordNum = 0
    with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
        for row in cursor:
            row[0] = WC_1kPaArray[recordNum]
            row[1] = WC_3kPaArray[recordNum]
            row[2] = WC_10kPaArray[recordNum]
            row[3] = WC_33kPaArray[recordNum]
            row[4] = WC_100kPaArray[recordNum]
            row[5] = WC_200kPaArray[recordNum]
            row[6] = WC_1000kPaArray[recordNum]
            row[7] = WC_1500kPaArray[recordNum]

            cursor.updateRow(row)
            recordNum += 1

def writeVGParams(outputShp, WC_residualArray, WC_satArray, alpha_VGArray, n_VGArray, m_VGArray):
    # Write VG parameters to the shapefile

    # Add fields
    arcpy.AddField_management(outputShp, "WC_res", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "WC_sat", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "alpha_VG", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "n_VG", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "m_VG", "DOUBLE", 10, 6)

    outputFields = ["WC_res", "WC_sat", "alpha_VG", "n_VG", "m_VG"]

    recordNum = 0
    with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
        for row in cursor:
            row[0] = WC_residualArray[recordNum]
            row[1] = WC_satArray[recordNum]
            row[2] = alpha_VGArray[recordNum]
            row[3] = n_VGArray[recordNum]
            row[4] = m_VGArray[recordNum]

            cursor.updateRow(row)
            recordNum += 1

def plotVG(outputFolder, record, WC_residualArray, WC_satArray, alpha_VGArray, n_VGArray, m_VGArray, nameArray, textureArray):
    # Create Van Genuchten plots
    import matplotlib.pyplot as plt
    import numpy as np

    ################################
    ### Plot 0: individual plots ###
    ################################

    # Plot 0: pressure on the y-axis and water content on the x-axis
    for i in range(0, len(record)):
        outName = str(nameArray[i]) + '.png'
        outPath = os.path.join(outputFolder, outName)
        title = 'Van Genuchten plot for ' + str(nameArray[i])

        # Set pressure vector
        psi_kPa = np.linspace(0.0, 1500.0, 1500)

        # Calculate WC over that pressure vector
        vg_WC = calcVGfxn(psi_kPa, WC_residualArray[i], WC_satArray[i], alpha_VGArray[i], n_VGArray[i], m_VGArray[i])
        
        # Convert pressure to cm for plotting purposes
        psi_cm = 10.0 * (psi_kPa)

        plt.plot(vg_WC, psi_kPa, label=str(nameArray[i]))
        plt.legend()
        plt.axhline(y=33.0)
        plt.axhline(y=0.0)
        plt.axhline(y=1500.0)
        plt.yscale('log')
        plt.title(title)
        plt.xlabel('Water content')
        plt.ylabel('- kPa')
        plt.savefig(outPath, transparent=False)
        plt.close()
        log.info('Plot created for soil ' + str(nameArray[i]))

    #########################################
    ### Plot 1: one plot with all records ###
    #########################################

    # Plot 1: pressure on the y-axis, water content on the x-axis
    outPath = os.path.join(outputFolder, 'plotVG.png')
    title = 'Van Genuchten plots of ' + str(len(record)) + ' soils'

    psi_kPa = np.linspace(0.0, 1500.0, 1500)
    labels = []    
    for i in range(0, len(record)):

        # Calculate WC for pressure vector
        vg_WC = calcVGfxn(psi_kPa, WC_residualArray[i], WC_satArray[i], alpha_VGArray[i], n_VGArray[i], m_VGArray[i])
        
        # Convert pressure to cm for plotting
        psi_cm = 10.0 * psi_kPa

        plt.plot(vg_WC, psi_kPa, label=str(nameArray[i]))

    plt.legend(ncol=2, fontsize=12)
    plt.axhline(y=33.0)
    plt.axhline(y=0.0)
    plt.axhline(y=1500.0)
    plt.xlim([0, 1])
    plt.yscale('log')
    plt.title(title)
    plt.xlabel('Water content')
    plt.ylabel('- kPa')
    plt.savefig(outPath, transparent=False)
    plt.close()
    log.info('Plot created')

    #########################################
    ### Plot 2: one plot with all records ###
    #########################################

    # Plot 2: pressure on the x-axis, WC on the y-axis
    outPath = os.path.join(outputFolder, 'plotVG_WC_yaxis.png')
    title = 'Van Genuchten plots of ' + str(len(record)) + ' soils (water content on y-axis)'

    # Define pressure vector 
    psi_kPa = np.linspace(0.0, 1500.0, 1500)
    labels = []
    for i in range(0, len(record)):

        # Calculate WC 
        vg_WC = calcVGfxn(psi_kPa, WC_residualArray[i], WC_satArray[i], alpha_VGArray[i], n_VGArray[i], m_VGArray[i])
        
        plt.plot(psi_kPa, vg_WC, label=str(nameArray[i]))

    plt.legend(ncol=2, fontsize=12)
    plt.axvline(x=33.0)
    plt.axvline(x=0.0)
    plt.axvline(x=1500.0)
    plt.xlim([1, 1000000.0])
    plt.ylim([0, 1.0])
    plt.xscale('log')
    plt.title(title)
    plt.ylabel('Water content')
    plt.xlabel('- kPa')
    plt.savefig(outPath, transparent=False)
    plt.close()
    log.info('Plot created with water content on the y-axis')

    #########################################
    ### Plot 3: one plot with all records ###
    #########################################

    # Plot 3: WC on the y-axis zoomed in to 1 to 600 kPa
    outPath = os.path.join(outputFolder, 'plotVG_200kPa.png')
    title = 'Van Genuchten plots of ' + str(len(record)) + ' soils (water content on y-axis)'

    psi_kPa = np.linspace(1.0, 300.0, 600)
    labels = []
    for i in range(0, len(record)):
        vg_WC = calcVGfxn(psi_kPa, WC_residualArray[i], WC_satArray[i], alpha_VGArray[i], n_VGArray[i], m_VGArray[i])
        plt.plot(psi_kPa, vg_WC, label=str(nameArray[i]))

    plt.legend(ncol=2, fontsize=12)
    plt.axvline(x=33.0)
    plt.axvline(x=0.0)
    plt.xlim([0, 600.0])
    plt.ylim([0, 1.0])
    plt.title(title)
    plt.ylabel('Water content')
    plt.xlabel('- kPa')
    plt.savefig(outPath, transparent=False)
    plt.close()
    log.info('Plot created with lines for important thresholds')

def calcPressuresVG(x, WC_residual, WC_sat, alpha_VG, n_VG, m_VG, vgPressures):

    # Calculates water content at user-input pressures
    record = x + 1
    wcValues = [record]

    for pressure in vgPressures:

        waterContent = calcVGfxn(pressure, WC_residual, WC_sat, alpha_VG, n_VG, m_VG)
        wcValues.append(waterContent)

    return wcValues

def writeWaterContent(outputFolder, record, headings, wcArrays):

    outCSV = os.path.join(outputFolder, 'WaterContent.csv')

    with open(outCSV, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headings)

        for i in range(0, len(record)):
            row = wcArrays[i]
            writer.writerow(row)

        msg = 'Output CSV with water content saved to: ' + str(outCSV)
        log.info(msg)

    csv_file.close()

def calcMVG(K_sat, alpha_VG, n_VG, m_VG, l_MvG):

    # Initialise empty arrays
    Se_1kPaArray = []
    Se_3kPaArray = []
    Se_10kPaArray = []
    Se_33kPaArray = []
    Se_100kPaArray = []
    Se_1500kPaArray = []

    K_Se_1kPaArray = []
    K_Se_3kPaArray = []
    K_Se_10kPaArray = []
    K_Se_33kPaArray = []
    K_Se_100kPaArray = []
    K_Se_1500kPaArray = []
    
    for x in range(0, len(alpha_VG)):

        # Calculate Se and K_Se at different pressures
        Se_1kPa, K_Se_1kPa = calcMVGfxn(1.0, K_sat[x], alpha_VG[x], n_VG[x], m_VG[x], l_MvG[x])
        Se_3kPa, K_Se_3kPa = calcMVGfxn(3.0, K_sat[x], alpha_VG[x], n_VG[x], m_VG[x], l_MvG[x])
        Se_10kPa, K_Se_10kPa = calcMVGfxn(10.0, K_sat[x], alpha_VG[x], n_VG[x], m_VG[x], l_MvG[x])
        Se_33kPa, K_Se_33kPa = calcMVGfxn(33.0, K_sat[x], alpha_VG[x], n_VG[x], m_VG[x], l_MvG[x])
        Se_100kPa, K_Se_100kPa = calcMVGfxn(100.0, K_sat[x], alpha_VG[x], n_VG[x], m_VG[x], l_MvG[x])
        Se_1500kPa, K_Se_1500kPa = calcMVGfxn(1500.0, K_sat[x], alpha_VG[x], n_VG[x], m_VG[x], l_MvG[x])

        Se_1kPaArray.append(Se_1kPa)
        Se_3kPaArray.append(Se_3kPa)
        Se_10kPaArray.append(Se_10kPa)
        Se_33kPaArray.append(Se_33kPa)
        Se_100kPaArray.append(Se_100kPa)
        Se_1500kPaArray.append(Se_1500kPa)

        K_Se_1kPaArray.append(K_Se_1kPa)
        K_Se_3kPaArray.append(K_Se_3kPa)
        K_Se_10kPaArray.append(K_Se_10kPa)
        K_Se_33kPaArray.append(K_Se_33kPa)
        K_Se_100kPaArray.append(K_Se_100kPa)
        K_Se_1500kPaArray.append(K_Se_1500kPa)

    return Se_1kPaArray, Se_3kPaArray, Se_10kPaArray, Se_33kPaArray, Se_100kPaArray, Se_1500kPaArray, K_Se_1kPaArray, K_Se_3kPaArray, K_Se_10kPaArray, K_Se_33kPaArray, K_Se_100kPaArray, K_Se_1500kPaArray

def writeOutputMVG(outputShp, Se_1kPaArray, Se_3kPaArray, Se_10kPaArray, Se_33kPaArray, Se_100kPaArray, Se_1500kPaArray, K_Se_1kPaArray, K_Se_3kPaArray, K_Se_10kPaArray, K_Se_33kPaArray, K_Se_100kPaArray, K_Se_1500kPaArray):
    # Write the outputs to the output shapefile

    # Add fields
    arcpy.AddField_management(outputShp, "Se1kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "Se3kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "Se10kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "Se33kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "Se100kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "Se1500kPa", "DOUBLE", 10, 6)

    arcpy.AddField_management(outputShp, "KSe1kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "KSe3kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "KSe10kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "KSe33kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "KSe100kPa", "DOUBLE", 10, 6)
    arcpy.AddField_management(outputShp, "KSe1500kPa", "DOUBLE", 10, 6)

    outputFields = ["Se1kPa", "Se3kPa", "Se10kPa", "Se33kPa", "Se100kPa", "Se1500kPa", "KSe1kPa", "KSe3kPa", "KSe10kPa", "KSe33kPa", "KSe100kPa", "KSe1500kPa"]

    recordNum = 0
    with arcpy.da.UpdateCursor(outputShp, outputFields) as cursor:
        for row in cursor:
            row[0] = Se_1kPaArray[recordNum]
            row[1] = Se_3kPaArray[recordNum]
            row[2] = Se_10kPaArray[recordNum]
            row[3] = Se_33kPaArray[recordNum]
            row[4] = Se_100kPaArray[recordNum]
            row[5] = Se_1500kPaArray[recordNum]
            row[6] = K_Se_1kPaArray[recordNum]
            row[7] = K_Se_3kPaArray[recordNum]
            row[8] = K_Se_10kPaArray[recordNum]
            row[9] = K_Se_33kPaArray[recordNum]
            row[10] = K_Se_100kPaArray[recordNum]
            row[11] = K_Se_1500kPaArray[recordNum]

            cursor.updateRow(row)
            recordNum += 1

def plotMVG(outputFolder, record, K_satArray, alpha_VGArray, n_VGArray, m_VGArray, l_MvGArray, WC_satArray, WC_residualArray, nameArray, textureArray):
    # Create Van Genuchten plots
    import matplotlib.pyplot as plt
    import numpy as np

    ################################
    ### Plot 0: individual plots ###
    ################################

    # Plot 0: individual plots of K(h) on the y-axis and h on the x-axis
    for i in range(0, len(record)):
        outName = 'MVG_' + str(nameArray[i]) + '.png'
        outPath = os.path.join(outputFolder, outName)
        title = 'Mualem-Van Genuchten plot for ' + str(nameArray[i])

        # h
        x = np.linspace(0.0, 1500.0, 1500)

        # K(h)
        y = calcKhfxn(x, K_satArray[i], alpha_VGArray[i], n_VGArray[i], m_VGArray[i], l_MvGArray[i])
        
        plt.plot(x, y, label=str(nameArray[i]))
        plt.legend()
        plt.yscale('log')
        plt.xscale('log')
        plt.title(title)
        plt.xlabel('- kPa')
        plt.ylabel('K(h)')
        plt.savefig(outPath, transparent=False)
        plt.close()
        log.info('MVG plot created for soil ' + str(nameArray[i]))

    #########################################
    ### Plot 1: one plot with all records ###
    #########################################

    # Plot 1: K(h) on the y-axis, h on the x-axis
    outPath = os.path.join(outputFolder, 'plotMVG.png')
    title = 'Mualem-van Genuchten plots of ' + str(len(record)) + ' soils'

    x = np.linspace(0.0, 1500.0, 1500)
    labels = []
    for i in range(0, len(record)):
        y = calcKhfxn(x, K_satArray[i], alpha_VGArray[i], n_VGArray[i], m_VGArray[i], l_MvGArray[i])
        plt.plot(x, y, label=str(nameArray[i]))

    plt.yscale('log')
    plt.xscale('log')
    plt.title(title)
    plt.ylabel('k(h)')
    plt.xlabel('- kPa')
    plt.legend(ncol=2, fontsize=12)
    plt.xlim([1, 150000])
    plt.savefig(outPath, transparent=False)
    plt.close()
    log.info('Plot created')

    #########################################
    ### Plot 2: one plot with all records ###
    #########################################

    # Plot 2: k(theta) vs theta(h)
    outPath2 = os.path.join(outputFolder, 'plotMVG_Ktheta.png')
    title = 'Mualem-van Genuchten plots of ' + str(len(record)) + ' soils'

    pressureVal = np.linspace(0.0, 1500.0, 1500)
    for i in range(0, len(record)):
        thetaH, Ktheta = calcthetaHKfxn(pressureVal, WC_residualArray[i], WC_satArray[i], alpha_VGArray[i], n_VGArray[i], m_VGArray[i], K_satArray[i], l_MvGArray[i])          
        plt.plot(thetaH, Ktheta, label=str(nameArray[i]))

    plt.title(title)
    plt.yscale('log')
    plt.ylabel('k(theta)')
    plt.xlabel('theta(h)')
    plt.legend(ncol=2, fontsize=12)
    plt.xlim([0, 1])
    plt.savefig(outPath2, transparent=False)
    plt.close()
    log.info('Plot created')

    #########################################
    ### Plot 3: one plot with all records ###
    #########################################

    # Plot 3: k(theta) vs h
    outPath3 = os.path.join(outputFolder, 'plotMVG_Ktheta_h.png')
    title = 'Mualem-van Genuchten plots of ' + str(len(record)) + ' soils'

    pressureVal = np.linspace(1.0, 1500.0, 1500)
    for i in range(0, len(record)):
        thetaH, Ktheta = calcthetaHKfxn(pressureVal, WC_residualArray[i], WC_satArray[i], alpha_VGArray[i], n_VGArray[i], m_VGArray[i], K_satArray[i], l_MvGArray[i])
        plt.plot(pressureVal, Ktheta, label=str(nameArray[i]))

    plt.title(title)
    plt.yscale('log')
    plt.xscale('log')
    plt.ylabel('k(theta)')
    plt.xlabel('h (- cm)')
    plt.legend(ncol=2, fontsize=12)
    plt.xlim([1, 150000])
    plt.savefig(outPath3, transparent=False)
    plt.close()
    log.info('Plot created')
