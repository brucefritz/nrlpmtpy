# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 23:46:11 2024

@author: bfritz


; NAME: sun2000.pro
; PURPOSE:;   To compute the RA and Dec of the Sun at a given date.
; CALLING SEQUENCE:
;   out = SUN2000(yr, mo, dy, ut)
; INPUTS:
;       yr = year.
;       mo = month number.
;       dy = month day number.
;       ut = UT1 time in hours.
; OUTPUTS:
;       structure type sun2000info containing fields
;         jd                = Julian date (double)
;         yr,mo,dy          = Calendar date(int)
;         UT                = UT in hours (double)
;         TDT               = approximate Terrestrial Dynamical Time in hours (double)
;         GMST              = accurate to 0.1s
;         ra_app,dec_app    = apparent right ascension, declination for mean date (double)
;         ecl_lon,ecl_lat   = ecliptic latitude (approx) and longitude for mean date (double)
;         ecl_lon2000,
;           ecl_lat2000     = ecliptic latitude (approx) and latitude for J2000 (double)
;         x_gei,y_gei,z_gei = geocentric inertial coordinates for mean date (double)
;         x_gei2000,
;           y_gei2000,
;           z_gei2000       = geocentric inertial coordinate for J2000 (double)
;         ss_lat,ss_lon     = geodetic (GEO) sub-solar latitude and longitude
;         r_sun             = Earth-sun distance (approx)
;
; OPTIONAL INPUT KEYWORD:
;   RADIAN - If this keyword is set and non-zero, then all angular output variables
;       are given in Radians rather than Degrees
;   AU     - If this keyword is set and non-zero, then all distance magnitudes
;            output are in AU rather than KM.
;	HELP
;
; CALLED ROUTINES:
;	intrpl
;	fjulian
;	geocgeod
;
; NOTES:
;   The accuracy in the 20th century  should be within 1"; however this
;   has not been extensively tested.  The returned RA and Dec are in the
;   given date's equinox.
;
;   Procedure was extensively revised in May 1996, and the new calling
;   sequence is incompatible with the old one.
;
;   Procedure further revised in August 1998.  Unfortunately, the approximations
;   for calculating the solar distance and solar ecliptic lattitude are much less
;   accurate than the RA and DEC calculations.  Solar distance is good to 0.001%
;   and calculation for solar angular position in ecliptic lat, lon is good to
;   roughly 10".
;
; METHOD:
;   Uses a truncated version of Newcomb's Sun.    Adapted from the IDL
;   routine SUN_POS by CD Pike, which was adapted from a FORTRAN routine
;   by B. Emerson (RGO).
; EXAMPLE:
;   (1) Find the apparent RA and Dec of the Sun on May 1, 1982
;
;   IDL> jdcnv, 1982, 5, 1,0 ,jd      ;Find Julian date jd = 2445090.5
;   IDL> sunpos, jd, ra, dec
;   IDL> print,adstring(ra,dec,2)
;        02 31 32.61  +14 54 34.9
;
;   The Astronomical Almanac gives 02 31 32.58 +14 54 34.9 so the error
;       in SUNPOS for this case is < 0.5".
;
;   (2) Find the apparent RA and Dec of the Sun for every day in 1997
;
;   IDL> jdcnv, 1997,1,1,0, jd                ;Julian date on Jan 1, 1997
;   IDL> sunpos, jd+ dindgen(365), ra, dec    ;RA and Dec for each day
;
; MODIFICATION HISTORY:
;   Written by Michael R. Greason, STX, 28 October 1988.
;   Accept vector arguments, W. Landsman     April,1989
;   Eliminated negative right ascensions.  MRG, Hughes STX, 6 May 1992.
;   Rewritten using the 1993 Almanac.  Keywords added.  MRG, HSTX,
;       10 February 1994.
;   Major rewrite, improved accuracy, always return values in degrees
;   W. Landsman  May, 1996
;   Added /RADIAN keyword,    W. Landsman       August, 1997
;   Converted to IDL V5.0   W. Landsman   September 1997
;   Extensively dapted by Scott Budzien (Naval Research Lab) 8/13/98
;        converted to function format; utilized structure output; additional
;        calculations for Earth-Sun distance, precession to J2000, and GEI
;        coordinates added.
;
;		Version 0.9: Scott Alan Budzien, Jean Marie Valme, @NRL Code 7607,  12/10/1999
;                        version adapted to C++ for ARGOS-HIRAAS ephgen program.
;		Version 1.0: Scott Alan Budzien, NRL Code 7607,  04/08/2002
;           1.1: Updated code to current year, Damien Chua, NRL Code 7669, 10/21/2008
;           1.2: Updated TDT values through 2013 using data tabulated at
;                http://hpiers.obspm.fr/eop-pc/earthor/ut1lod/ut1-tai_pred.html
;                Damien Chua, NRL Code 7669, 7/21/2009.
"""

import numpy as np
from NRL_orbit_geometry import refgeoid
from scipy.interpolate import interp1d

def intrpl(x, y, xi):
    f = interp1d(x, y, kind='linear', fill_value="extrapolate")
    return f(xi)

def sun2000(yr, mo, dy, ut, RADIANS=False, AU=False, GMSTONLY=False):
    AU_CONSTANT = 149597870.66
    RAD2DEG = 180.0 / np.pi
    DEG2RAD = np.pi / 180.0
    # 
    # Parse input parameters
    nparm = max(len(yr), len(mo), len(dy), len(ut))
    if nparm < 4 or GMSTONLY:
        print("From Year, Month, and Day compute floating point Julian Day number.")
        print("jd = fjulian(y, m, d)")
        print("yr = Year (like 1987).")
        print("mo = month (like 7 for July).")
        print("dy = month day (like 23).")
        print("ut = universal time (hours).")
        print("/RADIANS = angles output in radians. (Default is DEG)")
        print("/AU = distances output in AU. (Default is KM)")
        return -1

    yr = np.array(yr)
    mo = np.array(mo)
    dy = np.array(dy)
    ut = np.array(ut)

    if (yr % 100 == yr).all():
        print("Use 4-digit year number.")
        return -1

    # Convert parameters
    yr = np.int_(np.atleast_1d(yr))
    mo = np.int_(np.atleast_1d(mo))
    dy = np.double(np.atleast_1d(dy))
    ut = np.double(np.atleast_1d(ut))

    # Useful constants
    dpi = np.pi
    au = AU_CONSTANT
    rad2deg = RAD2DEG
    deg2rad = DEG2RAD

    # Convert UT to TDT
    temp_list = [00,10,20,30,40,45,50,55,60,65,
                70,71,72,73,74,75,76,77,78,79,
                80,81,82,83,84,85,86,87,88,89,
                90,91,92,93,94,95,96,97,98,99,
                100,101,102,103,104,105,106,107,108,109,
                110,111,112,113,114,115,116,117,118,119,
                120,121,122,123,124]
    tdt_yr = np.array([1900. + i for i in temp_list])
    tdt_adj = np.array([-2.72, 10.46, 21.16, 24.02, 24.33, 26.77, 29.15, 31.07, 33.15, 35.73,
                        40.18, 41.17, 42.23, 43.37, 44.49, 45.48, 46.46, 47.52, 48.53, 49.59,
                        50.54, 51.38, 52.17, 52.96, 53.79, 54.34, 54.87, 55.32, 55.82, 56.30,
                        56.86, 57.57, 58.31, 59.12, 59.98, 60.78, 61.63, 62.29, 62.97, 63.47,
                        63.83, 64.09, 64.30, 64.47, 64.57, 64.62, 64.85, 65.15, 65.46, 65.78,
                        66.07, 66.32, 66.60, 67.20, 67.44, 67.68, 68.20, 68.63, 69.00, 69.32,
                        69.36, 69.36, 70.91, 71.49, 72])
    
    # func_yr = interp1d(tdt_yr, tdt_adj, kind='linear', fill_value="extrapolate")
    # return func_yr(xi)

    adj = intrpl(tdt_yr, tdt_adj, yr * np.ones(np.shape(yr)))
    tdt = ut + adj / 3600.0
    jd = fjulian(yr, mo, dy)
    mjd = fjulian(yr, mo, dy, mjd=True)

    # Julian centuries from 1900.0 and 2000.0
    t1900 = (jd - 2415020.0) / 36525.0
    t2000 = (jd - 2451545.0) / 36525.0

    # Sun's Geometric mean longitude J1900 in arcsec
    lambda_sun = (279.696678 + ((36000.768925 * t1900 + 0.041068639 * tdt) % 360.0)) * 3600.0

    # Allow for ellipticity of the orbit (equation of centre)
    # using the Earth's mean anomaly ME
    me = 358.475844 + ((35999.049750 * t1900 + 0.041066678 * tdt) % 360.0)
    ellcor = (6910.1 - 17.2 * t1900 - 1.9621264e-5 * tdt) * np.sin(me * deg2rad) + 72.3 * np.sin(
        2.0 * me * deg2rad)
    lambda_sun += ellcor

    # Allow for the Venus perturbations using the mean anomaly of Venus MV
    mv = 212.603219 + ((58517.803875 * t1900 + 0.066755423 * tdt) % 360.0)
    vencorr = 4.8 * np.cos((299.1017 + mv - me) * deg2rad) + \
              5.5 * np.cos((148.3133 + 2.0 * mv - 2.0 * me) * deg2rad) + \
              2.5 * np.cos((315.9433 + 2.0 * mv - 3.0 * me) * deg2rad) + \
              1.6 * np.cos((345.2533 + 3.0 * mv - 4.0 * me) * deg2rad) + \
              1.0 * np.cos((318.15 + 3.0 * mv - 5.0 * me) * deg2rad)
    lambda_sun += vencorr

    # Allow for the Mars perturbations using the mean anomaly of Mars MM
    mm = 319.529425 + ((19139.858500 * t1900 + 0.021834199 * tdt) % 360.0)
    marscorr = 2.0 * np.cos((343.8883 - 2.0 * mm + 2.0 * me) * deg2rad) + \
               1.8 * np.cos((200.4017 - 2.0 * mm + me) * deg2rad)
    lambda_sun += marscorr

    # Allow for the Jupiter perturbations using the mean anomaly of Jupiter MJ
    mj = 225.328328 + ((3034.6920239 * t1900 + 0.0034618891 * tdt) % 360.0)
    jupcorr = 7.2 * np.cos((179.5317 - mj + me) * deg2rad) + \
              2.6 * np.cos((263.2167 - mj) * deg2rad) + \
              2.7 * np.cos((87.1450 - 2.0 * mj + 2.0 * me) * deg2rad) + \
              1.6 * np.cos((109.4933 - 2.0 * mj + me) * deg2rad)
    lambda_sun += jupcorr

    # Allow for the Moon's perturbations using the mean elongation of
    # the Moon from the Sun D
    d = 350.7376814 + ((445267.11422 * t1900 + 0.50794788 * tdt) % 360.0)
    mooncorr = 6.5 * np.sin(d * deg2rad)
    lambda_sun += mooncorr

    # Allow for long period terms
    longterm = 6.4 * np.sin((231.19 + 20.20 * t1900 + 2.3043577e-5 * tdt) * deg2rad)
    lambda_sun += longterm

    # Make sure lambda_sun is positive by adding 720 (in arcsec)
    lambda_sun = (lambda_sun + 2592000.0) % 1296000.0

    # Allow for Aberration: Get apparent longitude, assume r_sun=1au
    lambda_app = lambda_sun - 20.5

    # Allow for Nutation using the longitude of the Moon's mean node OMEGA
    omega = 259.183275 - ((1934.142008 * t1900 + 0.0022064134 * tdt) % 360.0)
    lambda_app -= 17.2 * np.sin(omega * deg2rad)

    # Convert apparent and mean longitude to degrees
    lambda_sun /= 3600.0
    lambda_app /= 3600.0

    # Calculate GMST, required for sub-solar latitude
    # Equation from Astronomical Almanac, related to UT, converted to degrees
    t = t2000 + ut / 24.0 / 36525.0
    gmst = ((100.4606183688 + ((36000.7700536083 * t) % 360.0) +
             15.0 * ut +
             0.0038793333 * t ** 2 -
             2.5833333e-8 * t ** 3) + 720.0) % 360.0
    
    if GMSTONLY:
        return gmst / 15.0

    # Estimate the solar latitude: mean date
    beta = 0.0

    # Form the True Obliquity
    oblt = 23.452294 - 0.0130125 * t1900 - 1.4844284e-8 * tdt + (9.2 * np.cos(omega * deg2rad)) / 3600.0

    # Form Right Ascension and Declination: mean date of observation
    ra = np.arctan2(np.sin(lambda_app * deg2rad) * np.cos(oblt * deg2rad),
                    np.cos(lambda_app * deg2rad))

    neg = np.where(ra < 0.0)[0]
    ra[neg] += 2.0 * np.pi

    dec = np.arcsin(np.sin(lambda_app * deg2rad) * np.sin(oblt * deg2rad))

    # Calculate true distance to Sun using approximate formula for mean anomaly of Earth
    e = 0.016709 - 0.0000418 * t2000 - 4.7684e-11 * tdt
    w = 282.94 + 1.72 * t2000 + 1.9621e-6 * tdt
    nu = lambda_sun - w
    r_sun_au = (1.0 - e ** 2) / (1.0 + e * np.cos(nu * deg2rad))

    # Cartesian coordinates in ecliptic plane: mean date, true position
    x_ecl = r_sun_au * np.cos(lambda_sun * deg2rad) * np.cos(beta * deg2rad)
    y_ecl = r_sun_au * np.sin(lambda_sun * deg2rad) * np.cos(beta * deg2rad)
    z_ecl = r_sun_au * np.sin(beta * deg2rad)

    # Transformation Matrix to GEI: mean date, true position
    x_gei = x_ecl
    y_gei = y_ecl * np.cos(oblt * deg2rad) - z_ecl * np.sin(oblt * deg2rad)
    z_gei = y_ecl * np.sin(oblt * deg2rad) + z_ecl * np.cos(oblt * deg2rad)

    # Using GMST and ecliptic long., estimate equatorial long., calculate
    # sub-solar long. on Earth. Need to use apparent solar position!
    long_equ = np.degrees(np.arctan2(np.sin(lambda_app * deg2rad) * np.cos(oblt * deg2rad),
                                     np.cos(lambda_app * deg2rad)))  # in degrees
    lat_equ = np.degrees(np.arcsin(np.sin(lambda_app * deg2rad) * np.sin(oblt * deg2rad)))  # in degrees
    # sslon = [((x - y + 540.) % 360) - 180 for x,y in zip(long_equ, gmst)]
    sslon = (long_equ - gmst + 540) % 360 - 180  # in degrees
    sslat = geocgeod(lat_equ)  # assuming geocgeod is a defined function

    # Transform ecliptic latitude and longitude of mean date to J2000
    t2000p = t2000 + tdt / (24 * 36525)
    a = 1.396971 * t2000p + 0.0003086 * t2000p**2
    b = 0.013056 * t2000p - 0.0000092 * t2000p**2
    cp = 5.12362 - 1.155358 * t2000p - 0.0001964 * t2000p**2
    beta0 = beta - b * np.sin((lambda_sun + cp) * deg2rad)
    lambda0 = lambda_sun - a + b * np.cos((lambda_sun + cp) * deg2rad) * np.tan(beta0 * deg2rad)

    # Cartesian coordinates in ecliptic plane: J2000
    x_ecl2000 = r_sun_au * np.cos(lambda0 * deg2rad) * np.cos(beta0 * deg2rad)
    y_ecl2000 = r_sun_au * np.sin(lambda0 * deg2rad) * np.cos(beta0 * deg2rad)
    z_ecl2000 = r_sun_au * np.sin(beta0 * deg2rad)

    # Transformation Matrix to GEI 2000
    obl2000 = 23.439291
    x_gei2000 = x_ecl2000
    y_gei2000 = y_ecl2000 * np.cos(obl2000 * deg2rad) - z_ecl2000 * np.sin(obl2000 * deg2rad)
    z_gei2000 = y_ecl2000 * np.sin(obl2000 * deg2rad) + z_ecl2000 * np.cos(obl2000 * deg2rad)

    # Cartesian coordinates in ecliptic plane: mean date, apparent position
    x_ecl_app = r_sun_au * np.cos(lambda_app * deg2rad) * np.cos(beta * deg2rad)
    y_ecl_app = r_sun_au * np.sin(lambda_app * deg2rad) * np.cos(beta * deg2rad)
    z_ecl_app = r_sun_au * np.sin(beta * deg2rad)

    # Transformation Matrix to GEI: mean date, true position
    x_gei_app = x_ecl_app
    y_gei_app = y_ecl_app * np.cos(oblt * deg2rad) - z_ecl_app * np.sin(oblt * deg2rad)
    z_gei_app = y_ecl_app * np.sin(oblt * deg2rad) + z_ecl_app * np.cos(oblt * deg2rad)

    # Prepare output
    # d2r = deg2rad if radian else 1.0
    # r2d = 1 / deg2rad if radian else 1.0
    # a2k = 1.0 if not aufl else au

    out = {
        'JD': jd,
        'year': yr,
        'month': mo,
        'day': dy,
        'UT_hrs': ut,
        'tdt_hrs': tdt,
        'gmst_hrs': gmst/15.0,
        'sslon_geo': sslon,   # * d2r
        'sslat_geo': sslat,   # * d2r
        'ra_app': ra,   # * r2d
        'dec_app':dec,  # * r2d
        'ecl_lon':lambda_sun,  # * d2r
        'ecl_lat':beta,    # * d2r
        'x_gei2000': x_gei2000, # * a2k
        'y_gei2000': y_gei2000, # * a2k
        'z_gei2000': z_gei2000, # * a2k
        'x_gei_app': [x_gei_app, y_gei_app, z_gei_app], # * a2k
        'r_sun': r_sun_au   # * a2k
    }
    
    return out




# def regfal(funcname, a_in, b_in, tol=1e-5, nmax=200):
#     np = n_params(0)  # This should be fixable
#     if np < 5:
#         nmax = 200
#     if np < 4:
#         tol = 1e-5
#     if np < 3:
#         print("REGFAL error: too few parameters.")
#         return 0

#     a = min([a_in, b_in])
#     b = max([a_in, b_in])
#     if a == b:
#         print("REGFAL error: zero width domain.")
#         return 0

#     fa = call_function(funcname, a) ### These will require bespoke calls
#     if fa == 0:
#         return a
#     fb = call_function(funcname, b)
#     if fb == 0:
#         return b

#     # Initialize previous x-value to a bogus value
#     xl = 1e38

#     # Iterate toward a solution
#     for i in range(nmax):
#         xn = (a * fb - b * fa) / (fb - fa)
#         fn = call_function(funcname, xn)

#         if abs(xl - xn) <= tol:
#             return xn
#         else:
#             xl = xn

#         if fa * fn <= 0.:
#             b = xn
#             fb = fn
#         else:
#             a = xn
#             fa = fn

#     print("REGFAL warning: Maximum number of iterations completed.")
#     return xn


# def sg_tphfunc(theta):
#     tanpthpar = {'b': 0.0, 'm': 0.0, 'ae': 0.0, 'be': 0.0, 'zmin': 0.0}
#     b, m, ae, be, zmin = tanpthpar['b'], tanpthpar['m'], tanpthpar['ae'], tanpthpar['be'], tanpthpar['zmin']

#     c = np.cos(theta)
#     s = np.sin(theta)
#     psi = np.arctan2(be * s, ae * c)
#     re = np.sqrt(be**2 + (ae**2 - be**2) * np.sin(psi)**2)

#     return b - (re + zmin) * (s - m * c)

# def sg_tphfunc2(theta):
#     tanpthpar = {'b': 0.0, 'm': 0.0, 'ae': 0.0, 'be': 0.0, 'zmin': 0.0}
#     b, m, ae, be, zmin = tanpthpar['b'], tanpthpar['m'], tanpthpar['ae'], tanpthpar['be'], tanpthpar['zmin']

#     c = np.cos(theta)
#     s = np.sin(theta)
#     psi = np.arctan2(be * s, ae * c)
#     re = np.sqrt(be**2 + (ae**2 - be**2) * np.sin(psi)**2)

#     return b - (re + zmin) * c








"""
; NAME: GEOCGEOD.PRO
;
; LOCATION IN LIBRARY:
;
; TYPE:
;
; PURPOSE:     Convert the geocentriclatitude in degrees to geodetic latitude
;
; CATEGORY:
;
; CALLING SEQUENCE:    geodetic_lat = geocgeod( geoc_lat_deg, r_geoc, almanac=flag )
;
; INPUT ARGUMENTS: Variable Name         Type                    Description
; 		If only one parameter, assume geocentric lat is
; 		given for earth surface (ref geoid); if two pars,
; 		second parameter is radial distance
;
; OUTPUTS: Variable Name         Type                    Description
;
; INPUT KEYWORDS:
; 		almanac		Choose iteration or simple calculation method
;
; OUTPUT KEYWORDS:
;
; COMMON BLOCKS:
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
;		Version 1.0: Scott Alan Budzien, NRL Code 7607, 03/16/1998
"""
def geocgeod(geoc_lat_deg, r_geoc=None, almanac=False):
    d_pi = 3.14159265358979
    th = np.double(geoc_lat_deg) * d_pi / 180.0

    a_e = refgeoid(0)
    b_e = refgeoid(90)
    flag=0 
    
    # If only one parameter, assume geocentric lat is
    # given for the earth's surface (reference geoid).
    if r_geoc is None:
        r_geoc = refgeoid(geoc_lat_deg)
    else:
        # If height other than the surface was given, use the iteration method.
        flag = 1

    # Choose iteration or simple calculation method
    if flag > 0 or almanac is True:
        f = (1.0 - b_e / a_e)
        e2 = 2 * f - f**2
        r = np.cos(th) * r_geoc
        z = np.sin(th) * r_geoc
        phinew = np.arctan2(z, r)

        # Iteration method
        while np.max(np.abs(phinew - np.arctan2(z + a_e * np.cos(phinew) * e2 * np.sin(phinew), r))) > 2e-6:
            phi = phinew
            sinphi = np.sin(phi)
            c = (1.0 - e2 * sinphi**2)**(-0.5)
            phinew = np.arctan2(z + a_e * c * e2 * sinphi, r)

        return phinew * 180.0 / d_pi
    else:
        # Simple calculation method
        tan_geod = a_e**2 / b_e**2 * np.tan(th)
        return np.arctan(tan_geod) * 180.0 / d_pi






def fjulian(iy, im, iday, help=False, mjd=False):
    """
    From Year, Month, and Day compute the floating-point Julian Day number.

    Parameters:
    - iy: Year (like 1987).
    - im: Month (like 7 for July).
    - id: Month day (like 23).
    - help: Optional keyword to display help information.
    - mjd: Optional keyword for calculating modified Julian date since 24400000.5.

    Returns:
    - jd: Julian Day number or Modified Julian Day number if mjd is True.
    """

    # Display help information
    if help or len([iy, im, iday]) < 3:
        print("From Year, Month, and Day compute floating-point Julian Day number.")
        print("jd = fjulian(y, m, d)")
        print("   y = Year (like 1987).")
        print("   m = Month (like 7 for July).")
        print("   d = Month day (like 23).")
        print("   /MJD = optional modified Julian date since 24400000.5")
        return -1

    # Parse parameters
    ny = len(np.atleast_1d(iy))
    nm = len(np.atleast_1d(im))
    nd = len(np.atleast_1d(iday))
    n = max([ny, nm, nd])

    if (ny != 1 and ny != n) or (nm != 1 and nm != n) or (nd != 1 and nd != n):
        print("Mismatched parameter array sizes.")
        return -1

    # Convert parameters and make sure they are either scalar or vector
    y = np.atleast_1d(iy).astype(int)
    m = np.atleast_1d(im).astype(int)
    d = np.atleast_1d(iday).astype(float)

    # Calculation
    jd = 367 * y - 7 * (y + (m + 9) // 12) // 4 - 3 * ((y + (m - 9) // 7) // 100 + 1) // 4 + 275 * m // 9 + d + 1721028.5

    # Modified Julian date option
    if mjd:
        jd -= 2400000.5

    return jd


