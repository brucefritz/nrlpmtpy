# -*- coding: utf-8 -*-
"""
Created on Tue May 23 22:45:54 2023

@author: bfritz
"""
import os
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

def ecl0_analog_survey_plot(infile, save=0):
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
        if save > 0:
            path, fname = os.path.split(infile)
            s = str(utc)
            outname = f'{path}/{s[0:4]}{s[5:7]}{s[8:10]}-STPH9-ECLIPSE-ALS_Power.png'
            print(f' Saving plot ... {outname}')
            fig.savefig(outname)
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
        if save > 0:
            path, fname = os.path.split(infile)
            s = str(utc)
            outname = f'{path}/{s[0:4]}{s[5:7]}{s[8:10]}-STPH9-ECLIPSE-CTS_Power.png'
            print(f' Saving plot ... {outname}')
            fig.savefig(outname)
    except IndexError:
        print(f'No CTS Data in this file!!! \n')
    print(f'\n\n - Analog plot routine complete for {infile} - \n\n')
    # 
def ecl0_survey_plot(infile, unit='', content='PMT only', save=0):
    print(f'Plotting data values from {infile}')
    f = netCDF4.Dataset(infile)
    # print(f.variables.keys())
    print(f'Loading {unit} variables...')
    
    tip0_red   = f.variables['TIP_M0_RED']
    tip0_uv    = f.variables['TIP_M0_UV']
    tip0_dark  = f.variables['TIP_M0_DARK']
    
    mip0_mg    = f.variables['MIP_M0_MG']
    mip0_vk    = f.variables['MIP_M0_VK']
    mip0_dark  = f.variables['MIP_M0_DARK']
    
    utc_start = convert_gps_to_utc(f.variables['TIP_M0_MET'][59])
    utc_stop  = convert_gps_to_utc(f.variables['TIP_M0_MET'][-0])
    dStr_start = generate_dStr_from_astropy_utc(utc_start)
    dStr_stop = generate_dStr_from_astropy_utc(utc_stop)
    
    t1 = 0
    t2 = -1
    
    if content == 'TIP_HK':
        fig, ax = plt.subplots(4, figsize=(6.5,9))
        title = ''
        v = ''
        fig.suptitle(f'{title}\n{dStr_start} -- {dStr_stop[-5:]}\n{v} STP-H9 ECLIPSE - {unit} TIP Housekeeping') 
        tip0_runtime    = [(x-f.variables['TIP_M0_MET'][0])/3600 for x in f.variables['TIP_M0_MET']]
        t_lim = (tip0_runtime[t1], tip0_runtime[t2])
        
        ax[0].plot(tip0_runtime, tip0_red,  'r', label='Red')
        ax[0].plot(tip0_runtime, tip0_uv,   'b', label='UV')
        ax[0].plot(tip0_runtime, tip0_dark, 'k', label='Dark')
        ax[0].set(ylabel='Counts/sec', xlim=t_lim, yscale='log')
        ax[0].legend(loc=1, fontsize='x-small')
        
        ax[1].plot(tip0_runtime, f.variables['TIP_M0_HV_mon'], 'k')
        ax[1].plot(tip0_runtime, f.variables['TIP_M0_HV_Event'], 'g', label='HV Event')
        ax[1].plot(tip0_runtime, f.variables['TIP_M0_DK_EVENT'], 'c', label='DK Event')
        ax[1].plot(tip0_runtime, f.variables['TIP_M0_RD_EVENT'], 'r', label='RD Event')
        ax[1].plot(tip0_runtime, f.variables['TIP_M0_UV_EVENT'], 'b', label='UV Event')
        ax[1].plot(tip0_runtime, f.variables['TIP_M0_Sun_Event'],'y', label='SN Event')
        ax[1].set(ylabel='Voltage [V]', xlim=t_lim, yscale='log')
        ax[1].legend(loc=2, fontsize='x-small')
        
        ax[2].plot(tip0_runtime, f.variables['TIP_M0_TF1'],  'r', label='Filter 1')
        ax[2].plot(tip0_runtime, f.variables['TIP_M0_TF2'],  'b', label='Filter 2')
        ax[2].plot(tip0_runtime, f.variables['TIP_M0_TIDC'], 'g', label='IDC')
        ax[2].plot(tip0_runtime, f.variables['TIP_M0_HV'],   'k', label='HV')
        ax[2].set(ylabel='Temperature', xlim=t_lim)
        ax[2].legend(loc=2, fontsize='x-small')
        
        ax[3].plot(tip0_runtime, f.variables['TIP_M0_sun'], 'k')
        ax[3].set(xlabel='Time of Day [hr]', ylabel='Sun Sensor [V]',xlim=t_lim)
    
    if content == 'MIP_HK':
        fig, ax = plt.subplots(4, figsize=(6.5,9))
        title = ''
        v = ''
        fig.suptitle(f'{title}\n{dStr_start} -- {dStr_stop[-5:]}\n{v} STP-H9 ECLIPSE - {unit} MIP Housekeeping') 
        mip0_runtime    = [(x-f.variables['MIP_M0_MET'][0])/3600 for x in f.variables['MIP_M0_MET']]
        t_lim = (mip0_runtime[t1], mip0_runtime[t2])
        
        ax[0].plot(mip0_runtime, mip0_mg,  'r', label='Mg+')
        ax[0].plot(mip0_runtime, mip0_vk,   'b', label='VK')
        ax[0].plot(mip0_runtime, mip0_dark, 'k', label='Dark')
        ax[0].set(ylabel='Counts/sec', xlim=t_lim, yscale='log')
        ax[0].legend(loc=1, fontsize='x-small')
        
        ax[1].plot(mip0_runtime, f.variables['MIP_M0_HV_mon'], 'k')
        ax[1].plot(mip0_runtime, f.variables['MIP_M0_HV_Event'], 'g', label='HV Event')
        ax[1].plot(mip0_runtime, f.variables['MIP_M0_DK_EVENT'], 'c', label='DK Event')
        ax[1].plot(mip0_runtime, f.variables['MIP_M0_RD_EVENT'], 'r', label='RD Event')
        ax[1].plot(mip0_runtime, f.variables['MIP_M0_UV_EVENT'], 'b', label='UV Event')
        ax[1].plot(mip0_runtime, f.variables['MIP_M0_Sun_Event'],'y', label='SN Event')
        ax[1].set(ylabel='Voltage [V]', xlim=t_lim, ylim=(0.5,1500), yscale='log')
        ax[1].legend(loc=2, fontsize='x-small')
        
        ax[2].plot(mip0_runtime, f.variables['MIP_M0_TLENS'],'r', label='Lens')
        ax[2].plot(mip0_runtime, f.variables['MIP_M0_TPMT'], 'b', label='PMT')
        ax[2].plot(mip0_runtime, f.variables['MIP_M0_TIDC'], 'g', label='IDC')
        ax[2].plot(mip0_runtime, f.variables['MIP_M0_HV'],   'k', label='HV')
        ax[2].set(ylabel='Temperature', xlim=t_lim)
        ax[2].legend(loc=2, fontsize='x-small')
        
        ax[3].plot(mip0_runtime, f.variables['MIP_M0_sun'], 'k')
        ax[3].set(xlabel='Time of Day [hr]', ylabel='Sun Sensor [V]',xlim=t_lim)
    
    if content == 'SUVM_HK':
        fig, ax = plt.subplots(5, figsize=(6.5,9))
        title = ''
        v = ''
        fig.suptitle(f'{title}\n{dStr_start} -- {dStr_stop[-5:]}\n{v} STP-H9 ECLIPSE - {unit} SUVM Housekeeping') 
        
        tip0_runtime = [(x-f.variables['TIP_SUVM_TIME'][0])/3600 for x in f.variables['TIP_SUVM_TIME'][:-2]]
        mip0_runtime = [(x-f.variables['MIP_SUVM_TIME'][0])/3600 for x in f.variables['MIP_SUVM_TIME'][:-2]]
        
        t_lim = (mip0_runtime[t1], mip0_runtime[t2])
        
        ax[0].plot(tip0_runtime,f.variables['TIP_SUVM_V5_IMON'][:-2], 'k',label='I$_{5V}$')
        ax[0].plot(tip0_runtime,f.variables['TIP_SUVM_V3_IMON'][:-2], 'b',label='I$_{3.3V}$')
        ax[0].plot(tip0_runtime,f.variables['TIP_SUVM_V22_IMON'][:-2],'r',label='I$_{22V}$ ')
        ax[0].plot(tip0_runtime,f.variables['TIP_SUVM_MOTOR_IMON'][:-2],'g',label='I$_{MOT}$ ')
        ax[0].set(ylabel='TIP SUVM\nCurrent', xlim=t_lim)
        ax[0].legend(loc=1, fontsize='x-small')
        
        ax[1].plot(tip0_runtime,f.variables['TIP_SUVM_V5_VMON'][:-2], 'k',label='V$_{5V}$')
        ax[1].plot(tip0_runtime,f.variables['TIP_SUVM_V3_VMON'][:-2], 'b',label='V$_{3.3V}$')
        ax[1].plot(tip0_runtime,f.variables['TIP_SUVM_V22_VMON'][:-2],'r',label='V$_{22V}$')
        ax[1].set(ylabel='TIP SUVM\nVoltage', xlim=t_lim)
        ax[1].legend(loc=1, fontsize='x-small')
        
        ax[2].plot(mip0_runtime,f.variables['MIP_SUVM_V5_IMON'][:-2], 'k',label='I$_{5V}$')
        ax[2].plot(mip0_runtime,f.variables['MIP_SUVM_V3_IMON'][:-2], 'b',label='I$_{3.3V}$')
        ax[2].plot(mip0_runtime,f.variables['MIP_SUVM_V22_IMON'][:-2],'r',label='I$_{22V}$ ')
        ax[2].plot(mip0_runtime,f.variables['MIP_SUVM_MOTOR_IMON'][:-2],'g',label='I$_{MOT}$ ')
        ax[2].set(ylabel='MIP SUVM\nCurrent', xlim=t_lim)
        ax[2].legend(loc=1, fontsize='x-small')
        
        ax[3].plot(mip0_runtime,f.variables['MIP_SUVM_V5_VMON'][:-2], 'k',label='V$_{5V}$')
        ax[3].plot(mip0_runtime,f.variables['MIP_SUVM_V3_VMON'][:-2], 'b',label='V$_{3.3V}$')
        ax[3].plot(mip0_runtime,f.variables['MIP_SUVM_V22_VMON'][:-2],'r',label='V$_{22V}$')
        ax[3].set(ylabel='MIP SUVM\nVoltage', xlim=t_lim)
        ax[3].legend(loc=1, fontsize='x-small')
        
        ax[4].plot(tip0_runtime,f.variables['TIP_SUVM_TEMP'][:-2],'k',label='TIP')
        ax[4].plot(mip0_runtime,f.variables['MIP_SUVM_TEMP'][:-2],'r',label='MIP')
        ax[4].set(xlabel='Time of Day [hr]', ylabel='Temperatures [C]', xlim=t_lim)
        ax[4].legend(loc=1, fontsize='x-small')
    
    if save > 0:
        path, fname = os.path.split(infile)
        s = str(utc_start)
        outname = f'{path}/{s[0:4]}{s[5:7]}{s[8:10]}-STPH9-ECLIPSE-{unit}_{content}.png'
        print(f' Saving plot ... {outname}')
        fig.savefig(outname)

    """
    Variable list
    'TIP_SUVM_ENCODER_TARGET_ANGLE', 'MIP_SUVM_ENCODER_TARGET_ANGLE']
    'TIP_SUVM_ENCODER_ZERO_OFFSET', 'MIP_SUVM_ENCODER_ZERO_OFFSET', 
    'TIP_SUVM_ENCODER_CURRENT_CT', 'MIP_SUVM_ENCODER_CURRENT_CT', 
    'TIP_SUVM_ENCODER_TARGET', 'MIP_SUVM_ENCODER_TARGET', 
    'TIP_SUVM_PWM_RATE', 'MIP_SUVM_PWM_RATE', 
    'TIP_SUVM_PWM_CTS_REMAIN', 'MIP_SUVM_PWM_CTS_REMAIN', 
    
    List of variables not currently plotted anywhere:
    'TIP_M0_TIME', 'TIP_M1_RUNTIME' -- Internal system counters
    'TIP_M0_HV_adj', 'TIP_M0_HEATER', 'TIP_M0_VREF', 'TIP_M0_HV_Status'
    'TIP_M0_Sun_Override','TIP_M0_Dark_Override','TIP_M0_Red_Override',
    'TIP_M0_UV_Override','TIP_M0_HV_Override','TIP_M0_Shutter_Override',
    'TIP_M0_5V_Override'
    
    'MIP_M0_TIME', 'MIP_M1_RUNTIME' -- Internal system counters
    'MIP_M0_HV_adj', 'MIP_M0_VREF', 'MIP_M0_HV_Status'
    'MIP_M0_Sun_Override','MIP_M0_Dark_Override','MIP_M0_Red_Override',
    'MIP_M0_UV_Override','MIP_M0_HV_Override','MIP_M0_Shutter_Override',
    'MIP_M0_5V_Override',
    
    'TIP_SUVM_SEQUENCE', 'MIP_SUVM_SEQUENCE', 
    'TIP_SUVM_System_Counter', 'MIP_SUVM_System_Counter', 
    'TIP_SUVM_GPS_PPS', 'MIP_SUVM_GPS_PPS', 
    'TIP_SUVM_ENCODER_PROFILE_INDEX', 'MIP_SUVM_ENCODER_PROFILE_INDEX',
    
    'TIP_SUVM_LAST_COMMAND_STATUS', 'MIP_SUVM_LAST_COMMAND_STATUS', 
    'TIP_SUVM_LAST_COMMAND_ID', 'MIP_SUVM_LAST_COMMAND_ID', 
    'TIP_SUVM_LAST_OP_CODE', 'MIP_SUVM_LAST_OP_CODE', 
    'TIP_SUVM_LAST_CMD_TIME', 'MIP_SUVM_LAST_CMD_TIME', 
    'TIP_SUVM_LAST_CMD_SUCCESS', 'MIP_SUVM_LAST_CMD_SUCCESS', 
    'TIP_SUVM_LAST_CMD_FAIL', 'MIP_SUVM_LAST_CMD_FAIL', 
    'TIP_SUVM_LAST_CRC', 'MIP_SUVM_LAST_CRC', 
    'TIP_SUVM_CRC', 'MIP_SUVM_CRC', 
    """
    
    print(f'\n ------ {unit} plot routine complete ------- \n')
    # 
def ecl_primary_data_plot(infile, unit='', content='', quartile='', save=0):
    print(f'Plotting data values from {infile}')
    f = netCDF4.Dataset(infile)
    # print(f.variables.keys())
    print(f'Loading {unit} variables...')
    
    tip0_met  = f.variables['TIP_M0_MET']
    tip0_red  = f.variables['TIP_M0_RED']
    tip0_uv   = f.variables['TIP_M0_UV']
    tip0_dark = f.variables['TIP_M0_DARK']
    tips_time = f.variables['TIP_SUVM_TIME'][:-2]
    
    tip1_met  = f.variables['TIP_M1_MET']
    tip1_red  = f.variables['TIP_M1_RED']
    tip1_uv   = f.variables['TIP_M1_UV']
    tip1_dark = f.variables['TIP_M1_DARK']
    
    mip0_met  = f.variables['MIP_M0_MET']
    mip0_mg   = f.variables['MIP_M0_MG']
    mip0_vk   = f.variables['MIP_M0_VK']
    mip0_dark = f.variables['MIP_M0_DARK']
    mips_time = f.variables['MIP_SUVM_TIME'][:-2]
    
    mip1_met  = f.variables['MIP_M1_MET']
    mip1_mg   = f.variables['MIP_M1_MG']
    mip1_vk   = f.variables['MIP_M1_VK']
    mip1_dark = f.variables['MIP_M1_DARK']

    # mmg0_redux  = [x/10 for x in f.variables['MIP_M0_MG']]
    tip0_met = f.variables['TIP_M0_MET']
    mip0_met = f.variables['MIP_M0_MET']
    
    utc_start = convert_gps_to_utc(tip0_met[59])
    utc_stop  = convert_gps_to_utc(mip0_met[-0])
    dStr_start = generate_dStr_from_astropy_utc(utc_start)
    dStr_stop = generate_dStr_from_astropy_utc(utc_stop)
    
    if quartile == 'first':
        t1 = 0
        t2 = len(tip0_met)/4
        qrt = '_a'
    elif quartile == 'second':
        t1 = len(tip0_met)/4
        t2 = len(tip0_met)/2
        qrt = '_b'
    elif quartile == 'third':
        t1 = len(tip0_met)/2
        t2 = len(tip0_met)*3/4
        qrt = '_c'
    elif quartile == 'fourth':
        t1 = len(tip0_met)*3/4
        t2 = -1
        qrt = '_d'
    elif quartile == 'custom':
        t1 = len(tip0_met)*2/3 + 2900
        t2 = t1 + 200
    else:
        t1 = 0
        t2 = -1
    
    t_lim = (tip0_met[t1], tip0_met[t2])
    
    if content == 'PMT_10Hz':
        fig, ax = plt.subplots(4, figsize=(6.5, 9))
        title = ''
        v = ''
        fig.suptitle(f'{title}\n{dStr_start}\n{v} STP-H9 ECLIPSE - {unit} 6 Hour PMT Plot') 
        
        ax[0].plot(tip0_met, tip0_red, 'r', label='Red')
        ax[0].plot(tip0_met, tip0_uv,  'b', label='UV')
        ax[0].plot(tip0_met, tip0_dark,'k', label='Dark')
        ax[0].set(ylabel='Tri-TIP M0 (1 Hz)', xlim=t_lim, yscale = 'log')
        ax[0].legend(loc=1, fontsize='x-small')
        
        ax[1].plot(tip1_met, tip1_red, 'r', label='Red')
        ax[1].plot(tip1_met, tip1_uv,  'b', label='UV')
        ax[1].plot(tip1_met, tip1_dark,'k', label='Dark')
        ax[1].set(ylabel='Tri-TIP M1 (10 Hz)', xlim=t_lim, yscale = 'log')
        ax[1].legend(loc=1, fontsize='x-small')
        
        ax[2].plot(mip0_met, mip0_mg,  'r', label='Mg+')
        ax[2].plot(mip0_met, mip0_vk,  'b', label='VK')
        ax[2].plot(mip0_met, mip0_dark,'k', label='Dark')
        ax[2].set(xlabel='GPS Time', ylabel='Tri-MIP M1 (1 Hz)', xlim=t_lim, yscale = 'log')
        ax[2].legend(loc=1, fontsize='x-small')
        
        ax[3].plot(mip1_met, mip1_mg,  'r', label='Mg+')
        ax[3].plot(mip1_met, mip1_vk,  'b', label='VK')
        ax[3].plot(mip1_met, mip1_dark,'k', label='Dark')
        ax[3].set(xlabel='GPS Time', ylabel='Tri-MIP M1 (10 Hz)', xlim=t_lim, yscale = 'log')
        ax[3].legend(loc=1, fontsize='x-small')
        
    if content == 'PMT+SUVM':
        fig, ax = plt.subplots(4, figsize=(6.5, 9))
        title = ''
        v = ''
        fig.suptitle(f'{title}\n{dStr_start}\n{v} STP-H9 ECLIPSE - {unit} 6 Hour SUVM Plot') 
        
        ax[0].plot(tip0_met, tip0_red, 'r', label='Red')
        ax[0].plot(tip0_met, tip0_uv,  'b', label='UV')
        ax[0].plot(tip0_met, tip0_dark,'k', label='Dark')
        ax[0].set(ylabel='Tri-TIP M0 (1 Hz)', xlim=t_lim, yscale = 'log')
        ax[0].legend(loc=1, fontsize='x-small')
        
        ax[1].plot(tips_time, f.variables['TIP_SUVM_ENCODER_ANGLE'][:-2], 'k')
        ax[1].set(ylabel='Tri-TIP SUVM', xlim=t_lim, ylim=(0,46))
        
        ax[2].plot(mip0_met, mip0_mg,  'r', label='Mg+')
        ax[2].plot(mip0_met, mip0_vk,  'b', label='VK')
        ax[2].plot(mip0_met, mip0_dark,'k', label='Dark')
        ax[2].set(xlabel='GPS Time', ylabel='Tri-MIP M1 (10 Hz)', xlim=t_lim, yscale = 'log')
        ax[2].legend(loc=1, fontsize='x-small')
        
        ax[3].plot(mips_time, f.variables['MIP_SUVM_ENCODER_ANGLE'][:-2], 'k')
        ax[3].set(xlabel='GPS Time', ylabel='Tri-MIP SUVM', xlim=t_lim, ylim=(0,46))
    
    if save > 0:
        path, fname = os.path.split(infile)
        s = str(utc_start)
        outname = f'{path}/{s[0:4]}{s[5:7]}{s[8:10]}-STPH9-ECLIPSE-{unit}_{content}{qrt}.png'
        print(f' Saving plot ... {outname}')
        fig.savefig(outname)
    # 
def ecl0_suvm_log(infile, unit='', content='PMT only'):
    print(f'Plotting data values from {infile}')
    f = netCDF4.Dataset(infile)
    # print(f.variables.keys())
    print(f'Loading {unit} variables...')

    print(f.variables['TIP_SUVM_LAST_CRC'][0:10])

def main():
    DOY = 219
    tic = time.time()
    cts_file = f'C:/data/ECLIPSE/flt/L0_CTS/NRL_1729_2023{DOY}_ECLIPSE_L0_CTS.nc'
    als_file = f'C:/data/ECLIPSE/flt/L0_ALS/NRL_1729_2023{DOY}_ECLIPSE_L0_ALS.nc'
    analog_file = f'C:/data/ECLIPSE/flt/L0_analog/NRL_1729_2023{DOY}_ECLIPSE_L0_analog.nc'
    # 
    ### Analog plots for both ALS and CTS
    ecl0_analog_survey_plot(analog_file, save=1)
    
    # Day long summary plots
    ecl0_survey_plot(als_file, unit='ALS', content='TIP_HK', save=1)
    ecl0_survey_plot(cts_file, unit='CTS', content='TIP_HK', save=1)
    ecl0_survey_plot(als_file, unit='ALS', content='MIP_HK', save=1)
    ecl0_survey_plot(cts_file, unit='CTS', content='MIP_HK', save=1)
    ecl0_survey_plot(als_file, unit='ALS', content='SUVM_HK', save=1)
    ecl0_survey_plot(cts_file, unit='CTS', content='SUVM_HK', save=1)
    
    # ecl_primary_data_plot(cts_file, unit='ALS', content='PMT_10Hz', quartile='custom', save=0)
    
    # 6-hour summary plots
    ecl_primary_data_plot(cts_file, unit='CTS', content='PMT_10Hz', quartile='first', save=1)
    ecl_primary_data_plot(cts_file, unit='CTS', content='PMT_10Hz', quartile='second', save=1)
    ecl_primary_data_plot(cts_file, unit='CTS', content='PMT_10Hz', quartile='third', save=1)
    ecl_primary_data_plot(cts_file, unit='CTS', content='PMT_10Hz', quartile='fourth', save=1)
    
    ecl_primary_data_plot(cts_file, unit='CTS', content='PMT+SUVM', quartile='first', save=1)
    ecl_primary_data_plot(cts_file, unit='CTS', content='PMT+SUVM', quartile='second', save=1)
    ecl_primary_data_plot(cts_file, unit='CTS', content='PMT+SUVM', quartile='third', save=1)
    ecl_primary_data_plot(cts_file, unit='CTS', content='PMT+SUVM', quartile='fourth', save=1)
    
    ecl_primary_data_plot(als_file, unit='ALS', content='PMT_10Hz', quartile='first', save=1)
    ecl_primary_data_plot(als_file, unit='ALS', content='PMT_10Hz', quartile='second', save=1)
    ecl_primary_data_plot(als_file, unit='ALS', content='PMT_10Hz', quartile='third', save=1)
    ecl_primary_data_plot(als_file, unit='ALS', content='PMT_10Hz', quartile='fourth', save=1)
    
    ecl_primary_data_plot(als_file, unit='ALS', content='PMT+SUVM', quartile='first', save=1)
    ecl_primary_data_plot(als_file, unit='ALS', content='PMT+SUVM', quartile='second', save=1)
    ecl_primary_data_plot(als_file, unit='ALS', content='PMT+SUVM', quartile='third', save=1)
    ecl_primary_data_plot(als_file, unit='ALS', content='PMT+SUVM', quartile='fourth', save=1)
    
    # ###ecl0_suvm_log(cts_file, unit='CTS')
    
    """
    Will probably want to add multiple x labels to plots in the future:
    https://stackoverflow.com/questions/53043732/multiple-x-labels-on-pyplot
    """
    toc = time.time()
    print(f' Done processing data from DOY {DOY}')
    print(f' Total time (sec) to process = {toc-tic}')
    # 
if __name__ == "__main__":
    print(f"==== {__file__} ====")
    main()