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

"""

Unclear why these two methods give different results!!

"""
from matplotlib import pyplot as plt

def vector_engine(spv_gei, ldv_gei, sov_gei, utinfo, zmin=None):
    # INPUT VARIABLES
    # spv_gei: Spacecraft position vector in GEI coordinates
    # ldv_gei: Look direction vector in GEI coordinates
    # sov_gei: Slit orientation vector in GEI coordinates
    # utinfo: UT information
    # zmin: Minimum altitude (optional)
    
    # OUTPUT VARIABLES
    # look_azi, lza, look_ra, look_dec, sc_lat, sc_lon, sc_alt
    # sc_zen, sc_radial, tp, tp_lat, tp_lon, tp_alt, tp_zen, sc_sza, tp_sza, suninfo
    # slit_azimuth, slit_roll
    epoch_time = apt.Time(1368578401, format='gps')
    gei_pos = apc.CartesianRepresentation((spv_gei[0,:], spv_gei[1,:], spv_gei[2,:])*u.km)
    gei_vel = apc.CartesianDifferential((spv_gei[0,:], spv_gei[1,:], spv_gei[2,:])*u.km/u.s)
    teme = apc.TEME(gei_pos.with_differentials(gei_vel), obstime=epoch_time)
    
    itrs_geo = teme.transform_to(apc.ITRS(obstime=epoch_time))
    # print(itrs_geo.earth_location.geodetic.lon[0:10])
    
    ### Compute the location on the Earth below the spacecraft.
    sscp = orbgeom.subtanpt(spv_gei)
    # plt.plot(list(range(len(spv_gei[0,:]))), sscp[0,:])
    # print(sscp[:,0:5])
    sc_lat = sscp[3]
    
    # plt.plot(list(range(len(sscp[0,:]))), itrs_geo.earth_location.geodetic.lat)
    # 
    ### Compute the local vertical direction vector and altitude at the spacecraft
    sc_zen = np.array([spv_gei[0] - sscp[0,:], spv_gei[1] - sscp[1,:], spv_gei[2] - sscp[2,:]])
    sc_alt = np.linalg.norm(sc_zen, axis=0)
    
    sc_zen = sc_zen / sc_alt
    # sc_radial = np.array([spv_gei[0], spv_gei[1], spv_gei[2]])
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
    # sc_east = np.array([[-spv_gei[1]], [spv_gei[0]], [0. * spv_gei[2]]])
    # sc_east /= np.sqrt(np.sum(sc_east ** 2, axis=0))
    # sc_north = np.array([
    #     sc_zen[1] * sc_east[2] - sc_zen[2] * sc_east[1],
    #     sc_zen[2] * sc_east[0] - sc_zen[0] * sc_east[2],
    #     sc_zen[0] * sc_east[1] - sc_zen[1] * sc_east[0]
    # ])
    # sc_north /= np.sqrt(np.sum(sc_north ** 2, axis=0))
    # look_azi = np.degrees(np.arctan2(
    #     np.sum(ldv_gei * sc_east, axis=0),
    #     np.sum(ldv_gei * sc_north, axis=0)
    # ))
    # 
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
    tp = orbgeom.tanpoint(spv_gei[0,:], spv_gei[1,:], spv_gei[2,:],
                          ldv_gei[0,:], ldv_gei[1,:], ldv_gei[2,:], zmin=zmin)

    plt.plot(list(range(len(sscp[0,:]))), np.squeeze(tp[1,:]))
    
    ### Compute the location on the Earth below the tangent point
    # stp = orbgeom.subtanpt(tp[0], tp[1], tp[2])
    # tp_lat = stp[3]
    # 
    ### Compute the local vertical direction vector and altitude
    # stp_ra_rad = np.arctan2(stp[1], stp[0])
    # stp_lat_rad = tp_lat * np.pi / 180
    # tp_zen = np.array([
    #     np.cos(stp_ra_rad) * np.cos(stp_lat_rad),
    #     np.sin(stp_ra_rad) * np.cos(stp_lat_rad),
    #     np.sin(stp_lat_rad)
    # ])
    # tp_zen /= np.sqrt(np.sum(tp_zen * tp_zen, axis=0))
    # 
    ### Compute the tangent point altitude
    # tp_alt = np.sum((tp - stp[0:3]) * tp_zen, axis=0)
    # 
    ### Time-related issues: Solar location and GMST
    # suninfo = sun2000(utinfo['year'], utinfo['month'], utinfo['day'], utinfo['secondofday'] / 3600.0)

    ### Compute solar zenith angle at spacecraft
    # sc2sun = np.array([[suninfo['x_gei2000']], [suninfo['y_gei2000']], [suninfo['z_gei2000']]]) - np.array([
    #     [spv_gei[0]], [spv_gei[1]], [spv_gei[2]]
    # ])
    # sc2sun /= np.sqrt(np.sum(sc2sun ** 2, axis=0))
    # sc_sza = np.degrees(np.arccos(np.where(np.sum(sc2sun * sc_zen, axis=0) < 1., 1., -1.)))

    ### Compute solar zenith angle at tangent location
    # tp2sun = np.array([[suninfo['x_gei2000']], [suninfo['y_gei2000']], [suninfo['z_gei2000']]]) - np.array(tp)
    # tp2sun /= np.sqrt(np.sum(tp2sun ** 2, axis=0))
    # tp_sza = np.degrees(np.arccos(np.where(np.sum(tp2sun * tp_zen, axis=0) < 1., 1., -1.)))

    ### Compute the longitude of the spacecraft and the tangent point
    # sc_lon = ((np.arctan2(spv_gei[1], spv_gei[0]) * 180. / np.pi
    #             - suninfo['gmst_hrs'] * 15. + 540.) % 360) - 180.
    # tp_lon = ((np.arctan2(tp[1], tp[0]) * 180. / np.pi
    #             - suninfo['gmst_hrs'] * 15. + 540.) % 360) - 180.

    # Return the results
    return 0
    # return {
    #     'look_azi': look_azi, 'lza': lza, 'look_ra': look_ra, 'look_dec': look_dec,
    #     'sc_lat': sc_lat, 'sc_lon': sc_lon, 'sc_alt': sc_alt, 'sc_zen': sc_zen,
    #     'sc_radial': sc_radial, 'tp': tp, 'tp_lat': tp_lat, 'tp_lon': tp_lon,
    #     'tp_alt': tp_alt, 'tp_zen': tp_zen, 'sc_sza': sc_sza, 'tp_sza': tp_sza,
    #     'suninfo': suninfo, 'slit_azimuth': slit_azimuth, 'slit_roll': slit_roll
    # }

# Example usage:
# spv_gei = np.array([[ 4404.54405245,  4402.27734455,  4400.00355363,  4397.72482031,   4395.44000604],
#                     [ 4596.72585323,  4601.67287742,  4606.61404985,  4611.54935371,   4616.47882803],
#                     [-2376.11915343, -2370.72722013, -2365.33217622, -2359.93388219,  -2354.53283427]])
# ldv_gei = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
# sov_gei = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
# utinfo = {'year': 2024, 'month': 1, 'day': 22, 'secondofday': 3600}
# result = vector_engine(spv_gei, ldv_gei, sov_gei, utinfo)
# print(result)

