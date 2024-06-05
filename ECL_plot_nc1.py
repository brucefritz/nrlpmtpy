# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 23:39:16 2024

@author: bfritz
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import netCDF4
import astropy.time as apt

def xip_single_orbit_plot(df_10Hz, t1=0, t2=-1, unit=None, save=''):
    iso_t1 = apt.Time(int(df_10Hz['GPS_SEC'][t1]), format='gps')
    if t2 < 0:
        iso_t2 = apt.Time(int(max(df_10Hz['GPS_SEC'])), format='gps')
    else:
        iso_t2 = apt.Time(int(df_10Hz['GPS_SEC'][t2]), format='gps')
    # 
    if unit is None:
        print('No unit selected, exiting plot routine')
        return
    plot_time = df_10Hz['GPS_SEC'][t1:t2]
    if unit[8:11] == 'TIP':
        ch1_data = np.log10(df_10Hz['UV_CTS'][t1:t2])
        ch1_label = 'UV'
        ch2_data = np.log10(df_10Hz['RD_CTS'][t1:t2])
        ch2_label = 'Red'
        ch3_data = np.log10(df_10Hz['DK_CTS'][t1:t2])
        ch3_label = 'Dark'
        scan_angle = df_10Hz['XIP1_SCAN_ANGLE'][t1:t2]
    # 
    if unit[8:11] == 'MIP':
        ch1_data = np.log10(df_10Hz['MG_CTS'][t1:t2])
        ch1_label = 'Mg+'
        ch2_data = np.log10(df_10Hz['VK_CTS'][t1:t2])
        ch2_label = 'VK'
        ch3_data = np.log10(df_10Hz['DK_CTS'][t1:t2])
        ch3_label = 'Dark'
        scan_angle = 45.0 - df_10Hz['XIP1_SCAN_ANGLE'][t1:t2]
    symsize = 20
    if unit[0:3] == 'ALS': symsize = 45
    
    # 
    fig, ax = plt.subplots(3, figsize=(12.5, 8))
    fig.suptitle(f'\nECLIPSE {unit}\nBegin {iso_t1.fits} UTC\n  End {iso_t2.fits} UTC\n') 
    # 
    try:
        ax[0].scatter(plot_time, scan_angle, c=ch1_data, cmap='plasma', 
                      label=ch1_label, s=symsize, marker='_')
        ax[0].set(ylabel='Scan Angle [deg.]', xlabel='GPS Seconds')
        ax[0].legend(loc=2)
    except:
        print(f'Not enough Ch1 Data in {save}')
    # 
    try:
        ax[1].scatter(plot_time, scan_angle, c=ch2_data, cmap='magma',
                      label=ch2_label, s=symsize, marker='_')
        ax[1].set(ylabel='Scan Angle [deg.]', xlabel='GPS Seconds')
        ax[1].legend(loc=2)
    except:
        print(f'Not enough Ch2 Data in {save}')
    # 
    try:
        ax[2].scatter(plot_time, scan_angle, c=ch3_data, label=ch3_label,
                      s=symsize, marker='_')
        ax[2].set(ylabel='Scan Angle [deg.]', xlabel='GPS Seconds')
        ax[2].legend(loc=2)
    except:
        print(f'Not enough Ch3 Data in {save}')
    # 
    if len(save) > 0:
        print(f'Saving file: \n ... {save}')
        fig.savefig(f'{save}.png')    
    return 0

def tip_test_nc_plot(f, filename, t1=0, t2=-1, unit=None):
    print(f'Plotting {filename}')
    
    tgps    = [int(x) for x in np.array(f['GPS_SEC_10Hz'][t1:t2])]
    # angle   = [float(x) for x in np.array(f['SCAN_ANGLE_10Hz'][t1:t2])]
    with np.errstate(divide='ignore'):
        # uv_cts  = [int(x) for x in np.array(f['TIP_UV_10Hz'][t1:t2])]
        # rd_cts  = [int(x) for x in np.array(f['TIP_RED_10Hz'][t1:t2])]
        uv_cts  = [np.log10(int(x)) for x in np.array(f['TIP_UV_10Hz'][t1:t2])]
        rd_cts  = [np.log10(int(x)) for x in np.array(f['TIP_RED_10Hz'][t1:t2])]
        tot_cts = [x - y for x,y in 
                    zip(np.array(f['TIP_UV_10Hz'][t1:t2]),np.array(f['TIP_RED_10Hz'][t1:t2]))]
    iss_lat = [float(x) for x in np.array(f['Geo_Lat_10Hz'][t1:t2])]
    iss_lon = [float(x) for x in np.array(f['Geo_Lon_10Hz'][t1:t2])]
    tp_lat = [float(x) for x in np.array(f['Tan_Pt_Lat_10Hz'][t1:t2])]
    tp_lon = [float(x) for x in np.array(f['Tan_Pt_Lon_10Hz'][t1:t2])]
    
    iso_t = apt.Time(int(tgps[0]), format='gps')
    
    # fig, ax = plt.subplots(2, figsize=(6.5,8))
    # ax[0].scatter(tgps, angle, c=uv_cts, cmap='plasma')
    # ax[1].scatter(tgps, angle, c=rd_cts)
    
    fig = plt.figure(figsize=(8,8))
    fig.suptitle(f'\nECLIPSE Tri-TIP\n{iso_t.fits} UTC\n ') 
    gs = fig.add_gridspec(7, 3)
    
    # ax = fig.add_subplot(1,1,1, projection=ccrs.PlateCarree(central_longitude=180))
    # ax.scatter(iss_lon, iss_lat, c=uv_cts, cmap='plasma', s=4)
    clon = np.median(iss_lon)
    
    ax1 = fig.add_subplot(gs[0:3, :], projection=ccrs.PlateCarree(central_longitude=clon))
    # ax1.set_extent([clon-180, clon+180, -50, 50], crs=ccrs.PlateCarree())
    ax1.add_feature(cfeature.COASTLINE, linewidth=1.5, edgecolor='black')
    ax1.add_feature(cfeature.BORDERS, linestyle='-', linewidth=1, edgecolor='black')
    ax1.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
    ax1.gridlines(draw_labels=True, linewidth=0.5, color='gray', linestyle='--')
    # ax1.set_xlabel('')
    
    ax1.scatter(tp_lon, tp_lat, c=tot_cts, cmap='plasma', transform=ccrs.PlateCarree())
    # ax1.scatter(tp_lon, tp_lat, c=uv_cts, cmap='plasma', transform=ccrs.PlateCarree())
    
    # ax2 = fig.add_subplot(gs[4:, :], projection=ccrs.PlateCarree(central_longitude=clon))
    # ax2.add_feature(cfeature.COASTLINE, linewidth=1.5, edgecolor='black')
    # ax2.add_feature(cfeature.BORDERS, linestyle='-', linewidth=1, edgecolor='black')
    # ax2.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
    # ax2.gridlines(draw_labels=True, linewidth=0.5, color='gray', linestyle='--')
    
    # ax2.scatter(tp_lon, tp_lat, c=rd_cts, transform=ccrs.PlateCarree())
    
    """
    Totality Path Plot
    """
    # totality_file = 'C:/data/ECLIPSE/20240408-eclipse_path.txt'
    # with open(totality_file) as f:
    #     csv_dict = csv.DictReader(f, delimiter='\t')
    #     df = pd.DataFrame(csv_dict)
    
    # ax1.plot(np.float32(df['Lon'][29:94]), np.float32(df['Lat'][29:94]), 
    #           c='k', transform=ccrs.PlateCarree())
    # ax2.plot(np.float32(df['Lon'][29:94]), np.float32(df['Lat'][29:94]), 
    #           c='k', transform=ccrs.PlateCarree())
    
    
    
    # Leftover --- Details to make a map
    # ax = fig.add_subplot(gs[0:3, :], projection=ccrs.PlateCarree()) # central_longitude=clon
    # ax.set_extent([-70, -20, -20,+40], crs=ccrs.PlateCarree())
    # ax.add_feature(cfeature.COASTLINE, linewidth=1.5, edgecolor='black')
    # ax.add_feature(cfeature.BORDERS, linestyle='-', linewidth=1, edgecolor='black')
    # ax.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
    # ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', linestyle='--')

    # ax.scatter(vg0['tp_lon'][500:1800], vg0['tp_lat'][500:1800], c=df_1Hz['UV_CTS'][500:1800], cmap='plasma', s=50)
    # ax = fig.add_subplot(1,1,1)
    # ax.scatter(vg1['tp_lon'], vg1['tp_lat'], c=df_10Hz['UV_CTS'], cmap='plasma', s=20)
    
    
    #### The most recent plot to go with the map detailed above
    # ax.scatter(vg0['tp_lon'], vg0['tp_lat'], c=df_1Hz['UV_CTS'],
    #            cmap='gnuplot', s=20, transform=ccrs.PlateCarree())
        
    # ax2 = fig.add_subplot(gs[3:5, :])
    # mg_target = ax2.scatter(vg0['tp_lon'][0:30], vg0['tp_lat'][0:30], c=df_1Hz['UV_CTS'][0:30], cmap='plasma', s=4)
    # ax2.set_xlabel('Tangent Point Longitude [deg.]')
    # ax2.set_ylabel('Tangent Point Altitude [km]')
    
    
    return None

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

def eclipse_multi_orbit_mip_plot(flist):
    fig = plt.figure(figsize=(8,8))
    gs = fig.add_gridspec(3, 3)
    ax1 = fig.add_subplot(gs[:, :], projection=ccrs.PlateCarree()) # central_longitude=clon
    ax1.add_feature(cfeature.COASTLINE, linewidth=1.5, edgecolor='black')
    ax1.add_feature(cfeature.BORDERS, linestyle='-', linewidth=1, edgecolor='black')
    ax1.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
    ax1.gridlines(draw_labels=True, linewidth=0.5, color='gray', linestyle='--')
    t1=0
    t2=-1
    for i,fname in enumerate(flist):
        print(f'Loading {fname}')
        f = netCDF4.Dataset(fname)
        
        df1 = pd.DataFrame()
        df10 = pd.DataFrame()
        
        df1['GPS_SEC'] = f['GPS_SEC_1Hz'][:]
        df1['MG_CTS']  = f['MIP_MG_1Hz'][:]
        
        df1 = df1[df1['MG_CTS'] > 200]
        df1.reset_index(inplace=True, drop=True)
        
        df10['GPS_SEC'] = f['GPS_SEC_10Hz'][:]
        df10['MG_CTS'] = f['MIP_MG_10Hz'][:]
        df10['VK_CTS'] = f['MIP_VK_10Hz'][:]
        df10['TP_LAT'] = f['Tan_Pt_Lat_10Hz'][:]
        df10['TP_LON'] = f['Tan_Pt_Lon_10Hz'][:]
        
        df10 = df10[(df10['GPS_SEC'] > df1['GPS_SEC'][0]) & (df10['GPS_SEC'] < max(df1['GPS_SEC']))]
        df10.reset_index(inplace=True, drop=True)
        
        tgps    = [int(x) for x in np.array(f['GPS_SEC_10Hz'][t1:t2])]
        # angle   = [float(x) for x in np.array(f['SCAN_ANGLE_10Hz'][t1:t2])]
        with np.errstate(divide='ignore'):
            mg_cts  = [np.log10(float(x) + 0.2) for x in np.array(df10['MG_CTS'])]
            vk_cts  = [int(x) + 0.1 for x in np.array(df10['VK_CTS'])]
            # uv_cts  = [np.log10(int(x)) for x in np.array(f['TIP_UV_10Hz'][t1:t2])]
            # rd_cts  = [np.log10(int(x)) for x in np.array(f['TIP_RED_10Hz'][t1:t2])]
            # tot_cts = [np.log10(x - y) for x,y in zip(uv_cts, rd_cts)]
            
        # iss_lat = [float(x) for x in np.array(f['Geo_Lat_10Hz'][t1:t2])]
        # iss_lon = [float(x) for x in np.array(f['Geo_Lon_10Hz'][t1:t2])]
        tp_lat = [float(x)*1e0 for x in np.array(df10['TP_LAT'])]
        tp_lon = [float(x)*1e0 for x in np.array(df10['TP_LON'])]
        
        m = ax1.scatter(tp_lon, tp_lat, c=mg_cts, cmap='plasma', s=15, marker='d',
                    transform=ccrs.PlateCarree())
        
        f.close()
        
    plt.colorbar(m, label='Counts (log 10)', orientation='horizontal')
    # ax1.set_extent([-120, 120, -45,+45], crs=ccrs.PlateCarree()) # 2023-05-01/02
    ax1.set_extent([-240, 0, -50,+50], crs=ccrs.PlateCarree())
    
    return None

def eclipse_multi_orbit_tip_plot(flist):
    fig = plt.figure(figsize=(8,8))
    gs = fig.add_gridspec(3, 3)
    ax1 = fig.add_subplot(gs[:, :], projection=ccrs.PlateCarree()) # central_longitude=clon
    ax1.add_feature(cfeature.COASTLINE, linewidth=1.5, edgecolor='black')
    ax1.add_feature(cfeature.BORDERS, linestyle='-', linewidth=1, edgecolor='black')
    ax1.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
    ax1.gridlines(draw_labels=True, linewidth=0.5, color='gray', linestyle='--')
    t1=0
    t2=-1
    for i,fname in enumerate(flist):
        print(f'Loading {fname}')
        f = netCDF4.Dataset(fname)
        
        df1 = pd.DataFrame()
        df10 = pd.DataFrame()
        
        df1['GPS_SEC'] = f['GPS_SEC_1Hz'][:]
        df1['UV_CTS']  = f['TIP_UV_1Hz'][:]
        
        df1 = df1[df1['UV_CTS'] > 1]
        df1.reset_index(inplace=True, drop=True)
        
        df10['GPS_SEC'] = f['GPS_SEC_10Hz'][:]
        df10['UV_CTS'] = f['TIP_UV_10Hz'][:]
        df10['RD_CTS'] = f['TIP_RED_10Hz'][:]
        # df10['ISS_LAT'] = f['TIP_UV_10Hz'][:]
        # df10['ISS_LON'] = f['TIP_UV_10Hz'][:]
        df10['TP_LAT'] = f['Tan_Pt_Lat_10Hz'][:]
        df10['TP_LON'] = f['Tan_Pt_Lon_10Hz'][:]
        
        df10 = df10[(df10['GPS_SEC'] > df1['GPS_SEC'][0]) & (df10['GPS_SEC'] < max(df1['GPS_SEC']))]
        df10.reset_index(inplace=True, drop=True)
        
        tgps    = [int(x) for x in np.array(f['GPS_SEC_10Hz'][t1:t2])]
        # angle   = [float(x) for x in np.array(f['SCAN_ANGLE_10Hz'][t1:t2])]
        with np.errstate(divide='ignore'):
            uv_cts  = [int(x) + 0.2 for x in np.array(df10['UV_CTS'])]
            rd_cts  = [int(x)*8 + 0.1 for x in np.array(df10['RD_CTS'])]
            # uv_cts  = [np.log10(int(x)) for x in np.array(f['TIP_UV_10Hz'][t1:t2])]
            # rd_cts  = [np.log10(int(x)) for x in np.array(f['TIP_RED_10Hz'][t1:t2])]
            tot_cts = [np.log10(x - y) for x,y in zip(uv_cts, rd_cts)]
            
        # iss_lat = [float(x) for x in np.array(f['Geo_Lat_10Hz'][t1:t2])]
        # iss_lon = [float(x) for x in np.array(f['Geo_Lon_10Hz'][t1:t2])]
        tp_lat = [float(x)*1e0 for x in np.array(df10['TP_LAT'])]
        tp_lon = [float(x)*1e0 for x in np.array(df10['TP_LON'])]
        
        m = ax1.scatter(tp_lon, tp_lat, c=tot_cts, cmap='plasma', s=15, marker='d',
                    transform=ccrs.PlateCarree())
        
        f.close()
        
    plt.colorbar(m, label='Counts (log 10)', orientation='horizontal')
    # ax1.set_extent([-120, 120, -45,+45], crs=ccrs.PlateCarree()) # 2023-05-01/02
    ax1.set_extent([-240, 0, -50,+50], crs=ccrs.PlateCarree())
    
    return None

def main():
    """
    GOLD Files
    """
    gdir = 'C:/data/GOLD/L1C_N1/'
    # gold_nc_file_A = f'{gdir}2023/306/GOLD_L1C_CHA_NI1_2023_306_21_52_v05_r01_c01.nc'
    # gold_nc_file_B = f'{gdir}2023/306/GOLD_L1C_CHA_NI1_2023_306_21_52_v05_r01_c01.nc'
    gold_nc_file_A = f'{gdir}2023/121/GOLD_L1C_CHA_NI1_2023_121_22_52_v05_r01_c01.nc'
    gold_nc_file_B = f'{gdir}2023/121/GOLD_L1C_CHB_NI1_2023_121_22_55_v05_r01_c01.nc'
    # gold_nc_file = f'{gdir}2023/121/GOLD_L1C_CHA_NI1_2023_121_23_10_v05_r01_c01.nc'
    """
    Eclipse
    """
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
    
    # ecl_sub = 'L1_CTIP/2402/'
    # multiple_ctip_names = [
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5362_20240224_011821_025114_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5363_20240224_025114_042406_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5365_20240224_055659_072952_v0.1.nc',
    #     f'{ecl_root}{ecl_sub}eclipse_tip_disk_L1A_REV5366_20240224_072952_090244_v0.1.nc'
    #     ]
    
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
    
    ecl_sub = 'L1_CMIP/2402/'
    multiple_cmip_names = [
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5408_20240227_003331_020627_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5409_20240227_020627_033923_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5410_20240227_033923_051220_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5411_20240227_051220_064516_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5412_20240227_064516_081812_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5413_20240227_081812_095108_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5414_20240227_095108_112404_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5415_20240227_112404_125700_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5416_20240227_125700_142956_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5417_20240227_142956_160252_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5418_20240227_160252_173548_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5419_20240227_173548_190844_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5420_20240227_190844_204141_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5421_20240227_204141_221437_v0.1.nc',
        f'{ecl_root}{ecl_sub}eclipse_mip_disk_L1A_REV5422_20240227_221437_234733_v0.1.nc'
        ]
    eclipse_multi_orbit_mip_plot(multiple_cmip_names)
    # 
if __name__ == "__main__":
    print(f"==== {__file__} ====")
    main()