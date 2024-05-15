# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 00:23:53 2024

@author: bfritz
"""
import numpy as np
import NRL_orbit_geometry as orbgeom
from NRL_sun2000 import sun2000
import astropy.coordinates as apc
import astropy.time as apt
import astropy.units as u
from datetime import datetime, timedelta

"""
;***************************************************************************************
;+
; NAME: mmddyyyyhhmm_d.pro
;
; PURPOSE: Convert a date and time into a day number (1-366) and
;                  a fractional day remainder from the time
;
; INPUT ARGUMENTS: Variable Name         Type                    Description
;     MM = integer scalar or vector (1-12)
;     DD = integer scalar or vector (1-31)
;     YY = integer scalar or vector (00-99)
;          optional 4-digit value may be used
;     HH = integer scalar or vector (0-23), optional
;     MIN = integer scalar or vector (0-60), optional
;     SS = float scalar or vector (0-60), optional
;
; OUTPUTS: Variable Name         Type                    Description
;     floating point scalar or vector of day numbers
;
; RESTRICTIONS: This IDL routine is to be distributed only by the Naval
;				Research Laboratory, Code 7607.
;
; MODIFICATION HISTORY:
;		Version 1.0: Scott Alan Budzien, NRL Code 7607, 10/4/97 Corrected for year 2000 bug
;-
;***************************************************************************************
"""
# def mmddyyyyhhmm_d(mm, dd, yy, hh=None, minute=None, ss=None):
#     # Parse input arguments
#     ny = np.size(yy) #     nm = np.size(mm) #     nd = np.size(dd)
#     nh = np.size(hh) #     nmi = np.size(minute) #     ns = np.size(ss)
#     nmax = max([ny, nm, nd, nh, nmi, ns])

#     if ny != nmax and ny != 1: #         raise ValueError(f"YY must be either scalar or a vector of {nmax} elements.")
#     if nm != nmax and nm != 1: #         raise ValueError(f"MM must be either scalar or a vector of {nmax} elements.")
#     if nd != nmax and nd != 1: #         raise ValueError(f"DD must be either scalar or a vector of {nmax} elements.")
#     if nh != 0 and nh != nmax and nh != 1: #         raise ValueError(f"HH must be either scalar or a vector of {nmax} elements.")
#     if nmi != 0 and nmi != nmax and nmi != 1: #         raise ValueError(f"MIN must be either scalar or a vector of {nmax} elements.")
#     if ns != 0 and ns != nmax and ns != 1: #         raise ValueError(f"SS must be either scalar or a vector of {nmax} elements.")

#     # Create cumulative days previous to each month array
#     dpm = np.array([-999, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334])
    
#     # Convert possible scalar month, year values into an array
#     mma = np.broadcast_to(mm, nmax) #     yyyy = np.broadcast_to(yy, nmax)
    
#     # Perform leap year logic
#     mod4 = yyyy - yyyy // 4 * 4 #     mod100 = yyyy - yyyy // 100 * 100
#     mod400 = yyyy - yyyy // 400 * 400
#     intercalary_day = (((mod4 == 0) & (mod100 != 0)) | (mod400 == 0)) & (mma >= 3)
    
#     # Calculate fractional day of the year
#     day = (dpm[mma] + dd) + hh / 24. + minute / 1440. + ss / 86400. + intercalary_day
#     return day

    # Calling sequence
    # doy = mmddyyyyhhmm_d(iso_t.ymdhms.month, iso_t.ymdhms.day, iso_t.ymdhms.year, hr % 24,mn,sc)
    
    # 
def xip_make_vg_utinfo_structure(t0, input_gps_time):
    dayname = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    leap_sec = 18  # Add leap seconds to find MET
    launch_gps_met0 = t0['gpsweek'] * 86400. * 7 + t0['gpssecofweek'] + leap_sec
    met = np.double(input_gps_time) - launch_gps_met0
    
    launch_sec = t0['gpssecofweek']
    launch_week = t0['gpsweek']
    
    hr = int(np.floor(launch_sec/3600.))
    mn = int(np.floor(launch_sec/60.)) - hr*60
    sc = int(np.floor(launch_sec)) - hr*3600 - mn*60
    launch_time = datetime(t0['year'], t0['month'], t0['day'],hr % 24,mn,sc)
    remainder = launch_sec - np.floor(launch_sec)
    launch_jd = apt.Time(launch_time).jd  + remainder/86400.
    
    sec = (launch_sec + met) % 604800.0  # 604,800 sec / week
    week = np.fix((launch_sec + met) / 604800.0 + launch_week)
    jd = launch_jd + np.double(met) / 86400.0
    iso_t = apt.Time(jd, format='jd')
    
    dfrac =  + (iso_t.ymdhms.hour % 24.)/24. + iso_t.ymdhms.minute/24./60. + iso_t.ymdhms.second/24./3600.
    
    fd = iso_t.ymdhms.day + dfrac
    doy = iso_t.yday
    time_obj = iso_t.datetime
    
    sdoy = np.array(iso_t.utc.strftime('%j'))
    doy = [float(x) + y for x,y in zip(sdoy,dfrac)]
    
    utinfo = {
        'year': np.zeros_like(input_gps_time),
        'month': np.zeros_like(input_gps_time),
        'day': np.zeros_like(input_gps_time),
        'hour': np.zeros_like(input_gps_time),
        'min': np.zeros_like(input_gps_time),
        'sec': np.zeros_like(input_gps_time),
        'secondofday': np.zeros_like(input_gps_time),
        'secondofweek': np.zeros_like(input_gps_time),
        'dayofweek': np.zeros_like(input_gps_time, dtype=np.uint8),
        'dayname': np.zeros_like(input_gps_time, dtype='S3'),
        'dayofyear': np.zeros_like(input_gps_time),
        'julian': np.zeros_like(input_gps_time),
        'met': np.zeros_like(input_gps_time, dtype=np.int64),
        'gps': np.zeros_like(input_gps_time, dtype=np.int64)
    }

    for i in range(len(input_gps_time)):
        utinfo['year'][i] = iso_t[i].ymdhms.year
        utinfo['month'][i] = iso_t[i].ymdhms.month
        utinfo['day'][i] = iso_t[i].ymdhms.day
        utinfo['hour'][i] = fd[i] * 24.
        utinfo['min'][i] = int(fd[i] * 1440.) % 60
        utinfo['secondofday'][i] = fd[i] * 86400.0
        utinfo['sec'][i] = utinfo['secondofday'][i] % 60.
        utinfo['dayofyear'][i] = doy[i]
        utinfo['secondofweek'][i] = (((launch_sec + met[i]) % 604800.0) + 604800.0) % 604800.0  # avoid negative values
        utinfo['dayofweek'][i] = int(utinfo['secondofweek'][i] / 86400.0) + 1
        utinfo['dayname'][i] = dayname[utinfo['dayofweek'][i] - 1]
        utinfo['julian'][i] = jd[i]
        utinfo['met'][i] = met[i]
        utinfo['gps'][i] = int(input_gps_time[i])  # this truncates a fractional second, which is just fine

    return utinfo
    # 
def cartesian_gei_to_geodetic(x_gei, y_gei, z_gei, vx_gei, vy_gei, vz_gei, epoch_time=None):
    """
    Convert spacecraft GEI Cartesian coordinates to geodetic latitude and longitude.

    Parameters:
        x_gei: float, spacecraft x-coordinate in GEI (kilometers)
        y_gei: float, spacecraft y-coordinate in GEI (kilometers)
        z_gei: float, spacecraft z-coordinate in GEI (kilometers)
        vx_gei: float, spacecraft velocity in GEI along x-axis (kilometers per second)
        vy_gei: float, spacecraft velocity in GEI along y-axis (kilometers per second)
        vz_gei: float, spacecraft velocity in GEI along z-axis (kilometers per second)
        epoch_time: astropy.time.Time, the time at which the conversion is performed

    Returns:
        tuple: (latitude, longitude, altitude, velocity in AltAz frame)
    """
    # Convert GEI Cartesian coordinates to Cartesian representation
    # gei_coordinates = apc.CartesianRepresentation(x=x_gei, y=y_gei, z=z_gei)
    
    # Set the epoch time
    if epoch_time is None: epoch_time = apt.Time.now()
    # 
    # Create an EarthLocation object for geodetic transformation
    spacecraft_location = apc.EarthLocation(x_gei * u.km, y_gei * u.km, z_gei * u.km)
    
    # Transform GEI coordinates to AltAz frame (geodetic coordinates)
    geodetic_coord = spacecraft_location.to_geodetic()
    
    # Return geodetic latitude, longitude, altitude, and velocity in AltAz frame
    return geodetic_coord.lat, geodetic_coord.lon, geodetic_coord.height #, [vx_gei, vy_gei, vz_gei]

# Example usage
# x_gei = [3500.0, 3510.0, 3520.0]  # GEI x-coordinate in kilometers
# y_gei = [-4500.0,-4510.0,-4520.0]  # GEI y-coordinate in kilometers
# z_gei = [4000.0, 4010.0, 4020.0]  # GEI z-coordinate in kilometers
# vx_gei = [2.0,2.1,2.2]    # GEI velocity along x-axis in kilometers per second
# vy_gei = [-1.0,-1.1,-1.2]   # GEI velocity along y-axis in kilometers per second
# vz_gei = [0.5,0.4,0.3]    # GEI velocity along z-axis in kilometers per second

# epoch_time = apt.Time('2024-01-29T12:00:00')  # Example epoch time
# epoch_time = apt.Time(1390685068, format='gps')

# latitude, longitude, altitude = cartesian_gei_to_geodetic(x_gei, y_gei, z_gei, vx_gei, vy_gei, vz_gei)

# print(f"Geodetic Latitude: {latitude}")
# print(f"Geodetic Longitude: {longitude}")
# print(f"Altitude: {altitude}")

# From here
# https://docs.astropy.org/en/stable/coordinates/satellites.html
# gei_pos = apc.CartesianRepresentation((x_gei, y_gei, z_gei)*u.km)
# gei_vel = apc.CartesianDifferential((vx_gei, vy_gei, vz_gei)*u.km/u.s)
# teme = apc.TEME(gei_pos.with_differentials(gei_vel), obstime=epoch_time)

# itrs_geo = teme.transform_to(apc.ITRS(obstime=epoch_time))
# print(itrs_geo.earth_location.geodetic)

# print(f"Geodetic Latitude: {itrs_geo.earth_location.geodetic.lat}")
# print(f"Geodetic Longitude: {itrs_geo.earth_location.geodetic.lon}")
# print(f"Altitude: {itrs_geo.earth_location.geodetic.height}")

def vector_engine(spv_gei, ldv_gei, sov_gei, utinfo, zmin=None):
    # INPUT VARIABLES
    # spv_gei: Spacecraft position vector in GEI coordinates
    # ldv_gei: Look direction vector in GEI coordinates
    # sov_gei: Slit orientation vector in GEI coordinates
    # utinfo: UT information
    # zmin: Minimum altitude (optional)
    
    # OUTPUT VARIABLES
    # look_azi, lza, look_ra, look_dec, sc_lat, sc_lon, sc_alt
    # sc_zen, sc_radial, tp, tp_lat, tp_lon, tp_alt, tp_zen, sc_sza, tp_sza
    # slit_azimuth, slit_roll, suninfo
    
    # epoch_time = apt.Time(1368578401, format='gps')
    epoch_time = apt.Time(utinfo['gps'], format='gps')
    
    gei_pos = apc.CartesianRepresentation((spv_gei[0,:], spv_gei[1,:], spv_gei[2,:])*u.km)
    gei_vel = apc.CartesianDifferential((spv_gei[0,:], spv_gei[1,:], spv_gei[2,:])*u.km/u.s)
    teme = apc.TEME(gei_pos.with_differentials(gei_vel), obstime=epoch_time)
    
    # itrs_geo = teme.transform_to(apc.ITRS(obstime=epoch_time))
    # print(itrs_geo.earth_location.geodetic.lon[0:10])
    
    ### Time-related issues: Solar location and GMST
    suninfo = sun2000(utinfo['year'], utinfo['month'], utinfo['day'], utinfo['secondofday'] / 3600.0)
    
    ### Compute the location on the Earth below the spacecraft.
    sscp = orbgeom.subtanpt(spv_gei)
    sc_lat = sscp[3]
    sc_lon = ((np.arctan2(spv_gei[1], spv_gei[0]) * 180. / np.pi
                - suninfo['gmst_hrs'] * 15. + 540.) % 360) - 180.
    # 
    ### Compute the local vertical direction vector and altitude at the spacecraft
    sc_zen = np.array([spv_gei[0] - sscp[0,:], spv_gei[1] - sscp[1,:], spv_gei[2] - sscp[2,:]])
    sc_alt = np.linalg.norm(sc_zen, axis=0)
    
    sc_zen = sc_zen / sc_alt
    sc2sun = np.array([[suninfo['x_gei2000']], [suninfo['y_gei2000']], [suninfo['z_gei2000']]]) - np.array([
        [spv_gei[0]], [spv_gei[1]], [spv_gei[2]]
    ])
    sc2sun /= np.linalg.norm(sc2sun, axis=0)
    sc_sza = np.degrees(np.arccos(np.where(np.sum(sc2sun * sc_zen, axis=0) < 1., 1., -1.)))
    
    rnorm = np.linalg.norm(spv_gei, axis=0)
    sc_radial = spv_gei / rnorm
    ### Compute the look zenith angle at the spacecraft
    lza = np.degrees(np.clip(np.arccos(np.sum(ldv_gei * sc_zen, axis=0)),-1.,1.))
    # 
    ### Compute look ra & dec
    look_ra = np.degrees(np.arctan2(ldv_gei[1], ldv_gei[0]))
    look_ra = (look_ra + 360.) % 360
    look_dec = np.degrees(np.clip(np.arcsin(ldv_gei[2]),-1.,1.))
    # 
    ### Compute the look azimuth
    sc_east = np.squeeze(np.array([[-spv_gei[1]], [spv_gei[0]], [0. * spv_gei[2]]]))
    sc_east /= np.linalg.norm(sc_east, axis=0)
    sc_north = np.cross(sc_zen, sc_east, axis=0)
    sc_north /= np.linalg.norm(sc_north, axis=0)
    look_azi = np.degrees(np.arctan2(np.sum(ldv_gei * sc_east, axis=0),
                                        np.sum(ldv_gei * sc_north, axis=0)))
    ### Compute the slit orientation angle
    # lk_east = np.array([[-ldv_gei[1]], [ldv_gei[0]], [np.zeros_like(ldv_gei[2])]])
    # lk_east /= np.sqrt(lk_east[0] ** 2 + lk_east[1] ** 2)
    # lk_north = np.array([
    #     ldv_gei[1] * lk_east[2] - ldv_gei[2] * lk_east[1],
    #     ldv_gei[2] * lk_east[0] - ldv_gei[0] * lk_east[2],
    #     ldv_gei[0] * lk_east[1] - ldv_gei[1] * lk_east[0]
    # ])
    # slit_n = sov_gei[0] * lk_north[0] + sov_gei[1] * lk_north[1] + sov_gei[2] * lk_north[2]
    # slit_e = sov_gei[0] * lk_east[0] + sov_gei[1] * lk_east[1] + sov_gei[2] * lk_east[2]
    # slit_azimuth = (np.degrees(np.arctan2(slit_e, slit_n)) + 720.) % 360
    # 
    ### Compute the slit roll with respect to the horizon
    # horz_ref = -np.array([
    #     ldv_gei[1] * sc_zen[2] - ldv_gei[2] * sc_zen[1],
    #     ldv_gei[2] * sc_zen[0] - ldv_gei[0] * sc_zen[2],
    #     ldv_gei[0] * sc_zen[1] - ldv_gei[1] * sc_zen[0]
    # ])
    # horz_ref /= np.sqrt(np.sum(horz_ref ** 2, axis=0))
    # slit_h = sov_gei[0] * horz_ref[0] + sov_gei[1] * horz_ref[1] + sov_gei[2] * horz_ref[2]
    # slit_v = sov_gei[0] * sc_zen[0] + sov_gei[1] * sc_zen[1] + sov_gei[2] * sc_zen[2]
    # slit_roll = np.degrees(np.arctan2(slit_v, slit_h))
    # 
    ### Now compute the tangent point location above the oblate Earth
    if zmin is None: zmin = 0
    tp = orbgeom.tanpoint(spv_gei, ldv_gei, zmin=zmin)
    ### Compute the location on the Earth below the tangent point
    stp = orbgeom.subtanpt(tp)
    tp_lat = stp[3]
    tp_lon = ((np.arctan2(tp[1], tp[0]) * 180. / np.pi
                - suninfo['gmst_hrs'] * 15. + 540.) % 360) - 180.
    # 
    ### Compute the local vertical direction vector and altitude
    stp_ra_rad = np.arctan2(stp[1], stp[0])
    stp_lat_rad = tp_lat * np.pi / 180
    tp_zen = np.array([
        np.cos(stp_ra_rad) * np.cos(stp_lat_rad),
        np.sin(stp_ra_rad) * np.cos(stp_lat_rad),
        np.sin(stp_lat_rad)
    ])
    tp_zen /= np.sqrt(np.sum(tp_zen * tp_zen, axis=0))
    # 
    ### Compute the tangent point values
    tp_alt = np.sum((tp - stp[0:3]) * tp_zen, axis=0)
    
    ### Compute solar zenith angle at tangent location
    tp2sun = np.array([[suninfo['x_gei2000']], [suninfo['y_gei2000']], [suninfo['z_gei2000']]]) - np.array(tp)
    tp2sun /= np.sqrt(np.sum(tp2sun ** 2, axis=0))
    tp_sza = np.degrees(np.arccos(np.where(np.sum(tp2sun * tp_zen, axis=0) < 1., 1., -1.)))

    return {'tp': tp, 'tp_lat': tp_lat, 'tp_lon': tp_lon, 'tp_alt': tp_alt,
            'sc_lat': sc_lat,'sc_lon': sc_lon,
            'look_azi': look_azi,
            'lza': lza,
            'look_ra': look_ra,
            'look_dec': look_dec,
            'sc_alt': sc_alt,
            'sc_zen': sc_zen,
            'sc_radial': sc_radial, 
            'tp_zen': tp_zen,
            'sc_sza': sc_sza,
            'tp_sza': tp_sza,
            'suninfo': suninfo}
