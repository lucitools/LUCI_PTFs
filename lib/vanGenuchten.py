import arcpy
import os
import sys
import csv

from LUCI_PTFs.lib.external import six # Python 2/3 compatibility module
import configuration
import LUCI_PTFs.lib.log as log

from LUCI_PTFs.lib.refresh_modules import refresh_modules
refresh_modules([log])

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
        WC_1kPa = WC_residual[x] + ((WC_sat[x] - WC_residual[x]) / ((1.0 + ((alpha_VG[x] * 10.0) ** n_VG[x]))) ** m_VG[x])
        WC_3kPa = WC_residual[x] + ((WC_sat[x] - WC_residual[x]) / ((1.0 + ((alpha_VG[x] * 30.0) ** n_VG[x]))) ** m_VG[x])
        WC_10kPa = WC_residual[x] + ((WC_sat[x] - WC_residual[x]) / ((1.0 + ((alpha_VG[x] * 100.0) ** n_VG[x]))) ** m_VG[x])
        WC_33kPa = WC_residual[x] + ((WC_sat[x] - WC_residual[x]) / ((1.0 + ((alpha_VG[x] * 330.0) ** n_VG[x]))) ** m_VG[x])
        WC_100kPa = WC_residual[x] + ((WC_sat[x] - WC_residual[x]) / ((1.0 + ((alpha_VG[x] * 1000.0) ** n_VG[x]))) ** m_VG[x])
        WC_200kPa = WC_residual[x] + ((WC_sat[x] - WC_residual[x]) / ((1.0 + ((alpha_VG[x] * 2000.0) ** n_VG[x]))) ** m_VG[x])
        WC_1000kPa = WC_residual[x] + ((WC_sat[x] - WC_residual[x]) / ((1.0 + ((alpha_VG[x] * 10000.0) ** n_VG[x]))) ** m_VG[x])
        WC_1500kPa = WC_residual[x] + ((WC_sat[x] - WC_residual[x]) / ((1.0 + ((alpha_VG[x] * 15000.0) ** n_VG[x]))) ** m_VG[x])

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

def plotVG(outputFolder, record, WC_residualArray, WC_satArray, alpha_VGArray, n_VGArray, m_VGArray):
    # Create Van Genuchten plots
    import matplotlib.pyplot as plt
    import numpy as np

    # Plot 1: pressure on the y-axis, water content on the x-axis
    outPath = os.path.join(outputFolder, 'plotVG.png')
    title = 'Van Genuchten plots of ' + str(len(record)) + ' records'

    y = np.linspace(1.0, 100000.0, 100000)
    labels = []
    for i in range(0, len(record)):
        x = WC_residualArray[i] + ((WC_satArray[i] - WC_residualArray[i]) / ((1.0 + ((alpha_VGArray[i] * y * 10.0) ** n_VGArray[i]))) ** m_VGArray[i])
        plt.plot(x, y)

    plt.axhline(y=33.0)
    plt.axhline(y=0.0)
    plt.axhline(y=1500.0)
    plt.yscale('log')
    plt.title(title)
    plt.xlabel('Water content')
    plt.ylabel('kPa')
    plt.savefig(outPath, transparent=False)
    plt.close()
    log.info('Plot created')

    # Plot 2: pressure on the x-axis, WC on the y-axis
    outPath = os.path.join(outputFolder, 'plotVG_WC_yaxis.png')
    title = 'Van Genuchten plots of ' + str(len(record)) + ' records (water content on y-axis)'

    x = np.linspace(1.0, 2000.0, 10000)
    labels = []
    for i in range(0, len(record)):
        y = WC_residualArray[i] + ((WC_satArray[i] - WC_residualArray[i]) / ((1.0 + ((alpha_VGArray[i] * x * 10.0) ** n_VGArray[i]))) ** m_VGArray[i])
        plt.plot(x, y)

    plt.axvline(x=33.0)
    plt.axvline(x=0.0)
    plt.axvline(x=1500.0)
    plt.xscale('log')
    plt.title(title)
    plt.ylabel('Water content')
    plt.xlabel('kPa')
    plt.savefig(outPath, transparent=False)
    plt.close()
    log.info('Plot created with water content on the y-axis')

    # Plot 3: WC on the y-axis zoomed in to 1 to 600 kPa
    outPath = os.path.join(outputFolder, 'plotVG_200kPa.png')
    title = 'Van Genuchten plots of ' + str(len(record)) + ' records (water content on y-axis)'

    x = np.linspace(1.0, 300.0, 600)
    labels = []
    for i in range(0, len(record)):
        y = WC_residualArray[i] + ((WC_satArray[i] - WC_residualArray[i]) / ((1.0 + ((alpha_VGArray[i] * x * 10.0) ** n_VGArray[i]))) ** m_VGArray[i])
        plt.plot(x, y)

    plt.axvline(x=33.0)
    plt.axvline(x=0.0)
    plt.title(title)
    plt.ylabel('Water content')
    plt.xlabel('kPa')
    plt.savefig(outPath, transparent=False)
    plt.close()
    log.info('Plot created with lines for important thresholds')

def calcPressuresVG(x, WC_residual, WC_sat, alpha_VG, n_VG, m_VG, vgPressures):

    # Calculates water content at user-input pressures
    record = x + 1
    wcValues = [record]

    for pressure in vgPressures:

        waterContent = WC_residual + ((WC_sat - WC_residual) / ((1.0 + ((alpha_VG * pressure * 10.0) ** n_VG))) ** m_VG)
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
        # Calculate Se at different pressures
        Se_1kPa = 1.0 / float((1.0 + (alpha_VG[x] * 10.0) ** n_VG[x]) ** m_VG[x])
        Se_3kPa = 1.0 / float((1.0 + (alpha_VG[x] * 30.0) ** n_VG[x]) ** m_VG[x])
        Se_10kPa = 1.0 / float((1.0 + (alpha_VG[x] * 100.0) ** n_VG[x]) ** m_VG[x])
        Se_33kPa = 1.0 / float((1.0 + (alpha_VG[x] * 330.0) ** n_VG[x]) ** m_VG[x])
        Se_100kPa = 1.0 / float((1.0 + (alpha_VG[x] * 1000.0) ** n_VG[x]) ** m_VG[x])
        Se_1500kPa = 1.0 / float((1.0 + (alpha_VG[x] * 15000.0) ** n_VG[x]) ** m_VG[x])

        # Calculate K_Se at different pressures
        K_Se_1kPa = K_sat[x] * Se_1kPa ** l_MvG[x] * (1.0 - (1.0 - Se_1kPa ** (1.0 / m_VG[x])) ** m_VG[x]) ** 2.0
        K_Se_3kPa = K_sat[x] * Se_3kPa ** l_MvG[x] * (1.0 - (1.0 - Se_3kPa ** (1.0 / m_VG[x])) ** m_VG[x]) ** 2.0
        K_Se_10kPa = K_sat[x] * Se_10kPa ** l_MvG[x] * (1.0 - (1.0 - Se_10kPa ** (1.0 / m_VG[x])) ** m_VG[x]) ** 2.0
        K_Se_33kPa = K_sat[x] * Se_33kPa ** l_MvG[x] * (1.0 - (1.0 - Se_33kPa ** (1.0 / m_VG[x])) ** m_VG[x]) ** 2.0
        K_Se_100kPa = K_sat[x] * Se_100kPa ** l_MvG[x] * (1.0 - (1.0 - Se_100kPa ** (1.0 / m_VG[x])) ** m_VG[x]) ** 2.0
        K_Se_1500kPa = K_sat[x] * Se_1500kPa ** l_MvG[x] * (1.0 - (1.0 - Se_1500kPa ** (1.0 / m_VG[x])) ** m_VG[x]) ** 2.0

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

def plotMVG(outputFolder, record, K_satArray, alpha_VGArray, n_VGArray, m_VGArray, l_MvGArray, WC_satArray, WC_residualArray):
    # Create Van Genuchten plots
    import matplotlib.pyplot as plt
    import numpy as np

    # Plot 1: K(h) on the y-axis, h on the x-axis
    outPath = os.path.join(outputFolder, 'plotMVG.png')
    title = 'Mualem-van Genuchten plots of ' + str(len(record)) + ' records'

    x = np.linspace(1.0, 15000.0, 100000)
    labels = []
    for i in range(0, len(record)):
        y = K_satArray[i] * (((((1.0 + (alpha_VGArray[i] * x)**n_VGArray[i])**m_VGArray[i]) - (alpha_VGArray[i] * x)**(n_VGArray[i] - 1.0))**2.0) / (((1.0 + (alpha_VGArray[i] * x)**n_VGArray[i]))**(m_VGArray[i] * (l_MvGArray[i] + 2.0))))
        plt.plot(x, y)

    # plt.axvline(x=33.0)
    # plt.axvline(x=0.0)
    # plt.axvline(x=1500.0)
    plt.yscale('log')
    plt.xscale('log')
    plt.title(title)
    plt.ylabel('k(h)')
    plt.xlabel('kPa')
    plt.savefig(outPath, transparent=False)
    plt.close()
    log.info('Plot created')

    # Plot 2: k(theta) vs theta(h)
    outPath2 = os.path.join(outputFolder, 'plotMVG_Ktheta.png')
    title = 'Mualem-van Genuchten plots of ' + str(len(record)) + ' records'

    pressureVal = np.linspace(1.0, 15000.0, 10000)
    for i in range(0, len(record)):

        thetaHArray = []
        kthetaArray = []

        for j in range(0, len(pressureVal)):

            thetaH = WC_residualArray[i] + ((WC_satArray[i] - WC_residualArray[i]) / float((1.0 + (alpha_VGArray[i] * pressureVal[j])**n_VGArray[i])**m_VGArray[i]))
            thetaHArray.append(thetaH)

            Ktheta = K_satArray[i] * (((thetaH - WC_residualArray[i]) / float(WC_satArray[i] - WC_residualArray[i]))**l_MvGArray[i]) * (1.0 - (1.0 - ((thetaH - WC_residualArray[i]) / float(WC_satArray[i] - WC_residualArray[i]))**(1.0/m_VGArray[i]))**m_VGArray[i])**2.0
            kthetaArray.append(Ktheta)
            

        plt.plot(thetaHArray, kthetaArray)

    plt.title(title)
    plt.yscale('log')
    # plt.xscale('log')
    plt.ylabel('k(theta)')
    plt.xlabel('theta(h)')
    plt.savefig(outPath2, transparent=False)
    plt.close()
    log.info('Plot created')

    # Plot 3: k(theta) vs h
    outPath3 = os.path.join(outputFolder, 'plotMVG_Ktheta_h.png')
    title = 'Mualem-van Genuchten plots of ' + str(len(record)) + ' records'

    pressureVal = np.linspace(1.0, 15000.0, 10000)
    for i in range(0, len(record)):

        thetaHArray = []
        kthetaArray = []

        for j in range(0, len(pressureVal)):

            thetaH = WC_residualArray[i] + ((WC_satArray[i] - WC_residualArray[i]) / float((1.0 + (alpha_VGArray[i] * pressureVal[j])**n_VGArray[i])**m_VGArray[i]))
            thetaHArray.append(thetaH)

            Ktheta = K_satArray[i] * (((thetaH - WC_residualArray[i]) / float(WC_satArray[i] - WC_residualArray[i]))**l_MvGArray[i]) * (1.0 - (1.0 - ((thetaH - WC_residualArray[i]) / float(WC_satArray[i] - WC_residualArray[i]))**(1.0/m_VGArray[i]))**m_VGArray[i])**2.0
            kthetaArray.append(Ktheta)
            
        plt.plot(pressureVal, kthetaArray)

    plt.title(title)
    plt.yscale('log')
    plt.xscale('log')
    plt.ylabel('k(theta)')
    plt.xlabel('h (kPa)')
    plt.savefig(outPath3, transparent=False)
    plt.close()
    log.info('Plot created')
