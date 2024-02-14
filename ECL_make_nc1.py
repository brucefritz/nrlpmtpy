# -*- coding: utf-8 -*-
"""

Created on Fri Dec 22 20:16:48 2023

@author: bfritz
"""
import os
import time
import netCDF4
import calendar as cdr
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from astropy.time import Time
from scipy.interpolate import InterpolatedUnivariateSpline as IUS
import csv
import NRL_orbit_geometry as orbgeom
import NRL_quaternion_calculator as quatcalc
import NRL_viewgeom as nvg

def load_L0_data(ecl_file, iss_file):
    fe = netCDF4.Dataset(ecl_file)
    fi = netCDF4.Dataset(iss_file)
    print(f'Loading ECL data from: {ecl_file}')
    print(f'Loading ISS data from: {iss_file}\n')
    # 
    
    
    """
    Choosing data from the file for TIP can be as simple as findingin when Mode = 2
    - Do I pick out the chunks of data here and loop over to calculate L1A nested?
    - This will have to be done on a case-by-case basis for now without a proper database to pull from
    - Populate the individual file with TIP data
    - Interpolate SUVM data (scan angle is really all I need at this point to feed to VG...)
    - Interpolate ISS data
    
    - Calculate look angle based on simple rotation matrices, then apply quat
    
    - Calculate viewgeometry
    
    
    Naming the files becomes a little stickier, I'd still love to have the orbit #
    
    2023-3-15, 00:30:00 UT ; GPS Week 2253, GPSSECOFWEEK = 261000
    
    """
    # gps_time_tip0 = fe.variables['TIP_M0_GPS_TIME'][:] # !!! Really should trace back and change these names
    # gps_time_tip1 = fe.variables['TIP_M1_GPS_TIME'][:] # !!! Really should trace back and change these names
    # gps_time_tips = fe.variables['TIP_SUVM_TIME'][:]
    # gps_time_iss  = fi.variables['GPS_cumul'][:]
    
    # print(float(gps_time_tip0[0]), float(gps_time_tip1[0]))
    # print(float(gps_time_tips[0]), float(gps_time_iss[0]))
    
    fe.close()
    fi.close()
    return 0

def L1_CTS_TIP(outfilename, ecl_file, iss_file, t1, t2):
    fe = netCDF4.Dataset(ecl_file)
    fi = netCDF4.Dataset(iss_file)
    print(f'Loading ECL data from: {ecl_file}')
    print(f'Loading ISS data from: {iss_file}\n')
    
    dfe0 = pd.DataFrame()
    dfe1 = pd.DataFrame()
    dfes = pd.DataFrame()
    dfi  = pd.DataFrame()
    """
    TIP 1 Hz
    """
    dfe0['TIP_GPS'] = fe.variables['TIP_M0_GPS_TIME'][:]
    dfe0['UV_CTS']  = fe.variables['TIP_M0_UV'][:]
    dfe0['RD_CTS']  = fe.variables['TIP_M0_RED'][:]
    dfe0['DK_CTS']  = fe.variables['TIP_M0_DARK'][:]
    dfe0['HVstatus'] = fe.variables['TIP_M0_HV_Status'][:]
    """
    TIP 10 Hz
    """
    dfe1['TIP_GPS'] = fe.variables['TIP_M1_GPS_TIME'][:]
    dfe1['UV_CTS']  = fe.variables['TIP_M1_UV'][:]
    dfe1['RD_CTS']  = fe.variables['TIP_M1_RED'][:]
    dfe1['DK_CTS']  = fe.variables['TIP_M1_DARK'][:]
    """
    SUVM Mirror Angle
    """
    dfes['SUVM_GPS']     = fe.variables['TIP_SUVM_TIME'][:]
    dfes['SUVM_ANGLE']   = fe.variables['TIP_SUVM_ENCODER_ANGLE'][:]
    dfes['SUVM_SYSTIME'] = fe.variables['TIP_SUVM_System_Counter'][:]
    dfes['GPS_PPS']      = fe.variables['TIP_SUVM_GPS_PPS'][:]
    """
    ISS Position
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
    # 
    fe.close()
    fi.close()
    
    seg0 = dfe0[(dfe0['TIP_GPS'] >= int(t1)) & (dfe0['TIP_GPS'] <= int(t2))]
    # seg0 = seg0[ seg0['HVstatus'] > 0 ]
    seg0.reset_index(inplace=True, drop=True)
    
    seg1 = dfe1[(dfe1['TIP_GPS'] >= seg0['TIP_GPS'][0]) & (dfe1['TIP_GPS'] <= max(seg0['TIP_GPS']))]
    seg1.reset_index(inplace=True, drop=True)
    
    segs = dfes[(dfes['SUVM_GPS'] >= seg0['TIP_GPS'][0]) & (dfes['SUVM_GPS'] <= max(seg0['TIP_GPS']))]
    segs.reset_index(inplace=True, drop=True)
    
    segi = dfi[(dfi['ISS_GPS'] >= seg0['TIP_GPS'][0]) & (dfi['ISS_GPS'] <= max(seg0['TIP_GPS']))]
    segi.reset_index(inplace=True, drop=True)
    # 
    # Create final output data frames
    df_1Hz = pd.DataFrame()
    df_10Hz = pd.DataFrame()
    # 
    df_1Hz['GPS_SEC'] = seg0['TIP_GPS']
    df_1Hz['UV_CTS']  = seg0['UV_CTS']
    df_1Hz['RD_CTS']  = seg0['RD_CTS']
    df_1Hz['DK_CTS']  = seg0['DK_CTS']
    # 
    df_10Hz['GPS_SEC'] = seg1['TIP_GPS']
    df_10Hz['UV_CTS']  = seg1['UV_CTS']
    df_10Hz['RD_CTS']  = seg1['RD_CTS']
    df_10Hz['DK_CTS']  = seg1['DK_CTS']
    # 
    runtimes  = [x - int(segs['GPS_PPS'][0]) for x in segs['GPS_PPS']]
    SUVM_GPS_DEC = [x + segs['SUVM_GPS'][0] for x in runtimes]
    SUVM_scan_model = IUS(SUVM_GPS_DEC, segs['SUVM_ANGLE'], k=1)
    df_1Hz['TIP0_SCAN_ANGLE']  = SUVM_scan_model(seg0['TIP_GPS'])
    df_10Hz['TIP1_SCAN_ANGLE'] = SUVM_scan_model(seg1['TIP_GPS'])
    # 
    ISS_POS_X_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_posn_x'])
    df_1Hz['TIP0_eci_posn_x']  = ISS_POS_X_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_eci_posn_x'] = ISS_POS_X_MODEL(seg1['TIP_GPS'])
    ISS_POS_Y_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_posn_y'])
    df_1Hz['TIP0_eci_posn_y']  = ISS_POS_Y_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_eci_posn_y'] = ISS_POS_Y_MODEL(seg1['TIP_GPS'])
    ISS_POS_Z_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_posn_z'])
    df_1Hz['TIP0_eci_posn_z']  = ISS_POS_Z_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_eci_posn_z'] = ISS_POS_Z_MODEL(seg1['TIP_GPS'])
    # 
    ISS_VEL_X_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_vel_x'])
    df_1Hz['TIP0_eci_vel_x']  = ISS_VEL_X_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_eci_vel_x'] = ISS_VEL_X_MODEL(seg1['TIP_GPS'])
    ISS_VEL_Y_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_vel_y'])
    df_1Hz['TIP0_eci_vel_y']  = ISS_VEL_Y_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_eci_vel_y'] = ISS_VEL_Y_MODEL(seg1['TIP_GPS'])
    ISS_VEL_Z_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_vel_z'])
    df_1Hz['TIP0_eci_vel_z']  = ISS_VEL_Z_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_eci_vel_z'] = ISS_VEL_Z_MODEL(seg1['TIP_GPS'])
    # 
    ISS_ECI_Q0_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_q0'])
    df_1Hz['TIP0_eci_q0']  = ISS_ECI_Q0_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_eci_q0'] = ISS_ECI_Q0_MODEL(seg1['TIP_GPS'])
    ISS_ECI_Q1_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_q1'])
    df_1Hz['TIP0_eci_q1']  = ISS_ECI_Q1_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_eci_q1'] = ISS_ECI_Q1_MODEL(seg1['TIP_GPS'])
    ISS_ECI_Q2_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_q2'])
    df_1Hz['TIP0_eci_q2']  = ISS_ECI_Q2_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_eci_q2'] = ISS_ECI_Q2_MODEL(seg1['TIP_GPS'])
    ISS_ECI_Q3_MODEL = IUS(segi['ISS_GPS'], segi['ISS_eci_q3'])
    df_1Hz['TIP0_eci_q3']  = ISS_ECI_Q3_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_eci_q3'] = ISS_ECI_Q3_MODEL(seg1['TIP_GPS'])
    # 
    ISS_LVLH_Q0_MODEL = IUS(segi['ISS_GPS'], segi['ISS_lvlh_q0'])
    df_1Hz['TIP0_lvlh_q0']  = ISS_LVLH_Q0_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_lvlh_q0'] = ISS_LVLH_Q0_MODEL(seg1['TIP_GPS'])
    ISS_LVLH_Q1_MODEL = IUS(segi['ISS_GPS'], segi['ISS_lvlh_q1'])
    df_1Hz['TIP0_lvlh_q1']  = ISS_LVLH_Q1_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_lvlh_q1'] = ISS_LVLH_Q1_MODEL(seg1['TIP_GPS'])
    ISS_LVLH_Q2_MODEL = IUS(segi['ISS_GPS'], segi['ISS_lvlh_q2'])
    df_1Hz['TIP0_lvlh_q2']  = ISS_LVLH_Q2_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_lvlh_q2'] = ISS_LVLH_Q2_MODEL(seg1['TIP_GPS'])
    ISS_LVLH_Q3_MODEL = IUS(segi['ISS_GPS'], segi['ISS_lvlh_q3'])
    df_1Hz['TIP0_lvlh_q3']  = ISS_LVLH_Q3_MODEL(seg0['TIP_GPS'])
    df_10Hz['TIP1_lvlh_q3'] = ISS_LVLH_Q3_MODEL(seg1['TIP_GPS'])
    
    
    vg = ECL_calc_viewgeom(df_1Hz)
    
    
    # print(df_1Hz.iloc[0])
    # print(df_10Hz)
    # for number in seg0['TIP_GPS'][0:50]: print(f'{number:10.2f}')
    # 
    
    plot_time = [x-seg0.TIP_GPS[0] for x in seg0.TIP_GPS]
    # plot_time1 = [x-seg1.TIP_GPS[0] for x in seg1.TIP_GPS]
    # # plot_times = [x-segs.SUVM_GPS_DEC[0] for x in segs.SUVM_GPS_DEC]
    
    # fix,ax = plt.subplots(1)
    
    # ax.plot(plot_time0, df_1Hz.UV_CTS)
    # ax.plot(plot_time0, df_1Hz.RD_CTS)
    # ax.plot(plot_time0, df_1Hz.DK_CTS)
    # ax.plot(plot_time1, seg1.UV_CTS)
    # ax.plot(plot_time1, seg1.SCAN_ANGLE)
    # # ax.plot(plot_times, segs['SUVM_ANGLE'])
    # ax.set(xlim=(500,2500))
    
    print(f'\n\nCreating file ... \n ... {outfilename}')
    ncfile = netCDF4.Dataset(outfilename,mode='w',format='NETCDF4')
    # 
    ncfile.createDimension('nRec1Hz',  len(df_1Hz))
    ncfile.createDimension('nRec10Hz', len(df_10Hz))
    ncfile.createDimension('nVec', 3)
    ncfile.createDimension('nQuat', 4)
    # 
    V01 = ncfile.createVariable('GPS_SEC', 'f8', ('nRec1Hz',), zlib=True)
    V01.units = 'seconds'
    V01.long_name = 'GPS_time'
    V01[:] = df_1Hz['GPS_SEC']
    # 
    V02 = ncfile.createVariable('TIP_UV_1Hz', 'u8', ('nRec1Hz',), zlib=True)
    V02.units = 'counts/sec'
    V02.long_name = 'UV_PMT_counts'
    V02[:] = df_1Hz['UV_CTS']
    # 
    V03 = ncfile.createVariable('TIP_RED_1Hz', 'u8', ('nRec1Hz',), zlib=True)
    V03.units = 'counts/sec'
    V03.long_name = 'red_PMT_counts'
    V03[:] = df_1Hz['RD_CTS']
    # 
    V04 = ncfile.createVariable('TIP_DARK_1Hz', 'u8', ('nRec1Hz',), zlib=True)
    V04.units = 'counts/sec'
    V04.long_name = 'dark_PMT_counts'
    V04[:] = df_1Hz['DK_CTS']
    # 
    ncfile.close()
    # print(df_1Hz['GPS_SEC'][0:3])
    # print(np.max(df_1Hz['GPS_SEC'][:]))
    return 0
    
def ECL_calc_viewgeom(df):
    from matplotlib import pyplot as plt
    # print(df['TIP0_SCAN_ANGLE'][0])
    
    # Pull SUVM scan angle from SUVM data to calculte look angle
    # Use rotation matrices to convert SUVM scan angle to ISS coordinates
    
    # specbins = [0.0, 0.0] # Trash
    # nspecbins = len(specbins)
    # nspecbins = 1
    # nimgbins = 1
    
    nframes = len(df)
    
    ECL_pos_gei = np.zeros((3,nframes))
    ECL_pos_gei[0,:] = df['TIP0_eci_posn_x']
    ECL_pos_gei[1,:] = df['TIP0_eci_posn_y']
    ECL_pos_gei[2,:] = df['TIP0_eci_posn_z']
    usgnc_quat_inert = np.zeros((4,nframes))
    usgnc_quat_inert[0,:] = df['TIP0_eci_q0']
    usgnc_quat_inert[1,:] = df['TIP0_eci_q1']
    usgnc_quat_inert[2,:] = df['TIP0_eci_q2']
    usgnc_quat_inert[3,:] = df['TIP0_eci_q3']
    
    # ISS coordinates --> +X is along RAM, +Z is along NADIR
    # Ang1 is the angle wedged down from -X axis, positive in this order
    # of Euler rotation calculation (CW when viewed with axis of rotation
    # pointed at you)
    # CTS is "wedged down" 90 degrees from -X, and also only
    # rotated 90 degrees around the z axis (i.e. ang2)
    # 
    ang1 = (90.0) * np.pi / 180.0 # it was 14.5 - imgbins[kk]
    ang2 = (90.0) * np.pi / 180.0 # it was 180.5  - specbins[jj]
    R1 = np.array([[np.cos(ang1), 0, np.sin(ang1)],
                   [0, 1.0, 0],
                   [-np.sin(ang1), 0, np.cos(ang1)]])
    R2 = np.array([[np.cos(ang2), -np.sin(ang2), 0],
                   [np.sin(ang2), np.cos(ang2), 0],
                   [0, 0, 1.0]])
    # Adding ".T" invokes the Transpose of the matrix
    CTS_to_iss = np.matmul(R1, R2).T # tweaked until it matched IDL output...
    # CTS_to_iss = np.linalg.multi_dot(R1.T, R2.T)
    # 
    look_CTS = np.zeros((3, nframes))
    angle_from_CTS_ctr = 0.0
    look_CTS[0, :] = np.cos(angle_from_CTS_ctr * np.pi / 180)
    look_CTS[2, :] = np.sin(angle_from_CTS_ctr * np.pi / 180)
    # 
    look_iss = np.dot(CTS_to_iss, look_CTS)
    look_gei = quatcalc.apply_quaternion(usgnc_quat_inert, look_iss)
    # 
    slit_CTS = np.zeros((3, nframes))
    slit_CTS[2, :] = 1.0
    # 
    slit_iss = np.dot(CTS_to_iss, slit_CTS)
    slit_gei = quatcalc.apply_quaternion(usgnc_quat_inert, slit_iss)
    # We are not interpolating for now, but leave this for information later
    # Here we have a problem. We need quaternions and look vectors at the same
    # cadence, with no good way to interpolate, because quaternions are nasty.
    # Just pick the closest quaternion in time. This could introduce errors on
    # the order of 0.1 degrees. This will affect photometers mostly since the
    # spectrometers collect spectra over a long period of time.
        
    vg_tmp = nvg.vector_engine(ECL_pos_gei, look_gei, slit_gei, df)
     
    
    
    # plt.plot(list(range(nframes)), look_gei[0,:])
    
    
    
    
    # vg_tmp.SW_Version = SW_Version
    # vg_tmp.file = file
    # vg_tmp.process_UT = process_time
    # vg = np.append(vg, [vg_tmp], axis=0)
    
    # out = NRL_regfal(3, 5, 4, 2, 5, 10) ## remnant from testin
    
    vg = pd.DataFrame()
    
    return vg


    """
    e. Slingshot cleans up the position information at this point
     - Litesviewgeom
    f. Set up structures to hold output [data class]
     - viewing_geometry_vector_engine (spv_gei,ldv_gei,sov_gei,utinfo, $ ;INPUT VARIABLES)
    g.  Compute the location on the Earth below the spacecraft.
    ; This computes the true local vertical according to the oblate
    ; Earth and uses a quickly-converging iterative aproach
    ;
    sscp = subtanpt(reform(spv_gei(0,*)),reform(spv_gei(1,*)),reform(spv_gei(2,*)))
    sc_lat = sscp(*,3)
    
    ---> This uses subtanpt.pro
        - This will be hard to convert directly, since S.A.B. computes this iteratively
    
    h. Compute the local vertical direction vector and altitude at the spacecraft
    sc_zen = double([[reform(spv_gei(0,*))],[reform(spv_gei(1,*))],[reform(spv_gei(2,*))]])-sscp
    
    sc_alt = sqrt(total((sc_zen)^2,2))
    sc_zen = sc_zen/(sc_alt#[1,1,1])
    sc_radial = double([[reform(spv_gei(0,*))],[reform(spv_gei(1,*))],[reform(spv_gei(2,*))]])
    rnorm = sqrt(total((sc_radial)^2,2))
    sc_radial = sc_radial/(rnorm#[1,1,1])
    
    i. Compute the look zenith angle at the spacecraft
    lza = acos(((reform(ldv_gei(0,*))*sc_zen(*,0) + $
                 reform(ldv_gei(1,*))*sc_zen(*,1) + $
                 reform(ldv_gei(2,*))*sc_zen(*,2) )<1.)>(-1.))*180./!pi
    
    j. Compute look ra & dec
    look_ra = atan(reform(ldv_gei(1,*)),reform(ldv_gei(0,*)))*180./!pi
    s = where(look_ra lt 0)
    if s(0) ne -1 then look_ra(s) = look_ra(s)+360
    look_dec = asin((reform(ldv_gei(2,*))<1.)>(-1.))*180./!pi
    
    
    k. Compute the look azimuth
    sc_east = [[-reform(spv_gei(1,*))   ],$
               [reform(spv_gei(0,*))    ],$
               [ 0.*reform(spv_gei(2,*))]]
    sc_east = sc_east/(sqrt(total((sc_east)^2,2))#[1,1,1])
    sc_north = [[sc_zen(*,1)*sc_east(*,2) - sc_zen(*,2)*sc_east(*,1)],$
                [sc_zen(*,2)*sc_east(*,0) - sc_zen(*,0)*sc_east(*,2)],$
                [sc_zen(*,0)*sc_east(*,1) - sc_zen(*,1)*sc_east(*,0)]]
    sc_north = sc_north/(sqrt(total((sc_north)^2,2))#[1,1,1])
    look_azi = atan(reform(ldv_gei(0,*))*sc_east(*,0) + $
                    reform(ldv_gei(1,*))*sc_east(*,1) + $
                    reform(ldv_gei(2,*))*sc_east(*,2), $
                    reform(ldv_gei(0,*))*sc_north(*,0) + $
                    reform(ldv_gei(1,*))*sc_north(*,1) + $
                    reform(ldv_gei(2,*))*sc_north(*,2)   )*180./!pi
    
    
    l. Now compute the tangent point location above the oblate Earth
    ; If tangent altitudes fall below zmin, the intersections of zmin and LOS is estimated.
    ;
    if not keyword_set(zmin) then zmin=0.
    tp = tanpoint(reform(spv_gei(0,*)),reform(spv_gei(1,*)),reform(spv_gei(2,*)),$
                  reform(ldv_gei(0,*)),reform(ldv_gei(1,*)),reform(ldv_gei(2,*)),zmin)
    ;
    ; Compute the location on the Earth below the tangent point.
    ; This computes the true local vertical according to the oblate
    ; Earth and uses a quickly-converging iterative aproach
    ;
    stp = subtanpt(tp(*,0),tp(*,1),tp(*,2))
    tp_lat = stp(*,3)                          ;geodetic lat
    ;
    ; Compute the local vertical direction vector and altitude
    ; Note that the subtangent point is always at the surface,
    ; so use the surface normal vector at that location
    ;
    stp_ra_rad = (atan(stp(*,1),stp(*,0)))(*)
    stp_lat_rad = tp_lat(*)*!dpi/180
    tp_zen = [[cos(stp_ra_rad)*cos(stp_lat_rad)],$
              [sin(stp_ra_rad)*cos(stp_lat_rad)],$
              [sin(stp_lat_rad)]                ]
    tp_zen = tp_zen/(sqrt(total(tp_zen*tp_zen,2,/double))#[1,1,1])
    
    ; Compute the tangent point altitude:  compute the dot product
    ; of the vector from the subtangent point to the tangent point
    ; with local vertical.  If negative, the tangent point is below
    ; the surface--hopefully only slightly
    tp_alt = total((tp-stp(*,0:2))*tp_zen,2)
    
    ; Time related issues:  Solar location and GMST
    suninfo = sun2000(utinfo.year,utinfo.month,utinfo.day,utinfo.secondofday/3600.)
    
    ; Compute solar zenith angle at spacecraft
    sc2sun = [[suninfo.x_gei2000],[suninfo.y_gei2000],[suninfo.z_gei2000]] $
             - [[reform(spv_gei(0,*))],[reform(spv_gei(1,*))],[reform(spv_gei(2,*))]]
    sc2sun = sc2sun/(sqrt(total(sc2sun^2,2))#[1,1,1])
    sc_sza = acos((total(sc2sun*sc_zen,2)<1.)>(-1.))*180./!pi
    
    ; Compute solar zenith angle at tangent location
    tp2sun = [[suninfo.x_gei2000],[suninfo.y_gei2000],[suninfo.z_gei2000]] - tp
    tp2sun = tp2sun/(sqrt(total(tp2sun^2,2))#[1,1,1])
    tp_sza = acos((total(tp2sun*tp_zen,2,/double)<1.)>(-1.))*180./!pi
    
    ; Compute the longitude of the spacecraft and the tangent point
    sc_lon = ((atan(reform(spv_gei(1,*)),reform(spv_gei(0,*)))*180./!pi $
               - suninfo.gmst_hrs*15. + 540.      ) mod 360) - 180.
    tp_lon = ((atan(reform(tp(*,1)),reform(tp(*,0)))*180./!pi $
               - suninfo.gmst_hrs*15. + 540.        ) mod 360) - 180.
    """


def main(YEAR=None, DIR=None, DOY=None):
    tic = time.time()
    # if YEAR == None: YEAR = 2024
    # if DIR  == None: DIR  = '2401'
    # if DOY  == None: DOY  = 2
    if YEAR == None: YEAR = 2023
    if DIR  == None: DIR  = '2305'
    if DOY  == None: DOY  = 140
    if DOY < 10: DOY = f'00{DOY}'
    # 
    # als_file = f'C:/data/ECLIPSE/flt/L0_ALS/{DIR}/NRL_1729_{YEAR}{DOY}_ECLIPSE_L0_ALS.nc'
    cts_file = f'C:/data/ECLIPSE/flt/L0_CTS/{DIR}/NRL_1729_{YEAR}{DOY}_ECLIPSE_L0_CTS.nc'
    # iss_file = f'C:/data/STPH9/flt/{DIR}/NRL_589_{YEAR}{DOY}_L0.nc' # Prior 2023/284
    iss_file = f'C:/data/ECLIPSE/flt/L0_ISS/{DIR}/NRL_1729_{YEAR}{DOY}_ECLIPSE_L0_ISS.nc'
    # output = load_L0_data(cts_file, iss_file)
    
    terminator_file = 'C:/data/STPH9/tle/stp_h9_terminator_log.tsv'
    with open(terminator_file) as f:
        csv_dict = csv.DictReader(f, delimiter='\t')
        # for row in csv_dict:
        #     print(row['H9REV'])
        df = pd.DataFrame(csv_dict)
    # print(df.iloc[4526])
    # print('\n\n')
    
    (fpath, fbase_ext) = os.path.split(cts_file)
    (fbase, f_ext) = os.path.splitext(fbase_ext)
    
    unit = fbase_ext[28:31] # ALS | CTS
    # choose = 4539  # An interesting orbit of data
    choose = 1022 # Overlap with SB test case
    this_orbit = df.iloc[choose]
    next_orbit = df.iloc[choose+1]
    RevNum = str(this_orbit['H9REV'])
    if len(RevNum) == 1: RevNum = f'0000{RevNum}'
    if len(RevNum) == 2: RevNum = f'000{RevNum}'
    if len(RevNum) == 3: RevNum = f'00{RevNum}'
    if len(RevNum) == 4: RevNum = f'0{RevNum}'
    # 
    YYYYMMDD = str(f"{this_orbit['DATE2'][0:4]}{this_orbit['DATE2'][5:7]}{this_orbit['DATE2'][8:10]}")
    TIME1 = str(f"{this_orbit['UTC2'][0:2]}{this_orbit['UTC2'][3:5]}{this_orbit['UTC2'][6:8]}")
    TIME2 = str(f"{next_orbit['UTC2'][0:2]}{next_orbit['UTC2'][3:5]}{next_orbit['UTC2'][6:8]}")
    # 
    fnew_ext = f'eclipse_tip_{unit}_L1A_REV{RevNum}_{YYYYMMDD}_{TIME1}_{TIME2}'
    outname = f'C:/data/ECLIPSE/flt/L1_CTS/{fnew_ext}'
    # 
    # print(this_orbit.GPS2, next_orbit.GPS2)
    L1_CTS_TIP(outname, cts_file, iss_file, this_orbit.GPS2, next_orbit.GPS2)
    
    toc = time.time()
    print(f' Done processing data from DOY {DOY}')
    print(f' Total time (sec) to process = {toc-tic}')
    # 
if __name__ == "__main__":
    print(f"==== {__file__} ====")
    main()