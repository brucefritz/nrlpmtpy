# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 23:39:16 2024

@author: bfritz
"""
import numpy as np
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import netCDF4
from astropy.time import Time
import astropy.time as apt

def tip_test_plot(df_10Hz, t1=0, t2=-1):
    
    fig, ax = plt.subplots(2, figsize=(6.5,8))
    residual = np.log10(df_10Hz['UV_CTS'] - df_10Hz['RD_CTS'])
    
    ax[0].scatter(df_10Hz['GPS_SEC'][t1:t2], df_10Hz['XIP1_SCAN_ANGLE'][t1:t2], 
                  c=np.log10(df_10Hz['UV_CTS'][t1:t2]), cmap='plasma')
    ax[1].scatter(df_10Hz['GPS_SEC'][t1:t2], df_10Hz['XIP1_SCAN_ANGLE'][t1:t2], 
                  c=np.log10(df_10Hz['RD_CTS'][t1:t2]))
    # ax[2].scatter(df_10Hz['GPS_SEC'], df_10Hz['XIP1_SCAN_ANGLE'], c=residual, cmap='plasma')
    # ax[2].scatter(df_10Hz['GPS_SEC'], df_10Hz['TIP1_SCAN_ANGLE'], c=np.log10(df_10Hz['DK_CTS']), cmap='plasma')
    
    
    # Details to make a map
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
    
    return 0

def mip_test_plot(df_10Hz, t1=0, t2=-1):
    fig, ax = plt.subplots(2, figsize=(6.5,8))
    gs = fig.add_gridspec(5, 3)
    
    mod_scan_angle = 45.0 - df_10Hz['XIP1_SCAN_ANGLE'][t1:t2]
    
    ax[0].scatter(df_10Hz['GPS_SEC'][t1:t2], mod_scan_angle, 
                  c=np.log10(df_10Hz['MG_CTS'][t1:t2]), cmap='magma')
    ax[1].scatter(df_10Hz['GPS_SEC'][t1:t2], mod_scan_angle, 
                  c=np.log10(df_10Hz['VK_CTS'][t1:t2]), cmap='cividis')
    
    return 0

def tip_test_nc_plot(f, filename, t1=0, t2=-1):
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
    
    return None

def main():
    ecl_dir = 'C:/data/ECLIPSE/flt/'
    # 
    """
    Eclipse
    """
    # ecl_file = 'eclipse_tip_disk_L1A_REV6055_20240408_190023_203321_v0.1'
    # ncpathfile = f'{ecl_dir}L1_CTIP/2404/{ecl_file}'
    # 
    # ecl_file = 'eclipse_tip_disk_L1A_REV5901_20240329_202632_215928_v0.1'
    ecl_file = 'eclipse_tip_disk_L1A_REV5902_20240329_215928_233224_v0.1'
    ncpathfile = f'{ecl_dir}L1_CTIP/2403/{ecl_file}'
    # 
    # ecl_file = 'eclipse_tip_disk_L1A_REV1212_20230601_043057_060350_v0.1'
    # ncpathfile = f'{ecl_dir}L1_CTIP/2306/{ecl_file}'
    # 
    f = netCDF4.Dataset(ncpathfile)
    # 
    tip_test_nc_plot(f, ncpathfile, t1=30_000, t2=50_000) #
    # tip_test_nc_plot(f, ncpathfile, t1=15_000, t2=28_000) # eclipse time window
    # tip_test_nc_plot(f, ncpathfile, t1=34_000, t2=46_000) # For 23/06/01 0430 UT
    
    f.close()

    # 
if __name__ == "__main__":
    print(f"==== {__file__} ====")
    main()