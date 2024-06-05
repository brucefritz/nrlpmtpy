# -*- coding: utf-8 -*-
"""
Separate file to take care of book keeping for ECLIPSE L1A Files

Inputs:
    xip [STRING] - Either 'TIP' or 'MIP'
    outfilename [STRING]
    df_1Hz, df_10Hz - Pandas DataFrame with xip data
    vg0, vg1 - Pandas DataFrame with view geometry information

@author: bruce
"""
import netCDF4
import time

def generate_L1A_ncfile(xip, outfilename, df_1Hz, df_10Hz, vg0, vg1):
    if xip == 'MIP' or xip == 'TIP': 
        print(f'Making a {xip} file from {outfilename}')
    else:
        print('\n\n\n Not Valid XIP Type \n\n\n')
        return
    ncfile = netCDF4.Dataset(f'{outfilename}.nc', mode='w', format='NETCDF4')
    # 
    ncfile.createDimension('nRec1Hz',  len(df_1Hz))
    ncfile.createDimension('nRec10Hz', len(df_10Hz))
    ncfile.createDimension('nVec', 3)
    ncfile.createDimension('nQuat', 4)
    """
    Global Variables
    """
    ncfile.title = 'ECLIPSE'
    ncfile.source_name = 'ECL>ECLIPSE'
    ncfile.descriptor = 'Experiment for Characterizing the Lower Ionosphere & Prediction of Sporadic-E'
    ncfile.PI_name = 'Kenneth F. Dymond'
    ncfile.PI_affiliation = 'U.S. Naval Research Laboratory'
    ncfile.mission_group = 'DoD Space Test Program (STP)'
    ncfile.mission = 'STP-H9'
    ncfile.instrument_type = 'Imaging and Remote Sensing (ITM/Earth)'
    ncfile.discipline = 'Space Physics > Ionospheric Science'
    ncfile.time_resolution = '1 & 10 second'
    ncfile.data_type = "H0>Photometer_Counts"
    
    ncfile.generated_by = 'Bruce A. Fritz'
    ncfile.generation_date = time.asctime(time.localtime(time.time()))
    
    ncfile.logical_file_id = f"ECL_H0_{xip}_20220801_V01 [TBR]"
    ncfile.logical_source  = f"SLN_H0_{xip} [TBR]"
    ncfile.logical_source_description = f"Tri-{xip} Photometer Counts"
    ncfile.mods = "Initial Release"

    # eclipse_rr_text = ["See Nicholas et al. (2019) for Tri-MIP description,", $
    #                   " https://doi.org/10.1117/12.2594905"]
    # ACK_TEXT   = "[TBR] Tri-MIP is funded by the DARPA, data archival is supported by the Chief of Naval Research"
    # RULES_TEXT = "[TBR] Contact the author for more details" 
    
    # ncfile.text = eclipse_rr_text
    # ncfile.project = "SPDS>Space Physics Data System"
    # ;; See ISTP exchangeable data products for more info
    # ;; Additional optional Global attributes .... see https://spdf.gsfc.nasa.gov/istp_guide/gattributes.html
    # ncfile.acknowledgement = ACK_TEXT
    # ncfile.rules_of_use = RULES_TEXT
    # ncfile.doi = "DOI: [TBD]" # contact SPASE to register
    # ncfile.spase_DatasetResourceID = "TBD", # * Recommended
    # ncfile.software_version = 'TBD'
    
    """
    1 Hz Data
    """
    V01 = ncfile.createVariable('GPS_SEC_1Hz', 'f8', ('nRec1Hz',), zlib=True)
    V01.units = 'seconds'
    V01.long_name = 'GPS_time'
    V01[:] = df_1Hz['GPS_SEC']
    #
    if xip == 'TIP':
        V02 = ncfile.createVariable(f'{xip}_UV_1Hz', 'u8', ('nRec1Hz',), zlib=True)
        V02.units = 'counts/sec'
        V02.long_name = 'UV_PMT_counts'
        V02[:] = df_1Hz['UV_CTS']
        # 
        V03 = ncfile.createVariable(f'{xip}_RED_1Hz', 'u8', ('nRec1Hz',), zlib=True)
        V03.units = 'counts/sec'
        V03.long_name = 'red_PMT_counts'
        V03[:] = df_1Hz['RD_CTS']
        # 
        V04 = ncfile.createVariable(f'{xip}_DARK_1Hz', 'u8', ('nRec1Hz',), zlib=True)
        V04.units = 'counts/sec'
        V04.long_name = 'dark_PMT_counts'
        V04[:] = df_1Hz['DK_CTS']
        # 
    if xip == 'MIP':
        V02 = ncfile.createVariable(f'{xip}_MG_1Hz', 'u8', ('nRec1Hz',), zlib=True)
        V02.units = 'counts/sec'
        V02.long_name = 'MG_PMT_counts'
        V02[:] = df_1Hz['MG_CTS']
        # 
        V03 = ncfile.createVariable(f'{xip}_VK_1Hz', 'u8', ('nRec1Hz',), zlib=True)
        V03.units = 'counts/sec'
        V03.long_name = 'VK_PMT_counts'
        V03[:] = df_1Hz['VK_CTS']
        # 
        V04 = ncfile.createVariable(f'{xip}_DARK_1Hz', 'u8', ('nRec1Hz',), zlib=True)
        V04.units = 'counts/sec'
        V04.long_name = 'dark_PMT_counts'
        V04[:] = df_1Hz['DK_CTS']
        # 
    V05 = ncfile.createVariable('HV_Mon_1Hz', 'f4', ('nRec1Hz',), zlib=True)
    V05.units = 'volts'
    V05.long_name = 'High_Voltage_Monitor'
    V05[:] = df_1Hz['HV_mon']
    # 
    V10 = ncfile.createVariable('SCAN_ANGLE_1Hz', 'f8', ('nRec1Hz',), zlib=True)
    V10.units = 'degrees'
    V10.long_name = 'SUVM_Scan_Angle'
    V10[:] = df_1Hz['XIP0_SCAN_ANGLE']
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
    W01[:] = df_10Hz['GPS_SEC']
    # 
    if xip == 'TIP':
        W02 = ncfile.createVariable(f'{xip}_UV_10Hz', 'u8', ('nRec10Hz',), zlib=True)
        W02.units = 'counts/sec'
        W02.long_name = 'UV_PMT_counts'
        W02[:] = df_10Hz['UV_CTS']
        # 
        W03 = ncfile.createVariable(f'{xip}_RED_10Hz', 'u8', ('nRec10Hz',), zlib=True)
        W03.units = 'counts/sec'
        W03.long_name = 'red_PMT_counts'
        W03[:] = df_10Hz['RD_CTS']
        # 
        W04 = ncfile.createVariable(f'{xip}_DARK_10Hz', 'u8', ('nRec10Hz',), zlib=True)
        W04.units = 'counts/sec'
        W04.long_name = 'dark_PMT_counts'
        W04[:] = df_10Hz['DK_CTS']
    if xip == 'MIP':
        W02 = ncfile.createVariable(f'{xip}_MG_10Hz', 'u8', ('nRec10Hz',), zlib=True)
        W02.units = 'counts/sec'
        W02.long_name = 'MG_PMT_counts'
        W02[:] = df_10Hz['MG_CTS']
        # 
        W03 = ncfile.createVariable(f'{xip}_VK_10Hz', 'u8', ('nRec10Hz',), zlib=True)
        W03.units = 'counts/sec'
        W03.long_name = 'VK_PMT_counts'
        W03[:] = df_10Hz['VK_CTS']
        # 
        W04 = ncfile.createVariable(f'{xip}_DARK_10Hz', 'u8', ('nRec10Hz',), zlib=True)
        W04.units = 'counts/sec'
        W04.long_name = 'dark_PMT_counts'
        W04[:] = df_10Hz['DK_CTS']
    # 
    W10 = ncfile.createVariable('SCAN_ANGLE_10Hz', 'f8', ('nRec10Hz',), zlib=True)
    W10.units = 'degrees'
    W10.long_name = 'SUVM_Scan_Angle'
    W10[:] = df_10Hz['XIP1_SCAN_ANGLE']
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
