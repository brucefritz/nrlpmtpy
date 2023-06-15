# -*- coding: utf-8 -*-
"""
Created on Tue May 23 22:45:54 2023

@author: bfritz
"""
import time
import netCDF4
import calendar as cdr
import numpy as np
from matplotlib import pyplot as plt
from astropy.time import Time

def convert_gps_to_utc(gps_in):
    t_gps = Time(gps_in, format='gps')
    return Time(t_gps, format='iso', scale='utc')

def generate_dStr_from_astropy_utc(tin):
    sin = str(tin)
    uyr = int(sin[0:4]) # yr
    umo = int(sin[5:7]) # mon
    udy = int(sin[8:10]) # day
    uhr = int(sin[11:13])
    umn = int(sin[14:16])
    return f'{udy} {cdr.month_name[umo]} {uyr}, {uhr:02}:{umn:02}'

def ecl0_analog_survey_plot(infile):
    print(f'Plotting data values from {infile}')
    f = netCDF4.Dataset(infile)
    print(f'Loading ALS variables...')
    amet        = f.variables['ALS_MET']
    atip_12V_V  = f.variables['ALS_TIP_V_12V']
    atip_12V_I  = f.variables['ALS_TIP_I_12V']
    amip_12V_V  = f.variables['ALS_MIP_V_12V']
    amip_12V_I  = f.variables['ALS_MIP_I_12V']
    atip_3V_V   = f.variables['ALS_TIP_V_3V']
    atip_3V_I   = f.variables['ALS_TIP_I_3V']
    amip_3V_V   = f.variables['ALS_MIP_V_3V']
    amip_3V_I   = f.variables['ALS_MIP_I_3V']
    atsm_28V_V  = f.variables['ALS_TIP_SUVM_V_28V']
    amsm_28V_V  = f.variables['ALS_MIP_SUVM_V_28V']
    atsm_5V_V   = f.variables['ALS_TIP_SUVM_V_5V']
    atsm_5V_I   = f.variables['ALS_TIP_SUVM_I_5V']
    amsm_5V_V   = f.variables['ALS_MIP_SUVM_V_5V']
    amsm_5V_I   = f.variables['ALS_MIP_SUVM_I_5V']
    atsm_3V_V   = f.variables['ALS_TIP_SUVM_V_3V']
    atsm_3V_I   = f.variables['ALS_TIP_SUVM_I_3V']
    amsm_3V_V   = f.variables['ALS_MIP_SUVM_V_3V']
    amsm_3V_I   = f.variables['ALS_MIP_SUVM_I_3V']

    try:
        fig, ax = plt.subplots(4, figsize=(6,7))
        t0 = time.localtime(amet[59])
        
        utc = convert_gps_to_utc(amet[59])
        dStr = generate_dStr_from_astropy_utc(utc)
        
        # if tstyle==None:
        #     dStr = f'{t0[2]} {cdr.month_name[t0[1]]} {t0[0]}, {t0[3]}:{t0[4]:02d}'
        
        title = ''
        v = ''
        fig.suptitle(f'{title}\n{dStr}\n{v} STP-H9 ECLIPSE - ALS Power Draw') 
    
        # # ta = (a['MET']-a['MET'][0])/60
        ta = [(x-amet[0])/3600 for x in amet]
        
        # if t_lim == None:
        t_lim = [0, np.max(ta)]
        #
        ax[0].plot(ta, atip_12V_V, 'k', label='12V')
        ax[0].plot(ta, atip_3V_V, 'purple',  label='3.3V')
        ax[0].set(ylabel='Tri-TIP [V]', xlim=(t_lim), ylim=(0,20))
        ax2 = ax[0].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(ta, atip_12V_I, 'r--', label='I$_{12V}$')
        ax2.plot(ta, atip_3V_I, 'b--', label='I$_{3V}$')
        ax2.set(ylabel='Tri-TIP [A]', ylim=(-0.2, 0.8))
        ax2.legend(loc=1, fontsize='x-small')
        # 
        ax[1].plot(ta, atsm_28V_V, 'g', label='28V')
        ax[1].plot(ta, atsm_5V_V, 'k', label='5V')
        ax[1].plot(ta, atsm_3V_V, 'purple', label='3.3V')
        ax[1].set(ylabel='TIP SUVM [V]', xlim=(t_lim), ylim=(0,35))
        # 
        ax2 = ax[1].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(ta, atsm_5V_I, 'r--', label='I$_{5V}$')
        ax2.plot(ta, atsm_3V_I, 'b--', label='I$_{3.3V}$')
        ax2.set(ylabel='TIP SUVM [A]', ylim=(-0.1, 0.25))
        ax2.legend(loc=1, fontsize='x-small')
        # 
        ax[2].plot(ta, amip_12V_V, 'k', label='12V')
        ax[2].plot(ta, amip_3V_V, 'purple',  label='3.3V')
        ax[2].set(ylabel='Tri-MIP [V]', xlim=(t_lim), ylim=(0,20))
        # 
        ax2 = ax[2].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(ta, amip_12V_I, 'r--', label='I$_{12V}$')
        ax2.plot(ta, amip_3V_I, 'b--', label='I$_{3V}$')
        ax2.set(ylabel='Tri-MIP [A]', ylim=(-0.2, 0.8))
        ax2.legend(loc=1, fontsize='x-small')
        # 
        ax[3].plot(ta, amsm_28V_V, 'g', label='28V')
        ax[3].plot(ta, amsm_5V_V, 'k', label='5V')
        ax[3].plot(ta, amsm_3V_V, 'purple', label='3.3V')
        ax[3].set(xlabel='UT [hr]', ylabel='MIP SUVM [V]', xlim=(t_lim), ylim=(0,35))
    
        ax2 = ax[3].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(ta, amsm_5V_I, 'r--', label='I$_{5V}$')
        ax2.plot(ta, amsm_3V_I, 'b--', label='I$_{3.3V}$')
        ax2.set(ylabel='MIP SUVM [A]', ylim=(-0.1, 0.25))
        ax2.legend(loc=1, fontsize='x-small')
        # 
        for z in range(4):
            ax[z].legend(loc=2, fontsize='x-small')
            ax[z].grid()
        # 
    except IndexError:
        print(f'No ALS data in this file!!!\n')
    # 
    print(f'Loading CTS variables...')
    cmet        = f.variables['CTS_MET']
    ctip_12V_V  = f.variables['CTS_TIP_V_12V']
    ctip_12V_I  = f.variables['CTS_TIP_I_12V']
    cmip_12V_V  = f.variables['CTS_MIP_V_12V']
    cmip_12V_I  = f.variables['CTS_MIP_I_12V']
    ctip_3V_V   = f.variables['CTS_TIP_V_3V']
    ctip_3V_I   = f.variables['CTS_TIP_I_3V']
    cmip_3V_V   = f.variables['CTS_MIP_V_3V']
    cmip_3V_I   = f.variables['CTS_MIP_I_3V']
    ctsm_28V_V  = f.variables['CTS_TIP_SUVM_V_28V']
    cmsm_28V_V  = f.variables['CTS_MIP_SUVM_V_28V']
    ctsm_5V_V   = f.variables['CTS_TIP_SUVM_V_5V']
    ctsm_5V_I   = f.variables['CTS_TIP_SUVM_I_5V']
    cmsm_5V_V   = f.variables['CTS_MIP_SUVM_V_5V']
    cmsm_5V_I   = f.variables['CTS_MIP_SUVM_I_5V']
    ctsm_3V_V   = f.variables['CTS_TIP_SUVM_V_3V']
    ctsm_3V_I   = f.variables['CTS_TIP_SUVM_I_3V']
    cmsm_3V_V   = f.variables['CTS_MIP_SUVM_V_3V']
    cmsm_3V_I   = f.variables['CTS_MIP_SUVM_I_3V']
    # 
    try:
        fig, ax = plt.subplots(4, figsize=(6,7))
        utc = convert_gps_to_utc(cmet[59])
        dStr = generate_dStr_from_astropy_utc(utc)
        
        # t0 = time.localtime(cmet[59])
        # if tstyle==None:
        #     dStr = f'{t0[2]} {cdr.month_name[t0[1]]} {t0[0]}, {t0[3]}:{t0[4]:02d}'
        
        title = ''
        v = ''
        fig.suptitle(f'{title}\n{dStr}\n{v} STP-H9 ECLIPSE - CTS Power Draw') 
    
        # # ta = (a['MET']-a['MET'][0])/60
        tc = [(x-cmet[0])/3600 for x in cmet]
        
        # if t_lim == None:
        t_lim = [0, np.max(tc)]
        #
        ax[0].plot(tc, ctip_12V_V, 'k', label='12V')
        ax[0].plot(tc, ctip_3V_V, 'purple',  label='3.3V')
        ax[0].set(ylabel='Tri-TIP [V]', xlim=(t_lim), ylim=(0,20))
        ax2 = ax[0].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(tc, ctip_12V_I, 'r--', label='I$_{12V}$')
        ax2.plot(tc, ctip_3V_I, 'b--', label='I$_{3V}$')
        ax2.set(ylabel='Tri-TIP [A]', ylim=(-0.2, 0.8))
        ax2.legend(loc=1, fontsize='x-small')
        # 
        ax[1].plot(tc, ctsm_28V_V, 'g', label='28V')
        ax[1].plot(tc, ctsm_5V_V, 'k', label='5V')
        ax[1].plot(tc, ctsm_3V_V, 'purple', label='3.3V')
        ax[1].set(ylabel='TIP SUVM [V]', xlim=(t_lim), ylim=(0,35))
        # 
        ax2 = ax[1].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(tc, ctsm_5V_I, 'r--', label='I$_{5V}$')
        ax2.plot(tc, ctsm_3V_I, 'b--', label='I$_{3.3V}$')
        ax2.set(ylabel='TIP SUVM [A]', ylim=(-0.1, 0.25))
        ax2.legend(loc=1, fontsize='x-small')
        # 
        ax[2].plot(tc, cmip_12V_V, 'k', label='12V')
        ax[2].plot(tc, cmip_3V_V, 'purple',  label='3.3V')
        ax[2].set(ylabel='Tri-MIP [V]', xlim=(t_lim), ylim=(0,20))
        # 
        ax2 = ax[2].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(tc, cmip_12V_I, 'r--', label='I$_{12V}$')
        ax2.plot(tc, cmip_3V_I, 'b--', label='I$_{3V}$')
        ax2.set(ylabel='Tri-MIP [A]', ylim=(-0.2, 0.8))
        ax2.legend(loc=1, fontsize='x-small')
        # 
        ax[3].plot(tc, cmsm_28V_V, 'g', label='28V')
        ax[3].plot(tc, cmsm_5V_V, 'k', label='5V')
        ax[3].plot(tc, cmsm_3V_V, 'purple', label='3.3V')
        ax[3].set(xlabel='UT [hr]', ylabel='MIP SUVM [V]', xlim=(t_lim), ylim=(0,35))
    
        ax2 = ax[3].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(tc, cmsm_5V_I, 'r--', label='I$_{5V}$')
        ax2.plot(tc, cmsm_3V_I, 'b--', label='I$_{3.3V}$')
        ax2.set(ylabel='MIP SUVM [A]', ylim=(-0.1, 0.25))
        ax2.legend(loc=1, fontsize='x-small')
        # 
        for z in range(4):
            ax[z].legend(loc=2, fontsize='x-small')
            ax[z].grid()
    except IndexError:
        print(f'No CTS Data in this file!!! \n')
    print(f'\n\n ------ Analog plot routine complete ------- \n\n')
    # 
def ecl0_cts_survey_plot(infile):
    print(f'Plotting data values from {infile}')
    f = netCDF4.Dataset(infile)
    # print(f.variables.keys())
    print(f'Loading ALS variables...')
    tmet0       = f.variables['TIP_M0_MET']
    print(tmet0[0:10])
    """
    ['TIP_M0_MET', 'MIP_M0_MET', 'TIP_M0_TIME', 'MIP_M0_TIME', 
     'TIP_M0_DARK', 'MIP_M0_DARK', 'TIP_M0_RED', 
     'MIP_M0_MG', 'TIP_M0_UV', 'MIP_M0_VK', 
     'TIP_M0_HEATER', 'TIP_M0_TF1', 'MIP_M0_TLENS', 'TIP_M0_TF2', 'MIP_M0_TPMT', 
     'TIP_M0_HV_mon', 'MIP_M0_HV_mon', 'TIP_M0_HV_adj', 'MIP_M0_HV_adj', 
     'TIP_M0_sun', 'MIP_M0_sun', 'TIP_M0_VREF', 'MIP_M0_VREF', 
     'TIP_M0_TIDC', 'MIP_M0_TIDC', 'TIP_M0_HV', 'MIP_M0_HV', 
     'TIP_M0_HV_Status', 'MIP_M0_HV_Status', 'TIP_M0_HV_Event', 'MIP_M0_HV_Event', 
     'TIP_M0_Sun_Event', 'MIP_M0_Sun_Event', 'TIP_M0_DK_EVENT', 'MIP_M0_DK_EVENT', 
     'TIP_M0_RD_EVENT', 'MIP_M0_RD_EVENT', 'TIP_M0_UV_EVENT', 'MIP_M0_UV_EVENT', 
     'TIP_M0_Sun_Override', 'MIP_M0_Sun_Override', 
     'TIP_M0_Dark_Override', 'MIP_M0_Dark_Override', 
     'TIP_M0_Red_Override', 'MIP_M0_Red_Override', 
     'TIP_M0_UV_Override', 'MIP_M0_UV_Override', 
     'TIP_M0_HV_Override', 'MIP_M0_HV_Override', 
     'TIP_M0_Shutter_Override', 'MIP_M0_Shutter_Override', 
     'TIP_M0_5V_Override', 'MIP_M0_5V_Override', 
     'TIP_M1_MET', 'MIP_M1_MET', 'TIP_M1_RUNTIME', 'MIP_M1_RUNTIME', 
     'TIP_M1_DARK', 'MIP_M1_DARK', 'TIP_M1_RED', 'MIP_M1_MG', 'TIP_M1_UV', 'MIP_M1_VK', 
     'TIP_SUVM_TIME', 'MIP_SUVM_TIME', 'TIP_SUVM_SEQUENCE', 'MIP_SUVM_SEQUENCE', 
     'TIP_SUVM_System_Counter', 'MIP_SUVM_System_Counter', 
     'TIP_SUVM_GPS_PPS', 'MIP_SUVM_GPS_PPS', 
     'TIP_SUVM_LAST_COMMAND_STATUS', 'MIP_SUVM_LAST_COMMAND_STATUS', 
     'TIP_SUVM_LAST_COMMAND_ID', 'MIP_SUVM_LAST_COMMAND_ID', 
     'TIP_SUVM_LAST_OP_CODE', 'MIP_SUVM_LAST_OP_CODE', 
     'TIP_SUVM_LAST_CMD_TIME', 'MIP_SUVM_LAST_CMD_TIME', 
     'TIP_SUVM_LAST_CMD_SUCCESS', 'MIP_SUVM_LAST_CMD_SUCCESS', 
     'TIP_SUVM_LAST_CMD_FAIL', 'MIP_SUVM_LAST_CMD_FAIL', 
     'TIP_SUVM_LAST_CRC', 'MIP_SUVM_LAST_CRC', 
     'TIP_SUVM_V5_IMON', 'MIP_SUVM_V5_IMON', 'TIP_SUVM_V5_VMON', 'MIP_SUVM_V5_VMON', 
     'TIP_SUVM_V3_IMON', 'MIP_SUVM_V3_IMON', 'TIP_SUVM_V3_VMON', 'MIP_SUVM_V3_VMON', 
     'TIP_SUVM_V22_IMON', 'MIP_SUVM_V22_IMON', 'TIP_SUVM_V22_VMON', 'MIP_SUVM_V22_VMON', 
     'TIP_SUVM_MOTOR_IMON', 'MIP_SUVM_MOTOR_IMON', 'TIP_SUVM_TEMP', 'MIP_SUVM_TEMP', 
     'TIP_SUVM_ENCODER_ZERO_OFFSET', 'MIP_SUVM_ENCODER_ZERO_OFFSET', 
     'TIP_SUVM_ENCODER_CURRENT_CT', 'MIP_SUVM_ENCODER_CURRENT_CT', 
     'TIP_SUVM_ENCODER_TARGET', 'MIP_SUVM_ENCODER_TARGET', 
     'TIP_SUVM_ENCODER_PROFILE_INDEX', 'MIP_SUVM_ENCODER_PROFILE_INDEX', 
     'TIP_SUVM_PWM_RATE', 'MIP_SUVM_PWM_RATE', 
     'TIP_SUVM_PWM_CTS_REMAIN', 'MIP_SUVM_PWM_CTS_REMAIN', 
     'TIP_SUVM_CRC', 'MIP_SUVM_CRC', 
     'TIP_SUVM_ENCODER_ANGLE', 'MIP_SUVM_ENCODER_ANGLE', 
     'TIP_SUVM_ENCODER_TARGET_ANGLE', 'MIP_SUVM_ENCODER_TARGET_ANGLE']
    """
    
    print(f'\n\n ------ CTS plot routine complete ------- \n\n')
    # 

def main():
    # cts_file = 'C:/data/ECLIPSE/flt/L0_CTS/NRL_1729_2023130_ECLIPSE_L0_CTS.nc'
    # ecl0_cts_survey_plot(cts_file)
    
    analog_file = 'C:/data/ECLIPSE/flt/L0_analog/2305/NRL_1729_2023130_ECLIPSE_L0_analog.nc'
    ecl0_analog_survey_plot(analog_file)
    
    
    
    """
    Will probably want to add multiple x labels to plots in the future:
    https://stackoverflow.com/questions/53043732/multiple-x-labels-on-pyplot
    """
    # 
if __name__ == "__main__":
    print(f"==== {__file__} ====")
    main()