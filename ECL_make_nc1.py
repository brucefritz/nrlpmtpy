# -*- coding: utf-8 -*-
"""

Created on Fri Dec 22 20:16:48 2023

@author: bfritz
"""
import os
import sys
import time
import netCDF4
import calendar as cdr
import numpy as np
import pandas as pd
from astropy.time import Time
import astropy.time as apt
from scipy.interpolate import InterpolatedUnivariateSpline as IUS
import csv
import NRL_orbit_geometry as orbgeom
import NRL_quaternion_calculator as quatcalc
import NRL_viewgeom as nvg

from ECL_plot_nc1 import tip_test_plot
from ECL_plot_nc1 import mip_test_plot

from matplotlib import pyplot as plt

def load_L0_data(iss_file, ecl_file):
    dft0 = pd.DataFrame()
    dfm0 = pd.DataFrame()
    dft1 = pd.DataFrame()
    dfm1 = pd.DataFrame()
    dfts = pd.DataFrame()
    dfms = pd.DataFrame()
    dfi  = pd.DataFrame()
    # 
    if os.path.exists(ecl_file):
        fe = netCDF4.Dataset(ecl_file)
        print(f'Loading ECL L0 data from: {ecl_file}')
    else:
        print(f'File does not exist:   {ecl_file}\n')
        sys.exit()
    """
    TIP 1 Hz
    """
    try:
        dft0['TIP_GPS'] = fe.variables['TIP_M0_GPS_TIME'][:]
        dft0['UV_CTS']  = fe.variables['TIP_M0_UV'][:]
        dft0['RD_CTS']  = fe.variables['TIP_M0_RED'][:]
        dft0['DK_CTS']  = fe.variables['TIP_M0_DARK'][:]
        dft0['HVstatus'] = fe.variables['TIP_M0_HV_Status'][:]
    except KeyError:
        print(f'No TIP data at all in {ecl_file}, exiting program')
        # sys.exit()
        return dfi, dft0, dft1, dfm0, dfm1, dfts, dfms
    """
    MIP 1 Hz
    """
    dfm0['MIP_GPS'] = fe.variables['MIP_M0_GPS_TIME'][:]
    dfm0['MG_CTS']  = fe.variables['MIP_M0_MG'][:]
    dfm0['VK_CTS']  = fe.variables['MIP_M0_VK'][:]
    dfm0['DK_CTS']  = fe.variables['MIP_M0_DARK'][:]
    dfm0['HVstatus'] = fe.variables['MIP_M0_HV_Status'][:]
    """
    TIP 10 Hz
    """
    dft1['TIP_GPS'] = fe.variables['TIP_M1_GPS_TIME'][:]
    dft1['UV_CTS']  = fe.variables['TIP_M1_UV'][:]
    dft1['RD_CTS']  = fe.variables['TIP_M1_RED'][:]
    dft1['DK_CTS']  = fe.variables['TIP_M1_DARK'][:]
    """
    MIP 10 Hz
    """
    dfm1['MIP_GPS'] = fe.variables['MIP_M1_GPS_TIME'][:]
    dfm1['MG_CTS']  = fe.variables['MIP_M1_MG'][:]
    dfm1['VK_CTS']  = fe.variables['MIP_M1_VK'][:]
    dfm1['DK_CTS']  = fe.variables['MIP_M1_DARK'][:]
    """
    TIP SUVM Mirror Angle
    """
    dfts['SUVM_HRT_GPS'] = fe.variables['TIP_SUVM_TIME'][:]
    dfts['SUVM_SYSTIME'] = fe.variables['TIP_SUVM_System_Counter'][:]
    dfts['SUVM_GPS_PPS'] = fe.variables['TIP_SUVM_GPS_PPS'][:]
    dfts['SUVM_ANGLE']   = fe.variables['TIP_SUVM_ENCODER_ANGLE'][:]
    """
    MIP SUVM Mirror Angle
    """
    dfms['SUVM_HRT_GPS'] = fe.variables['MIP_SUVM_TIME'][:]
    dfms['SUVM_SYSTIME'] = fe.variables['MIP_SUVM_System_Counter'][:]
    dfms['SUVM_GPS_PPS'] = fe.variables['MIP_SUVM_GPS_PPS'][:]
    dfms['SUVM_ANGLE']   = fe.variables['MIP_SUVM_ENCODER_ANGLE'][:]
    # 
    fe.close()
    # 
    fi = netCDF4.Dataset(iss_file)
    print(f'Loading ISS L0 data from: {iss_file}\n')
    """
    ISS Position / Attitude
    """
    dfi['ISS_GPS']        = fi.variables['USGNC_SEC'][:]
    dfi['ISS_eci_posn_x'] = fi.variables['USGNC_POSN_INERT'][:,0]
    dfi['ISS_eci_posn_y'] = fi.variables['USGNC_POSN_INERT'][:,1]
    dfi['ISS_eci_posn_z'] = fi.variables['USGNC_POSN_INERT'][:,2]
    dfi['ISS_eci_vel_x']  = fi.variables['USGNC_VEL_INERT'][:,0]
    dfi['ISS_eci_vel_y']  = fi.variables['USGNC_VEL_INERT'][:,1]
    dfi['ISS_eci_vel_z']  = fi.variables['USGNC_VEL_INERT'][:,2]
    dfi['ISS_eci_q0']  = fi.variables['USGNC_QUAT_INERT'][:,0]
    dfi['ISS_eci_q1']  = fi.variables['USGNC_QUAT_INERT'][:,1]
    dfi['ISS_eci_q2']  = fi.variables['USGNC_QUAT_INERT'][:,2]
    dfi['ISS_eci_q3']  = fi.variables['USGNC_QUAT_INERT'][:,3]
    dfi['ISS_lvlh_q0']  = fi.variables['USGNC_QUAT_LVLH'][:,0]
    dfi['ISS_lvlh_q1']  = fi.variables['USGNC_QUAT_LVLH'][:,1]
    dfi['ISS_lvlh_q2']  = fi.variables['USGNC_QUAT_LVLH'][:,2]
    dfi['ISS_lvlh_q3']  = fi.variables['USGNC_QUAT_LVLH'][:,3]
    fi.close()
    # 
    return dfi, dft0, dft1, dfm0, dfm1, dfts, dfms


def load_orbit_data(iss_file, ecl_file, t1, t2):
    """
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    THINGS I NEED TO DEBUG
    3) Incorporate SAB position correction for ISS data
    4) Check for existence of data file and/or contents relevant to the orbit
    
    THINGS TO ANNOTATE
    1) Time bases aren't very illuminating for SUVM
    .time is pulled from the HRT packet header
    .system_counter is a running time that just counts seconds since power up
    .gps_pps tracks the PPS signal in the system_counter time base at 1 Hz
    
    --> It's possible the system_counter and gps_pps will diverge over time but
        seem to track pretty closely; does the GPS_PPS do any good? The real
        question I have is whether the HRT packet time stamp is close enough to 
        interpolate off of over long periods of time;
        
        ... for now it will have to do 
    
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    This function loads the L0 data files and breaks up into time chunks based
    on the time limits [t1, t2]
    
    Parameters
    ----------
    ecl_file : STRING -- Path/File for eclipse data
    iss_file : STRING -- Path/file for iss data
    t1, t2   : INT -- GPS times for interval of data to load
    
    Returns
    -------
    dft_1Hz     pandas dataframe with single orbit of data
    dfm_1Hz     pandas dataframe with single orbit of data
    dft_10Hz    pandas dataframe with single orbit of data
    dfm_10Hz    pandas dataframe with single orbit of data
    """
    # 
    dft_1Hz = pd.DataFrame() # Final Output
    dft_10Hz = pd.DataFrame() # Final Output
    dfm_1Hz = pd.DataFrame() # Final Output
    dfm_10Hz = pd.DataFrame() # Final Output
    
    dfi, dft0, dft1, dfm0, dfm1, dfts, dfms = load_L0_data(iss_file, ecl_file)
    
    iso_t1 = apt.Time(int(t1), format='gps')
    doy_t1 = iso_t1.utc.strftime('%j')
    iso_t2 = apt.Time(int(t2), format='gps')
    doy_t2 = iso_t2.utc.strftime('%j')
    
    if abs(int(doy_t2)-int(doy_t1)) > 0:
        ### Orbit spans multiple UT days
        print(f'\n Orbit crosses between DOYs, loading second dataset...\n')
        iso_t = apt.Time(int(t2), format='gps')
        NEXT_DIR = f"{iso_t.utc.strftime('%Y')[2:4]}{iso_t.utc.strftime('%m')}"
        NEXT_DOY = iso_t.utc.strftime('%j')
        # 
        ecl_file2 = f"{ecl_file[0:27]}{NEXT_DIR}{ecl_file[31:45]}{NEXT_DOY}{ecl_file[48:]}"
        iss_file2 = f"{iss_file[0:27]}{NEXT_DIR}{iss_file[31:45]}{NEXT_DOY}{iss_file[48:]}"
        print(f'\n Loading data from {NEXT_DOY = }')
        # 
        dfi2, dft02, dft12, dfm02, dfm12, dfts2, dfms2 = load_L0_data(iss_file2, ecl_file2)
        dfi  = pd.concat([dfi,  dfi2])
        dfi.reset_index(inplace=True, drop=True)
        dft0 = pd.concat([dft0, dft02])
        dft0.reset_index(inplace=True, drop=True)
        dft1 = pd.concat([dft1, dft12])
        dft1.reset_index(inplace=True, drop=True)
        dfm0 = pd.concat([dfm0, dfm02])
        dfm0.reset_index(inplace=True, drop=True)
        dfm1 = pd.concat([dfm1, dfm12])
        dfm1.reset_index(inplace=True, drop=True)
        dfts = pd.concat([dfts, dfts2])
        dfts.reset_index(inplace=True, drop=True)
        dfms = pd.concat([dfms, dfms2])
        dfms.reset_index(inplace=True, drop=True)
        # 
    
    print(f'ISS TLM ... {int(t1)} ... {int(t2)} --> {(int(t2) - int(t1))/60.0:4.4} min')
    
    try:
        tseg0 = dft0[(dft0['TIP_GPS'] >= int(t1)) & (dft0['TIP_GPS'] <= int(t2))]
        tseg0.reset_index(inplace=True, drop=True)
        mseg0 = dfm0[(dfm0['MIP_GPS'] >= int(t1)) & (dfm0['MIP_GPS'] <= int(t2))]
        mseg0.reset_index(inplace=True, drop=True)
        tip_duration = (tseg0['TIP_GPS'][len(tseg0)-1] - tseg0['TIP_GPS'][0])/60.0
        mip_duration = (mseg0['MIP_GPS'][len(mseg0)-1] - mseg0['MIP_GPS'][0])/60.0
    except KeyError:
        print(f'No data for this orbit in {ecl_file}, exiting program\n')
        return dft_1Hz, dft_10Hz, dfm_1Hz, dfm_10Hz
        # sys.exit()
    if tip_duration < 0.25 or mip_duration < 0.25:
        print('Insufficient XIP data to proceed')
        return dft_1Hz, dft_10Hz, dfm_1Hz, dfm_10Hz
        # sys.exit()
    
    print(f"TIP TLM ... {tseg0['TIP_GPS'][0]} ... {tseg0['TIP_GPS'][len(tseg0)-1]} --> {tip_duration:4.4} min")
    print(f"MIP TLM ... {mseg0['MIP_GPS'][0]} ... {mseg0['MIP_GPS'][len(mseg0)-1]} --> {mip_duration:4.4} min\n")
    
    tseg1 = dft1[(dft1['TIP_GPS'] >= tseg0['TIP_GPS'][0]) & (dft1['TIP_GPS'] <= max(tseg0['TIP_GPS']))]
    mseg1 = dfm1[(dfm1['MIP_GPS'] >= mseg0['MIP_GPS'][0]) & (dfm1['MIP_GPS'] <= max(mseg0['MIP_GPS']))]
    tseg1.reset_index(inplace=True, drop=True)
    mseg1.reset_index(inplace=True, drop=True)
    
    # dfts.loc[dfts.SUVM_SYSTIME < 400_000, 'SUVM_SYSTIME'] += dfts['SUVM_SYSTIME'][1]
    dfts = dfts[dfts.SUVM_SYSTIME < 400_000]
    dfts.reset_index(inplace=True, drop=True)
    dfms = dfms[dfms.SUVM_SYSTIME < 400_000]
    dfms.reset_index(inplace=True, drop=True)
    plt.plot(dfms['SUVM_SYSTIME'])
    print(tseg0['TIP_GPS'][0])
    print(max(tseg0['TIP_GPS']))
    
    dfts['TSUVM_GPS_DEC']  = dfts['SUVM_SYSTIME'] - int(dfts['SUVM_SYSTIME'][0]) + dfts['SUVM_HRT_GPS'][0]
    dfms['MSUVM_GPS_DEC']  = dfms['SUVM_SYSTIME'] - int(dfms['SUVM_SYSTIME'][0]) + dfms['SUVM_HRT_GPS'][0]
    print(dfts['TSUVM_GPS_DEC'])
    
    # print(max(dfts['SUVM_SYSTIME']))
    
    # tsegs = dfts[(dfts['SUVM_HRT_GPS'] >= tseg0['TIP_GPS'][0]) & (dfts['SUVM_HRT_GPS'] <= max(tseg0['TIP_GPS']))]
    # msegs = dfms[(dfms['SUVM_HRT_GPS'] >= mseg0['MIP_GPS'][0]) & (dfms['SUVM_HRT_GPS'] <= max(mseg0['MIP_GPS']))]
    tsegs = dfts[(dfts['TSUVM_GPS_DEC'] >= tseg0['TIP_GPS'][0]) & (dfts['TSUVM_GPS_DEC'] <= max(tseg0['TIP_GPS']))]
    msegs = dfms[(dfms['MSUVM_GPS_DEC'] >= mseg0['MIP_GPS'][0]) & (dfms['MSUVM_GPS_DEC'] <= max(mseg0['MIP_GPS']))]
    tsegs.reset_index(inplace=True, drop=True)
    msegs.reset_index(inplace=True, drop=True)
    
    segi = dfi[(dfi['ISS_GPS'] >= tseg0['TIP_GPS'][0]) & (dfi['ISS_GPS'] <= max(tseg0['TIP_GPS']))]
    segi.reset_index(inplace=True, drop=True)
    # 
    dft_1Hz['GPS_SEC'] = tseg0['TIP_GPS']
    dft_1Hz['UV_CTS']  = tseg0['UV_CTS']
    dft_1Hz['RD_CTS']  = tseg0['RD_CTS']
    dft_1Hz['DK_CTS']  = tseg0['DK_CTS']
    # 
    dfm_1Hz['GPS_SEC'] = mseg0['MIP_GPS']
    dfm_1Hz['MG_CTS']  = mseg0['MG_CTS']
    dfm_1Hz['VK_CTS']  = mseg0['VK_CTS']
    dfm_1Hz['DK_CTS']  = mseg0['DK_CTS']
    # 
    dft_10Hz['GPS_SEC'] = tseg1['TIP_GPS']
    dft_10Hz['UV_CTS']  = tseg1['UV_CTS']
    dft_10Hz['RD_CTS']  = tseg1['RD_CTS']
    dft_10Hz['DK_CTS']  = tseg1['DK_CTS']
    # 
    dfm_10Hz['GPS_SEC'] = mseg1['MIP_GPS']
    dfm_10Hz['MG_CTS']  = mseg1['MG_CTS']
    dfm_10Hz['VK_CTS']  = mseg1['VK_CTS']
    dfm_10Hz['DK_CTS']  = mseg1['DK_CTS']
    # 
    """
    Interpolate ISS and SUVM data to match TIP observations
    """
    TSUVM_scan_model = IUS(tsegs['TSUVM_GPS_DEC'], tsegs['SUVM_ANGLE'], k=1)
    MSUVM_scan_model = IUS(msegs['MSUVM_GPS_DEC'], msegs['SUVM_ANGLE'], k=1)
    
    # plt.plot(segi['ISS_GPS'])
    
    ISS_POS_X_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_posn_x'])
    ISS_POS_Y_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_posn_y'])
    ISS_POS_Z_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_posn_z'])
    ISS_VEL_X_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_vel_x'])
    ISS_VEL_Y_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_vel_y'])
    ISS_VEL_Z_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_vel_z'])
    ISS_ECI_Q0_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_q0'])
    ISS_ECI_Q1_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_q1'])
    ISS_ECI_Q2_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_q2'])
    ISS_ECI_Q3_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_q3'])
    ISS_LVLH_Q0_MODEL = IUS(segi['ISS_GPS'], segi['ISS_lvlh_q0'])
    ISS_LVLH_Q1_MODEL = IUS(segi['ISS_GPS'], segi['ISS_lvlh_q1'])
    ISS_LVLH_Q2_MODEL = IUS(segi['ISS_GPS'], segi['ISS_lvlh_q2'])
    ISS_LVLH_Q3_MODEL = IUS(segi['ISS_GPS'], segi['ISS_lvlh_q3'])
    # 
    dft_1Hz['XIP0_SCAN_ANGLE']  = TSUVM_scan_model(tseg0['TIP_GPS'])
    dft_10Hz['XIP1_SCAN_ANGLE'] = TSUVM_scan_model(tseg1['TIP_GPS'])
    dfm_1Hz['XIP0_SCAN_ANGLE']  = 45.0-MSUVM_scan_model(mseg0['MIP_GPS'])
    dfm_10Hz['XIP1_SCAN_ANGLE'] = 45.0-MSUVM_scan_model(mseg1['MIP_GPS'])
    # 
    dft_1Hz['XIP0_eci_posn_x'] = ISS_POS_X_MODEL(tseg0['TIP_GPS'])
    dft_1Hz['XIP0_eci_posn_y'] = ISS_POS_Y_MODEL(tseg0['TIP_GPS'])
    dft_1Hz['XIP0_eci_posn_z'] = ISS_POS_Z_MODEL(tseg0['TIP_GPS'])
    dfm_1Hz['XIP0_eci_posn_x'] = ISS_POS_X_MODEL(mseg0['MIP_GPS'])
    dfm_1Hz['XIP0_eci_posn_y'] = ISS_POS_Y_MODEL(mseg0['MIP_GPS'])
    dfm_1Hz['XIP0_eci_posn_z'] = ISS_POS_Z_MODEL(mseg0['MIP_GPS'])
    # 
    dft_10Hz['XIP1_eci_posn_x'] = ISS_POS_X_MODEL(tseg1['TIP_GPS'])
    dft_10Hz['XIP1_eci_posn_y'] = ISS_POS_Y_MODEL(tseg1['TIP_GPS'])
    dft_10Hz['XIP1_eci_posn_z'] = ISS_POS_Z_MODEL(tseg1['TIP_GPS'])
    dfm_10Hz['XIP1_eci_posn_x'] = ISS_POS_X_MODEL(mseg1['MIP_GPS'])
    dfm_10Hz['XIP1_eci_posn_y'] = ISS_POS_Y_MODEL(mseg1['MIP_GPS'])
    dfm_10Hz['XIP1_eci_posn_z'] = ISS_POS_Z_MODEL(mseg1['MIP_GPS'])
    # 
    dft_1Hz['XIP0_eci_vel_x'] = ISS_VEL_X_MODEL(tseg0['TIP_GPS'])
    dft_1Hz['XIP0_eci_vel_y'] = ISS_VEL_Y_MODEL(tseg0['TIP_GPS'])
    dft_1Hz['XIP0_eci_vel_z'] = ISS_VEL_Z_MODEL(tseg0['TIP_GPS'])
    dfm_1Hz['XIP0_eci_vel_x'] = ISS_VEL_X_MODEL(mseg0['MIP_GPS'])
    dfm_1Hz['XIP0_eci_vel_y'] = ISS_VEL_Y_MODEL(mseg0['MIP_GPS'])
    dfm_1Hz['XIP0_eci_vel_z'] = ISS_VEL_Z_MODEL(mseg0['MIP_GPS'])
    # 
    dft_10Hz['XIP1_eci_vel_x'] = ISS_VEL_X_MODEL(tseg1['TIP_GPS'])
    dft_10Hz['XIP1_eci_vel_y'] = ISS_VEL_Y_MODEL(tseg1['TIP_GPS'])
    dft_10Hz['XIP1_eci_vel_z'] = ISS_VEL_Z_MODEL(tseg1['TIP_GPS'])
    dfm_10Hz['XIP1_eci_vel_x'] = ISS_VEL_X_MODEL(mseg1['MIP_GPS'])
    dfm_10Hz['XIP1_eci_vel_y'] = ISS_VEL_Y_MODEL(mseg1['MIP_GPS'])
    dfm_10Hz['XIP1_eci_vel_z'] = ISS_VEL_Z_MODEL(mseg1['MIP_GPS'])
    # 
    dft_1Hz['XIP0_eci_q0']  = ISS_ECI_Q0_MODEL(tseg0['TIP_GPS'])
    dft_1Hz['XIP0_eci_q1']  = ISS_ECI_Q1_MODEL(tseg0['TIP_GPS'])
    dft_1Hz['XIP0_eci_q2']  = ISS_ECI_Q2_MODEL(tseg0['TIP_GPS'])
    dft_1Hz['XIP0_eci_q3']  = ISS_ECI_Q3_MODEL(tseg0['TIP_GPS'])
    dfm_1Hz['XIP0_eci_q0']  = ISS_ECI_Q0_MODEL(mseg0['MIP_GPS'])
    dfm_1Hz['XIP0_eci_q1']  = ISS_ECI_Q1_MODEL(mseg0['MIP_GPS'])
    dfm_1Hz['XIP0_eci_q2']  = ISS_ECI_Q2_MODEL(mseg0['MIP_GPS'])
    dfm_1Hz['XIP0_eci_q3']  = ISS_ECI_Q3_MODEL(mseg0['MIP_GPS'])
    # 
    dft_10Hz['XIP1_eci_q0'] = ISS_ECI_Q0_MODEL(tseg1['TIP_GPS'])
    dft_10Hz['XIP1_eci_q1'] = ISS_ECI_Q1_MODEL(tseg1['TIP_GPS'])
    dft_10Hz['XIP1_eci_q2'] = ISS_ECI_Q2_MODEL(tseg1['TIP_GPS'])
    dft_10Hz['XIP1_eci_q3'] = ISS_ECI_Q3_MODEL(tseg1['TIP_GPS'])
    dfm_10Hz['XIP1_eci_q0'] = ISS_ECI_Q0_MODEL(mseg1['MIP_GPS'])
    dfm_10Hz['XIP1_eci_q1'] = ISS_ECI_Q1_MODEL(mseg1['MIP_GPS'])
    dfm_10Hz['XIP1_eci_q2'] = ISS_ECI_Q2_MODEL(mseg1['MIP_GPS'])
    dfm_10Hz['XIP1_eci_q3'] = ISS_ECI_Q3_MODEL(mseg1['MIP_GPS'])
    # 
    dft_1Hz['XIP0_lvlh_q0']  = ISS_LVLH_Q0_MODEL(tseg0['TIP_GPS'])
    dft_1Hz['XIP0_lvlh_q1']  = ISS_LVLH_Q1_MODEL(tseg0['TIP_GPS'])
    dft_1Hz['XIP0_lvlh_q2']  = ISS_LVLH_Q2_MODEL(tseg0['TIP_GPS'])
    dft_1Hz['XIP0_lvlh_q3']  = ISS_LVLH_Q3_MODEL(tseg0['TIP_GPS'])
    dfm_1Hz['XIP0_lvlh_q0']  = ISS_LVLH_Q0_MODEL(mseg0['MIP_GPS'])
    dfm_1Hz['XIP0_lvlh_q1']  = ISS_LVLH_Q1_MODEL(mseg0['MIP_GPS'])
    dfm_1Hz['XIP0_lvlh_q2']  = ISS_LVLH_Q2_MODEL(mseg0['MIP_GPS'])
    dfm_1Hz['XIP0_lvlh_q3']  = ISS_LVLH_Q3_MODEL(mseg0['MIP_GPS'])
    # 
    dft_10Hz['XIP1_lvlh_q0'] = ISS_LVLH_Q0_MODEL(tseg1['TIP_GPS'])
    dft_10Hz['XIP1_lvlh_q1'] = ISS_LVLH_Q1_MODEL(tseg1['TIP_GPS'])
    dft_10Hz['XIP1_lvlh_q2'] = ISS_LVLH_Q2_MODEL(tseg1['TIP_GPS'])
    dft_10Hz['XIP1_lvlh_q3'] = ISS_LVLH_Q3_MODEL(tseg1['TIP_GPS'])
    dfm_10Hz['XIP1_lvlh_q0'] = ISS_LVLH_Q0_MODEL(mseg1['MIP_GPS'])
    dfm_10Hz['XIP1_lvlh_q1'] = ISS_LVLH_Q1_MODEL(mseg1['MIP_GPS'])
    dfm_10Hz['XIP1_lvlh_q2'] = ISS_LVLH_Q2_MODEL(mseg1['MIP_GPS'])
    dfm_10Hz['XIP1_lvlh_q3'] = ISS_LVLH_Q3_MODEL(mseg1['MIP_GPS'])
    # 
    return dft_1Hz, dft_10Hz, dfm_1Hz, dfm_10Hz

def make_TIP_ncfile(outfilename, dft_1Hz, dft_10Hz, vg0, vg1):
    ncfile = netCDF4.Dataset(outfilename, mode='w', format='NETCDF4')
    # 
    ncfile.createDimension('nRec1Hz',  len(dft_1Hz))
    ncfile.createDimension('nRec10Hz', len(dft_10Hz))
    ncfile.createDimension('nVec', 3)
    ncfile.createDimension('nQuat', 4)
    # 
    """
    1 Hz Data
    """
    V01 = ncfile.createVariable('GPS_SEC_1Hz', 'f8', ('nRec1Hz',), zlib=True)
    V01.units = 'seconds'
    V01.long_name = 'GPS_time'
    V01[:] = dft_1Hz['GPS_SEC']
    # 
    V02 = ncfile.createVariable('TIP_UV_1Hz', 'u8', ('nRec1Hz',), zlib=True)
    V02.units = 'counts/sec'
    V02.long_name = 'UV_PMT_counts'
    V02[:] = dft_1Hz['UV_CTS']
    # 
    V03 = ncfile.createVariable('TIP_RED_1Hz', 'u8', ('nRec1Hz',), zlib=True)
    V03.units = 'counts/sec'
    V03.long_name = 'red_PMT_counts'
    V03[:] = dft_1Hz['RD_CTS']
    # 
    V04 = ncfile.createVariable('TIP_DARK_1Hz', 'u8', ('nRec1Hz',), zlib=True)
    V04.units = 'counts/sec'
    V04.long_name = 'dark_PMT_counts'
    V04[:] = dft_1Hz['DK_CTS']
    # 
    V10 = ncfile.createVariable('SCAN_ANGLE_1Hz', 'f8', ('nRec1Hz',), zlib=True)
    V10.units = 'degrees'
    V10.long_name = 'SUVM_Scan_Angle'
    V10[:] = dft_1Hz['XIP0_SCAN_ANGLE']
    # 
    V20 = ncfile.createVariable('Geo_Lat_1Hz', 'f8', ('nRec1Hz',), zlib=True)
    V20.units = 'degrees'
    V20.long_name = 'ISS_Geographic_Latitude'
    V20[:] = vg0['sc_lat']
    # 
    V21 = ncfile.createVariable('Geo_Lon_1Hz', 'f8', ('nRec1Hz',), zlib=True)
    V21.units = 'degrees'
    V21.long_name = 'ISS_Geographic_Longitude'
    V21[:] = vg0['sc_lon']
    # 
    V22 = ncfile.createVariable('Tan_Pt_Lat_1Hz', 'f8', ('nRec1Hz',), zlib=True)
    V22.units = 'degrees'
    V22.long_name = 'Tangent_Point_Geographic_Latitude'
    V22[:] = vg0['tp_lat']
    # 
    V23 = ncfile.createVariable('Tan_Pt_Lon_1Hz', 'f8', ('nRec1Hz',), zlib=True)
    V23.units = 'degrees'
    V23.long_name = 'Tangent_Point_Geographic_Longitude'
    V23[:] = vg0['tp_lon']
    # 
    """
    10 Hz Data
    """
    W01 = ncfile.createVariable('GPS_SEC_10Hz', 'f8', ('nRec10Hz',), zlib=True)
    W01.units = 'seconds'
    W01.long_name = 'GPS_time'
    W01[:] = dft_10Hz['GPS_SEC']
    # 
    W02 = ncfile.createVariable('TIP_UV_10Hz', 'u8', ('nRec10Hz',), zlib=True)
    W02.units = 'counts/sec'
    W02.long_name = 'UV_PMT_counts'
    W02[:] = dft_10Hz['UV_CTS']
    # 
    W03 = ncfile.createVariable('TIP_RED_10Hz', 'u8', ('nRec10Hz',), zlib=True)
    W03.units = 'counts/sec'
    W03.long_name = 'red_PMT_counts'
    W03[:] = dft_10Hz['RD_CTS']
    # 
    W04 = ncfile.createVariable('TIP_DARK_10Hz', 'u8', ('nRec10Hz',), zlib=True)
    W04.units = 'counts/sec'
    W04.long_name = 'dark_PMT_counts'
    W04[:] = dft_10Hz['DK_CTS']
    # 
    W10 = ncfile.createVariable('SCAN_ANGLE_10Hz', 'f8', ('nRec10Hz',), zlib=True)
    W10.units = 'degrees'
    W10.long_name = 'SUVM_Scan_Angle'
    W10[:] = dft_10Hz['XIP1_SCAN_ANGLE']
    # 
    W20 = ncfile.createVariable('Geo_Lat_10Hz', 'f8', ('nRec10Hz',), zlib=True)
    W20.units = 'degrees'
    W20.long_name = 'ISS_Geographic_Latitude'
    W20[:] = vg1['sc_lat']
    # 
    W21 = ncfile.createVariable('Geo_Lon_10Hz', 'f8', ('nRec10Hz',), zlib=True)
    W21.units = 'degrees'
    W21.long_name = 'ISS_Geographic_Longitude'
    W21[:] = vg1['sc_lon']
    # 
    W22 = ncfile.createVariable('Tan_Pt_Lat_10Hz', 'f8', ('nRec10Hz',), zlib=True)
    W22.units = 'degrees'
    W22.long_name = 'Tangent_Point_Geographic_Latitude'
    W22[:] = vg1['tp_lat']
    # 
    W23 = ncfile.createVariable('Tan_Pt_Lon_10Hz', 'f8', ('nRec10Hz',), zlib=True)
    W23.units = 'degrees'
    W23.long_name = 'Tangent_Point_Geographic_Longitude'
    W23[:] = vg1['tp_lon']
    # 
    # dict_keys(['tp', 'tp_alt',
    # 'look_azi', 'lza', 'look_ra', 'look_dec', 'sc_alt', 'sc_zen',
    # 'sc_radial', 'tp_zen', 'sc_sza', 'tp_sza', 'suninfo'])
    
    # vg.SW_Version = SW_Version
    # vg.file = file
    # vg.process_UT = process_time
    # vg = np.append(vg, [vg_tmp], axis=0)
    
    # for number in tseg0['TIP_GPS'][0:50]: print(f'{number:10.2f}')
    
    
    
    ncfile.close()
    return 0

def make_MIP_ncfile(outfilename, dfm_1Hz, dfm_10Hz, vg0, vg1):
    ncfile = netCDF4.Dataset(outfilename, mode='w', format='NETCDF4')
    # 
    ncfile.createDimension('nRec1Hz',  len(dfm_1Hz))
    ncfile.createDimension('nRec10Hz', len(dfm_10Hz))
    ncfile.createDimension('nVec', 3)
    ncfile.createDimension('nQuat', 4)
    # 
    V01 = ncfile.createVariable('GPS_SEC', 'f8', ('nRec1Hz',), zlib=True)
    V01.units = 'seconds'
    V01.long_name = 'GPS_time'
    V01[:] = dfm_1Hz['GPS_SEC']
    # 
    V02 = ncfile.createVariable('MIP_UV_1Hz', 'u8', ('nRec1Hz',), zlib=True)
    V02.units = 'counts/sec'
    V02.long_name = 'MG_PMT_counts'
    V02[:] = dfm_1Hz['MG_CTS']
    # 
    V03 = ncfile.createVariable('MIP_RED_1Hz', 'u8', ('nRec1Hz',), zlib=True)
    V03.units = 'counts/sec'
    V03.long_name = 'VK_PMT_counts'
    V03[:] = dfm_1Hz['VK_CTS']
    # 
    V04 = ncfile.createVariable('MIP_DARK_1Hz', 'u8', ('nRec1Hz',), zlib=True)
    V04.units = 'counts/sec'
    V04.long_name = 'dark_PMT_counts'
    V04[:] = dfm_1Hz['DK_CTS']
    
    # 
    ncfile.close()
    return 0


def L1_ALS_TIP(dft_1Hz, dft_10Hz, outfilename):
    print(f'\n\nCreating file ... \n ... {outfilename}')
    vg0 = ECL_calc_viewgeom(dft_1Hz, unit = 'ALS')
    vg1 = ECL_calc_viewgeom(dft_10Hz, data_rate='10Hz', unit = 'ALS')
    make_TIP_ncfile(outfilename, dft_1Hz, dft_10Hz, vg0, vg1)
    
    # tip_test_plot(dft_10Hz)
    # 
    print(' ... Complete')
    return 0
    
def L1_ALS_MIP(dfm_1Hz, dfm_10Hz, outfilename):
    print(f'\n\nCreating file ... \n ... {outfilename}')
    # vg0 = ECL_calc_viewgeom(dfm_1Hz, unit = 'ALS')
    # vg1 = ECL_calc_viewgeom(dfm_10Hz, data_rate='10Hz', unit = 'ALS')
    # make_MIP_ncfile(outfilename, dfm_1Hz, dfm_10Hz, vg0, vg1)
    
    # mip_test_plot(dfm_10Hz)
    # 
    print(' ... Complete')
    return 0
    
def L1_CTS_MIP(dfm_1Hz, dfm_10Hz, outfilename):
    print(f'\n\nCreating file ... \n ... {outfilename}')
    # vg0 = ECL_calc_viewgeom(dfm_1Hz, unit = 'CTS')
    # vg1 = ECL_calc_viewgeom(dfm_10Hz, data_rate='10Hz', unit = 'CTS')
    # make_MIP_ncfile(outfilename, dfm_1Hz, dfm_10Hz, vg0, vg1)
    
    # mip_test_plot(dft_10Hz)
    # 
    print(' ... Complete')
    return 0
    
def L1_CTS_TIP(dft_1Hz, dft_10Hz, outfilename):
    print(f'\n\nCreating file ... \n ... {outfilename}')
    vg0 = ECL_calc_viewgeom(dft_1Hz, unit = 'CTS')
    vg1 = ECL_calc_viewgeom(dft_10Hz, data_rate='10Hz', unit = 'CTS')
    make_TIP_ncfile(outfilename, dft_1Hz, dft_10Hz, vg0, vg1)
    
    #### Test plot routine to look at data
    # clon = np.median(vg0['sc_lon'])
    # tip_test_plot(dft_10Hz)
    
    # 
    print(' ... Complete')
    return 0
    
def ECL_calc_viewgeom(df, data_rate = '1Hz', unit = 'CTS'):
    """
    Routine to pre-compute the viewing geometry specific to ECLIPSE on the ISS
    
    Parameters
    ----------
    df : Pandas Data Frame
        Contents of combined ISS / ECLIPSE data
    data_rate : STRING, optional
        DESCRIPTION. The default is '1Hz'.
    unit : STRING, optional
        DESCRIPTION. The default is '1Hz'.
    
    Returns
    -------
    vg : Pandas Data Frame
        Viewing Geometry parameters
    """
    if data_rate == '1Hz':
        ECL_pos_gei = np.array([df['XIP0_eci_posn_x'],
                                df['XIP0_eci_posn_y'],
                                df['XIP0_eci_posn_z']])
        usgnc_quat_inert = np.array([df['XIP0_eci_q1'],
                                     df['XIP0_eci_q2'],
                                     df['XIP0_eci_q3'],
                                     df['XIP0_eci_q0']])
        mirror_angle = df['XIP0_SCAN_ANGLE']
        
    if data_rate == '10Hz':
        ECL_pos_gei = np.array([df['XIP1_eci_posn_x'],
                                df['XIP1_eci_posn_y'],
                                df['XIP1_eci_posn_z']])
        usgnc_quat_inert = np.array([df['XIP1_eci_q1'],
                                     df['XIP1_eci_q2'],
                                     df['XIP1_eci_q3'],
                                     df['XIP1_eci_q0']])
        mirror_angle = df['XIP1_SCAN_ANGLE']
        
    # ISS coordinates --> +X is along RAM, +Z is along NADIR
    # Ang1 is the angle wedged down from -X axis, positive in this order
    # of Euler rotation calculation (CW when viewed with axis of rotation
    # pointed at you)
    # CTS is "wedged down" 90 degrees from -X, and also only
    # rotated 90 degrees around the z axis (i.e. ang2)
    # 
    # for i,k in enumerate(mirror_angle):
    if unit == 'CTS':
        ang1 = (90.0) * np.pi / 180.0 # it was 14.5 - imgbins[kk]
        ang2 = (90.0) * np.pi / 180.0 # it was 180.5  - specbins[jj]
    if unit == 'ALS':
        ang1 = (0.0) * np.pi / 180.0 # it was 14.5 - imgbins[kk]
        ang2 = (0.0) * np.pi / 180.0 # it was 180.5  - specbins[jj]
    
    R1 = np.array([[np.cos(ang1), 0, np.sin(ang1)],
                   [0, 1.0, 0],
                   [-np.sin(ang1), 0, np.cos(ang1)]])
    R2 = np.array([[np.cos(ang2), -np.sin(ang2), 0],
                   [np.sin(ang2), np.cos(ang2), 0],
                   [0, 0, 1.0]])
    # Adding ".T" invokes the Transpose of the matrix
    ECL_to_iss = np.matmul(R1, R2).T # tweaked until it matched IDL output...
    # ECL_to_iss = np.linalg.multi_dot(R1.T, R2.T)
    # 
    look_ECL = np.zeros((3, len(df)))
    angle_from_ECL_ctr = -(mirror_angle * 2.0 - 45.0)
    look_ECL[0, :] = np.cos(angle_from_ECL_ctr * np.pi / 180)
    look_ECL[2, :] = np.sin(angle_from_ECL_ctr * np.pi / 180)
    # 
    look_iss = np.dot(ECL_to_iss, look_ECL)
    look_gei = quatcalc.apply_quaternion(usgnc_quat_inert, look_iss)
    # 
    slit_CTS = np.zeros((3, len(df)))
    slit_CTS[2, :] = 1.0
    # 
    slit_iss = np.dot(ECL_to_iss, slit_CTS)
    slit_gei = quatcalc.apply_quaternion(usgnc_quat_inert, slit_iss)
    # 
    stph9_launchtime = {'mission_name': 'STPH9',
        'year': 2023, 'month': 3, 'day': 15,
        'hour_ut': 0, 'minute': 30, 'second': 0.,
        'gpsweek': 2253, 'gpssecofweek': 261000,  # this is NOT intrinsic GPS time! (leap secs have been adjusted)
        'ticksperday': 86400.0
    }
    # 
    eclipse_utinfo = nvg.xip_make_vg_utinfo_structure(stph9_launchtime, df.GPS_SEC)
    vg = nvg.vector_engine(ECL_pos_gei, look_gei, slit_gei, eclipse_utinfo)
    return vg
    
def main(x=None):
    tic = time.time()
    """
    Current version
    Date: 2024-04-18, v0.1
    
    # x = 1023 # Overlap with SB test case
    
    Orbits 1209-xxxx  ---  1 Jun 2023
    
    
    Orbit  4545  # An interesting orbit of data
    
    Orbits 4633-4641  ---  8 Jan 2024
    Orbits 4865-      --- 23 Jan 2024 --> Shit data
    Orbits 4911-4918+ --- 26 Jan 2024
    Orbits 5361- --- 24 Feb
    Orbits 5376 --- 25 Feb --> interesting ionosphere bubble structure!
    Orbits 5407 --- 27 Feb
    
    Orbits 5900-5901 --- 29 March GOOD TIP DATA, SHIT ISS
    
    # x = 6054  # eclipse
    """
    version = 'v0.1'
    terminator_file = 'C:/data/STPH9/tle/stp_h9_terminator_log.tsv'
    
    orbit0 = 5901
    num_orb = 1
    for x in range(orbit0, orbit0+num_orb): 
        # Orbit selection
        # x = 4639 
        with open(terminator_file) as f:
            csv_dict = csv.DictReader(f, delimiter='\t')
            df = pd.DataFrame(csv_dict)
        # 
        this_orb = df.iloc[x]
        next_orb = df.iloc[x+1]
        # 
        RevNum = str(this_orb.H9REV).zfill(4)
        print(f'Orbit {RevNum} starts {df.iloc[x].DATE1} at {df.iloc[x].UTC1}')
        print(f'Orbit {RevNum}  ends  {df.iloc[x+1].DATE1} at {df.iloc[x+1].UTC1}\n')
        # 
        YEAR = int(df.iloc[x].DATE1[0:4])
        DIR = f'{df.iloc[x].DATE1[2:4]}{df.iloc[x].DATE1[5:7]}'
        iso_t = apt.Time(df.iloc[x].GPS1, format='gps')
        DOY = iso_t.utc.strftime('%j')
        # 
        als_file = f'C:/data/ECLIPSE/flt/L0_ALS/{DIR}/NRL_1729_{YEAR}{DOY}_ECLIPSE_L0_ALS.nc'
        cts_file = f'C:/data/ECLIPSE/flt/L0_CTS/{DIR}/NRL_1729_{YEAR}{DOY}_ECLIPSE_L0_CTS.nc'
        iss_file = f'C:/data/ECLIPSE/flt/L0_ISS/{DIR}/NRL_1729_{YEAR}{DOY}_ECLIPSE_L0_ISS.nc'
        # 
        atip_1Hz, atip_10Hz, amip_1Hz, amip_10Hz = load_orbit_data(iss_file, als_file, this_orb.GPS1, next_orb.GPS1)
        ctip_1Hz, ctip_10Hz, cmip_1Hz, cmip_10Hz = load_orbit_data(iss_file, cts_file, this_orb.GPS1, next_orb.GPS1)
        # 
        YYYYMMDD = str(f"{this_orb.DATE1[0:4]}{this_orb.DATE1[5:7]}{this_orb.DATE1[8:10]}")
        TIME1 = str(f"{this_orb.UTC1[0:2]}{this_orb.UTC1[3:5]}{this_orb.UTC1[6:8]}")
        TIME2 = str(f"{next_orb.UTC1[0:2]}{next_orb.UTC1[3:5]}{next_orb.UTC1[6:8]}")
        # 
        atip_fname = f'eclipse_tip_limb_L1A_REV{RevNum}_{YYYYMMDD}_{TIME1}_{TIME2}'
        ctip_fname = f'eclipse_tip_disk_L1A_REV{RevNum}_{YYYYMMDD}_{TIME1}_{TIME2}'
        amip_fname = f'eclipse_mip_limb_L1A_REV{RevNum}_{YYYYMMDD}_{TIME1}_{TIME2}'
        cmip_fname = f'eclipse_mip_disk_L1A_REV{RevNum}_{YYYYMMDD}_{TIME1}_{TIME2}'
        # 
        atip_namepath = f'C:/data/ECLIPSE/flt/L1_ATIP/{DIR}/{atip_fname}_{version}'
        ctip_namepath = f'C:/data/ECLIPSE/flt/L1_CTIP/{DIR}/{ctip_fname}_{version}'
        amip_namepath = f'C:/data/ECLIPSE/flt/L1_AMIP/{DIR}/{amip_fname}_{version}'
        cmip_namepath = f'C:/data/ECLIPSE/flt/L1_CMIP/{DIR}/{cmip_fname}_{version}'
        # 
        """
        Make the damn data files
        """
        L1_ALS_TIP(atip_1Hz, atip_10Hz, atip_namepath)
        L1_ALS_MIP(amip_1Hz, amip_10Hz, amip_namepath)
        L1_CTS_TIP(ctip_1Hz, ctip_10Hz, ctip_namepath)
        L1_CTS_MIP(cmip_1Hz, cmip_10Hz, cmip_namepath)
        # 
        
        # plt.plot(ctip_10Hz['UV_CTS'])
        
        tip_test_plot(ctip_10Hz)
        mip_test_plot(cmip_10Hz)
        tip_test_plot(atip_10Hz)
        mip_test_plot(amip_10Hz)
        
        # tip_test_plot(atip_10Hz, t1=10_000, t2=28_000)
        # mip_test_plot(amip_10Hz, t1=10_000, t2=28_000)
        # 
        # tip_test_plot(ctip_10Hz, t1=10_000, t2=28_000)
        # mip_test_plot(cmip_10Hz, t1=10_000, t2=28_000)
        
        # 
        toc = time.time()
        print(f'  Done processing data from Orbit {RevNum} on {YEAR} {DOY = }')
        print(f'  Total time (sec) to process = {toc-tic}')
        # 
if __name__ == "__main__":
    print(f"==== {__file__} ====")
    main()