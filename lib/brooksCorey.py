import arcpy
import os
import sys
import csv

from LUCI_PTFs.lib.external import six # Python 2/3 compatibility module
import configuration
import LUCI_PTFs.lib.log as log

from LUCI_PTFs.lib.refresh_modules import refresh_modules
refresh_modules([log])

def calcBrooksCoreyFXN(pressure, hb_BC, theta_r, theta_s, lambda_BC):

    log.info('DEBUG: pressure: ' + str(pressure))
    log.info('DEBUG: hb_BC: ' + str(hb_BC))
    log.info('DEBUG: theta_r: ' + str(theta_r))
    log.info('DEBUG: theta_s: ' + str(theta_s))
    log.info('DEBUG: lambda_BC: ' + str(lambda_BC))

    bcArray = []

    for i in range(0, len(pressure)):

        # Calculate the WC @ pressure using Brooks-Corey
        if pressure[i] <= hb_BC:
            # if pressure is less than/equal to hb_BC
            bc_WC = theta_s
            bcArray.append(bc_WC)

        else:
            # if pressure is greater than hb_BC
            bc_WC = theta_r + (((theta_s - theta_r) * (hb_BC ** lambda_BC)) / (pressure[i] ** lambda_BC))
            
            ## From Anh: but is this right? I have doubts
            bc_WC = theta_r + ((theta_s - theta_r) * (hb_BC / float(pressure)) ** lamda_BC[i])

            bcArray.append(bc_WC)

    return bcArray

def plotBrooksCorey(outputFolder, record, WC_resArray, WC_satArray, hbArray, lambdaArray, nameArray):
    # Create Brooks-Corey plots
    import matplotlib.pyplot as plt
    import numpy as np

    ################################
    ### Plot 0: individual plots ###
    ################################

    # Plot 0: pressure on the y-axis and water content on the x-axis
    for i in range(0, len(record)):
        outName = str(nameArray[i]) + '.png'
        outPath = os.path.join(outputFolder, outName)
        title = 'Brooks-Corey plot for ' + str(nameArray[i])

        # Set pressure vector
        psi_kPa = np.linspace(0.01, 1500.0, 1500)

        # Calculate WC over that pressure vector
        bc_WC = calcBrooksCoreyFXN(psi_kPa, hbArray[i], WC_resArray[i], WC_satArray[i], lambdaArray[i])
        
        '''
        # Convert pressure to cm for plotting purposes
        psi_cm = 10.0 * (psi_kPa)

        kPa_sat = np.where(psi_kPa==0)
        vg_WC_sat = vg_WC[kPa_sat]
        
        if vg_WC_sat > WC_satArray[i]:
            log.warning('Warning: calculated water content at saturation using the soil moisture retention curve is higher than theta(sat)')
            log.warning('Please check soil: ' + nameArray[i])
            log.warning('Water content at saturation calculated using the SMRC: ' + str(vg_WC_sat))
            log.warning('theta(sat) calculated using the PTF: ' + str(WC_satArray[i]))
        
        minWC = min(vg_WC)
        maxWC = max(vg_WC)
        log.info('DEBUG minWC: ' + str(minWC))
        log.info('DEBUG maxWC: ' + str(maxWC))
        '''

        plt.plot(bc_WC, psi_kPa, label=str(nameArray[i]))
        plt.legend(loc="best")
        plt.axhline(y=33.0, color='r', linestyle='-')
        plt.yscale('log')
        # plt.xlim([0, WC_satArray[i] + 0.1])
        # plt.xlim([minWC - 0.1, maxWC + 0.1])
        plt.title(title)
        plt.xlabel('Water content')
        plt.ylabel('- kPa')
        plt.savefig(outPath, transparent=False)
        plt.close()
        log.info('Plot created for soil ' + str(nameArray[i]))