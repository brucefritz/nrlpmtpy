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
import NRL_quaternion_calculator as qcalc

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
    atime = f.variables['ALS_GPS_time'][:]
    # 
    try:
        fig, ax = plt.subplots(4, figsize=(6,7))
        t0 = time.localtime(atime[59])
        utc = convert_gps_to_utc(atime[59])
        dStr = generate_dStr_from_astropy_utc(utc)
        fig.suptitle(f'\n{dStr}\nSTP-H9 ECLIPSE - ALS Power Draw') 
        # 
        ta = atime - atime[0]
        t_lim = [np.min(ta), np.max(ta)]
        '''
        ALS Tri-TIP Power
        '''
        ax[0].plot(ta, f.variables['ALS_TIP_V_12V'][:],  'k', label='12V')
        ax[0].plot(ta, f.variables['ALS_TIP_V_3V'][:],   'purple',label='3.3V')
        ax[0].set(ylabel='Tri-TIP [V]', xlim=(t_lim), ylim=(0,20))
        ax2 = ax[0].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(ta, f.variables['ALS_TIP_I_12V'][:], 'r--', label='I$_{12V}$')
        ax2.plot(ta, f.variables['ALS_TIP_I_3V'][:],  'b--', label='I$_{3V}$')
        ax2.set(ylabel='Tri-TIP [A]', ylim=(-0.2, 0.8))
        ax2.legend(loc=1, fontsize='x-small')
        '''
        ALS Tri-TIP SUVM Power
        '''
        ax[1].plot(ta, f.variables['ALS_TIP_SUVM_V_28V'][:], 'g', label='28V')
        ax[1].plot(ta, f.variables['ALS_TIP_SUVM_V_5V'][:],  'k', label='5V')
        ax[1].plot(ta, f.variables['ALS_TIP_SUVM_V_3V'][:], 'purple', label='3.3V')
        ax[1].set(ylabel='TIP SUVM [V]', xlim=(t_lim), ylim=(0,35))
        ax2 = ax[1].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(ta, f.variables['ALS_TIP_SUVM_I_5V'][:], 'r--', label='I$_{5V}$')
        ax2.plot(ta, f.variables['ALS_TIP_SUVM_I_3V'][:], 'b--', label='I$_{3.3V}$')
        ax2.set(ylabel='TIP SUVM [A]', ylim=(-0.1, 0.25))
        ax2.legend(loc=1, fontsize='x-small')
        '''
        ALS Tri-MIP Power
        '''
        ax[2].plot(ta, f.variables['ALS_MIP_V_12V'][:],  'k', label='12V')
        ax[2].plot(ta, f.variables['ALS_MIP_V_3V'][:],   'purple',label='3.3V')
        ax[2].set(ylabel='Tri-MIP [V]', xlim=(t_lim), ylim=(0,20))
        # 
        ax2 = ax[2].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(ta, f.variables['ALS_MIP_I_12V'][:], 'r--', label='I$_{12V}$')
        ax2.plot(ta, f.variables['ALS_MIP_I_3V'][:],  'b--', label='I$_{3V}$')
        ax2.set(ylabel='Tri-MIP [A]', ylim=(-0.2, 0.8))
        ax2.legend(loc=1, fontsize='x-small')
        '''
        ALS Tri-MIP SUVM Power
        '''
        ax[3].plot(ta, f.variables['ALS_MIP_SUVM_V_28V'][:], 'g', label='28V')
        ax[3].plot(ta, f.variables['ALS_MIP_SUVM_V_5V'][:], 'k', label='5V')
        ax[3].plot(ta, f.variables['ALS_MIP_SUVM_V_3V'][:], 'purple', label='3.3V')
        ax[3].set(xlabel='Time [sec]', ylabel='MIP SUVM [V]', xlim=(t_lim), ylim=(0,35))
        ax2 = ax[3].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(ta, f.variables['ALS_MIP_SUVM_I_5V'][:], 'r--', label='I$_{5V}$')
        ax2.plot(ta, f.variables['ALS_MIP_SUVM_I_3V'][:], 'b--', label='I$_{3.3V}$')
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
    ctime        = f.variables['CTS_GPS_time'][:]
    # 
    try:
        fig, ax = plt.subplots(4, figsize=(6,7))
        utc = convert_gps_to_utc(ctime[59])
        dStr = generate_dStr_from_astropy_utc(utc)
        fig.suptitle(f'\n{dStr}\nSTP-H9 ECLIPSE - CTS Power Draw') 
        # 
        tc = ctime - ctime[0]
        t_lim = [np.min(tc), np.max(tc)]
        '''
        CTS Tri-TIP Power
        '''
        ax[0].plot(tc, f.variables['CTS_TIP_V_12V'][:], 'k', label='12V')
        ax[0].plot(tc, f.variables['CTS_TIP_V_3V'][:], 'purple',  label='3.3V')
        ax[0].set(ylabel='Tri-TIP [V]', xlim=(t_lim), ylim=(0,20))
        ax2 = ax[0].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(tc, f.variables['CTS_TIP_I_12V'][:], 'r--', label='I$_{12V}$')
        ax2.plot(tc, f.variables['CTS_TIP_I_3V'][:], 'b--', label='I$_{3V}$')
        ax2.set(ylabel='Tri-TIP [A]', ylim=(-0.2, 0.8))
        ax2.legend(loc=1, fontsize='x-small')
        '''
        CTS Tri-TIP SUVM Power
        '''
        ax[1].plot(tc, f.variables['CTS_TIP_SUVM_V_28V'][:], 'g', label='28V')
        ax[1].plot(tc, f.variables['CTS_TIP_SUVM_V_5V'][:], 'k', label='5V')
        ax[1].plot(tc, f.variables['CTS_TIP_SUVM_V_3V'][:], 'purple', label='3.3V')
        ax[1].set(ylabel='TIP SUVM [V]', xlim=(t_lim), ylim=(0,35))
        ax2 = ax[1].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(tc, f.variables['CTS_TIP_SUVM_I_5V'][:], 'r--', label='I$_{5V}$')
        ax2.plot(tc, f.variables['CTS_TIP_SUVM_I_3V'][:], 'b--', label='I$_{3.3V}$')
        ax2.set(ylabel='TIP SUVM [A]', ylim=(-0.1, 0.25))
        ax2.legend(loc=1, fontsize='x-small')
        '''
        CTS Tri-MIP Power
        '''
        ax[2].plot(tc, f.variables['CTS_MIP_V_12V'][:], 'k', label='12V')
        ax[2].plot(tc, f.variables['CTS_MIP_V_3V'][:], 'purple',  label='3.3V')
        ax[2].set(ylabel='Tri-MIP [V]', xlim=(t_lim), ylim=(0,20))
        ax2 = ax[2].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(tc, f.variables['CTS_MIP_I_12V'][:], 'r--', label='I$_{12V}$')
        ax2.plot(tc, f.variables['CTS_MIP_I_3V'][:], 'b--', label='I$_{3V}$')
        ax2.set(ylabel='Tri-MIP [A]', ylim=(-0.2, 0.8))
        ax2.legend(loc=1, fontsize='x-small')
        '''
        CTS Tri-MIP SUVM Power
        '''
        ax[3].plot(tc, f.variables['CTS_MIP_SUVM_V_28V'][:], 'g', label='28V')
        ax[3].plot(tc, f.variables['CTS_MIP_SUVM_V_5V'][:], 'k', label='5V')
        ax[3].plot(tc, f.variables['CTS_MIP_SUVM_V_3V'][:], 'purple', label='3.3V')
        ax[3].set(xlabel='Time [sec]', ylabel='MIP SUVM [V]', xlim=(t_lim), ylim=(0,35))
        ax2 = ax[3].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.plot(tc, f.variables['CTS_MIP_SUVM_I_5V'][:], 'r--', label='I$_{5V}$')
        ax2.plot(tc, f.variables['CTS_MIP_SUVM_I_3V'][:], 'b--', label='I$_{3.3V}$')
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
    f.close()
    # 
def ecl0_survey_plot(infile, unit='', content='PMT only', save=0):
    print(f'Plotting data values from {infile}')
    f = netCDF4.Dataset(infile)
    # print(f.variables.keys())
    print(f'Loading {unit} variables...')
    
    try:
        utc_start = convert_gps_to_utc(f.variables['TIP_M0_GPS_TIME'][59])
        utc_stop  = convert_gps_to_utc(f.variables['TIP_M0_GPS_TIME'][-1])
        dStr_start = generate_dStr_from_astropy_utc(utc_start)
        dStr_stop = generate_dStr_from_astropy_utc(utc_stop)
        t1 = 0
        t2 = -1
        
        if content == 'TIP_HK':
            fig, ax = plt.subplots(4, figsize=(6.5,8))
            fig.suptitle(f'\n{dStr_start} -- {dStr_stop[-5:]}\nSTP-H9 ECLIPSE - {unit} TIP Housekeeping') 
            tip0_runtime    = f.variables['TIP_M0_GPS_TIME'][:]
            t_lim = (tip0_runtime[t1], tip0_runtime[t2])
            
            ax[0].plot(tip0_runtime, f.variables['TIP_M0_RED'][:],  'r', label='Red')
            ax[0].plot(tip0_runtime, f.variables['TIP_M0_UV'][:],   'b', label='UV')
            ax[0].plot(tip0_runtime, f.variables['TIP_M0_DARK'][:], 'k', label='Dark')
            ax[0].set(ylabel='Counts/sec', xlim=t_lim, yscale='log')
            ax[0].legend(loc=1, fontsize='x-small')
            
            ax[1].plot(tip0_runtime, f.variables['TIP_M0_HV_mon'][:], 'k')
            ax[1].plot(tip0_runtime, f.variables['TIP_M0_HV_Event'][:], 'g', label='HV Event')
            ax[1].plot(tip0_runtime, f.variables['TIP_M0_DK_EVENT'][:], 'c', label='DK Event')
            ax[1].plot(tip0_runtime, f.variables['TIP_M0_RD_EVENT'][:], 'r', label='RD Event')
            ax[1].plot(tip0_runtime, f.variables['TIP_M0_UV_EVENT'][:], 'b', label='UV Event')
            ax[1].plot(tip0_runtime, f.variables['TIP_M0_Sun_Event'][:],'y', label='SN Event')
            ax[1].set(ylabel='Voltage [V]', xlim=t_lim, yscale='log')
            ax[1].legend(loc=2, fontsize='x-small')
            
            ax[2].plot(tip0_runtime, f.variables['TIP_M0_TF1'][:],  'r', label='Filter 1')
            ax[2].plot(tip0_runtime, f.variables['TIP_M0_TF2'][:],  'b', label='Filter 2')
            ax[2].plot(tip0_runtime, f.variables['TIP_M0_TIDC'][:], 'g', label='IDC')
            ax[2].plot(tip0_runtime, f.variables['TIP_M0_THV'][:],   'k', label='HV')
            ax[2].set(ylabel='Temperature', xlim=t_lim)
            ax[2].legend(loc=2, fontsize='x-small')
            
            ax[3].plot(tip0_runtime, f.variables['TIP_M0_sun'][:], 'k')
            ax[3].set(xlabel='Time of Day [sec]', ylabel='Sun Sensor [V]',xlim=t_lim)
    
        if content == 'MIP_HK':
            fig, ax = plt.subplots(4, figsize=(6.5,8))
            fig.suptitle(f'\n{dStr_start} -- {dStr_stop[-5:]}\nSTP-H9 ECLIPSE - {unit} MIP Housekeeping') 
            mip0_runtime    = f.variables['MIP_M0_GPS_TIME'][:]
            t_lim = (mip0_runtime[t1], mip0_runtime[t2])
            # 
            ax[0].plot(mip0_runtime, f.variables['MIP_M0_MG'][:],  'r', label='Mg+')
            ax[0].plot(mip0_runtime, f.variables['MIP_M0_VK'][:],   'b', label='VK')
            ax[0].plot(mip0_runtime, f.variables['MIP_M0_DARK'][:], 'k', label='Dark')
            ax[0].set(ylabel='Counts/sec', xlim=t_lim, yscale='log')
            ax[0].legend(loc=1, fontsize='x-small')
            
            ax[1].plot(mip0_runtime, f.variables['MIP_M0_HV_mon'][:], 'k')
            ax[1].plot(mip0_runtime, f.variables['MIP_M0_HV_Event'][:], 'g', label='HV Event')
            ax[1].plot(mip0_runtime, f.variables['MIP_M0_DK_EVENT'][:], 'c', label='DK Event')
            ax[1].plot(mip0_runtime, f.variables['MIP_M0_RD_EVENT'][:], 'r', label='RD Event')
            ax[1].plot(mip0_runtime, f.variables['MIP_M0_UV_EVENT'][:], 'b', label='UV Event')
            ax[1].plot(mip0_runtime, f.variables['MIP_M0_Sun_Event'][:],'y', label='SN Event')
            ax[1].set(ylabel='Voltage [V]', xlim=t_lim, ylim=(0.5,1500), yscale='log')
            ax[1].legend(loc=2, fontsize='x-small')
            
            ax[2].plot(mip0_runtime, f.variables['MIP_M0_TLENS'][:],'r', label='Lens')
            ax[2].plot(mip0_runtime, f.variables['MIP_M0_TPMT'][:], 'b', label='PMT')
            ax[2].plot(mip0_runtime, f.variables['MIP_M0_TIDC'][:], 'g', label='IDC')
            ax[2].plot(mip0_runtime, f.variables['MIP_M0_THV'][:],   'k', label='HV')
            ax[2].set(ylabel='Temperature', xlim=t_lim)
            ax[2].legend(loc=2, fontsize='x-small')
            
            ax[3].plot(mip0_runtime, f.variables['MIP_M0_sun'][:], 'k')
            ax[3].set(xlabel='Time of Day [sec]', ylabel='Sun Sensor [V]',xlim=t_lim)
        
        if content == 'SUVM_HK':
            fig, ax = plt.subplots(5, figsize=(6.5,8))
            fig.suptitle(f'\n{dStr_start} -- {dStr_stop[-5:]}\nSTP-H9 ECLIPSE - {unit} SUVM Housekeeping') 
            
            tip0_runtime = f.variables['TIP_SUVM_TIME'][:-2] - f.variables['TIP_SUVM_TIME'][0]
            mip0_runtime = f.variables['MIP_SUVM_TIME'][:-2] - f.variables['TIP_SUVM_TIME'][0]
            
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
            ax[4].set(xlabel='Time of Day [sec]', ylabel='Temperatures [C]', xlim=t_lim)
            ax[4].legend(loc=1, fontsize='x-small')
    
        if save > 0:
            path, fname = os.path.split(infile)
            s = str(utc_start)
            outname = f'{path}/{s[0:4]}{s[5:7]}{s[8:10]}-STPH9-ECLIPSE-{unit}_{content}.png'
            print(f' Saving plot ... {outname}')
            fig.savefig(outname)
        print(f'\n ------ {unit} plot routine complete ------- \n')
        
    except IndexError:
        print(f'\nNo data in {infile}\n\n Skipping plot \n')
    
    f.close()
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
    # 
def ecl_primary_data_plot(infile, unit='', content='', sextile='', save=0, tspan=(0,-1)):
    print(f'Plotting data values from {infile}')
    f = netCDF4.Dataset(infile)
    # print(f.variables.keys())
    print(f'Loading {unit} variables...')
    
    tip0_gps_t  = f.variables['TIP_M0_GPS_TIME'][:]
    tip1_gps_t  = f.variables['TIP_M1_GPS_TIME'][:]
    mip0_gps_t  = f.variables['MIP_M0_GPS_TIME'][:]
    mip1_gps_t  = f.variables['MIP_M1_GPS_TIME'][:]
    
    try:
        if sextile == 'first':
            t1 = 0
            t2 = round(len(tip0_gps_t)/12)
            qrt = '_0000Z'
        elif sextile == 'second':
            t1 = round(len(tip0_gps_t)/12)
            t2 = round(len(tip0_gps_t)/6)
            qrt = '_0200Z'
        elif sextile == 'third':
            t1 = round(len(tip0_gps_t)/6)
            t2 = round(len(tip0_gps_t)/4)
            qrt = '_0400Z'
        elif sextile == 'fourth':
            t1 = round(len(tip0_gps_t)/4)
            t2 = round(len(tip0_gps_t)/3)
            qrt = '_0600Z'
        elif sextile == 'fifth':
            t1 = round(len(tip0_gps_t)/3)
            t2 = round(len(tip0_gps_t)*5/12)
            qrt = '_0800Z'
        elif sextile == 'sixth':
            t1 = round(len(tip0_gps_t)*5/12)
            t2 = round(len(tip0_gps_t)/2)
            qrt = '_1000Z'
        elif sextile == 'seven':
            t1 = round(len(tip0_gps_t)/2)
            t2 = round(len(tip0_gps_t)*7/12)
            qrt = '_1200Z'
        elif sextile == 'eight':
            t1 = round(len(tip0_gps_t)*7/12)
            t2 = round(len(tip0_gps_t)*2/3)
            qrt = '_1400Z'
        elif sextile == 'nine':
            t1 = round(len(tip0_gps_t)*2/3)
            t2 = round(len(tip0_gps_t)*3/4)
            qrt = '_1600Z'
        elif sextile == 'ten':
            t1 = round(len(tip0_gps_t)*3/4)
            t2 = round(len(tip0_gps_t)*5/6)
            qrt = '_1800Z'
        elif sextile == 'eleven':
            t1 = round(len(tip0_gps_t)*5/6)
            t2 = round(len(tip0_gps_t)*11/12)
            qrt = '_2000Z'
        elif sextile == 'twelve':
            t1 = round(len(tip0_gps_t)*11/12)
            t2 = -1
            qrt = '_2200Z'
        elif sextile == 'custom':
            t1 = tspan[0]
            t2 = tspan[1]
        else:
            t1 = 0
            t2 = -1
        
        utc_start = convert_gps_to_utc(tip0_gps_t[t1+30])
        utc_stop  = convert_gps_to_utc(mip0_gps_t[t2])
        dStr_start = generate_dStr_from_astropy_utc(utc_start)
        dStr_stop = generate_dStr_from_astropy_utc(utc_stop)
        
        tplot0 = tip0_gps_t - tip0_gps_t[0]
        tplot1 = tip1_gps_t - tip1_gps_t[0]
        tips_time = f.variables['TIP_SUVM_TIME'][:-2]
        tplots = tips_time - tips_time[0]
        
        mplot0 = mip0_gps_t - mip0_gps_t[0]
        mplot1 = mip1_gps_t - mip1_gps_t[0]
        mips_time = f.variables['MIP_SUVM_TIME'][:-2]
        mplots = mips_time - mips_time[0]
        
        t_lim = (tplot0[t1], tplot0[t2])
                
        fig, ax = plt.subplots(4, figsize=(6.5, 8))
        fig.suptitle(f'\n{dStr_start}\nSTP-H9 ECLIPSE - {unit} PMT & SUVM Plot') 
        '''
        Tri-TIP 1 Hz Plot
        '''
        ax[0].plot(tplot0, f.variables['TIP_M0_RED'][:], 'r', label='Red')
        ax[0].plot(tplot0, f.variables['TIP_M0_UV'][:],  'b', label='UV')
        ax[0].plot(tplot0, f.variables['TIP_M0_DARK'][:],'k', label='Dark')
        ax[0].set(ylabel='Tri-TIP M0 (1 Hz)', xlim=t_lim, yscale = 'log')
        ax[0].legend(loc=1, fontsize='x-small')
        '''
        Tri-TIP 10 Hz Plot
        '''
        ax[1].plot(tplot1, f.variables['TIP_M1_RED'][:], 'r', label='Red', zorder=40)
        ax[1].plot(tplot1, f.variables['TIP_M1_UV'][:],  'b', label='UV',  zorder=30)
        ax[1].plot(tplot1, f.variables['TIP_M1_DARK'][:],'k', label='Dark', zorder=20)
        ax[1].set(ylabel='Tri-TIP M1 (10 Hz)', xlim=t_lim, yscale = 'log', zorder=10, facecolor='none')
        ax[1].legend(loc=1,fontsize='x-small')
        ax1 = ax[1].twinx()  # instantiate a second axes that shares the same x-axis
        ax1.plot(tplots, f.variables['TIP_SUVM_ENCODER_ANGLE'][:-2], 'g')
        ax1.set(ylabel='Tri-TIP SUVM [deg.]', xlim=t_lim, ylim=(0,46))
        '''
        Tri-MIP 1 Hz Plot
        '''
        ax[2].plot(mplot0, f.variables['MIP_M0_MG'][:],   'r', label='Mg+')
        ax[2].plot(mplot0, f.variables['MIP_M0_VK'][:],   'b', label='VK')
        ax[2].plot(mplot0, f.variables['MIP_M0_DARK'][:], 'k', label='Dark')
        ax[2].set(ylabel='Tri-MIP M0 (1 Hz)', xlim=t_lim, yscale = 'log')
        ax[2].legend(loc=1, fontsize='x-small')
        '''
        Tri-MIP 10 Hz Plot
        '''
        ax[3].plot(mplot1, f.variables['MIP_M1_MG'][:],  'r', label='Mg+')
        ax[3].plot(mplot1, f.variables['MIP_M1_VK'][:],  'b', label='VK')
        ax[3].plot(mplot1, f.variables['MIP_M1_DARK'][:],'k', label='Dark')
        ax[3].set(xlabel='Time of Day [sec]', ylabel='Tri-MIP M1 (10 Hz)',
                  xlim=t_lim, yscale = 'log', zorder=10, facecolor='none')
        ax[3].legend(loc=1, fontsize='x-small')
        ax3 = ax[3].twinx()  # instantiate a second axes that shares the same x-axis
        ax3.plot(mplots, f.variables['MIP_SUVM_ENCODER_ANGLE'][:-2],'g')
        ax3.set(ylabel='Tri-MIP SUVM [deg.]', xlim=t_lim, ylim=(0,46))
            
        if save > 0:
            path, fname = os.path.split(infile)
            s = str(utc_start)
            outname = f'{path}/{s[0:4]}{s[5:7]}{s[8:10]}-STPH9-ECLIPSE-{unit}_{content}{qrt}.png'
            print(f' Saving plot ... {outname}')
            fig.savefig(outname)
    except IndexError:
        print(f'\nNo data in {infile}\n\n Skipping plot \n')
    f.close()
    # 
def ecl0_suvm_log(infile, unit='', content='PMT only'):
    print(f'Plotting data values from {infile}')
    f = netCDF4.Dataset(infile)
    # print(f.variables.keys())
    print(f'Loading {unit} variables...')
    print(f.variables['TIP_SUVM_LAST_CRC'][0:10])
    
    f.close()
    
def ecl0_iss_data_plot(infile, save=0):
    print(f'Plotting data values from {infile}')
    f = netCDF4.Dataset(infile)
    
    Year0    = f.variables['Year'][0]
    Month0   = f.variables['Month'][59]
    Day0     = f.variables['Day'][0]
    Hour0    = f.variables['Hour'][59]
    Minute0  = f.variables['Minute'][59]
    Second0  = f.variables['Second'][59]
    # Day_name = f.variables['Day_name'][59]
    DOY0     = f.variables['DOY'][59]
    Jul_date = f.variables['Julian'][:]
    t_GPS    = f.variables['GPS'][:]   # also have 'GPS_CUMUL' available
    t_MET    = f.variables['MET'][:]
    t_USGNC  = f.variables['USGNC_SEC'][:]
    ECI_GNC_x = f.variables['USGNC_POSN_INERT'][:,0]
    ECI_GNC_y = f.variables['USGNC_POSN_INERT'][:,1]
    ECI_GNC_z = f.variables['USGNC_POSN_INERT'][:,2]
    ECI_GNC_q0 = f.variables['USGNC_QUAT_INERT'][:,0]
    ECI_GNC_q1 = f.variables['USGNC_QUAT_INERT'][:,1]
    ECI_GNC_q2 = f.variables['USGNC_QUAT_INERT'][:,2]
    ECI_GNC_q3 = f.variables['USGNC_QUAT_INERT'][:,3]
    
    # q0 = f.variables['USGNC_QUAT_LVLH'][:,0]
    # q1 = f.variables['USGNC_QUAT_LVLH'][:,1]
    # q2 = f.variables['USGNC_QUAT_LVLH'][:,2]
    # q3 = f.variables['USGNC_QUAT_LVLH'][:,3]
    
    q0 = f.variables['USGNC_QUAT_LVLH'][:,0]
    q1 = f.variables['USGNC_QUAT_LVLH'][:,1]
    q2 = f.variables['USGNC_QUAT_LVLH'][:,2]
    q3 = f.variables['USGNC_QUAT_LVLH'][:,3]
    
    """
    function quat2yawpitchroll, quat


qcalc.qnorm ( [q0,q1,q2,q3] )

q = qnorm( double(quat) )


s = where(v eq 1d)        ;vertical pitch
if s[0] ne -1 then begin
    yaw[s] = 2d0*atan(q1[s],q0[s])
    roll[s] = 0.
endif
s = where(v eq -1d)        ;vertical pitch
if s[0] ne -1 then begin
    yaw[s] = -2d0*atan(q1[s],q0[s])
    roll[s] = 0.
endif

;Output
 out = replicate({yaw:0.,pitch:0.,roll:0.},n_elements(q1))
 out.yaw = yaw*180/!dpi
 out.pitch = pitch*180/!dpi
 out.roll = roll*180/!dpi
 
 return,out
end
    
    """
    
    yaw = np.degrees(np.arctan2(2.0*(q0*q3+q1*q2), 1.0 - 2.0*(q2*q2+q3*q3)))
    v = 2.0*(q0*q2 - q3*q1) # Constrain to range -1 < x < 1?
    pitch = np.degrees(np.arcsin(v))
    roll = np.degrees(np.arctan2(2.0*(q0*q1 + q2*q3), 1.0 - 2.0*(q1*q1+q2*q2)))
    
    
    # Unused: Sec_of_day(nPoints, float64) & Sec_of_week(nPoints, float64)
    #         Day_of_week(nPoints, int8)
    #         GPS_WEEK(nPoints, int64)     & GPS_SEC(nPoints, int32 ... sec of week)
    # float64 RADIUS(nPoints)
    # float64 RHAT(nPoints, nVector)
    # float32 USGNC_VEL_INERT(nPoints, nVector)
    # float64 Speed(nPoints)
    # float64 VHAT(nPoints, nVector)
    # float32 USGNC_RATE_INERT(nPoints, nVector)
    # float32 USGNC_QUAT_LVLH(nPoints, nQuaternion)
    # float32 USGNC_POSN_CTRS(nPoints, nVector)
    # float32 USGNC_VEL_CTRS(nPoints, nVector)
    # float32 USGNC_QUAT_CTRS(nPoints, nQuaternion)
    # variables(dimensions):
    # print(f.variables['USGNC_POSN_INERT'][:])
    
    f.close()
    
    utc_start = convert_gps_to_utc(t_USGNC[59])
    utc_stop  = convert_gps_to_utc(t_USGNC[-1])
    dStr_start = generate_dStr_from_astropy_utc(utc_start)
    dStr_stop = generate_dStr_from_astropy_utc(utc_stop)
    t1 = 0
    t2 = -1
    
    tplot0 = t_USGNC - t_USGNC[0]
    t_lim = (tplot0[t1], tplot0[t2])
            
    fig, ax = plt.subplots(2, figsize=(7.5, 6))
    fig.suptitle(f'\n{dStr_start}\nISS H&S Information') 
    '''
    ECI Positions
    '''
    ax[0].scatter(tplot0, ECI_GNC_x, c='k', label='x', s=0.5)
    ax[0].scatter(tplot0, ECI_GNC_y, c='r', label='y', s=0.5)
    ax[0].scatter(tplot0, ECI_GNC_z, c='b', label='z', s=0.5)
    ax[0].set(ylabel='ECI Position [km]', xlim=t_lim)
    # ax[0].legend(loc=1, fontsize='x-small')
    '''
    ECI Quaternions
    '''
    ax[1].scatter(tplot0, yaw, c='k', label='Yaw', s=1)
    ax[1].scatter(tplot0, pitch, c='r', label='Pitch', s=1)
    ax[1].scatter(tplot0, roll, c='g', label='Roll', s=1)
    # ax[1].scatter(tplot0, ECI_GNC_q0, c='k', label='q0', s=1)
    # ax[1].scatter(tplot0, ECI_GNC_q1, c='r', label='q1', s=1)
    # ax[1].scatter(tplot0, ECI_GNC_q2, c='g', label='q2', s=1)
    # ax[1].scatter(tplot0, ECI_GNC_q3, c='b', label='q3', s=1)
    ax[1].set(ylabel='ECI Quaternion', xlim=t_lim)
    
    if save > 0:
        path, fname = os.path.split(infile)
        s = str(utc_start)
        outname = f'{path}/{s[0:4]}{s[5:7]}{s[8:10]}-STPH9-ISS-Position.png'
        print(f' Saving plot ... {outname}')
        fig.savefig(outname)
    
def main():
    YEAR = '2023'
    DIR  = '2305/'
    for DOY in range(121, 152):
        if DOY < 10: sDOY = f'00{DOY}'
        if DOY > 9 and DOY < 100: sDOY = f'0{DOY}'
        if DOY > 99: sDOY = f'{DOY}'
        tic = time.time()
        cts_file = f'C:/data/ECLIPSE/flt/L0_CTS/{DIR}NRL_1729_{YEAR}{sDOY}_ECLIPSE_L0_CTS.nc'
        als_file = f'C:/data/ECLIPSE/flt/L0_ALS/{DIR}NRL_1729_{YEAR}{sDOY}_ECLIPSE_L0_ALS.nc'
        analog_file = f'C:/data/ECLIPSE/flt/L0_analog/{DIR}NRL_1729_{YEAR}{sDOY}_ECLIPSE_L0_analog.nc'
        
        ### iss_file = f'C:/data/STPH9/flt/{DIR}/NRL_589_{YEAR}{sDOY}_L0.nc' # Prior 2023/284
        ### iss_file = f'C:/data/STPH9/flt/{DIR}NRL_674_{YEAR}{sDOY}_L0.nc'
        iss_file = f'C:/data/ECLIPSE/flt/L0_ISS/{DIR}NRL_1729_{YEAR}{sDOY}_ECLIPSE_L0_ISS.nc'
        ecl0_iss_data_plot(iss_file, save=1)
        # 
        # ### Analog plots for both ALS and CTS
        # ecl0_analog_survey_plot(analog_file, save=1)
        
        # # Day long summary plots
        # ecl0_survey_plot(cts_file, unit='CTS', content='TIP_HK', save=1)
        # ecl0_survey_plot(cts_file, unit='CTS', content='MIP_HK', save=1)
        # ecl0_survey_plot(cts_file, unit='CTS', content='SUVM_HK', save=1)
        
        # # 2-hour summary plots
        # ecl_primary_data_plot(cts_file, unit='CTS', sextile='first', save=1)
        # ecl_primary_data_plot(cts_file, unit='CTS', sextile='second', save=1) 
        # ecl_primary_data_plot(cts_file, unit='CTS', sextile='third', save=1) 
        # ecl_primary_data_plot(cts_file, unit='CTS', sextile='fourth', save=1) 
        # ecl_primary_data_plot(cts_file, unit='CTS', sextile='fifth', save=1) 
        # ecl_primary_data_plot(cts_file, unit='CTS', sextile='sixth', save=1) 
        # ecl_primary_data_plot(cts_file, unit='CTS', sextile='seven', save=1) 
        # ecl_primary_data_plot(cts_file, unit='CTS', sextile='eight', save=1) 
        # ecl_primary_data_plot(cts_file, unit='CTS', sextile='nine', save=1) 
        # ecl_primary_data_plot(cts_file, unit='CTS', sextile='ten', save=1) 
        # ecl_primary_data_plot(cts_file, unit='CTS', sextile='eleven', save=1) 
        # ecl_primary_data_plot(cts_file, unit='CTS', sextile='twelve', save=1) 
        
        ##### ecl_primary_data_plot(cts_file, unit='CTS', sextile='custom',tspan=(0,3600))
        
        # # Day long summary plots
        # ecl0_survey_plot(als_file, unit='ALS', content='TIP_HK', save=1)
        # ecl0_survey_plot(als_file, unit='ALS', content='MIP_HK', save=1)
        # ecl0_survey_plot(als_file, unit='ALS', content='SUVM_HK', save=1)
        
        # # 2-hour summary plots
        # ecl_primary_data_plot(als_file, unit='ALS', sextile='first', save=1) 
        # ecl_primary_data_plot(als_file, unit='ALS', sextile='second', save=1) 
        # ecl_primary_data_plot(als_file, unit='ALS', sextile='third', save=1) 
        # ecl_primary_data_plot(als_file, unit='ALS', sextile='fourth', save=1) 
        # ecl_primary_data_plot(als_file, unit='ALS', sextile='fifth', save=1) 
        # ecl_primary_data_plot(als_file, unit='ALS', sextile='sixth', save=1) 
        # ecl_primary_data_plot(als_file, unit='ALS', sextile='seven', save=1) 
        # ecl_primary_data_plot(als_file, unit='ALS', sextile='eight', save=1) 
        # ecl_primary_data_plot(als_file, unit='ALS', sextile='nine', save=1) 
        # ecl_primary_data_plot(als_file, unit='ALS', sextile='ten', save=1) 
        # ecl_primary_data_plot(als_file, unit='ALS', sextile='eleven', save=1) 
        # ecl_primary_data_plot(als_file, unit='ALS', sextile='twelve', save=1) 
        
        toc = time.time()
        print(f' Done processing data from {DOY = }')
        print(f' Total time (sec) to process = {(toc-tic):.2f}')
    # ###ecl0_suvm_log(cts_file, unit='CTS')
    
    """
    Will probably want to add multiple x labels to plots in the future:
    https://stackoverflow.com/questions/53043732/multiple-x-labels-on-pyplot
    """
    
    # 
if __name__ == "__main__":
    print(f"==== {__file__} ====")
    main()