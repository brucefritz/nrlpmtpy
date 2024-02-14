# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 21:06:35 2024

@author: bfritz
"""
import numpy as np

def refgeoid(lat_geoc_deg):
    # *** See S. Budzien IDL Code for references
    # Returns the radius of the Earth, assuming an ellipsoidal
    # reference geoid as a function of GEOCENTRIC (not geodetic) latitude.
    th = np.double(abs(lat_geoc_deg))*np.pi/180.
    # From the Astronomical Almanac
    a_e = 6378.137          #equatorial radius
    b_e = 6356.752314245    #polar rad=eq rad adjusted for flattening parameter
    # Convert the geocentric latitude to the parameter angle describing
    # the geoid ellipse.  The ellipsoid can be expressed in cylindrical
    # coordinates.
    #
    #    r_cyl = a_e*cos(parameter ang)
    #    z_cyl = b_e*sin(parameter ang)
    #    lat_geoc = atan(z_cyl/r_cyl) = atan(b_e/a_e*tan(parameter ang))
    #    lat_geod = atan(a_e/b_e*tan(parameter ang))
    par_ang = np.arctan(np.tan(th)*a_e/b_e)
    lat_geod = np.arctan(a_e/b_e*np.tan(par_ang))*180./np.pi*np.sign(lat_geoc_deg)
    
    return np.sqrt((a_e*np.cos(par_ang))**2+(b_e*np.sin(par_ang))**2)

def tanpoint(satx, saty, satz, lkx, lky, lkz, zmin=None, spherical_earth=False):
    # Convert to double precision
    shpx, shpy, shpz = np.double(satx), np.double(saty), np.double(satz)
    tpux, tpuy, tpuz = np.double(lkx), np.double(lky), np.double(lkz)

    shpnorm = np.sqrt(shpx**2 + shpy**2 + shpz**2)
    tpunorm = np.sqrt(tpux**2 + tpuy**2 + tpuz**2)
    
    # Define the normal vector to the Shuttle/line-of-sight/Earth plane using 
    # using the cross product. Passes through Earth center
    nvx = tpuy * shpz - tpuz * shpy
    nvy = tpuz * shpx - tpux * shpz
    nvz = tpux * shpy - tpuy * shpx
    nvnorm = np.sqrt(nvx**2 + nvy**2 + nvz**2)
    xynvnorm = np.sqrt(nvx**2 + nvy**2)
    # Geocentric colatitude for normal vector to SC/LOS/Earth plane
    costh = np.ones_like(nvx)
    theta = np.zeros_like(nvx)
    theta_deg = np.zeros_like(nvx)
    sinth = np.zeros_like(nvx)

    s = np.where(nvnorm != 0)[0]
    if len(s) > 0:
        costh[s] = np.clip((nvz[s] / nvnorm[s]), -1.0, 1.0)
        theta[s] = np.arccos(costh[s])
        theta_deg[s] = theta[s] * 180. / np.pi
        sinth[s] = xynvnorm[s] / nvnorm[s]
    # Compute azimuth angle (if defined) for the normal vector
    phi = np.arctan2(nvy, nvx)
    sinph = np.sin(phi)
    cosph = np.cos(phi)
    sel = np.where(xynvnorm == 0.)[0]
    if len(sel) > 0:
        phi[sel] = 0.0
        sinph[sel] = 0.0
        cosph[sel] = 1.0
    # 
    # The intersection of a plane passing through the origin
    # with an ellipsoid is an ellipse.  The major axis of the
    # ellipse is still the Earth's equatorial radius, but the
    # minor axis is in-between the equatorial and polar radii.
    # The offset of the normal from the z-axis is the same as
    # the maximum latitude of the intersecting plane.
    if spherical_earth:
        a_e = earthrad(areal=True)
        b_e = a_e
    else:
        a_e = refgeoid(0.)
        b_e = refgeoid(theta_deg)
    # Compute transformed coordinates for shuttle location and
    # line-of-sight direction
    px = shpx * cosph * costh + shpy * sinph * costh - shpz * sinth
    py = -shpx * sinph + shpy * cosph
    pz = shpx * cosph * sinth + shpy * sinph * sinth + shpz * costh
    # 
    ux = (tpux * cosph * costh + tpuy * sinph * costh - tpuz * sinth) / tpunorm
    uy = (-tpux * sinph + tpuy * cosph) / tpunorm
    uz = (tpux * cosph * sinth + tpuy * sinph * sinth + tpuz * costh) / tpunorm
    # 
    # Define the LOS in new coordinates using slope-intercept format
    # Initially define tangent x,y as observer location (loads default value 
    # for zero/infinite slope case)
    tanx = px
    tany = py
    m = np.zeros_like(uy)
    b = py
    # Select only cases with non-zero or non-infinite slopes
    s = np.where((ux != 0.) & (uy != 0.))[0]
    if len(s) > 0:
        m[s] = uy[s] / ux[s]
        b[s] = py[s] - m[s] * px[s]
        # Change coordinates so ellipse becomes a circle, and adjust the LOS
        # accordingly. Determine tangent location coordinates from where a
        # radial line intersects the LOS
        mu = m[s] * b_e[s] / a_e
        tanx[s] = -b[s] / (mu + 1. / mu)
        tany[s] = -tanx[s] / mu
        # Change back to old coordinates where the circle is an ellipse
        tanx[s] = b_e[s] / a_e * tanx[s]
        
    s = np.where(uy == 0.)[0]
    if len(s) > 0:
        tanx[s] = 0.  # tany = py, m=0. alreaady

    s = np.where(ux == 0.)[0]
    if len(s) > 0:
        tany[s] = 0.    # tanx = px already
        m[s] = np.inf
        b[s] = px[s]    # redefine the interceipt for later use
    # Convert back to the initial geocentric coordinate system
    tx = tanx * cosph * costh - tany * sinph
    ty = tanx * sinph * costh + tany * cosph
    tz = -tanx * sinth
    # Tangent Radial distance
    tr = np.sqrt(tx**2 + ty**2 + tz**2)
    sel = np.where(tr == 0)[0]
    if len(sel) > 0: tr[sel] = 1
    # If no zmin, exit
    if zmin is None:
        return np.array([[tx], [ty], [tz]])
    # Determine the geocentric tangent location altitude -- only an approximation
    # to the surface normal altitude
    ta = tr - refgeoid(90. - np.arccos(tz / tr) * 180. / np.pi)
    # Where geoc tangent altitude drops below the minimum value, find the location
    # of the minimum altitude. Use the coordinates of the SC/LOS/Earth plane
    # (where the geoid is an ellipse) Only search between the tangent location
    # and current SC position
    sel = np.where(ta < zmin)[0]
    if len(sel) > 0:
        thetap = np.arccos(costh[sel])
        tanrp = thetap
        ae = a_e
        # 
        for i in range(len(sel)):
            be = b_e[sel[i]]
            btemp = b[sel[i]]
            mtemp = m[sel[i]]
        # The LOS (y=mx+b) expressed in polar coordinates is r=b/sin(theta) - m*cos(theta)
        # We want to find theta where r - Re = zmin
            if ux[sel[i]] != 0.:
                xrange = [tanx[sel[i]], px[sel[i]]]
                yrange = [btemp + mtemp * xrange[0], btemp + mtemp * xrange[1]]
            else:
                yrange = [tany[sel[i]], py[sel[i]]]
                xrange = [px[sel[i]], px[sel[i]]]
            thrange = np.arctan2(yrange, xrange)
            thmax = np.max(thrange)
            thmin = np.min(thrange)
            diff = np.abs(thmax - thmin)
            if diff > np.pi:
                thmin = thmax
                thmax = thmin + (2. * np.pi - diff)
            if ux[sel[i]] != 0.:
                thetap[i] = regfal('sg_tphfunc', thmin, thmax, 1e-7)
                tanrp[i] = btemp / (np.sin(thetap[i]) - mtemp * np.cos(thetap[i]))
            else:
                thetap[i] = regfal('sg_tphfunc2', thmin, thmax, 1e-7)
                tanrp[i] = btemp / np.cos(thetap[i])
        tanxp = tanrp * np.cos(thetap)
        tanyp = tanrp * np.sin(thetap)
        #  Perform coordinate transformation to the global Cartesian coordinates
        tx[sel] = tanxp * cosph[sel] * costh[sel] - tanyp * sinph[sel]
        ty[sel] = tanxp * sinph[sel] * costh[sel] + tanyp * cosph[sel]
        tz[sel] = -tanxp * sinth[sel]
        tr[sel] = np.sqrt(tx[sel]**2 + ty[sel]**2 + tz[sel]**2)

    return np.array([[tx], [ty], [tz]])

"""
; Based on subtanpt.pro, written by S.A.B.
;		Version 1.0: Scott Alan Budzien, NRL Code 7607,  09/08/1993
;
; PURPOSE:
; Determine the GEODETIC sub-tangent location.  This is located
; somewhat off the radius vector to the tangent point.  This allows
; the latitude, longitude, and radius of the Earth to be calculated
; properly.
;
; This routine allows two options:  a more exact Regula-Falsi
;   interative solution of the problem and a single-step Regula-Falsi
;   approximation.  The iterative solution may take a prohibitively
;   long time for a large set of tangent point locations.
;
; CALLING SEQUENCE:	stp=subtanpt(tpx,tpy,tpz,tol=tol)
;
; INPUT ARGUMENTS: Variable Name         Type                    Description
;		tpx		scalar or array		tangent point x coordinate
;		tpy		scalar or array		tangent point y coordinate
;		tpz		scalar or array		tangent point z coordinate
;
; OUTPUTS: Variable Name         Type                    Description
;
; INPUT KEYWORDS:
;		tol		tolerance to find solution for iterative approach
;		quick	do a quick single-step approximation (ignores tolerance)
; CALLED ROUTINES:
;	stpfunc
; RESTRICTIONS: This IDL routine is to be distributed only by the Naval
;				Research Laboratory, Code 7607.
"""
from matplotlib import pyplot as plt

def subtanpt(invector,tol=None,quick=None):
    ae = refgeoid(0.)
    be = refgeoid(90.)
    # 
    # Azimuthal angle of tangent point location (not affected by oblateness)
    tphi = np.arctan2(invector[1,:],invector[0,:])
    trad = np.sqrt(invector[0,:]**2 + invector[1,:]**2) # Switch to Cyl Coord (r,z)
    tnorm = np.linalg.norm(invector, axis=0)
    # 
    # determine parametric angle of subtangent r-z location
    #   The largest difference between geocentric and geodetic latitudes is
    #   about 0.2 deg.  Therefore, psi should be pretty close to that
    #   corresponding to the geocentric latitude at the start.
    #   To give slack, use +/- .3 deg or .005 radians
    psi_marg = 0.005 # Rad
    psi = trad
    lat_geoc = np.arcsin(invector[2,:]/tnorm)
    tan_psi = (ae/be) * np.tan(lat_geoc)
    # 
    psi_lo  = np.clip(np.arctan(tan_psi) - psi_marg, -np.pi/2, np.pi/2)
    psi_hi  = np.clip(np.arctan(tan_psi) + psi_marg, -np.pi/2, np.pi/2)
    # 
    tr = trad   # place entire array in common block
    tz = invector[2,:]
    if quick is not None: # single iteration of Regula-Falsi
        fa = stpfunc(psi_lo, ae, be, tr, tz)
        fb = stpfunc(psi_hi, ae, be, tr, tz)
        psi = (psi_lo*fb - psi_hi*fa)/(fb-fa) # gets very close to true value
    else: # iterative approach
        if tol is None: tol = 1e-7
        for i in range(np.size(psi)):
            psi[i] = regfal(psi_lo[i],psi_hi[i],ae,be,tr[i],tz[i])
    
    # Convert back to rectangular
    strad = ae * np.cos(psi)
    stz =   be * np.sin(psi)
    stx = strad*np.cos(tphi)
    sty = strad*np.sin(tphi)
    # Calculate Geodetic Latitude
    lat = np.arctan(np.tan(psi)*ae/be)*180./np.pi
    
    """
    # Special case for along z-axis at the end
    ; If necessary: add --> Trap the simple cases for z-axis
    s = where(trad eq 0)
    if s(0) ne -1 then begin
        stx(s) = 0
        sty(s) = 0
        stz(s) = be*sign(tpz(s))
        lat(s) = 90.*sign(tpz(s))
    """
    output = np.zeros((4,np.size(psi)))
    output[0,:] = stx
    output[1,:] = sty
    output[2,:] = stz
    output[3,:] = lat
    return output
    
    """
    !!! Big grain of salt, this is from ChatGPT
    
    from astropy.coordinates import EarthLocation, AltAz, get_sun, solar_system_ephemeris
    from astropy.time import Time
    import astropy.units as u
    
    # Set the spacecraft location
    # Replace latitude, longitude, and altitude with the spacecraft's location
    spacecraft_location = EarthLocation(lat=latitude_degrees*u.deg, lon=longitude_degrees*u.deg, height=elevation_meters*u.m)
    
    # Get the current time
    current_time = Time.now()
    
    # Calculate the sub-tangent point
    with solar_system_ephemeris.set('builtin'):
        sun = get_sun(current_time)
        altaz_frame = AltAz(obstime=current_time, location=spacecraft_location)
        sub_tangent_point = sun.transform_to(altaz_frame)
    
    # Extract the latitude and longitude of the sub-tangent point
    sub_tangent_latitude = sub_tangent_point.transform_to('geocentric').lat.value
    sub_tangent_longitude = sub_tangent_point.transform_to('geocentric').lon.value
    
    print(f"Sub-tangent point coordinates: Latitude {sub_tangent_latitude}, Longitude {sub_tangent_longitude}")
    """
    
    
"""
; STPFUNC.PRO
;        Version 1.0: Scott Alan Budzien, NRL Code 7607,  09/07/1993
; PURPOSE:
;    function for determining where the surface normal
;    passes through a particular (r,z) location.
; --> A very ugly function for determining where the surface normal
; passes through a particular (r,z) location.
"""
def stpfunc(psi, ae, be, tr, tz):
    c = np.cos(psi)
    s = np.sin(psi)
    return (be**2)*c*s - be*tz*c + ae*tr*s - (ae**2)*s*c

"""
; NAME: REGFAL.PRO (Regula-Falsi 1-D root finder)
; MODIFICATION HISTORY:
;        Version 1.0: Scott Alan Budzien, NRL Code 7607, 01/07/1997

; CALLING SEQUENCE: regfal,funcname,a_in,b_in,tol,nmax
; INPUT ARGUMENTS: Variable Name         Type                    Description
;    funcname = string containing name of function
;    a_in, b_in      = bounds of region containing a root of "funcname"
;    tol (optional)  = convergence criterion in the value of x.  Defaults to 1e-5
;    nmax (optional) = maximum number of iterations allowed.  Defaults to 200.
"""

def regfal(a_in, b_in, ae, be, tr, tz, tol=None, nmax=None): # omit: funcname
    # Designed only for Sub-tangent point solver, for now (hence inputs: ae, be, tr, tz)
    if nmax is None: nmax = 200
    if tol  is None: tol = 1e-5
    a = min(a_in, b_in)
    b = max(a_in, b_in)
    if a == b:
        print('REGFAL error: zero width domain')
        return 0
    #
    fa = stpfunc(a, ae, be, tr, tz)
    if fa == 0: return a
    fb = stpfunc(b, ae, be, tr, tz)
    if fb == 0: return b
    #
    xl = 1e38 # Initialize previous x-value to bogus value
    for i in range(nmax): # Iterate to solution
        xn = (a*fb - b*fa)/(fb-fa)
        fn = stpfunc(xn, ae, be, tr, tz)
        if abs(xl-xn) <= tol:
            return xn
        else: xl = xn
        if fa*fn <= 0:
            b = xn
            fb = fn
        else:
            a = xn
            fa = fn
    # 
    print('REGFAL warning: Naximum number of iterations completed')
    return xn






"""
;+
; NAME: sg_TPHFUNC.PRO
;
; LOCATION IN LIBRARY:
;
; TYPE:
;
; PURPOSE:
; 		function for determining where the line-of-sight
; 		is a specified geocentric distance above the surface.
;
; CATEGORY:
;
; CALLING SEQUENCE:		tph=tphfunc(theta)
;
; INPUT ARGUMENTS: Variable Name         Type                    Description
;
; OUTPUTS: Variable Name         Type                    Description
;
; INPUT KEYWORDS:
;
; OUTPUT KEYWORDS:
;
; COMMON BLOCKS:
;		tanpthpar		b,m,ae,be,zmin
;
; CALLED ROUTINES:
;
; SIDE EFFECTS:
;
; RESTRICTIONS: This IDL routine is to be distributed only by the Naval
;				Research Laboratory, Code 7607.
;
; NOTES:
;
; MODIFICATION HISTORY:
;		Version 1.0: Scott Alan Budzien, NRL Code 7607,  09/08/1993
;-
"""
# function sg_tphfunc,theta
# ;
# common tanpthpar,b,m,ae,be,zmin
# ;
# c = cos(theta)
# s = sin(theta)
# psi = atan(be*s,ae*c)
# re = sqrt(be^2+(ae^2-be^2)*sin(psi)^2)
# return,b-(re+zmin)*(s-m*c)
# end

"""
; NAME: sg_TPHFUNC2.PRO
;
; LOCATION IN LIBRARY:
;
; TYPE:
;
; PURPOSE:
; 		Function for determining where the line-of-sight
; 		is a specified geocentric distance above the surface.
;		Differs from tphfunc by not adjusting by m.
;
; CATEGORY:
;
; CALLING SEQUENCE:
;
; INPUT ARGUMENTS: Variable Name         Type                    Description
;
; OUTPUTS: Variable Name         Type                    Description
;
; INPUT KEYWORDS:
;
; OUTPUT KEYWORDS:
;
; COMMON BLOCKS:
;		tanpthpar		b,m,ae,be,zmin
;
; CALLED ROUTINES:
;
; SIDE EFFECTS:
;
; RESTRICTIONS: This IDL routine is to be distributed only by the Naval
;				Research Laboratory, Code 7607.
;
; NOTES:
;
; MODIFICATION HISTORY:
;		Version 0.9: Scott Alan Budzien, NRL Code 7607,  09/08/1993 tphfunc
;		Version 1.0: Scott Alan Budzien, NRL Code 7607,  01/01/2001
;
"""
# function sg_tphfunc2,theta
# common tanpthpar,b,m,ae,be,zmin
# ;
# c = cos(theta)
# s = sin(theta)
# psi = atan(be*s,ae*c)
# re = sqrt(be^2+(ae^2-be^2)*sin(psi)^2)
# return,b-(re+zmin)*c
# end





















"""
; NAME:       EARTHRAD
; PURPOSE:    Return earth radius in specified units.
; CALLING SEQUENCE:
;       r = earthrad(units)
; INPUTS:
;       units = Units for earth radius (def='radians').   in
; OUTPUTS:
;       r = returned earth radius in requested units.     out
; NOTES:
;       Notes: Available units (use 2 letters min):
;         'radians' Radians (default).
;         'degrees' Degrees.
;         'nmiles'  Nautical miles.
;         'miles'   Statute miles.
;         'kms'     Kilometers.
;         'meters'  Meters.
;         'yards'   Yards.
;         'feet'    Feet.
; MODIFICATION HISTORY:
;       R. Sterner, 1996 Sep 03
;
; Copyright (C) 1996, Johns Hopkins University/Applied Physics Laboratory
; This software may be used, copied, or redistributed as long as it is not
; sold and this copyright notice is reproduced on each copy made.  This
; routine is provided as is without any express or implied warranties
; whatsoever.  Other limitations apply as described in the file disclaimer.txt.
"""
def earthrad(units='', help=False):
    """
    Return Earth radius in specified units.
    Parameters:
    - units (str): Units for Earth radius (default is 'radians').
    - help (bool): If True, display help information.
    Returns:
    - r: Returned Earth radius in requested units.
    """
    if help:
        print("Return Earth radius in specified units.")
        print("r = earthrad(units)")
        print("   units = Units for Earth radius (default='radians').")
        print("   r = returned Earth radius in requested units.")
        print("Notes: Available units (use 2 letters min):")
        print("   'radians' Radians (default).")
        print("   'degrees' Degrees.")
        print("   'nmiles' Nautical miles.")
        print("   'miles' Statute miles.")
        print("   'kms' Kilometers.")
        print("   'meters' Meters.")
        print("   'yards' Yards.")
        print("   'feet' Feet.")
        return ''
    # Deal with units
    if not units:        units = 'rad'
    un = units[:2].lower()
    # 
    # Earth's radius in requested units
    if un == 'ra':         cf = 1.0              # Radians/radian.
    elif un == 'de':       cf = 0.0174532925     # Degrees/radian.
    elif un == 'nm':       cf = 2.90682e-04      # Nautical mile/radian.
    elif un == 'mi':       cf = 2.52595e-04      # Miles/radian.
    elif un == 'km':       cf = 1.56956e-04      # Km/radian.
    elif un == 'me':       cf = 1.56956e-07      # Meters/radian.
    elif un == 'fe':       cf = 4.78401e-08      # Feet/radian.
    elif un == 'ya':       cf = 1.43520e-07      # Yards/radian.
    else:
        print('Error in earthrad: Unknown units: ' + units)
        print('Defaulting to radians.')
        cf = 1.0              # Radians/radian.

    return 1 / cf
