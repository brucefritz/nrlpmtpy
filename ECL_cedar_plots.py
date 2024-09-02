# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 23:39:16 2024

@author: bfritz
"""
import csv
import numpy as np
import pandas as pd
import scipy.io as sio
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import netCDF4
import astropy.time as apt

def annularity_path_plot():
    totality_file = 'C:/data/ECLIPSE/20231014-eclipse_path.txt'
    with open(totality_file) as f:
        csv_dict = csv.DictReader(f, delimiter='\t')
        df = pd.DataFrame(csv_dict)
    
    idl_file1 = 'C:/data/ECLIPSE/flt/L1_CMIP/NRL_1729_2023287_ECLIPSE_CMIP_REV3312_vg.sav'
    idl_file2 = 'C:/data/ECLIPSE/flt/L1_CMIP/NRL_1729_2023287_ECLIPSE_CMIP_REV3313_vg.sav'
    idl_file3 = 'C:/data/ECLIPSE/flt/L1_CMIP/NRL_1729_2023287_ECLIPSE_CMIP_REV3314_vg.sav'
    
    idat1 = pd.DataFrame(sio.readsav(idl_file1, python_dict=True))
    idat2 = pd.DataFrame(sio.readsav(idl_file2, python_dict=True))
    idat3 = pd.DataFrame(sio.readsav(idl_file3, python_dict=True))
    
    fig = plt.figure(figsize=(8,8))
    fig.suptitle(f'\nECLIPSE (ISS) Trajectory vs. Annularity\n2024-10-14\n ') 
    gs = fig.add_gridspec(7, 3)
    
    ax1 = fig.add_subplot(gs[0:3, :], projection=ccrs.PlateCarree()) # central_longitude=clon
    # ax1.set_extent([clon-180, clon+180, -50, 50], crs=ccrs.PlateCarree())
    ax1.add_feature(cfeature.COASTLINE, linewidth=1.5, edgecolor='black')
    ax1.add_feature(cfeature.BORDERS, linestyle='-', linewidth=1, edgecolor='black')
    ax1.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
    ax1.gridlines(draw_labels=True, linewidth=0.5, color='gray', linestyle='--')
    
    t1 = 0
    t2 = -1
    ax1.plot(np.float32(df['LON'][t1:t2]), np.float32(df['LAT'][t1:t2]), label='Annularity',
              c='k', transform=ccrs.PlateCarree())
    idx1 =  4_000
    idx2 = 32_000
    ax1.plot(idat1.iss_lon[idx1:idx2], idat1.iss_lat[idx1:idx2], label='ISS Pass 1 (before)',
              c='r', transform=ccrs.PlateCarree())
    jdx1 =  6_000
    jdx2 = 35_000
    ax1.plot(idat2.iss_lon[jdx1:jdx2], idat2.iss_lat[jdx1:jdx2], label='ISS Pass 2 (during)',
              c='b', transform=ccrs.PlateCarree())
    kdx1 =  9_000
    kdx2 = 37_000
    ax1.plot(idat3.iss_lon[kdx1:kdx2], idat3.iss_lat[kdx1:kdx2], label='ISS Pass 3 (after)',
              c='g', transform=ccrs.PlateCarree())
    ax1.legend(loc=3, fontsize='small')
    
def totality_path_plot():
    totality_file = 'C:/data/ECLIPSE/20240408-eclipse_path.txt'
    with open(totality_file) as f:
        csv_dict = csv.DictReader(f, delimiter='\t')
        df = pd.DataFrame(csv_dict)
    
    idl_file1 = 'C:/data/ECLIPSE/flt/L1_CTIP/NRL_1729_2024099_ECLIPSE_CTIP_REV6055_vg.sav'
    idl_file2 = 'C:/data/ECLIPSE/flt/L1_CTIP/NRL_1729_2024099_ECLIPSE_CTIP_REV6056_vg.sav'
    
    idat1 = pd.DataFrame(sio.readsav(idl_file1, python_dict=True))
    idat2 = pd.DataFrame(sio.readsav(idl_file2, python_dict=True))
    
    fig = plt.figure(figsize=(8,8))
    fig.suptitle(f'\nECLIPSE (ISS) Trajectory vs. Totality\n2024-04-08\n ') 
    gs = fig.add_gridspec(7, 3)
    
    ax1 = fig.add_subplot(gs[0:3, :], projection=ccrs.PlateCarree()) # central_longitude=clon
    # ax1.set_extent([clon-180, clon+180, -50, 50], crs=ccrs.PlateCarree())
    ax1.add_feature(cfeature.COASTLINE, linewidth=1.5, edgecolor='black')
    ax1.add_feature(cfeature.BORDERS, linestyle='-', linewidth=1, edgecolor='black')
    ax1.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
    ax1.gridlines(draw_labels=True, linewidth=0.5, color='gray', linestyle='--')
    
    ax1.plot(np.float32(df['Lon'][29:94]), np.float32(df['Lat'][29:94]), label='Totality',
              c='k', transform=ccrs.PlateCarree())
    idx1 = 13_000
    idx2 = 26_000
    ax1.plot(idat1.iss_lon[idx1:idx2], idat1.iss_lat[idx1:idx2], label='ISS Pass 1 (during)',
              c='r', transform=ccrs.PlateCarree())
    jdx1 = 13_000
    jdx2 = 28_000
    ax1.plot(idat2.iss_lon[jdx1:jdx2], idat2.iss_lat[jdx1:jdx2], label='ISS Pass 2 (after)', 
              c='b', transform=ccrs.PlateCarree())
    ax1.legend(loc=3, fontsize='small')
    
def tip_single_orbit_nc_plot(ncfile, ifile, t1=0, t2=-1):
    print(f'Loading {ifile}')
    idat = pd.DataFrame(sio.readsav(ifile, python_dict=True))
    print(f'Loading {ncfile}')
    f = netCDF4.Dataset(ncfile)
    
    df10 = pd.DataFrame()
    df10['GPS_SEC'] = f['GPS_SEC_10Hz'][t1:t2]
    df10['UV_CTS'] = f['TIP_UV_10Hz'][t1:t2]
    df10['RD_CTS'] = f['TIP_RED_10Hz'][t1:t2]
    df10['SUVM_ANGLE'] = f['SCAN_ANGLE_10Hz'][t1:t2]
    df10.reset_index(inplace=True, drop=True)
    
    plot_time  = df10['GPS_SEC']
    scan_angle = df10['SUVM_ANGLE']
    
    idat = idat[t1:t2]
    idat.reset_index(inplace=True, drop=True)
    
    with np.errstate(divide='ignore'):
        uv_cts  = [np.log10(int(x) + 0.2) for x in np.array(df10['UV_CTS'])]
        rd_cts  = [np.log10(int(x) + 0.1) for x in np.array(df10['RD_CTS'])]
    
    ch1_label = 'UV Counts'
    ch2_label = 'Red Counts'
    
    iso_t1 = apt.Time(int(plot_time[0]), format='gps')
    
    fig = plt.figure(figsize=(8,8))
    # fig, ax = plt.subplots(figsize=(12.5, 8))
    fig.suptitle(f'\nECLIPSE Tri-TIP\nBegin {iso_t1.fits} UTC\n') 
    gs = fig.add_gridspec(7, 3)
    
    # symsize=30
    totality_file = 'C:/data/ECLIPSE/20240408-eclipse_path.txt'
    with open(totality_file) as f:
        csv_dict = csv.DictReader(f, delimiter='\t')
        df = pd.DataFrame(csv_dict)
    
    ax1 = fig.add_subplot(gs[0:3, :], projection=ccrs.PlateCarree()) # central_longitude=clon
    ax1.add_feature(cfeature.COASTLINE, linewidth=1.5, edgecolor='black')
    ax1.add_feature(cfeature.BORDERS, linestyle='-', linewidth=1, edgecolor='black')
    ax1.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
    ax1.gridlines(draw_labels=True, linewidth=0.5, color='gray', linestyle='--')
    
    ax1.plot(np.float32(df['Lon'][29:94]), np.float32(df['Lat'][29:94]), label='Totality',
              c='k', transform=ccrs.PlateCarree())
    
    ax1.scatter(idat.tpt_lon, idat.tpt_lat, c=uv_cts, cmap='plasma', 
                  label=ch1_label)
    ax1.set(ylabel='Scan Angle [deg.]', xlabel='GPS Seconds')
    ax1.legend(loc=2)
    
    # ax[1].scatter(plot_time, scan_angle, c=rd_cts, cmap='plasma', 
    #               label=ch2_label, s=symsize, marker='_')
    # ax[1].set(ylabel='Scan Angle [deg.]', xlabel='GPS Seconds')
    # ax[1].legend(loc=2)
    


def gold_test_plot(g, filename):
    # 
    # print(np.array(g['WAVELENGTH'][25,25,160]))
    
    # plt.plot(np.array(g['RADIANCE'][25,25,:]))
    plt.scatter(np.array(g['GRID_EW']), np.array(g['GRID_NS']), c=np.array(g['RADIANCE'][:,:,160]))
    # plt.scatter(np.array(g['REFERENCE_POINT_LON']), np.array(g['REFERENCE_POINT_LAT']), 
    #             c=np.array(g['RADIANCE'][:,:,160]))
    
    return None

def gold_eclipse_combo_plot(f, gA, gB, ffilename, gfilename, t1=0, t2=-1):
    # 
    tgps    = [int(x) for x in np.array(f['GPS_SEC_10Hz'][t1:t2])]
    # angle   = [float(x) for x in np.array(f['SCAN_ANGLE_10Hz'][t1:t2])]
    with np.errstate(divide='ignore'):
        uv_cts  = [int(x) + 0.2 for x in np.array(f['TIP_UV_10Hz'][t1:t2])]
        rd_cts  = [int(x) + 0.1 for x in np.array(f['TIP_RED_10Hz'][t1:t2])]
        # uv_cts  = [np.log10(int(x)) for x in np.array(f['TIP_UV_10Hz'][t1:t2])]
        # rd_cts  = [np.log10(int(x)) for x in np.array(f['TIP_RED_10Hz'][t1:t2])]
        tot_cts = [x - y for x,y in zip(uv_cts, rd_cts)]
    iss_lat = [float(x) for x in np.array(f['Geo_Lat_10Hz'][t1:t2])]
    iss_lon = [float(x) for x in np.array(f['Geo_Lon_10Hz'][t1:t2])]
    tp_lat = [float(x) for x in np.array(f['Tan_Pt_Lat_10Hz'][t1:t2])]
    tp_lon = [float(x) for x in np.array(f['Tan_Pt_Lon_10Hz'][t1:t2])]
    
    """
    GOLD 2023_121_23_10 use Channel 105 
    GOLD 2023_121_22_52 CHA use Channel 105  
    GOLD 2023_121_22_52 CHB use Channel 160
    """
    wl_channel_A = 105
    wl_channel_B = 160
    gewA = np.array(gA['REFERENCE_POINT_LON'])
    gewA = gewA[~np.isnan(gewA)] * 1e5
    gewB = np.array(gB['REFERENCE_POINT_LON'])
    gewB = gewB[~np.isnan(gewB)] * 1e5
    # print(gew)
    gnsA = np.array(gA['REFERENCE_POINT_LAT'])
    gnsA = gnsA[~np.isnan(gnsA)] * 1e5
    gnsB = np.array(gB['REFERENCE_POINT_LAT'])
    gnsB = gnsB[~np.isnan(gnsB)] * 1e5
    gradA = np.array(gA['RADIANCE'][:,:,wl_channel_A])
    gradA = np.log10(gradA[~np.isnan(gradA)])
    gradB = np.array(gB['RADIANCE'][:,:,wl_channel_B])
    gradB = np.log10(gradB[~np.isnan(gradB)])
    gwlA = gA['WAVELENGTH'][:,:,wl_channel_A]
    gwlA = gwlA[~np.isnan(gwlA)]
    gwlB = gB['WAVELENGTH'][:,:,wl_channel_B]
    gwlB = gwlB[~np.isnan(gwlB)]
    print(gwlA)
    print(gwlB)
    
    fig = plt.figure(figsize=(8,8))
    gs = fig.add_gridspec(3, 3)
    ax1 = fig.add_subplot(gs[0:3, :], projection=ccrs.Orthographic()) # central_longitude=clon
    ax1.add_feature(cfeature.COASTLINE, linewidth=1.5, edgecolor='black')
    ax1.add_feature(cfeature.BORDERS, linestyle='-', linewidth=1, edgecolor='black')
    ax1.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
    ax1.gridlines(draw_labels=True, linewidth=0.5, color='gray', linestyle='--')
    
    ax1.scatter(gewA, gnsA, c=gradA, marker='s', s=15, transform=ccrs.Orthographic())
    ax1.scatter(gewB, gnsB, c=gradB, marker='s', s=15, transform=ccrs.Orthographic())
    ax1.scatter(tp_lon, tp_lat, c=tot_cts, cmap='plasma',  marker='_', s=8,
                transform=ccrs.PlateCarree())
    
    return None




def eclipse_idl_vg_mip_annular(flist):
    fig = plt.figure(figsize=(8,8))
    gs = fig.add_gridspec(3, 3)
    ax1 = fig.add_subplot(gs[:, :], projection=ccrs.PlateCarree()) # central_longitude=clon
    ax1.add_feature(cfeature.COASTLINE, linewidth=1.5, edgecolor='black')
    ax1.add_feature(cfeature.BORDERS, linestyle='-', linewidth=1, edgecolor='black')
    ax1.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
    ax1.gridlines(draw_labels=True, linewidth=0.5, color='gray', linestyle='--')
    t1=0
    t2=-1
    vg_list = [
        'C:/data/ECLIPSE/flt/L1_CMIP/NRL_1729_2023287_ECLIPSE_CMIP_REV3312_vg.sav',
        'C:/data/ECLIPSE/flt/L1_CMIP/NRL_1729_2023287_ECLIPSE_CMIP_REV3313_vg.sav']
        # 'C:/data/ECLIPSE/flt/L1_CMIP/NRL_1729_2023287_ECLIPSE_CMIP_REV3314_vg.sav']
    for i,fname in enumerate(flist[0:2]):
        print(f'Loading {fname}')
        f = netCDF4.Dataset(fname)
        
        df1 = pd.DataFrame()
        df10 = pd.DataFrame()
        
        df1['GPS_SEC'] = f['GPS_SEC_1Hz'][:]
        df1['MG_CTS']  = f['MIP_MG_1Hz'][:]
        
        # df1 = df1[df1['MG_CTS'] > 100]
        # df1.reset_index(inplace=True, drop=True)
        
        df10['GPS_SEC'] = f['GPS_SEC_10Hz'][:]
        df10['MG_CTS'] = f['MIP_MG_10Hz'][:]
        df10['VK_CTS'] = f['MIP_VK_10Hz'][:]
        df10['DK_CTS'] = f['MIP_DARK_10Hz'][:]
        df10['TP_LAT'] = f['Tan_Pt_Lat_10Hz'][:]
        df10['TP_LON'] = f['Tan_Pt_Lon_10Hz'][:]
        
        idl_dat = sio.readsav(vg_list[i], python_dict=True)
        
        df10['vg_lat'] = idl_dat['tpt_lat']
        df10['vg_lon'] = idl_dat['tpt_lon']
        
        # df10 = df10[(df10['GPS_SEC'] > df1['GPS_SEC'][0]) & (df10['GPS_SEC'] < max(df1['GPS_SEC']))]
        df10[df10['MG_CTS'] > 1e10] = 0
        # df10.reset_index(inplace=True, drop=True)
        
        # plt.plot(df10['MG_CTS'])
        
        
        f.close()
        
        with np.errstate(divide='ignore'):
            mg_cts  = [int(x) + 0.2 for x in np.array(df10['MG_CTS'])]
       
        m = ax1.scatter(df10['vg_lon'][0:35_000], df10['vg_lat'][0:35_000], c=mg_cts[0:35_000], 
                        cmap='plasma', s=15, marker='d', transform=ccrs.PlateCarree())
    ax1.set_extent([-180, 0, -60,+60], crs=ccrs.PlateCarree())
    

def main():
    """
    Orbit track plots
    """
    # annularity_path_plot()
    # totality_path_plot()
    """
    Eclipse
    """
    ifile = 'C:/data/ECLIPSE/flt/L1_CTIP/NRL_1729_2024099_ECLIPSE_CTIP_REV6055_vg.sav'
    ncfile= 'C:/data/ECLIPSE/flt/L1_CTIP/2404/eclipse_tip_disk_L1A_REV6055_20240408_190023_203321_v0.1.nc'
    # tip_single_orbit_nc_plot(ncfile, ifile, t1=15_000, t2=28_000)
    
    
    
    
    
    ecl_root = 'C:/data/ECLIPSE/flt/'
    # 
    ecl_file = 'eclipse_tip_disk_L1A_REV0744_20230501_233004_010259_v0.1.nc'
    # ecl_file = 'eclipse_tip_disk_L1A_REV0744_20230501_233004_010259_v0.1.nc'
    # ncpathfile = f'{ecl_root}{ecl_sub}{ecl_file}'
    
    
    
    
    # ecl_file = 'eclipse_tip_disk_L1A_REV6055_20240408_190023_203321_v0.1'
    # ncpathfile = f'{ecl_dir}L1_CTIP/2404/{ecl_file}'
    # 
    # ecl_file = 'eclipse_tip_disk_L1A_REV5901_20240329_202632_215928_v0.1'
    # ecl_file = 'eclipse_tip_disk_L1A_REV5902_20240329_215928_233224_v0.1'
    # ncpathfile = f'{ecl_dir}L1_CTIP/2403/{ecl_file}'
    # 
    # ecl_file = 'eclipse_tip_disk_L1A_REV1212_20230601_043057_060350_v0.1'
    # ncpathfile = f'{ecl_dir}L1_CTIP/2306/{ecl_file}'
    # 
    # gA = netCDF4.Dataset(gold_nc_file_A)
    # gB = netCDF4.Dataset(gold_nc_file_B)
    # f = netCDF4.Dataset(ncpathfile)
    # 
    # tip_test_nc_plot(f, ncpathfile, t1=30_000, t2=50_000) #
    # tip_test_nc_plot(f, ncpathfile, t1=15_000, t2=28_000) # eclipse time window
    # tip_test_nc_plot(f, ncpathfile, t1=34_000, t2=46_000) # For 23/06/01 0430 UT
    
    # gold_test_plot(g, gold_nc_file)
    # gold_eclipse_combo_plot(f, gA, gB, ecl_file, gold_nc_file_A, t1=30_000, t2=50_000)
        
    # f.close()
    # gA.close()
    # gB.close()
    
    # Test plot early orbit activity
    # ecl_sub = 'L1_CTIP/2402/'
    # multiple_ctip_names = [
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV0740_20230501_171827_185121_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV0741_20230501_185121_202415_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV0742_20230501_202415_215710_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV0743_20230501_215710_233004_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV0744_20230501_233004_010259_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV0745_20230502_010259_023553_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV0746_20230502_023553_040848_v0.1.nc'
    #     ]
    
    ecl_sub = 'L1_CTIP/2402/'
    # multiple_ctip_names = [
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5362_20240224_011821_025114_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5363_20240224_025114_042406_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5365_20240224_055659_072952_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5366_20240224_072952_090244_v0.1.nc'
    #     ]
    multiple_ctip_names = [
        f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5383_20240225_094847_112140_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5384_20240225_112140_125432_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5385_20240225_125432_142725_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5386_20240225_142725_160017_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5387_20240225_160017_173310_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5388_20240225_173310_190603_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5389_20240225_190603_203855_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5390_20240225_203855_221148_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5391_20240225_221148_234440_v0.1.nc', # ! REV 5392 bad data
        f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5393_20240226_011929_025225_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5394_20240226_025225_042521_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5395_20240226_042521_055816_v0.1.nc', # ! REV 5396 bad data
        f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5397_20240226_073114_090410_v0.1.nc'
        ]
    
    # Almost full day on 2024/02/27 (REV 5407 - 5422, DOY 58)
    # ecl_sub = 'L1_CTIP/2402/'
    # multiple_ctip_names = [
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5408_20240227_003331_020627_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5409_20240227_020627_033923_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5410_20240227_033923_051220_v0.1.nc',
    #     # f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5411_20240227_051220_064516_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5412_20240227_064516_081812_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5413_20240227_081812_095108_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5414_20240227_095108_112404_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5415_20240227_112404_125700_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5416_20240227_125700_142956_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5417_20240227_142956_160252_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5418_20240227_160252_173548_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5419_20240227_173548_190844_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5420_20240227_190844_204141_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5421_20240227_204141_221437_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5422_20240227_221437_234733_v0.1.nc'
    #     ]
    # eclipse_multi_orbit_tip_plot(multiple_ctip_names)
    
    # ecl_sub = 'L1_CMIP/2402/'
    # multiple_cmip_names = [
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5408_20240227_003331_020627_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5409_20240227_020627_033923_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5410_20240227_033923_051220_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5411_20240227_051220_064516_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5412_20240227_064516_081812_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5413_20240227_081812_095108_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5414_20240227_095108_112404_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5415_20240227_112404_125700_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5416_20240227_125700_142956_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5417_20240227_142956_160252_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5418_20240227_160252_173548_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5419_20240227_173548_190844_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5420_20240227_190844_204141_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5421_20240227_204141_221437_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5422_20240227_221437_234733_v0.1.nc'
    #     ]
    ecl_sub = 'L1_CMIP/2310/'
    multiple_cmip_names = [
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV3312_20231014_173331_190631_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV3313_20231014_190631_203932_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV3314_20231014_203932_221232_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV3315_20231014_221232_234532_v0.1.nc',
        ]
    eclipse_idl_vg_mip_annular(multiple_cmip_names)    
    # # 
    
    # tip_test_file = f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5393_20240226_011929_025225_v0.1.nc'
    # eclipse_idl_comp(tip_test_file)
    
    
if __name__ == "__main__":
    print(f"==== {__file__} ====")
    main()