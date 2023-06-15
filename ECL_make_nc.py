# -*- coding: utf-8 -*-
"""
Created on Wed May  3 21:33:19 2023

@author: bfritz

exmample to follow at
https://unidata.github.io/python-training/workshop/Bonus/netcdf-writing/
"""
from netCDF4 import Dataset    # pip install netCDF4
from os import path
import numpy as np
import time
import ECLIPSE_telemetry_breakout as etb
import ECLIPSE_H9_ccsds as ehc
import ECLIPSE_iib_converter as eic
import XIP_packet_converter as xpc
import SUVM_packet_converter as spc

def ECL_global_attributes(ncfile):
    ncfile.title = 'ECLIPSE'
    ncfile.source_name = 'ECL>ECLIPSE'
    ncfile.descriptor = 'Experiment for Characterizing the Lower Ionosphere & Prediction of Sporadic-E'
    ncfile.PI_name = 'Kenneth F. Dymond'
    ncfile.PI_affiliation = 'U.S. Naval Research Laboratory'
    ncfile.mission_group = 'DoD Space Test Program (STP)'
    ncfile.mission = 'STP-H9'
    ncfile.instrument_type = 'Imaging and Remote Sensing (ITM/Earth)'
    ncfile.discipline = 'Space Physics > Ionospheric Science'
    ncfile.time_resolution = '1 second'
    ncfile.data_type = "H0>Photometer_Counts"
    
    ncfile.generated_by = 'Bruce A. Fritz'
    ncfile.generation_date = time.asctime(time.localtime(time.time()))
    
    # ncfile.logical_file_id = "ECL_H0_MIP_20220801_V01 [TBR]"
    # ncfile.logical_source  = "SLN_H0_MIP [TBR]"
    # ncfile.logical_source_description = "Tri-MIP Photometer Counts"
    # ncfile.mods = "Initial Release"

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
    

def ECL_L0_analog(fname, ebyte):
    try: ncfile.close()  # just to be safe, make sure dataset is not already open.
    except: pass
    
    (fpath, fbase_ext) = path.split(fname)
    (fbase, f_ext) = path.splitext(fbase_ext)
    
    fnew_ext = f"{fbase}_ECLIPSE_L0_analog.nc"
    outname = path.join(fpath, 'L0_analog', fnew_ext)
    
    print('Starting to generate the file ... ')
    print(' ... ' + outname)
    print('')
    
    ncfile = Dataset(outname,mode='w',format='NETCDF4') 
    
    analog1 = eic.eclipse_iib_converter(ebyte.analog1)
    analog2 = eic.eclipse_iib_converter(ebyte.analog2)
    
    # Define Dimensions
    time_dim_a = ncfile.createDimension('ALS_time', len(analog1.MET))
    time_dim_c = ncfile.createDimension('CTS_time', len(analog2.MET))
    # 
    # Create Attributes
    # 
    ### REQUIRED GLOBAL ATTRIBUTES
    ECL_global_attributes(ncfile)
    ### GLOBAL ATTRIBUTES specific to this file type
    ncfile.source_1 = fbase_ext
    ncfile.source_2 = 'TBD - Will be ISS telemetry file'
    ncfile.filename = outname
    ncfile.data_version = 'Raw Data'
    # 
    # Create Variables
    ALS_MET = ncfile.createVariable('ALS_MET', np.uint32, ('ALS_time',), zlib=True)
    ALS_MET.units = 'seconds'
    ALS_MET.long_name = 'mission_elapsed_time'
    ALS_MET[:] = analog1.MET
    # 
    CTS_MET = ncfile.createVariable('CTS_MET', np.uint32, ('CTS_time',), zlib=True)
    CTS_MET.units = 'seconds'
    CTS_MET.long_name = 'mission_elapsed_time'
    CTS_MET[:] = analog2.MET
    # 
    ALS_MIP_I_12V = ncfile.createVariable('ALS_MIP_I_12V', np.float32, ('ALS_time',), zlib=True)
    ALS_MIP_I_12V.units = 'Amps'
    ALS_MIP_I_12V.long_name = 'ALS_MIP_12V_current'
    ALS_MIP_I_12V[:] = analog1.I_mip12V
    # 
    CTS_MIP_I_12V = ncfile.createVariable('CTS_MIP_I_12V', np.float32, ('CTS_time',), zlib=True)
    CTS_MIP_I_12V.units = 'Amps'
    CTS_MIP_I_12V.long_name = 'CTS_MIP_12V_current'
    CTS_MIP_I_12V[:] = analog2.I_mip12V
    # 
    ALS_MIP_V_12V = ncfile.createVariable('ALS_MIP_V_12V', np.float32, ('ALS_time',), zlib=True)
    ALS_MIP_V_12V.units = 'Volts'
    ALS_MIP_V_12V.long_name = 'ALS_MIP_12V_voltage'
    ALS_MIP_V_12V[:] = analog1.V_mip12V
    # 
    CTS_MIP_V_12V = ncfile.createVariable('CTS_MIP_V_12V', np.float32, ('CTS_time',), zlib=True)
    CTS_MIP_V_12V.units = 'Volts'
    CTS_MIP_V_12V.long_name = 'CTS_MIP_12V_voltage'
    CTS_MIP_V_12V[:] = analog2.V_mip12V
    # 
    ALS_MIP_I_3V = ncfile.createVariable('ALS_MIP_I_3V', np.float32, ('ALS_time',), zlib=True)
    ALS_MIP_I_3V.units = 'Amps'
    ALS_MIP_I_3V.long_name = 'ALS_MIP_3V_current'
    ALS_MIP_I_3V[:] = analog1.I_mip3V
    # 
    CTS_MIP_I_3V = ncfile.createVariable('CTS_MIP_I_3V', np.float32, ('CTS_time',), zlib=True)
    CTS_MIP_I_3V.units = 'Amps'
    CTS_MIP_I_3V.long_name = 'CTS_MIP_3V_current'
    CTS_MIP_I_3V[:] = analog2.I_mip3V
    # 
    ALS_MIP_V_3V = ncfile.createVariable('ALS_MIP_V_3V', np.float32, ('ALS_time',), zlib=True)
    ALS_MIP_V_3V.units = 'Volts'
    ALS_MIP_V_3V.long_name = 'ALS_MIP_3V_voltage'
    ALS_MIP_V_3V[:] = analog1.V_mip3V
    # 
    CTS_MIP_V_3V = ncfile.createVariable('CTS_MIP_V_3V', np.float32, ('CTS_time',), zlib=True)
    CTS_MIP_V_3V.units = 'Volts'
    CTS_MIP_V_3V.long_name = 'CTS_MIP_3V_voltage'
    CTS_MIP_V_3V[:] = analog2.V_mip3V
    # 
    ALS_TIP_I_12V = ncfile.createVariable('ALS_TIP_I_12V', np.float32, ('ALS_time',), zlib=True)
    ALS_TIP_I_12V.units = 'Amps'
    ALS_TIP_I_12V.long_name = 'ALS_TIP_12V_current'
    ALS_TIP_I_12V[:] = analog1.I_tip12V
    # 
    CTS_TIP_I_12V = ncfile.createVariable('CTS_TIP_I_12V', np.float32, ('CTS_time',), zlib=True)
    CTS_TIP_I_12V.units = 'Amps'
    CTS_TIP_I_12V.long_name = 'CTS_TIP_12V_current'
    CTS_TIP_I_12V[:] = analog2.I_tip12V
    # 
    ALS_TIP_V_12V = ncfile.createVariable('ALS_TIP_V_12V', np.float32, ('ALS_time',), zlib=True)
    ALS_TIP_V_12V.units = 'Volts'
    ALS_TIP_V_12V.long_name = 'ALS_TIP_12V_voltage'
    ALS_TIP_V_12V[:] = analog1.V_tip12V
    # 
    CTS_TIP_V_12V = ncfile.createVariable('CTS_TIP_V_12V', np.float32, ('CTS_time',), zlib=True)
    CTS_TIP_V_12V.units = 'Volts'
    CTS_TIP_V_12V.long_name = 'CTS_TIP_12V_voltage'
    CTS_TIP_V_12V[:] = analog2.V_tip12V
    # 
    ALS_TIP_I_3V = ncfile.createVariable('ALS_TIP_I_3V', np.float32, ('ALS_time',), zlib=True)
    ALS_TIP_I_3V.units = 'Amps'
    ALS_TIP_I_3V.long_name = 'ALS_TIP_3V_current'
    ALS_TIP_I_3V[:] = analog1.I_tip3V
    # 
    CTS_TIP_I_3V = ncfile.createVariable('CTS_TIP_I_3V', np.float32, ('CTS_time',), zlib=True)
    CTS_TIP_I_3V.units = 'Amps'
    CTS_TIP_I_3V.long_name = 'CTS_TIP_3V_current'
    CTS_TIP_I_3V[:] = analog2.I_tip3V
    # 
    ALS_TIP_V_3V = ncfile.createVariable('ALS_TIP_V_3V', np.float32, ('ALS_time',), zlib=True)
    ALS_TIP_V_3V.units = 'Volts'
    ALS_TIP_V_3V.long_name = 'ALS_TIP_3V_voltage'
    ALS_TIP_V_3V[:] = analog1.V_tip3V
    # 
    CTS_TIP_V_3V = ncfile.createVariable('CTS_TIP_V_3V', np.float32, ('CTS_time',), zlib=True)
    CTS_TIP_V_3V.units = 'Volts'
    CTS_TIP_V_3V.long_name = 'CTS_TIP_3V_voltage'
    CTS_TIP_V_3V[:] = analog2.V_tip3V
    # 
    ALS_TIP_SUVM_I_5V = ncfile.createVariable('ALS_TIP_SUVM_I_5V', np.float32, ('ALS_time',), zlib=True)
    ALS_TIP_SUVM_I_5V.units = 'Amps'
    ALS_TIP_SUVM_I_5V.long_name = 'ALS_TIP_SUVM_5V_current'
    ALS_TIP_SUVM_I_5V[:] = analog1.I_tsm5V
    # 
    CTS_TIP_SUVM_I_5V = ncfile.createVariable('CTS_TIP_SUVM_I_5V', np.float32, ('CTS_time',), zlib=True)
    CTS_TIP_SUVM_I_5V.units = 'Amps'
    CTS_TIP_SUVM_I_5V.long_name = 'CTS_TIP_SUVM_5V_current'
    CTS_TIP_SUVM_I_5V[:] = analog2.I_tsm5V
    # 
    ALS_TIP_SUVM_V_5V = ncfile.createVariable('ALS_TIP_SUVM_V_5V', np.float32, ('ALS_time',), zlib=True)
    ALS_TIP_SUVM_V_5V.units = 'Volts'
    ALS_TIP_SUVM_V_5V.long_name = 'ALS_TIP_SUVM_5V_voltage'
    ALS_TIP_SUVM_V_5V[:] = analog1.V_tsm5V
    # 
    CTS_TIP_SUVM_V_5V = ncfile.createVariable('CTS_TIP_SUVM_V_5V', np.float32, ('CTS_time',), zlib=True)
    CTS_TIP_SUVM_V_5V.units = 'Volts'
    CTS_TIP_SUVM_V_5V.long_name = 'CTS_TIP_SUVM_5V_voltage'
    CTS_TIP_SUVM_V_5V[:] = analog2.V_tsm5V
    # 
    ALS_TIP_SUVM_I_3V = ncfile.createVariable('ALS_TIP_SUVM_I_3V', np.float32, ('ALS_time',), zlib=True)
    ALS_TIP_SUVM_I_3V.units = 'Amps'
    ALS_TIP_SUVM_I_3V.long_name = 'ALS_TIP_SUVM_3V_current'
    ALS_TIP_SUVM_I_3V[:] = analog1.I_tsm3V
    # 
    CTS_TIP_SUVM_I_3V = ncfile.createVariable('CTS_TIP_SUVM_I_3V', np.float32, ('CTS_time',), zlib=True)
    CTS_TIP_SUVM_I_3V.units = 'Amps'
    CTS_TIP_SUVM_I_3V.long_name = 'CTS_TIP_SUVM_3V_current'
    CTS_TIP_SUVM_I_3V[:] = analog2.I_tsm3V
    # 
    ALS_TIP_SUVM_V_3V = ncfile.createVariable('ALS_TIP_SUVM_V_3V', np.float32, ('ALS_time',), zlib=True)
    ALS_TIP_SUVM_V_3V.units = 'Volts'
    ALS_TIP_SUVM_V_3V.long_name = 'ALS_TIP_SUVM_3V_voltage'
    ALS_TIP_SUVM_V_3V[:] = analog1.V_tsm3V
    # 
    CTS_TIP_SUVM_V_3V = ncfile.createVariable('CTS_TIP_SUVM_V_3V', np.float32, ('CTS_time',), zlib=True)
    CTS_TIP_SUVM_V_3V.units = 'Volts'
    CTS_TIP_SUVM_V_3V.long_name = 'CTS_TIP_SUVM_3V_voltage'
    CTS_TIP_SUVM_V_3V[:] = analog2.V_tsm3V
    # 
    ALS_MIP_SUVM_I_5V = ncfile.createVariable('ALS_MIP_SUVM_I_5V', np.float32, ('ALS_time',), zlib=True)
    ALS_MIP_SUVM_I_5V.units = 'Amps'
    ALS_MIP_SUVM_I_5V.long_name = 'ALS_MIP_SUVM_5V_current'
    ALS_MIP_SUVM_I_5V[:] = analog1.I_msm5V
    # 
    CTS_MIP_SUVM_I_5V = ncfile.createVariable('CTS_MIP_SUVM_I_5V', np.float32, ('CTS_time',), zlib=True)
    CTS_MIP_SUVM_I_5V.units = 'Amps'
    CTS_MIP_SUVM_I_5V.long_name = 'CTS_MIP_SUVM_5V_current'
    CTS_MIP_SUVM_I_5V[:] = analog2.I_msm5V
    # 
    ALS_MIP_SUVM_V_5V = ncfile.createVariable('ALS_MIP_SUVM_V_5V', np.float32, ('ALS_time',), zlib=True)
    ALS_MIP_SUVM_V_5V.units = 'Volts'
    ALS_MIP_SUVM_V_5V.long_name = 'ALS_MIP_SUVM_5V_voltage'
    ALS_MIP_SUVM_V_5V[:] = analog1.V_msm5V
    # 
    CTS_MIP_SUVM_V_5V = ncfile.createVariable('CTS_MIP_SUVM_V_5V', np.float32, ('CTS_time',), zlib=True)
    CTS_MIP_SUVM_V_5V.units = 'Volts'
    CTS_MIP_SUVM_V_5V.long_name = 'CTS_MIP_SUVM_5V_voltage'
    CTS_MIP_SUVM_V_5V[:] = analog2.V_msm5V
    # 
    ALS_MIP_SUVM_I_3V = ncfile.createVariable('ALS_MIP_SUVM_I_3V', np.float32, ('ALS_time',), zlib=True)
    ALS_MIP_SUVM_I_3V.units = 'Amps'
    ALS_MIP_SUVM_I_3V.long_name = 'ALS_MIP_SUVM_3V_current'
    ALS_MIP_SUVM_I_3V[:] = analog1.I_msm3V
    # 
    CTS_MIP_SUVM_I_3V = ncfile.createVariable('CTS_MIP_SUVM_I_3V', np.float32, ('CTS_time',), zlib=True)
    CTS_MIP_SUVM_I_3V.units = 'Amps'
    CTS_MIP_SUVM_I_3V.long_name = 'CTS_MIP_SUVM_3V_current'
    CTS_MIP_SUVM_I_3V[:] = analog2.I_msm3V
    # 
    ALS_MIP_SUVM_V_3V = ncfile.createVariable('ALS_MIP_SUVM_V_3V', np.float32, ('ALS_time',), zlib=True)
    ALS_MIP_SUVM_V_3V.units = 'Volts'
    ALS_MIP_SUVM_V_3V.long_name = 'ALS_MIP_SUVM_3V_voltage'
    ALS_MIP_SUVM_V_3V[:] = analog1.V_msm3V
    # 
    CTS_MIP_SUVM_V_3V = ncfile.createVariable('CTS_MIP_SUVM_V_3V', np.float32, ('CTS_time',), zlib=True)
    CTS_MIP_SUVM_V_3V.units = 'Volts'
    CTS_MIP_SUVM_V_3V.long_name = 'CTS_MIP_SUVM_3V_voltage'
    CTS_MIP_SUVM_V_3V[:] = analog2.V_msm3V
    # 
    ALS_TIP_SUVM_V_28V = ncfile.createVariable('ALS_TIP_SUVM_V_28V', np.float32, ('ALS_time',), zlib=True)
    ALS_TIP_SUVM_V_28V.units = 'Volts'
    ALS_TIP_SUVM_V_28V.long_name = 'ALS_TIP_SUVM_28V_voltage'
    ALS_TIP_SUVM_V_28V[:] = analog1.V_tsm28V
    # 
    CTS_TIP_SUVM_V_28V = ncfile.createVariable('CTS_TIP_SUVM_V_28V', np.float32, ('CTS_time',), zlib=True)
    CTS_TIP_SUVM_V_28V.units = 'Volts'
    CTS_TIP_SUVM_V_28V.long_name = 'CTS_TIP_SUVM_28V_voltage'
    CTS_TIP_SUVM_V_28V[:] = analog2.V_tsm28V
    # 
    ALS_MIP_SUVM_V_28V = ncfile.createVariable('ALS_MIP_SUVM_V_28V', np.float32, ('ALS_time',), zlib=True)
    ALS_MIP_SUVM_V_28V.units = 'Volts'
    ALS_MIP_SUVM_V_28V.long_name = 'ALS_MIP_SUVM_28V_voltage'
    ALS_MIP_SUVM_V_28V[:] = analog1.V_msm28V
    # 
    CTS_MIP_SUVM_V_28V = ncfile.createVariable('CTS_MIP_SUVM_V_28V', np.float32, ('CTS_time',), zlib=True)
    CTS_MIP_SUVM_V_28V.units = 'Volts'
    CTS_MIP_SUVM_V_28V.long_name = 'CTS_MIP_SUVM_28V_voltage'
    CTS_MIP_SUVM_V_28V[:] = analog2.V_msm28V
    #     
    print(ncfile)
    ncfile.close()
    
    print(' Analog File Complete: ' + outname)
    print('')
    
    

def ECL_L0_ALS(fname, ebyte):
    try: ncfile.close()  # just to be safe, make sure dataset is not already open.
    except: pass
    
    (fpath, fbase_ext) = path.split(fname)
    (fbase, f_ext) = path.splitext(fbase_ext)
    
    fnew_ext = f"{fbase}_ECLIPSE_L0_ALS.nc"
    outname = path.join(fpath, 'L0_ALS', fnew_ext)
    
    print('Starting to generate the file ... ')
    print(' ... ' + outname)
    print('')
    
    ncfile = Dataset(outname,mode='w',format='NETCDF4') 
    # 
    tip0 = xpc.convert_m0_byt2dec(ebyte.tip1_m0,'TIP')
    tip1 = xpc.convert_m1_byt2dec(ebyte.tip1_m1,'TIP')
    mip0 = xpc.convert_m0_byt2dec(ebyte.mip3_m0,'MIP')
    mip1 = xpc.convert_m1_byt2dec(ebyte.mip3_m1,'MIP')
    # 
    suvm2_byte = etb.breakout_suvm_packet(ebyte.suvm2)
    s2_gen = spc.suvm_general_converter(suvm2_byte)
    suvm4_byte = etb.breakout_suvm_packet(ebyte.suvm4)
    s4_gen = spc.suvm_general_converter(suvm4_byte)
    # 
    # Define Dimensions
    time_dim_t0 = ncfile.createDimension('TIP_M0_MET', len(tip0.MET))
    time_dim_t1 = ncfile.createDimension('TIP_M1_MET', len(tip1.MET))
    time_dim_ts = ncfile.createDimension('TIP_SUVM_TIME', len(s2_gen.time))
    time_dim_m0 = ncfile.createDimension('MIP_M0_MET', len(mip0.MET))
    time_dim_m1 = ncfile.createDimension('MIP_M1_MET', len(mip1.MET))
    time_dim_ms = ncfile.createDimension('MIP_SUVM_TIME', len(s4_gen.time))
    # 
    # Create Attributes
    # 
    ### REQUIRED GLOBAL ATTRIBUTES
    ECL_global_attributes(ncfile)
    ### GLOBAL ATTRIBUTES specific to this file type
    ncfile.source_1 = fbase_ext
    ncfile.source_2 = 'TBD - Will be ISS telemetry file'
    ncfile.filename = outname
    ncfile.data_version = 'Raw Data'
    """ 
    # XIP Variables
    
    M0 Vlues Not included:
    #         self.IDC_ID = np.zeros(n, dtype='U4')
    #         self.MODE             = np.zeros(n, dtype='U2')
    """
    ATIP0_MET = ncfile.createVariable('TIP_M0_MET', np.uint64, ('TIP_M0_MET',), zlib=True)
    ATIP0_MET.units = 'seconds'
    ATIP0_MET.long_name = 'mission_elapsed_time'
    ATIP0_MET[:] = tip0.MET
    AMIP0_MET = ncfile.createVariable('MIP_M0_MET', np.uint64, ('MIP_M0_MET',), zlib=True)
    AMIP0_MET.units = 'seconds'
    AMIP0_MET.long_name = 'mission_elapsed_time'
    AMIP0_MET[:] = mip0.MET
    # 
    ATIP0_TIME = ncfile.createVariable('TIP_M0_TIME', np.uint64, ('TIP_M0_MET',), zlib=True)
    ATIP0_TIME.units = 'seconds'
    ATIP0_TIME.long_name = 'system_run_time'
    ATIP0_TIME[:] = tip0.time
    AMIP0_TIME = ncfile.createVariable('MIP_M0_TIME', np.uint64, ('MIP_M0_MET',), zlib=True)
    AMIP0_TIME.units = 'seconds'
    AMIP0_TIME.long_name = 'system_run_time'
    AMIP0_TIME[:] = mip0.time
    # 
    ATIP0_DARK = ncfile.createVariable('TIP_M0_DARK', np.uint64, ('TIP_M0_MET',), zlib=True)
    ATIP0_DARK.units = 'counts/sec'
    ATIP0_DARK.long_name = 'dark_PMT_counts'
    ATIP0_DARK[:] = tip0.dark
    AMIP0_DARK = ncfile.createVariable('MIP_M0_DARK', np.uint64, ('MIP_M0_MET',), zlib=True)
    AMIP0_DARK.units = 'counts/sec'
    AMIP0_DARK.long_name = 'dark_PMT_counts'
    AMIP0_DARK[:] = mip0.dark
    # 
    ATIP0_RED = ncfile.createVariable('TIP_M0_RED', np.uint64, ('TIP_M0_MET',), zlib=True)
    ATIP0_RED.units = 'counts/sec'
    ATIP0_RED.long_name = 'red_PMT_counts'
    ATIP0_RED[:] = tip0.red
    # 
    AMIP0_MG = ncfile.createVariable('MIP_M0_MG', np.uint64, ('MIP_M0_MET',), zlib=True)
    AMIP0_MG.units = 'counts/sec'
    AMIP0_MG.long_name = 'Mg_PMT_counts'
    AMIP0_MG[:] = mip0.Mg
    # 
    ATIP0_UV = ncfile.createVariable('TIP_M0_UV', np.uint64, ('TIP_M0_MET',), zlib=True)
    ATIP0_UV.units = 'counts/sec'
    ATIP0_UV.long_name = 'uv_PMT_counts'
    ATIP0_UV[:] = tip0.uv
    # 
    AMIP0_VK = ncfile.createVariable('MIP_M0_VK', np.uint64, ('MIP_M0_MET',), zlib=True)
    AMIP0_VK.units = 'counts/sec'
    AMIP0_VK.long_name = 'VK_PMT_counts'
    AMIP0_VK[:] = mip0.VK
    # 
    ATIP0_HEATER = ncfile.createVariable('TIP_M0_HEATER', np.uint32, ('TIP_M0_MET',), zlib=True)
    ATIP0_HEATER.long_name = 'heater_duty_cycle'
    ATIP0_HEATER[:] = tip0.heater
    # 
    # AMIP0_ERROR = ncfile.createVariable('MIP_M0_ERROR', np.uint32, ('MIP_M0_MET',), zlib=True)
    # AMIP0_ERROR.long_name = 'error'
    # AMIP0_ERROR[:] = mip0.error
    # 
    ATIP0_TF1 = ncfile.createVariable('TIP_M0_TF1', np.float32, ('TIP_M0_MET',), zlib=True)
    ATIP0_TF1.units = 'Celsius'
    ATIP0_TF1.long_name = 'filter_temperature_1'
    ATIP0_TF1[:] = tip0.T_F1
    # 
    AMIP0_TLENS = ncfile.createVariable('MIP_M0_TLENS', np.float32, ('MIP_M0_MET',), zlib=True)
    AMIP0_TLENS.units = 'Celsius'
    AMIP0_TLENS.long_name = 'Lens_temperature'
    AMIP0_TLENS[:] = mip0.T_LENS
    # 
    ATIP0_TF2 = ncfile.createVariable('TIP_M0_TF2', np.float32, ('TIP_M0_MET',), zlib=True)
    ATIP0_TF2.units = 'Celsius'
    ATIP0_TF2.long_name = 'filter_temperature_2'
    ATIP0_TF2[:] = tip0.T_F2
    #
    AMIP0_TPMT = ncfile.createVariable('MIP_M0_TPMT', np.float32, ('MIP_M0_MET',), zlib=True)
    AMIP0_TPMT.units = 'Celsius'
    AMIP0_TPMT.long_name = 'PMT_block_temperature'
    AMIP0_TPMT[:] = mip0.T_PMT
    #
    ATIP0_HVMON = ncfile.createVariable('TIP_M0_HV_mon', np.float32, ('TIP_M0_MET',), zlib=True)
    ATIP0_HVMON.units = 'Volts'
    ATIP0_HVMON.long_name = 'High_voltage_monitor'
    ATIP0_HVMON[:] = tip0.HV_mon
    AMIP0_HVMON = ncfile.createVariable('MIP_M0_HV_mon', np.float32, ('MIP_M0_MET',), zlib=True)
    AMIP0_HVMON.units = 'Volts'
    AMIP0_HVMON.long_name = 'High_voltage_monitor'
    AMIP0_HVMON[:] = mip0.HV_mon
    #
    ATIP0_HVADJ = ncfile.createVariable('TIP_M0_HV_adj', np.float32, ('TIP_M0_MET',), zlib=True)
    ATIP0_HVADJ.units = 'Volts'
    ATIP0_HVADJ.long_name = 'High_voltage_adjust'
    ATIP0_HVADJ[:] = tip0.HV_adj
    AMIP0_HVADJ = ncfile.createVariable('MIP_M0_HV_adj', np.float32, ('MIP_M0_MET',), zlib=True)
    AMIP0_HVADJ.units = 'Volts'
    AMIP0_HVADJ.long_name = 'High_voltage_adjust'
    AMIP0_HVADJ[:] = mip0.HV_adj
    #
    ATIP0_SUN = ncfile.createVariable('TIP_M0_sun', np.float32, ('TIP_M0_MET',), zlib=True)
    ATIP0_SUN.units = 'Volts'
    ATIP0_SUN.long_name = 'sun_sensor'
    ATIP0_SUN[:] = tip0.sun
    AMIP0_SUN = ncfile.createVariable('MIP_M0_sun', np.float32, ('MIP_M0_MET',), zlib=True)
    AMIP0_SUN.units = 'Volts'
    AMIP0_SUN.long_name = 'sun_sensor'
    AMIP0_SUN[:] = mip0.sun
    #
    ATIP0_VREF = ncfile.createVariable('TIP_M0_VREF', np.float32, ('TIP_M0_MET',), zlib=True)
    ATIP0_VREF.units = 'Volts'
    ATIP0_VREF.long_name = 'reference_voltage_2p5V'
    ATIP0_VREF[:] = tip0.vref
    AMIP0_VREF = ncfile.createVariable('MIP_M0_VREF', np.float32, ('MIP_M0_MET',), zlib=True)
    AMIP0_VREF.units = 'Volts'
    AMIP0_VREF.long_name = 'reference_voltage_2p5V'
    AMIP0_VREF[:] = mip0.vref
    #
    ATIP0_TIDC = ncfile.createVariable('TIP_M0_TIDC', np.float32, ('TIP_M0_MET',), zlib=True)
    ATIP0_TIDC.units = 'Celsius'
    ATIP0_TIDC.long_name = 'IDC_temperature'
    ATIP0_TIDC[:] = tip0.T_IDC
    AMIP0_TIDC = ncfile.createVariable('MIP_M0_TIDC', np.float32, ('MIP_M0_MET',), zlib=True)
    AMIP0_TIDC.units = 'Celsius'
    AMIP0_TIDC.long_name = 'IDC_temperature'
    AMIP0_TIDC[:] = mip0.T_IDC
    #
    ATIP0_THV = ncfile.createVariable('TIP_M0_HV', np.float32, ('TIP_M0_MET',), zlib=True)
    ATIP0_THV.units = 'Celsius'
    ATIP0_THV.long_name = 'high_voltage_temperature'
    ATIP0_THV[:] = tip0.T_HV
    AMIP0_THV = ncfile.createVariable('MIP_M0_HV', np.float32, ('MIP_M0_MET',), zlib=True)
    AMIP0_THV.units = 'Celsius'
    AMIP0_THV.long_name = 'high_voltage_temperature'
    AMIP0_THV[:] = mip0.T_HV
    #
    # ATIP0_DISCRETE = ncfile.createVariable('TIP_M0_DISCRETE', np.str, ('TIP_M0_MET',), zlib=True)
    # ATIP0_DISCRETE.long_name = 'discrete'
    # ATIP0_DISCRETE[:] = tip0.discrete
    # AMIP0_DISCRETE = ncfile.createVariable('MIP_M0_DISCRETE', np.str, ('MIP_M0_MET',), zlib=True)
    # AMIP0_DISCRETE.long_name = 'discrete'
    # AMIP0_DISCRETE[:] = mip0.discrete
    #
    ATIP0_HVSTAT = ncfile.createVariable('TIP_M0_HV_Status', np.ubyte, ('TIP_M0_MET',), zlib=True)
    ATIP0_HVSTAT.long_name = 'High_Voltage_Status'
    ATIP0_HVSTAT[:] = tip0.HV_STATUS
    AMIP0_HVSTAT = ncfile.createVariable('MIP_M0_HV_Status', np.ubyte, ('MIP_M0_MET',), zlib=True)
    AMIP0_HVSTAT.long_name = 'High_Voltage_Status'
    AMIP0_HVSTAT[:] = mip0.HV_STATUS
    # 
    ATIP0_HVEVENT = ncfile.createVariable('TIP_M0_HV_Event', np.ubyte, ('TIP_M0_MET',), zlib=True)
    ATIP0_HVEVENT.long_name = 'High_Voltage_Exceed_Threshold'
    ATIP0_HVEVENT[:] = tip0.HV_EVENT
    AMIP0_HVEVENT = ncfile.createVariable('MIP_M0_HV_Event', np.ubyte, ('MIP_M0_MET',), zlib=True)
    AMIP0_HVEVENT.long_name = 'High_Voltage_Exceed_Threshold'
    AMIP0_HVEVENT[:] = mip0.HV_EVENT
    # 
    ATIP0_SUNEVENT = ncfile.createVariable('TIP_M0_Sun_Event', np.ubyte, ('TIP_M0_MET',), zlib=True)
    ATIP0_SUNEVENT.long_name = 'Sun_Sensor_Exceed_Threshold'
    ATIP0_SUNEVENT[:] = tip0.SUN_EVENT
    AMIP0_SUNEVENT = ncfile.createVariable('MIP_M0_Sun_Event', np.ubyte, ('MIP_M0_MET',), zlib=True)
    AMIP0_SUNEVENT.long_name = 'Sun_Sensor_Exceed_Threshold'
    AMIP0_SUNEVENT[:] = mip0.SUN_EVENT
    # 
    ATIP0_DKEVENT = ncfile.createVariable('TIP_M0_DK_EVENT', np.ubyte, ('TIP_M0_MET',), zlib=True)
    ATIP0_DKEVENT.long_name = 'PMT_Dark_Pad_Exceed_Threshold'
    ATIP0_DKEVENT[:] = tip0.DK_EVENT
    AMIP0_DKEVENT = ncfile.createVariable('MIP_M0_DK_EVENT', np.ubyte, ('MIP_M0_MET',), zlib=True)
    AMIP0_DKEVENT.long_name = 'PMT_Dark_Pad_Exceed_Threshold'
    AMIP0_DKEVENT[:] = mip0.DK_EVENT
    # 
    ATIP0_RDEVENT = ncfile.createVariable('TIP_M0_RD_EVENT', np.ubyte, ('TIP_M0_MET',), zlib=True)
    ATIP0_RDEVENT.long_name = 'PMT_Red_Pad_Exceed_Threshold'
    ATIP0_RDEVENT[:] = tip0.RD_EVENT
    AMIP0_RDEVENT = ncfile.createVariable('MIP_M0_RD_EVENT', np.ubyte, ('MIP_M0_MET',), zlib=True)
    AMIP0_RDEVENT.long_name = 'PMT_Red_Pad_Exceed_Threshold'
    AMIP0_RDEVENT[:] = mip0.RD_EVENT
    # 
    ATIP0_UVEVENT = ncfile.createVariable('TIP_M0_UV_EVENT', np.ubyte, ('TIP_M0_MET',), zlib=True)
    ATIP0_UVEVENT.long_name = 'PMT_UV_Pad_Exceed_Threshold'
    ATIP0_UVEVENT[:] = tip0.UV_EVENT
    AMIP0_UVEVENT = ncfile.createVariable('MIP_M0_UV_EVENT', np.ubyte, ('MIP_M0_MET',), zlib=True)
    AMIP0_UVEVENT.long_name = 'PMT_UV_Pad_Exceed_Threshold'
    AMIP0_UVEVENT[:] = mip0.UV_EVENT
    # 
    ATIP0_SUNOVERRIDE = ncfile.createVariable('TIP_M0_Sun_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    ATIP0_SUNOVERRIDE.long_name = 'Sun_Sensor_Override'
    ATIP0_SUNOVERRIDE[:] = tip0.SUN_OVERRIDE
    AMIP0_SUNOVERRIDE = ncfile.createVariable('MIP_M0_Sun_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    AMIP0_SUNOVERRIDE.long_name = 'Sun_Sensor_Override'
    AMIP0_SUNOVERRIDE[:] = mip0.SUN_OVERRIDE
    # 
    ATIP0_DKOVERRIDE = ncfile.createVariable('TIP_M0_Dark_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    ATIP0_DKOVERRIDE.long_name = 'Dark_Count_Override'
    ATIP0_DKOVERRIDE[:] = tip0.DK_OVERRIDE
    AMIP0_DKOVERRIDE = ncfile.createVariable('MIP_M0_Dark_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    AMIP0_DKOVERRIDE.long_name = 'Dark_Count_Override'
    AMIP0_DKOVERRIDE[:] = mip0.DK_OVERRIDE
    # 
    ATIP0_RD_OVERRIDE = ncfile.createVariable('TIP_M0_Red_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    ATIP0_RD_OVERRIDE.long_name = 'Red_Count_Override'
    ATIP0_RD_OVERRIDE[:] = tip0.RD_OVERRIDE
    AMIP0_RD_OVERRIDE = ncfile.createVariable('MIP_M0_Red_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    AMIP0_RD_OVERRIDE.long_name = 'Red_Count_Override'
    AMIP0_RD_OVERRIDE[:] = mip0.RD_OVERRIDE
    # 
    ATIP0_UVOVERRIDE = ncfile.createVariable('TIP_M0_UV_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    ATIP0_UVOVERRIDE.long_name = 'UV_Count_Override'
    ATIP0_UVOVERRIDE[:] = tip0.UV_OVERRIDE
    AMIP0_UVOVERRIDE = ncfile.createVariable('MIP_M0_UV_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    AMIP0_UVOVERRIDE.long_name = 'UV_Count_Override'
    AMIP0_UVOVERRIDE[:] = mip0.UV_OVERRIDE
    # 
    ATIP0_HVOVERRIDE = ncfile.createVariable('TIP_M0_HV_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    ATIP0_HVOVERRIDE.long_name = 'High_Voltage_Override'
    ATIP0_HVOVERRIDE[:] = tip0.HV_OVERRIDE
    AMIP0_HVOVERRIDE = ncfile.createVariable('MIP_M0_HV_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    AMIP0_HVOVERRIDE.long_name = 'High_Voltage_Override'
    AMIP0_HVOVERRIDE[:] = mip0.HV_OVERRIDE
    # 
    ATIP0_SHUTTEROVERRIDE = ncfile.createVariable('TIP_M0_Shutter_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    ATIP0_SHUTTEROVERRIDE.long_name = 'Shutter_Override'
    ATIP0_SHUTTEROVERRIDE[:] = tip0.SHUTTER_OVERRIDE
    AMIP0_SHUTTEROVERRIDE = ncfile.createVariable('MIP_M0_Shutter_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    AMIP0_SHUTTEROVERRIDE.long_name = 'Shutter_Override'
    AMIP0_SHUTTEROVERRIDE[:] = mip0.SHUTTER_OVERRIDE
    # 
    ATIP0_V5OVERRIDE = ncfile.createVariable('TIP_M0_5V_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    ATIP0_V5OVERRIDE.long_name = '5V_Override'
    ATIP0_V5OVERRIDE[:] = tip0.V5_OVERRIDE
    AMIP0_V5OVERRIDE = ncfile.createVariable('MIP_M0_5V_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    AMIP0_V5OVERRIDE.long_name = '5V_Override'
    AMIP0_V5OVERRIDE[:] = mip0.V5_OVERRIDE
    """
    # M1 Variables
    
    Not included: 
        # tip1 / mip1 .dark_chk = np.zeros(10*n, dtype='uint64')
        # tip1        .red_chk = np.zeros(n, dtype='uint64')
        # tip1        .uv_chk  = np.zeros(n, dtype='uint64')
        # mip1        .Mg_chk = np.zeros(n, dtype='uint64')
        # mip1        .VK_chk = np.zeros(n, dtype='uint64')

    """
    ATIP1_MET = ncfile.createVariable('TIP_M1_MET', np.uint64, ('TIP_M1_MET',), zlib=True)
    ATIP1_MET.long_name = 'Mission_Elapsed_Time_10Hz'
    ATIP1_MET.units = 'Seconds'
    ATIP1_MET[:] = tip1.MET
    AMIP1_MET = ncfile.createVariable('MIP_M1_MET', np.uint64, ('MIP_M1_MET',), zlib=True)
    AMIP1_MET.long_name = 'Mission_Elapsed_Time_10Hz'
    AMIP1_MET.units = 'Seconds'
    AMIP1_MET[:] = mip1.MET
    # 
    ATIP1_TIME = ncfile.createVariable('TIP_M1_RUNTIME', np.uint64, ('TIP_M1_MET',), zlib=True)
    ATIP1_TIME.long_name = 'System_Run_Time_10Hz'
    ATIP1_TIME.units = 'Seconds'
    ATIP1_TIME[:] = tip1.time
    AMIP1_TIME = ncfile.createVariable('MIP_M1_RUNTIME', np.uint64, ('MIP_M1_MET',), zlib=True)
    AMIP1_TIME.long_name = 'System_Run_Time_10Hz'
    AMIP1_TIME.units = 'Seconds'
    AMIP1_TIME[:] = mip1.time
    # 
    ATIP1_DARK = ncfile.createVariable('TIP_M1_DARK', np.uint64, ('TIP_M1_MET',), zlib=True)
    ATIP1_DARK.long_name = 'Dark_Count_10Hz'
    ATIP1_DARK.units = 'Cts/sec'
    ATIP1_DARK[:] = tip1.dark
    AMIP1_DARK = ncfile.createVariable('MIP_M1_DARK', np.uint64, ('MIP_M1_MET',), zlib=True)
    AMIP1_DARK.long_name = 'Dark_Count_10Hz'
    AMIP1_DARK.units = 'Cts/sec'
    AMIP1_DARK[:] = mip1.dark
    # 
    ATIP1_RED = ncfile.createVariable('TIP_M1_RED', np.uint64, ('TIP_M1_MET',), zlib=True)
    ATIP1_RED.long_name = 'Red_Count_10Hz'
    ATIP1_RED.units = 'Cts/sec'
    ATIP1_RED[:] = tip1.red
    # 
    AMIP1_MG = ncfile.createVariable('MIP_M1_MG', np.uint64, ('MIP_M1_MET',), zlib=True)
    AMIP1_MG.long_name = 'Mg_Count_10Hz'
    AMIP1_MG.units = 'Cts/sec'
    AMIP1_MG[:] = mip1.Mg
    # 
    ATIP1_UV = ncfile.createVariable('TIP_M1_UV', np.uint64, ('TIP_M1_MET',), zlib=True)
    ATIP1_UV.long_name = 'UV_Count_10Hz'
    ATIP1_UV.units = 'Cts/sec'
    ATIP1_UV[:] = tip1.uv
    # 
    AMIP1_VK = ncfile.createVariable('MIP_M1_VK', np.uint64, ('MIP_M1_MET',), zlib=True)
    AMIP1_VK.long_name = 'VK_Count_10Hz'
    AMIP1_VK.units = 'Cts/sec'
    AMIP1_VK[:] = mip1.VK
    # 
    """
    SUVM Variables
    """
    ATIPSVM_TIME = ncfile.createVariable('TIP_SUVM_TIME', np.uint32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_TIME.long_name = 'TIP_Scan_Mirror_Run_Time'
    ATIPSVM_TIME.units = 'seconds'
    ATIPSVM_TIME[:] = s2_gen.time
    AMIPSVM_TIME = ncfile.createVariable('MIP_SUVM_TIME', np.uint32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_TIME.long_name = 'MIP_Scan_Mirror_Run_Time'
    AMIPSVM_TIME.units = 'seconds'
    AMIPSVM_TIME[:] = s4_gen.time
    # 
    ATIPSVM_SEQ = ncfile.createVariable('TIP_SUVM_SEQUENCE', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_SEQ.long_name = 'TIP_Scan_Mirror_Sequence_Count'
    ATIPSVM_SEQ[:] = s2_gen.sequence_count
    AMIPSVM_SEQ = ncfile.createVariable('MIP_SUVM_SEQUENCE', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_SEQ.long_name = 'MIP_Scan_Mirror_Sequence_Count'
    AMIPSVM_SEQ[:] = s4_gen.sequence_count
    # 
    ATIPSVM_SYSCT = ncfile.createVariable('TIP_SUVM_System_Counter', np.uint64, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_SYSCT.long_name = 'TIP_Scan_Mirror_System_Counter'
    ATIPSVM_SYSCT.units = 'seconds'
    ATIPSVM_SYSCT[:] = s2_gen.system_counter
    AMIPSVM_SYSCT = ncfile.createVariable('MIP_SUVM_System_Counter', np.uint64, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_SYSCT.long_name = 'MIP_Scan_Mirror_System_Counter'
    AMIPSVM_SYSCT.units = 'seconds'
    AMIPSVM_SYSCT[:] = s4_gen.system_counter
    # 
    ATIPSVM_GPSPPS = ncfile.createVariable('TIP_SUVM_GPS_PPS', np.uint64, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_GPSPPS.long_name = 'TIP_Scan_Mirror_GPS_PPS'
    ATIPSVM_GPSPPS.units = 'seconds'
    ATIPSVM_GPSPPS[:] = s2_gen.system_counter
    AMIPSVM_GPSPPS = ncfile.createVariable('MIP_SUVM_GPS_PPS', np.uint64, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_GPSPPS.long_name = 'MIP_Scan_Mirror_GPS_PPS'
    AMIPSVM_GPSPPS.units = 'seconds'
    AMIPSVM_GPSPPS[:] = s4_gen.system_counter
    # 
    ATIPSVM_LASTCMD_STAT = ncfile.createVariable('TIP_SUVM_LAST_COMMAND_STATUS', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_LASTCMD_STAT.long_name = 'TIP_Scan_Mirror_Last_Command_Status'
    ATIPSVM_LASTCMD_STAT[:] = s2_gen.last_cmd_status
    AMIPSVM_LASTCMD_STAT = ncfile.createVariable('MIP_SUVM_LAST_COMMAND_STATUS', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_LASTCMD_STAT.long_name = 'MIP_Scan_Mirror_Last_Command_Status'
    AMIPSVM_LASTCMD_STAT[:] = s4_gen.last_cmd_status
    # 
    ATIPSVM_LASTCMD_ID = ncfile.createVariable('TIP_SUVM_LAST_COMMAND_ID', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_LASTCMD_ID.long_name = 'TIP_Scan_Mirror_Last_Command_ID'
    ATIPSVM_LASTCMD_ID[:] = s2_gen.last_cmd_id
    AMIPSVM_LASTCMD_ID = ncfile.createVariable('MIP_SUVM_LAST_COMMAND_ID', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_LASTCMD_ID.long_name = 'MIP_Scan_Mirror_Last_Command_ID'
    AMIPSVM_LASTCMD_ID[:] = s4_gen.last_cmd_id
    # 
    ATIPSVM_LASTCMD_OPCODE = ncfile.createVariable('TIP_SUVM_LAST_OP_CODE', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_LASTCMD_OPCODE.long_name = 'TIP_Scan_Mirror_Last_Command_Op_Code'
    ATIPSVM_LASTCMD_OPCODE[:] = s2_gen.last_cmd_opcode
    AMIPSVM_LASTCMD_OPCODE = ncfile.createVariable('MIP_SUVM_LAST_OP_CODE', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_LASTCMD_OPCODE.long_name = 'MIP_Scan_Mirror_Last_Command_Op_Code'
    AMIPSVM_LASTCMD_OPCODE[:] = s4_gen.last_cmd_opcode
    # 
    ATIPSVM_LASTCMD_TIME = ncfile.createVariable('TIP_SUVM_LAST_CMD_TIME', np.uint64, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_LASTCMD_TIME.long_name = 'TIP_Scan_Mirror_Last_Command_Time'
    ATIPSVM_LASTCMD_TIME.units = 'seconds'
    ATIPSVM_LASTCMD_TIME[:] = s2_gen.last_cmd_time
    AMIPSVM_LASTCMD_TIME = ncfile.createVariable('MIP_SUVM_LAST_CMD_TIME', np.uint64, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_LASTCMD_TIME.long_name = 'MIP_Scan_Mirror_Last_Command_Time'
    AMIPSVM_LASTCMD_TIME.units = 'seconds'
    AMIPSVM_LASTCMD_TIME[:] = s4_gen.last_cmd_time
    # 
    ATIPSVM_LASTCMD_SUCCESS = ncfile.createVariable('TIP_SUVM_LAST_CMD_SUCCESS', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_LASTCMD_SUCCESS.long_name = 'TIP_Scan_Mirror_Last_Command_Success'
    ATIPSVM_LASTCMD_SUCCESS[:] = s2_gen.cmd_success
    AMIPSVM_LASTCMD_SUCCESS = ncfile.createVariable('MIP_SUVM_LAST_CMD_SUCCESS', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_LASTCMD_SUCCESS.long_name = 'MIP_Scan_Mirror_Last_Command_Success'
    AMIPSVM_LASTCMD_SUCCESS[:] = s4_gen.cmd_success
    # 
    ATIPSVM_LASTCMD_FAIL = ncfile.createVariable('TIP_SUVM_LAST_CMD_FAIL', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_LASTCMD_FAIL.long_name = 'TIP_Scan_Mirror_Last_Command_Fail'
    ATIPSVM_LASTCMD_FAIL[:] = s2_gen.cmd_fail
    AMIPSVM_LASTCMD_FAIL = ncfile.createVariable('MIP_SUVM_LAST_CMD_FAIL', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_LASTCMD_FAIL.long_name = 'MIP_Scan_Mirror_Last_Command_Fail'
    AMIPSVM_LASTCMD_FAIL[:] = s4_gen.cmd_fail
    # 
    ATIPSVM_LASTCRC = ncfile.createVariable('TIP_SUVM_LAST_CRC', np.uint32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_LASTCRC.long_name = 'TIP_Scan_Mirror_Last_CRC'
    ATIPSVM_LASTCRC[:] = s2_gen.last_crc
    AMIPSVM_LASTCRC = ncfile.createVariable('MIP_SUVM_LAST_CRC', np.uint32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_LASTCRC.long_name = 'MIP_Scan_Mirror_Last_CRC'
    AMIPSVM_LASTCRC[:] = s4_gen.last_crc
    # 
    ATIPSVM_V5IMON = ncfile.createVariable('TIP_SUVM_V5_IMON', np.float3232, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_V5IMON.long_name = 'TIP_Scan_Mirror_5V_Current_Monitor'
    ATIPSVM_V5IMON.units = 'Amperes'
    ATIPSVM_V5IMON[:] = s2_gen.V5_IMON
    AMIPSVM_V5IMON = ncfile.createVariable('MIP_SUVM_V5_IMON', np.float3232, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_V5IMON.long_name = 'MIP_Scan_Mirror_5V_Current_Monitor'
    AMIPSVM_V5IMON.units = 'Amperes'
    AMIPSVM_V5IMON[:] = s4_gen.V5_IMON
    # 
    ATIPSVM_V5VMON = ncfile.createVariable('TIP_SUVM_V5_VMON', np.float3232, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_V5VMON.long_name = 'TIP_Scan_Mirror_5V_Voltage_Monitor'
    ATIPSVM_V5VMON.units = 'Volts'
    ATIPSVM_V5VMON[:] = s2_gen.V5_VMON
    AMIPSVM_V5VMON = ncfile.createVariable('MIP_SUVM_V5_VMON', np.float3232, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_V5VMON.long_name = 'MIP_Scan_Mirror_5V_Voltage_Monitor'
    AMIPSVM_V5VMON.units = 'Volts'
    AMIPSVM_V5VMON[:] = s4_gen.V5_VMON
    # 
    ATIPSVM_V3IMON = ncfile.createVariable('TIP_SUVM_V3_IMON', np.float3232, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_V3IMON.long_name = 'TIP_Scan_Mirror_3V_Current_Monitor'
    ATIPSVM_V3IMON.units = 'Amperes'
    ATIPSVM_V3IMON[:] = s2_gen.V3_IMON
    AMIPSVM_V3IMON = ncfile.createVariable('MIP_SUVM_V3_IMON', np.float3232, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_V3IMON.long_name = 'MIP_Scan_Mirror_3V_Current_Monitor'
    AMIPSVM_V3IMON.units = 'Amperes'
    AMIPSVM_V3IMON[:] = s4_gen.V3_IMON
    # 
    ATIPSVM_V3VMON = ncfile.createVariable('TIP_SUVM_V3_VMON', np.float3232, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_V3VMON.long_name = 'TIP_Scan_Mirror_3V_Voltage_Monitor'
    ATIPSVM_V3VMON.units = 'Volts'
    ATIPSVM_V3VMON[:] = s2_gen.V3_VMON
    AMIPSVM_V3VMON = ncfile.createVariable('MIP_SUVM_V3_VMON', np.float3232, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_V3VMON.long_name = 'MIP_Scan_Mirror_3V_Voltage_Monitor'
    AMIPSVM_V3VMON.units = 'Volts'
    AMIPSVM_V3VMON[:] = s4_gen.V3_VMON
    # 
    ATIPSVM_V22IMON = ncfile.createVariable('TIP_SUVM_V22_IMON', np.float3232, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_V22IMON.long_name = 'TIP_Scan_Mirror_22V_Current_Monitor'
    ATIPSVM_V22IMON.units = 'Amperes'
    ATIPSVM_V22IMON[:] = s2_gen.V22_IMON
    AMIPSVM_V22IMON = ncfile.createVariable('MIP_SUVM_V22_IMON', np.float3232, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_V22IMON.long_name = 'MIP_Scan_Mirror_22V_Current_Monitor'
    AMIPSVM_V22IMON.units = 'Amperes'
    AMIPSVM_V22IMON[:] = s4_gen.V22_IMON
    # 
    ATIPSVM_V22VMON = ncfile.createVariable('TIP_SUVM_V22_VMON', np.float3232, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_V22VMON.long_name = 'TIP_Scan_Mirror_22V_Voltage_Monitor'
    ATIPSVM_V22VMON.units = 'Volts'
    ATIPSVM_V22VMON[:] = s2_gen.V22_VMON
    AMIPSVM_V22VMON = ncfile.createVariable('MIP_SUVM_V22_VMON', np.float3232, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_V22VMON.long_name = 'MIP_Scan_Mirror_22V_Voltage_Monitor'
    AMIPSVM_V22VMON.units = 'Volts'
    AMIPSVM_V22VMON[:] = s4_gen.V22_VMON
    # 
    ATIPSVM_MOTORIMON = ncfile.createVariable('TIP_SUVM_MOTOR_IMON', np.float3232, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_MOTORIMON.long_name = 'TIP_Scan_Mirror_Motor_Current_Monitor'
    ATIPSVM_MOTORIMON.units = 'Amperes'
    ATIPSVM_MOTORIMON[:] = s2_gen.MOTOR_IMON
    AMIPSVM_MOTORIMON = ncfile.createVariable('MIP_SUVM_MOTOR_IMON', np.float3232, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_MOTORIMON.long_name = 'MIP_Scan_Mirror_Motor_Current_Monitor'
    AMIPSVM_MOTORIMON.units = 'Amperes'
    AMIPSVM_MOTORIMON[:] = s4_gen.MOTOR_IMON
    # 
    ATIPSVM_TEMP = ncfile.createVariable('TIP_SUVM_TEMP', np.float3232, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_TEMP.long_name = 'TIP_Scan_Mirror_Temperature'
    ATIPSVM_TEMP.units = 'Celsius'
    ATIPSVM_TEMP[:] = s2_gen.temperature
    AMIPSVM_TEMP = ncfile.createVariable('MIP_SUVM_TEMP', np.float3232, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_TEMP.long_name = 'MIP_Scan_Mirror_Temperature'
    AMIPSVM_TEMP.units = 'Celsius'
    AMIPSVM_TEMP[:] = s4_gen.temperature
    # 
    ATIPSVM_ENCZERO_OFFSET = ncfile.createVariable('TIP_SUVM_ENCODER_ZERO_OFFSET', np.short, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_ENCZERO_OFFSET.long_name = 'TIP_Scan_Mirror_Encoder_Zero_Offset'
    ATIPSVM_ENCZERO_OFFSET[:] = s2_gen.encoder_zero_offset
    AMIPSVM_ENCZERO_OFFSET = ncfile.createVariable('MIP_SUVM_ENCODER_ZERO_OFFSET', np.short, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_ENCZERO_OFFSET.long_name = 'MIP_Scan_Mirror_Encoder_Zero_Offset'
    AMIPSVM_ENCZERO_OFFSET[:] = s4_gen.encoder_zero_offset
    # 
    ATIPSVM_ENC_COUNT = ncfile.createVariable('TIP_SUVM_ENCODER_CURRENT_CT', np.short, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_ENC_COUNT.long_name = 'TIP_Scan_Mirror_Encoder_Current_Count'
    ATIPSVM_ENC_COUNT[:] = s2_gen.encoder_current_ct
    AMIPSVM_ENC_COUNT = ncfile.createVariable('MIP_SUVM_ENCODER_CURRENT_CT', np.short, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_ENC_COUNT.long_name = 'MIP_Scan_Mirror_Encoder_Current_Count'
    AMIPSVM_ENC_COUNT[:] = s4_gen.encoder_current_ct
    # 
    ATIPSVM_ENC_TARGET = ncfile.createVariable('TIP_SUVM_ENCODER_TARGET', np.short, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_ENC_TARGET.long_name = 'TIP_Scan_Mirror_Encoder_Target'
    ATIPSVM_ENC_TARGET[:] = s2_gen.encoder_target
    AMIPSVM_ENC_TARGET = ncfile.createVariable('MIP_SUVM_ENCODER_TARGET', np.short, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_ENC_TARGET.long_name = 'MIP_Scan_Mirror_Encoder_Target'
    AMIPSVM_ENC_TARGET[:] = s4_gen.encoder_target
    # 
    ATIPSVM_PROFIDX = ncfile.createVariable('TIP_SUVM_ENCODER_PROFILE_INDEX', np.uint16, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_PROFIDX.long_name = 'TIP_Scan_Mirror_Encoder_Profile_Index'
    ATIPSVM_PROFIDX[:] = s2_gen.profile_index
    AMIPSVM_PROFIDX = ncfile.createVariable('MIP_SUVM_ENCODER_PROFILE_INDEX', np.uint16, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_PROFIDX.long_name = 'MIP_Scan_Mirror_Encoder_Profile_Index'
    AMIPSVM_PROFIDX[:] = s4_gen.profile_index
    # 
    ATIPSVM_PWMRATE = ncfile.createVariable('TIP_SUVM_PWM_RATE', np.uint32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_PWMRATE.long_name = 'TIP_Scan_Mirror_Motor_PWM_Rate'
    ATIPSVM_PWMRATE.units = 'Hz'
    ATIPSVM_PWMRATE[:] = s2_gen.pwm_rate
    AMIPSVM_PWMRATE = ncfile.createVariable('MIP_SUVM_PWM_RATE', np.uint32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_PWMRATE.long_name = 'MIP_Scan_Mirror_Motor_PWM_Rate'
    AMIPSVM_PWMRATE.units = 'Hz'
    AMIPSVM_PWMRATE[:] = s4_gen.pwm_rate
    # 
    ATIPSVM_PWMCTS_REMAIN = ncfile.createVariable('TIP_SUVM_PWM_CTS_REMAIN', np.uint32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_PWMCTS_REMAIN.long_name = 'TIP_Scan_Mirror_Motor_PWM_Counts_Remain'
    ATIPSVM_PWMCTS_REMAIN[:] = s2_gen.pwm_counts_remain
    AMIPSVM_PWMCTS_REMAIN = ncfile.createVariable('MIP_SUVM_PWM_CTS_REMAIN', np.uint32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_PWMCTS_REMAIN.long_name = 'MIP_Scan_Mirror_Motor_PWM_Counts_Remain'
    AMIPSVM_PWMCTS_REMAIN[:] = s4_gen.pwm_counts_remain
    # 
    ATIPSVM_CRC = ncfile.createVariable('TIP_SUVM_CRC', np.uint32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_CRC.long_name = 'TIP_Scan_Mirror_CRC'
    ATIPSVM_CRC[:] = s2_gen.crc
    AMIPSVM_CRC = ncfile.createVariable('MIP_SUVM_CRC', np.uint32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_CRC.long_name = 'MIP_Scan_Mirror_CRC'
    AMIPSVM_CRC[:] = s4_gen.crc
    # 
    ATIPSVM_ENCANGLE = ncfile.createVariable('TIP_SUVM_ENCODER_ANGLE', np.float3232, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_ENCANGLE.long_name = 'TIP_Scan_Mirror_Encoder_Angle'
    ATIPSVM_ENCANGLE.units = 'Degrees'
    ATIPSVM_ENCANGLE[:] = s2_gen.encoder_angle
    AMIPSVM_ENCANGLE = ncfile.createVariable('MIP_SUVM_ENCODER_ANGLE', np.float3232, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_ENCANGLE.long_name = 'MIP_Scan_Mirror_Encoder_Angle'
    AMIPSVM_ENCANGLE.units = 'Degrees'
    AMIPSVM_ENCANGLE[:] = s4_gen.encoder_angle
    # 
    ATIPSVM_TGTANGLE = ncfile.createVariable('TIP_SUVM_ENCODER_TARGET_ANGLE', np.float3232, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_TGTANGLE.long_name = 'TIP_Scan_Mirror_Encoder_Target_Angle'
    ATIPSVM_TGTANGLE.units = 'Degrees'
    ATIPSVM_TGTANGLE[:] = s2_gen.target_angle
    AMIPSVM_TGTANGLE = ncfile.createVariable('MIP_SUVM_ENCODER_TARGET_ANGLE', np.float3232, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_TGTANGLE.long_name = 'MIP_Scan_Mirror_Encoder_Target_Angle'
    AMIPSVM_TGTANGLE.units = 'Degrees'
    AMIPSVM_TGTANGLE[:] = s4_gen.target_angle
    # 
    
    print(ncfile)
    ncfile.close()
    
    print(' ALS File Complete: ' + outname)
    print('')
    
    """
    Unused SUVM bits                                        # Byte
    # self.header             = np.zeros(n, dtype='uintc')  #  0
    # self.apid               = np.zeros(n, dtype='ubyte')  #  4
    # self.length             = np.zeros(n, dtype='uint16') #  6
    # self.watchdog_counter   = np.zeros(n, dtype='uint32') # 24
    # self.version            = np.zeros(n, dtype='uint32') # 28
    # self.reset_status       = np.zeros(n, dtype='ubyte')  # 32
    # self.flash_last_op      = np.zeros(n, dtype='ubyte')  # 46
    # self.flash_status       = np.zeros(n, dtype='ubyte')  # 47
    # self.general_hk_flags   = np.zeros(n, dtype='uint32') # 48
    # self.ROM_SBE            = np.zeros(n, dtype='uint16') # 56
    # self.ROM_MBE            = np.zeros(n, dtype='uint16') # 58
    # self.RAM_SBE            = np.zeros(n, dtype='uint16') # 60
    # self.RAM_MBE            = np.zeros(n, dtype='uint16') # 62
    # self.GPIO_A             = np.zeros(n, dtype='uint32') # 64
    # self.GPIO_B             = np.zeros(n, dtype='uint32') # 68
    # self.launch_lock_flags  = np.zeros(n, dtype='uint32') # 72
    # self.VC_LIMIT_CHECK     = np.zeros(n, dtype='uint16') # 76
    # self.motor_flags        = np.zeros(n, dtype='uint16') # 104
    """

def ECL_L0_CTS(fname, ebyte):
    try: ncfile.close()  # just to be safe, make sure dataset is not already open.
    except: pass
    
    (fpath, fbase_ext) = path.split(fname)
    (fbase, f_ext) = path.splitext(fbase_ext)
    
    fnew_ext = f"{fbase}_ECLIPSE_L0_CTS.nc"
    outname = path.join(fpath, 'L0_CTS', fnew_ext)
    
    print('Starting to generate the file ... ')
    print(' ... ' + outname)
    print('')
    
    tip0 = xpc.convert_m0_byt2dec(ebyte.tip5_m0,'TIP')
    tip1 = xpc.convert_m1_byt2dec(ebyte.tip5_m1,'TIP')
    mip0 = xpc.convert_m0_byt2dec(ebyte.mip7_m0,'MIP')
    mip1 = xpc.convert_m1_byt2dec(ebyte.mip7_m1,'MIP')
    # 
    suvm6_byte = etb.breakout_suvm_packet(ebyte.suvm6)
    s6_gen = spc.suvm_general_converter(suvm6_byte)
    suvm8_byte = etb.breakout_suvm_packet(ebyte.suvm8)
    s8_gen = spc.suvm_general_converter(suvm8_byte)
    # 
    # Generate a NetCDF File
    # 
    ncfile = Dataset(outname,mode='w',format='NETCDF4') 
    # 
    # Define Dimensions
    time_dim_t0 = ncfile.createDimension('TIP_M0_MET', len(tip0.MET))
    time_dim_t1 = ncfile.createDimension('TIP_M1_MET', len(tip1.MET))
    time_dim_ts = ncfile.createDimension('TIP_SUVM_TIME', len(s6_gen.time))
    time_dim_m0 = ncfile.createDimension('MIP_M0_MET', len(mip0.MET))
    time_dim_m1 = ncfile.createDimension('MIP_M1_MET', len(mip1.MET))
    time_dim_ms = ncfile.createDimension('MIP_SUVM_TIME', len(s8_gen.time))
    # 
    # Create Attributes
    # 
    ### REQUIRED GLOBAL ATTRIBUTES
    ECL_global_attributes(ncfile)
    ### GLOBAL ATTRIBUTES specific to this file type
    ncfile.source_1 = fbase_ext
    ncfile.source_2 = 'TBD - Will be ISS telemetry file'
    ncfile.filename = outname
    ncfile.data_version = 'Raw Data'
    """ 
    # XIP Variables
    
    M0 Vlues Not included:
    #         self.IDC_ID = np.zeros(n, dtype='U4')
    #         self.MODE             = np.zeros(n, dtype='U2')
    """
    CTIP0_MET = ncfile.createVariable('TIP_M0_MET', np.uint64, ('TIP_M0_MET',), zlib=True)
    CTIP0_MET.units = 'seconds'
    CTIP0_MET.long_name = 'mission_elapsed_time'
    CTIP0_MET[:] = tip0.MET
    CMIP0_MET = ncfile.createVariable('MIP_M0_MET', np.uint64, ('MIP_M0_MET',), zlib=True)
    CMIP0_MET.units = 'seconds'
    CMIP0_MET.long_name = 'mission_elapsed_time'
    CMIP0_MET[:] = mip0.MET
    # 
    CTIP0_TIME = ncfile.createVariable('TIP_M0_TIME', np.uint64, ('TIP_M0_MET',), zlib=True)
    CTIP0_TIME.units = 'seconds'
    CTIP0_TIME.long_name = 'system_run_time'
    CTIP0_TIME[:] = tip0.time
    CMIP0_TIME = ncfile.createVariable('MIP_M0_TIME', np.uint64, ('MIP_M0_MET',), zlib=True)
    CMIP0_TIME.units = 'seconds'
    CMIP0_TIME.long_name = 'system_run_time'
    CMIP0_TIME[:] = mip0.time
    # 
    CTIP0_DARK = ncfile.createVariable('TIP_M0_DARK', np.uint64, ('TIP_M0_MET',), zlib=True)
    CTIP0_DARK.units = 'counts/sec'
    CTIP0_DARK.long_name = 'dark_PMT_counts'
    CTIP0_DARK[:] = tip0.dark
    CMIP0_DARK = ncfile.createVariable('MIP_M0_DARK', np.uint64, ('MIP_M0_MET',), zlib=True)
    CMIP0_DARK.units = 'counts/sec'
    CMIP0_DARK.long_name = 'dark_PMT_counts'
    CMIP0_DARK[:] = mip0.dark
    # 
    CTIP0_RED = ncfile.createVariable('TIP_M0_RED', np.uint64, ('TIP_M0_MET',), zlib=True)
    CTIP0_RED.units = 'counts/sec'
    CTIP0_RED.long_name = 'red_PMT_counts'
    CTIP0_RED[:] = tip0.red
    # 
    CMIP0_MG = ncfile.createVariable('MIP_M0_MG', np.uint64, ('MIP_M0_MET',), zlib=True)
    CMIP0_MG.units = 'counts/sec'
    CMIP0_MG.long_name = 'Mg_PMT_counts'
    CMIP0_MG[:] = mip0.Mg
    # 
    CTIP0_UV = ncfile.createVariable('TIP_M0_UV', np.uint64, ('TIP_M0_MET',), zlib=True)
    CTIP0_UV.units = 'counts/sec'
    CTIP0_UV.long_name = 'uv_PMT_counts'
    CTIP0_UV[:] = tip0.uv
    # 
    CMIP0_VK = ncfile.createVariable('MIP_M0_VK', np.uint64, ('MIP_M0_MET',), zlib=True)
    CMIP0_VK.units = 'counts/sec'
    CMIP0_VK.long_name = 'VK_PMT_counts'
    CMIP0_VK[:] = mip0.VK
    # 
    CTIP0_HEATER = ncfile.createVariable('TIP_M0_HEATER', np.uint32, ('TIP_M0_MET',), zlib=True)
    CTIP0_HEATER.long_name = 'heater_duty_cycle'
    CTIP0_HEATER[:] = tip0.heater
    # 
    # CMIP0_ERROR = ncfile.createVariable('MIP_M0_ERROR', np.uint32, ('MIP_M0_MET',), zlib=True)
    # CMIP0_ERROR.long_name = 'error'
    # CMIP0_ERROR[:] = mip0.error
    # 
    CTIP0_TF1 = ncfile.createVariable('TIP_M0_TF1', np.float32, ('TIP_M0_MET',), zlib=True)
    CTIP0_TF1.units = 'Celsius'
    CTIP0_TF1.long_name = 'filter_temperature_1'
    CTIP0_TF1[:] = tip0.T_F1
    # 
    CMIP0_TLENS = ncfile.createVariable('MIP_M0_TLENS', np.float32, ('MIP_M0_MET',), zlib=True)
    CMIP0_TLENS.units = 'Celsius'
    CMIP0_TLENS.long_name = 'Lens_temperature'
    CMIP0_TLENS[:] = mip0.T_LENS
    # 
    CTIP0_TF2 = ncfile.createVariable('TIP_M0_TF2', np.float32, ('TIP_M0_MET',), zlib=True)
    CTIP0_TF2.units = 'Celsius'
    CTIP0_TF2.long_name = 'filter_temperature_2'
    CTIP0_TF2[:] = tip0.T_F2
    #
    CMIP0_TPMT = ncfile.createVariable('MIP_M0_TPMT', np.float32, ('MIP_M0_MET',), zlib=True)
    CMIP0_TPMT.units = 'Celsius'
    CMIP0_TPMT.long_name = 'PMT_block_temperature'
    CMIP0_TPMT[:] = mip0.T_PMT
    #
    CTIP0_HVMON = ncfile.createVariable('TIP_M0_HV_mon', np.float32, ('TIP_M0_MET',), zlib=True)
    CTIP0_HVMON.units = 'Volts'
    CTIP0_HVMON.long_name = 'High_voltage_monitor'
    CTIP0_HVMON[:] = tip0.HV_mon
    CMIP0_HVMON = ncfile.createVariable('MIP_M0_HV_mon', np.float32, ('MIP_M0_MET',), zlib=True)
    CMIP0_HVMON.units = 'Volts'
    CMIP0_HVMON.long_name = 'High_voltage_monitor'
    CMIP0_HVMON[:] = mip0.HV_mon
    #
    CTIP0_HVADJ = ncfile.createVariable('TIP_M0_HV_adj', np.float32, ('TIP_M0_MET',), zlib=True)
    CTIP0_HVADJ.units = 'Volts'
    CTIP0_HVADJ.long_name = 'High_voltage_adjust'
    CTIP0_HVADJ[:] = tip0.HV_adj
    CMIP0_HVADJ = ncfile.createVariable('MIP_M0_HV_adj', np.float32, ('MIP_M0_MET',), zlib=True)
    CMIP0_HVADJ.units = 'Volts'
    CMIP0_HVADJ.long_name = 'High_voltage_adjust'
    CMIP0_HVADJ[:] = mip0.HV_adj
    #
    CTIP0_SUN = ncfile.createVariable('TIP_M0_sun', np.float32, ('TIP_M0_MET',), zlib=True)
    CTIP0_SUN.units = 'Volts'
    CTIP0_SUN.long_name = 'sun_sensor'
    CTIP0_SUN[:] = tip0.sun
    CMIP0_SUN = ncfile.createVariable('MIP_M0_sun', np.float32, ('MIP_M0_MET',), zlib=True)
    CMIP0_SUN.units = 'Volts'
    CMIP0_SUN.long_name = 'sun_sensor'
    CMIP0_SUN[:] = mip0.sun
    #
    CTIP0_VREF = ncfile.createVariable('TIP_M0_VREF', np.float32, ('TIP_M0_MET',), zlib=True)
    CTIP0_VREF.units = 'Volts'
    CTIP0_VREF.long_name = 'reference_voltage_2p5V'
    CTIP0_VREF[:] = tip0.vref
    CMIP0_VREF = ncfile.createVariable('MIP_M0_VREF', np.float32, ('MIP_M0_MET',), zlib=True)
    CMIP0_VREF.units = 'Volts'
    CMIP0_VREF.long_name = 'reference_voltage_2p5V'
    CMIP0_VREF[:] = mip0.vref
    #
    CTIP0_TIDC = ncfile.createVariable('TIP_M0_TIDC', np.float32, ('TIP_M0_MET',), zlib=True)
    CTIP0_TIDC.units = 'Celsius'
    CTIP0_TIDC.long_name = 'IDC_temperature'
    CTIP0_TIDC[:] = tip0.T_IDC
    CMIP0_TIDC = ncfile.createVariable('MIP_M0_TIDC', np.float32, ('MIP_M0_MET',), zlib=True)
    CMIP0_TIDC.units = 'Celsius'
    CMIP0_TIDC.long_name = 'IDC_temperature'
    CMIP0_TIDC[:] = mip0.T_IDC
    #
    CTIP0_THV = ncfile.createVariable('TIP_M0_HV', np.float32, ('TIP_M0_MET',), zlib=True)
    CTIP0_THV.units = 'Celsius'
    CTIP0_THV.long_name = 'high_voltage_temperature'
    CTIP0_THV[:] = tip0.T_HV
    CMIP0_THV = ncfile.createVariable('MIP_M0_HV', np.float32, ('MIP_M0_MET',), zlib=True)
    CMIP0_THV.units = 'Celsius'
    CMIP0_THV.long_name = 'high_voltage_temperature'
    CMIP0_THV[:] = mip0.T_HV
    #
    # CTIP0_DISCRETE = ncfile.createVariable('TIP_M0_DISCRETE', np.str, ('TIP_M0_MET',), zlib=True)
    # CTIP0_DISCRETE.long_name = 'discrete'
    # CTIP0_DISCRETE[:] = tip0.discrete
    # CMIP0_DISCRETE = ncfile.createVariable('MIP_M0_DISCRETE', np.str, ('MIP_M0_MET',), zlib=True)
    # CMIP0_DISCRETE.long_name = 'discrete'
    # CMIP0_DISCRETE[:] = mip0.discrete
    #
    CTIP0_HVSTAT = ncfile.createVariable('TIP_M0_HV_Status', np.ubyte, ('TIP_M0_MET',), zlib=True)
    CTIP0_HVSTAT.long_name = 'High_Voltage_Status'
    CTIP0_HVSTAT[:] = tip0.HV_STATUS
    CMIP0_HVSTAT = ncfile.createVariable('MIP_M0_HV_Status', np.ubyte, ('MIP_M0_MET',), zlib=True)
    CMIP0_HVSTAT.long_name = 'High_Voltage_Status'
    CMIP0_HVSTAT[:] = mip0.HV_STATUS
    # 
    CTIP0_HVEVENT = ncfile.createVariable('TIP_M0_HV_Event', np.ubyte, ('TIP_M0_MET',), zlib=True)
    CTIP0_HVEVENT.long_name = 'High_Voltage_Exceed_Threshold'
    CTIP0_HVEVENT[:] = tip0.HV_EVENT
    CMIP0_HVEVENT = ncfile.createVariable('MIP_M0_HV_Event', np.ubyte, ('MIP_M0_MET',), zlib=True)
    CMIP0_HVEVENT.long_name = 'High_Voltage_Exceed_Threshold'
    CMIP0_HVEVENT[:] = mip0.HV_EVENT
    # 
    CTIP0_SUNEVENT = ncfile.createVariable('TIP_M0_Sun_Event', np.ubyte, ('TIP_M0_MET',), zlib=True)
    CTIP0_SUNEVENT.long_name = 'Sun_Sensor_Exceed_Threshold'
    CTIP0_SUNEVENT[:] = tip0.SUN_EVENT
    CMIP0_SUNEVENT = ncfile.createVariable('MIP_M0_Sun_Event', np.ubyte, ('MIP_M0_MET',), zlib=True)
    CMIP0_SUNEVENT.long_name = 'Sun_Sensor_Exceed_Threshold'
    CMIP0_SUNEVENT[:] = mip0.SUN_EVENT
    # 
    CTIP0_DKEVENT = ncfile.createVariable('TIP_M0_DK_EVENT', np.ubyte, ('TIP_M0_MET',), zlib=True)
    CTIP0_DKEVENT.long_name = 'PMT_Dark_Pad_Exceed_Threshold'
    CTIP0_DKEVENT[:] = tip0.DK_EVENT
    CMIP0_DKEVENT = ncfile.createVariable('MIP_M0_DK_EVENT', np.ubyte, ('MIP_M0_MET',), zlib=True)
    CMIP0_DKEVENT.long_name = 'PMT_Dark_Pad_Exceed_Threshold'
    CMIP0_DKEVENT[:] = mip0.DK_EVENT
    # 
    CTIP0_RDEVENT = ncfile.createVariable('TIP_M0_RD_EVENT', np.ubyte, ('TIP_M0_MET',), zlib=True)
    CTIP0_RDEVENT.long_name = 'PMT_Red_Pad_Exceed_Threshold'
    CTIP0_RDEVENT[:] = tip0.RD_EVENT
    CMIP0_RDEVENT = ncfile.createVariable('MIP_M0_RD_EVENT', np.ubyte, ('MIP_M0_MET',), zlib=True)
    CMIP0_RDEVENT.long_name = 'PMT_Red_Pad_Exceed_Threshold'
    CMIP0_RDEVENT[:] = mip0.RD_EVENT
    # 
    CTIP0_UVEVENT = ncfile.createVariable('TIP_M0_UV_EVENT', np.ubyte, ('TIP_M0_MET',), zlib=True)
    CTIP0_UVEVENT.long_name = 'PMT_UV_Pad_Exceed_Threshold'
    CTIP0_UVEVENT[:] = tip0.UV_EVENT
    CMIP0_UVEVENT = ncfile.createVariable('MIP_M0_UV_EVENT', np.ubyte, ('MIP_M0_MET',), zlib=True)
    CMIP0_UVEVENT.long_name = 'PMT_UV_Pad_Exceed_Threshold'
    CMIP0_UVEVENT[:] = mip0.UV_EVENT
    # 
    CTIP0_SUNOVERRIDE = ncfile.createVariable('TIP_M0_Sun_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    CTIP0_SUNOVERRIDE.long_name = 'Sun_Sensor_Override'
    CTIP0_SUNOVERRIDE[:] = tip0.SUN_OVERRIDE
    CMIP0_SUNOVERRIDE = ncfile.createVariable('MIP_M0_Sun_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    CMIP0_SUNOVERRIDE.long_name = 'Sun_Sensor_Override'
    CMIP0_SUNOVERRIDE[:] = mip0.SUN_OVERRIDE
    # 
    CTIP0_DKOVERRIDE = ncfile.createVariable('TIP_M0_Dark_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    CTIP0_DKOVERRIDE.long_name = 'Dark_Count_Override'
    CTIP0_DKOVERRIDE[:] = tip0.DK_OVERRIDE
    CMIP0_DKOVERRIDE = ncfile.createVariable('MIP_M0_Dark_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    CMIP0_DKOVERRIDE.long_name = 'Dark_Count_Override'
    CMIP0_DKOVERRIDE[:] = mip0.DK_OVERRIDE
    # 
    CTIP0_RD_OVERRIDE = ncfile.createVariable('TIP_M0_Red_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    CTIP0_RD_OVERRIDE.long_name = 'Red_Count_Override'
    CTIP0_RD_OVERRIDE[:] = tip0.RD_OVERRIDE
    CMIP0_RD_OVERRIDE = ncfile.createVariable('MIP_M0_Red_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    CMIP0_RD_OVERRIDE.long_name = 'Red_Count_Override'
    CMIP0_RD_OVERRIDE[:] = mip0.RD_OVERRIDE
    # 
    CTIP0_UVOVERRIDE = ncfile.createVariable('TIP_M0_UV_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    CTIP0_UVOVERRIDE.long_name = 'UV_Count_Override'
    CTIP0_UVOVERRIDE[:] = tip0.UV_OVERRIDE
    CMIP0_UVOVERRIDE = ncfile.createVariable('MIP_M0_UV_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    CMIP0_UVOVERRIDE.long_name = 'UV_Count_Override'
    CMIP0_UVOVERRIDE[:] = mip0.UV_OVERRIDE
    # 
    CTIP0_HVOVERRIDE = ncfile.createVariable('TIP_M0_HV_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    CTIP0_HVOVERRIDE.long_name = 'High_Voltage_Override'
    CTIP0_HVOVERRIDE[:] = tip0.HV_OVERRIDE
    CMIP0_HVOVERRIDE = ncfile.createVariable('MIP_M0_HV_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    CMIP0_HVOVERRIDE.long_name = 'High_Voltage_Override'
    CMIP0_HVOVERRIDE[:] = mip0.HV_OVERRIDE
    # 
    CTIP0_SHUTTEROVERRIDE = ncfile.createVariable('TIP_M0_Shutter_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    CTIP0_SHUTTEROVERRIDE.long_name = 'Shutter_Override'
    CTIP0_SHUTTEROVERRIDE[:] = tip0.SHUTTER_OVERRIDE
    CMIP0_SHUTTEROVERRIDE = ncfile.createVariable('MIP_M0_Shutter_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    CMIP0_SHUTTEROVERRIDE.long_name = 'Shutter_Override'
    CMIP0_SHUTTEROVERRIDE[:] = mip0.SHUTTER_OVERRIDE
    # 
    CTIP0_V5OVERRIDE = ncfile.createVariable('TIP_M0_5V_Override', np.ubyte, ('TIP_M0_MET',), zlib=True)
    CTIP0_V5OVERRIDE.long_name = '5V_Override'
    CTIP0_V5OVERRIDE[:] = tip0.V5_OVERRIDE
    CMIP0_V5OVERRIDE = ncfile.createVariable('MIP_M0_5V_Override', np.ubyte, ('MIP_M0_MET',), zlib=True)
    CMIP0_V5OVERRIDE.long_name = '5V_Override'
    CMIP0_V5OVERRIDE[:] = mip0.V5_OVERRIDE
    """
    # M1 Variables
    
    Not included: 
        # tip1 / mip1 .dark_chk = np.zeros(10*n, dtype='uint64')
        # tip1        .red_chk = np.zeros(n, dtype='uint64')
        # tip1        .uv_chk  = np.zeros(n, dtype='uint64')
        # mip1        .Mg_chk = np.zeros(n, dtype='uint64')
        # mip1        .VK_chk = np.zeros(n, dtype='uint64')

    """
    CTIP1_MET = ncfile.createVariable('TIP_M1_MET', np.uint64, ('TIP_M1_MET',), zlib=True)
    CTIP1_MET.long_name = 'Mission_Elapsed_Time_10Hz'
    CTIP1_MET.units = 'Seconds'
    CTIP1_MET[:] = tip1.MET
    CMIP1_MET = ncfile.createVariable('MIP_M1_MET', np.uint64, ('MIP_M1_MET',), zlib=True)
    CMIP1_MET.long_name = 'Mission_Elapsed_Time_10Hz'
    CMIP1_MET.units = 'Seconds'
    CMIP1_MET[:] = mip1.MET
    # 
    CTIP1_TIME = ncfile.createVariable('TIP_M1_RUNTIME', np.uint64, ('TIP_M1_MET',), zlib=True)
    CTIP1_TIME.long_name = 'System_Run_Time_10Hz'
    CTIP1_TIME.units = 'Seconds'
    CTIP1_TIME[:] = tip1.time
    CMIP1_TIME = ncfile.createVariable('MIP_M1_RUNTIME', np.uint64, ('MIP_M1_MET',), zlib=True)
    CMIP1_TIME.long_name = 'System_Run_Time_10Hz'
    CMIP1_TIME.units = 'Seconds'
    CMIP1_TIME[:] = mip1.time
    # 
    CTIP1_DARK = ncfile.createVariable('TIP_M1_DARK', np.uint64, ('TIP_M1_MET',), zlib=True)
    CTIP1_DARK.long_name = 'Dark_Count_10Hz'
    CTIP1_DARK.units = 'Cts/sec'
    CTIP1_DARK[:] = tip1.dark
    CMIP1_DARK = ncfile.createVariable('MIP_M1_DARK', np.uint64, ('MIP_M1_MET',), zlib=True)
    CMIP1_DARK.long_name = 'Dark_Count_10Hz'
    CMIP1_DARK.units = 'Cts/sec'
    CMIP1_DARK[:] = mip1.dark
    # 
    CTIP1_RED = ncfile.createVariable('TIP_M1_RED', np.uint64, ('TIP_M1_MET',), zlib=True)
    CTIP1_RED.long_name = 'Red_Count_10Hz'
    CTIP1_RED.units = 'Cts/sec'
    CTIP1_RED[:] = tip1.red
    # 
    CMIP1_MG = ncfile.createVariable('MIP_M1_MG', np.uint64, ('MIP_M1_MET',), zlib=True)
    CMIP1_MG.long_name = 'Mg_Count_10Hz'
    CMIP1_MG.units = 'Cts/sec'
    CMIP1_MG[:] = mip1.Mg
    # 
    CTIP1_UV = ncfile.createVariable('TIP_M1_UV', np.uint64, ('TIP_M1_MET',), zlib=True)
    CTIP1_UV.long_name = 'UV_Count_10Hz'
    CTIP1_UV.units = 'Cts/sec'
    CTIP1_UV[:] = tip1.uv
    # 
    CMIP1_VK = ncfile.createVariable('MIP_M1_VK', np.uint64, ('MIP_M1_MET',), zlib=True)
    CMIP1_VK.long_name = 'VK_Count_10Hz'
    CMIP1_VK.units = 'Cts/sec'
    CMIP1_VK[:] = mip1.VK
    # 
    """
    SUVM Variables
    """
    CTIPSVM_TIME = ncfile.createVariable('TIP_SUVM_TIME', np.uint32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_TIME.long_name = 'TIP_Scan_Mirror_Run_Time'
    CTIPSVM_TIME.units = 'seconds'
    CTIPSVM_TIME[:] = s6_gen.time
    CMIPSVM_TIME = ncfile.createVariable('MIP_SUVM_TIME', np.uint32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_TIME.long_name = 'MIP_Scan_Mirror_Run_Time'
    CMIPSVM_TIME.units = 'seconds'
    CMIPSVM_TIME[:] = s8_gen.time
    # 
    CTIPSVM_SEQ = ncfile.createVariable('TIP_SUVM_SEQUENCE', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_SEQ.long_name = 'TIP_Scan_Mirror_Sequence_Count'
    CTIPSVM_SEQ[:] = s6_gen.sequence_count
    CMIPSVM_SEQ = ncfile.createVariable('MIP_SUVM_SEQUENCE', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_SEQ.long_name = 'MIP_Scan_Mirror_Sequence_Count'
    CMIPSVM_SEQ[:] = s8_gen.sequence_count
    # 
    CTIPSVM_SYSCT = ncfile.createVariable('TIP_SUVM_System_Counter', np.uint64, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_SYSCT.long_name = 'TIP_Scan_Mirror_System_Counter'
    CTIPSVM_SYSCT.units = 'seconds'
    CTIPSVM_SYSCT[:] = s6_gen.system_counter
    CMIPSVM_SYSCT = ncfile.createVariable('MIP_SUVM_System_Counter', np.uint64, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_SYSCT.long_name = 'MIP_Scan_Mirror_System_Counter'
    CMIPSVM_SYSCT.units = 'seconds'
    CMIPSVM_SYSCT[:] = s8_gen.system_counter
    # 
    CTIPSVM_GPSPPS = ncfile.createVariable('TIP_SUVM_GPS_PPS', np.uint64, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_GPSPPS.long_name = 'TIP_Scan_Mirror_GPS_PPS'
    CTIPSVM_GPSPPS.units = 'seconds'
    CTIPSVM_GPSPPS[:] = s6_gen.system_counter
    CMIPSVM_GPSPPS = ncfile.createVariable('MIP_SUVM_GPS_PPS', np.uint64, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_GPSPPS.long_name = 'MIP_Scan_Mirror_GPS_PPS'
    CMIPSVM_GPSPPS.units = 'seconds'
    CMIPSVM_GPSPPS[:] = s8_gen.system_counter
    # 
    CTIPSVM_LASTCMD_STAT = ncfile.createVariable('TIP_SUVM_LAST_COMMAND_STATUS', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_LASTCMD_STAT.long_name = 'TIP_Scan_Mirror_Last_Command_Status'
    CTIPSVM_LASTCMD_STAT[:] = s6_gen.last_cmd_status
    CMIPSVM_LASTCMD_STAT = ncfile.createVariable('MIP_SUVM_LAST_COMMAND_STATUS', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_LASTCMD_STAT.long_name = 'MIP_Scan_Mirror_Last_Command_Status'
    CMIPSVM_LASTCMD_STAT[:] = s8_gen.last_cmd_status
    # 
    CTIPSVM_LASTCMD_ID = ncfile.createVariable('TIP_SUVM_LAST_COMMAND_ID', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_LASTCMD_ID.long_name = 'TIP_Scan_Mirror_Last_Command_ID'
    CTIPSVM_LASTCMD_ID[:] = s6_gen.last_cmd_id
    CMIPSVM_LASTCMD_ID = ncfile.createVariable('MIP_SUVM_LAST_COMMAND_ID', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_LASTCMD_ID.long_name = 'MIP_Scan_Mirror_Last_Command_ID'
    CMIPSVM_LASTCMD_ID[:] = s8_gen.last_cmd_id
    # 
    CTIPSVM_LASTCMD_OPCODE = ncfile.createVariable('TIP_SUVM_LAST_OP_CODE', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_LASTCMD_OPCODE.long_name = 'TIP_Scan_Mirror_Last_Command_Op_Code'
    CTIPSVM_LASTCMD_OPCODE[:] = s6_gen.last_cmd_opcode
    CMIPSVM_LASTCMD_OPCODE = ncfile.createVariable('MIP_SUVM_LAST_OP_CODE', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_LASTCMD_OPCODE.long_name = 'MIP_Scan_Mirror_Last_Command_Op_Code'
    CMIPSVM_LASTCMD_OPCODE[:] = s8_gen.last_cmd_opcode
    # 
    CTIPSVM_LASTCMD_TIME = ncfile.createVariable('TIP_SUVM_LAST_CMD_TIME', np.uint64, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_LASTCMD_TIME.long_name = 'TIP_Scan_Mirror_Last_Command_Time'
    CTIPSVM_LASTCMD_TIME.units = 'seconds'
    CTIPSVM_LASTCMD_TIME[:] = s6_gen.last_cmd_time
    CMIPSVM_LASTCMD_TIME = ncfile.createVariable('MIP_SUVM_LAST_CMD_TIME', np.uint64, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_LASTCMD_TIME.long_name = 'MIP_Scan_Mirror_Last_Command_Time'
    CMIPSVM_LASTCMD_TIME.units = 'seconds'
    CMIPSVM_LASTCMD_TIME[:] = s8_gen.last_cmd_time
    # 
    CTIPSVM_LASTCMD_SUCCESS = ncfile.createVariable('TIP_SUVM_LAST_CMD_SUCCESS', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_LASTCMD_SUCCESS.long_name = 'TIP_Scan_Mirror_Last_Command_Success'
    CTIPSVM_LASTCMD_SUCCESS[:] = s6_gen.cmd_success
    CMIPSVM_LASTCMD_SUCCESS = ncfile.createVariable('MIP_SUVM_LAST_CMD_SUCCESS', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_LASTCMD_SUCCESS.long_name = 'MIP_Scan_Mirror_Last_Command_Success'
    CMIPSVM_LASTCMD_SUCCESS[:] = s8_gen.cmd_success
    # 
    CTIPSVM_LASTCMD_FAIL = ncfile.createVariable('TIP_SUVM_LAST_CMD_FAIL', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_LASTCMD_FAIL.long_name = 'TIP_Scan_Mirror_Last_Command_Fail'
    CTIPSVM_LASTCMD_FAIL[:] = s6_gen.cmd_fail
    CMIPSVM_LASTCMD_FAIL = ncfile.createVariable('MIP_SUVM_LAST_CMD_FAIL', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_LASTCMD_FAIL.long_name = 'MIP_Scan_Mirror_Last_Command_Fail'
    CMIPSVM_LASTCMD_FAIL[:] = s8_gen.cmd_fail
    # 
    CTIPSVM_LASTCRC = ncfile.createVariable('TIP_SUVM_LAST_CRC', np.uint32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_LASTCRC.long_name = 'TIP_Scan_Mirror_Last_CRC'
    CTIPSVM_LASTCRC[:] = s6_gen.last_crc
    CMIPSVM_LASTCRC = ncfile.createVariable('MIP_SUVM_LAST_CRC', np.uint32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_LASTCRC.long_name = 'MIP_Scan_Mirror_Last_CRC'
    CMIPSVM_LASTCRC[:] = s8_gen.last_crc
    # 
    CTIPSVM_V5IMON = ncfile.createVariable('TIP_SUVM_V5_IMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_V5IMON.long_name = 'TIP_Scan_Mirror_5V_Current_Monitor'
    CTIPSVM_V5IMON.units = 'Amperes'
    CTIPSVM_V5IMON[:] = s6_gen.V5_IMON
    CMIPSVM_V5IMON = ncfile.createVariable('MIP_SUVM_V5_IMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_V5IMON.long_name = 'MIP_Scan_Mirror_5V_Current_Monitor'
    CMIPSVM_V5IMON.units = 'Amperes'
    CMIPSVM_V5IMON[:] = s8_gen.V5_IMON
    # 
    CTIPSVM_V5VMON = ncfile.createVariable('TIP_SUVM_V5_VMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_V5VMON.long_name = 'TIP_Scan_Mirror_5V_Voltage_Monitor'
    CTIPSVM_V5VMON.units = 'Volts'
    CTIPSVM_V5VMON[:] = s6_gen.V5_VMON
    CMIPSVM_V5VMON = ncfile.createVariable('MIP_SUVM_V5_VMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_V5VMON.long_name = 'MIP_Scan_Mirror_5V_Voltage_Monitor'
    CMIPSVM_V5VMON.units = 'Volts'
    CMIPSVM_V5VMON[:] = s8_gen.V5_VMON
    # 
    CTIPSVM_V3IMON = ncfile.createVariable('TIP_SUVM_V3_IMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_V3IMON.long_name = 'TIP_Scan_Mirror_3V_Current_Monitor'
    CTIPSVM_V3IMON.units = 'Amperes'
    CTIPSVM_V3IMON[:] = s6_gen.V3_IMON
    CMIPSVM_V3IMON = ncfile.createVariable('MIP_SUVM_V3_IMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_V3IMON.long_name = 'MIP_Scan_Mirror_3V_Current_Monitor'
    CMIPSVM_V3IMON.units = 'Amperes'
    CMIPSVM_V3IMON[:] = s8_gen.V3_IMON
    # 
    CTIPSVM_V3VMON = ncfile.createVariable('TIP_SUVM_V3_VMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_V3VMON.long_name = 'TIP_Scan_Mirror_3V_Voltage_Monitor'
    CTIPSVM_V3VMON.units = 'Volts'
    CTIPSVM_V3VMON[:] = s6_gen.V3_VMON
    CMIPSVM_V3VMON = ncfile.createVariable('MIP_SUVM_V3_VMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_V3VMON.long_name = 'MIP_Scan_Mirror_3V_Voltage_Monitor'
    CMIPSVM_V3VMON.units = 'Volts'
    CMIPSVM_V3VMON[:] = s8_gen.V3_VMON
    # 
    CTIPSVM_V22IMON = ncfile.createVariable('TIP_SUVM_V22_IMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_V22IMON.long_name = 'TIP_Scan_Mirror_22V_Current_Monitor'
    CTIPSVM_V22IMON.units = 'Amperes'
    CTIPSVM_V22IMON[:] = s6_gen.V22_IMON
    CMIPSVM_V22IMON = ncfile.createVariable('MIP_SUVM_V22_IMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_V22IMON.long_name = 'MIP_Scan_Mirror_22V_Current_Monitor'
    CMIPSVM_V22IMON.units = 'Amperes'
    CMIPSVM_V22IMON[:] = s8_gen.V22_IMON
    # 
    CTIPSVM_V22VMON = ncfile.createVariable('TIP_SUVM_V22_VMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_V22VMON.long_name = 'TIP_Scan_Mirror_22V_Voltage_Monitor'
    CTIPSVM_V22VMON.units = 'Volts'
    CTIPSVM_V22VMON[:] = s6_gen.V22_VMON
    CMIPSVM_V22VMON = ncfile.createVariable('MIP_SUVM_V22_VMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_V22VMON.long_name = 'MIP_Scan_Mirror_22V_Voltage_Monitor'
    CMIPSVM_V22VMON.units = 'Volts'
    CMIPSVM_V22VMON[:] = s8_gen.V22_VMON
    # 
    CTIPSVM_MOTORIMON = ncfile.createVariable('TIP_SUVM_MOTOR_IMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_MOTORIMON.long_name = 'TIP_Scan_Mirror_Motor_Current_Monitor'
    CTIPSVM_MOTORIMON.units = 'Amperes'
    CTIPSVM_MOTORIMON[:] = s6_gen.MOTOR_IMON
    CMIPSVM_MOTORIMON = ncfile.createVariable('MIP_SUVM_MOTOR_IMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_MOTORIMON.long_name = 'MIP_Scan_Mirror_Motor_Current_Monitor'
    CMIPSVM_MOTORIMON.units = 'Amperes'
    CMIPSVM_MOTORIMON[:] = s8_gen.MOTOR_IMON
    # 
    CTIPSVM_TEMP = ncfile.createVariable('TIP_SUVM_TEMP', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_TEMP.long_name = 'TIP_Scan_Mirror_Temperature'
    CTIPSVM_TEMP.units = 'Celsius'
    CTIPSVM_TEMP[:] = s6_gen.temperature
    CMIPSVM_TEMP = ncfile.createVariable('MIP_SUVM_TEMP', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_TEMP.long_name = 'MIP_Scan_Mirror_Temperature'
    CMIPSVM_TEMP.units = 'Celsius'
    CMIPSVM_TEMP[:] = s8_gen.temperature
    # 
    CTIPSVM_ENCZERO_OFFSET = ncfile.createVariable('TIP_SUVM_ENCODER_ZERO_OFFSET', np.short, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_ENCZERO_OFFSET.long_name = 'TIP_Scan_Mirror_Encoder_Zero_Offset'
    CTIPSVM_ENCZERO_OFFSET[:] = s6_gen.encoder_zero_offset
    CMIPSVM_ENCZERO_OFFSET = ncfile.createVariable('MIP_SUVM_ENCODER_ZERO_OFFSET', np.short, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_ENCZERO_OFFSET.long_name = 'MIP_Scan_Mirror_Encoder_Zero_Offset'
    CMIPSVM_ENCZERO_OFFSET[:] = s8_gen.encoder_zero_offset
    # 
    CTIPSVM_ENC_COUNT = ncfile.createVariable('TIP_SUVM_ENCODER_CURRENT_CT', np.short, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_ENC_COUNT.long_name = 'TIP_Scan_Mirror_Encoder_Current_Count'
    CTIPSVM_ENC_COUNT[:] = s6_gen.encoder_current_ct
    CMIPSVM_ENC_COUNT = ncfile.createVariable('MIP_SUVM_ENCODER_CURRENT_CT', np.short, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_ENC_COUNT.long_name = 'MIP_Scan_Mirror_Encoder_Current_Count'
    CMIPSVM_ENC_COUNT[:] = s8_gen.encoder_current_ct
    # 
    CTIPSVM_ENC_TARGET = ncfile.createVariable('TIP_SUVM_ENCODER_TARGET', np.short, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_ENC_TARGET.long_name = 'TIP_Scan_Mirror_Encoder_Target'
    CTIPSVM_ENC_TARGET[:] = s6_gen.encoder_target
    CMIPSVM_ENC_TARGET = ncfile.createVariable('MIP_SUVM_ENCODER_TARGET', np.short, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_ENC_TARGET.long_name = 'MIP_Scan_Mirror_Encoder_Target'
    CMIPSVM_ENC_TARGET[:] = s8_gen.encoder_target
    # 
    CTIPSVM_PROFIDX = ncfile.createVariable('TIP_SUVM_ENCODER_PROFILE_INDEX', np.uint16, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_PROFIDX.long_name = 'TIP_Scan_Mirror_Encoder_Profile_Index'
    CTIPSVM_PROFIDX[:] = s6_gen.profile_index
    CMIPSVM_PROFIDX = ncfile.createVariable('MIP_SUVM_ENCODER_PROFILE_INDEX', np.uint16, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_PROFIDX.long_name = 'MIP_Scan_Mirror_Encoder_Profile_Index'
    CMIPSVM_PROFIDX[:] = s8_gen.profile_index
    # 
    CTIPSVM_PWMRATE = ncfile.createVariable('TIP_SUVM_PWM_RATE', np.uint32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_PWMRATE.long_name = 'TIP_Scan_Mirror_Motor_PWM_Rate'
    CTIPSVM_PWMRATE.units = 'Hz'
    CTIPSVM_PWMRATE[:] = s6_gen.pwm_rate
    CMIPSVM_PWMRATE = ncfile.createVariable('MIP_SUVM_PWM_RATE', np.uint32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_PWMRATE.long_name = 'MIP_Scan_Mirror_Motor_PWM_Rate'
    CMIPSVM_PWMRATE.units = 'Hz'
    CMIPSVM_PWMRATE[:] = s8_gen.pwm_rate
    # 
    CTIPSVM_PWMCTS_REMAIN = ncfile.createVariable('TIP_SUVM_PWM_CTS_REMAIN', np.uint32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_PWMCTS_REMAIN.long_name = 'TIP_Scan_Mirror_Motor_PWM_Counts_Remain'
    CTIPSVM_PWMCTS_REMAIN[:] = s6_gen.pwm_counts_remain
    CMIPSVM_PWMCTS_REMAIN = ncfile.createVariable('MIP_SUVM_PWM_CTS_REMAIN', np.uint32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_PWMCTS_REMAIN.long_name = 'MIP_Scan_Mirror_Motor_PWM_Counts_Remain'
    CMIPSVM_PWMCTS_REMAIN[:] = s8_gen.pwm_counts_remain
    # 
    CTIPSVM_CRC = ncfile.createVariable('TIP_SUVM_CRC', np.uint32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_CRC.long_name = 'TIP_Scan_Mirror_CRC'
    CTIPSVM_CRC[:] = s6_gen.crc
    CMIPSVM_CRC = ncfile.createVariable('MIP_SUVM_CRC', np.uint32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_CRC.long_name = 'MIP_Scan_Mirror_CRC'
    CMIPSVM_CRC[:] = s8_gen.crc
    # 
    CTIPSVM_ENCANGLE = ncfile.createVariable('TIP_SUVM_ENCODER_ANGLE', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_ENCANGLE.long_name = 'TIP_Scan_Mirror_Encoder_Angle'
    CTIPSVM_ENCANGLE.units = 'Degrees'
    CTIPSVM_ENCANGLE[:] = s6_gen.encoder_angle
    CMIPSVM_ENCANGLE = ncfile.createVariable('MIP_SUVM_ENCODER_ANGLE', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_ENCANGLE.long_name = 'MIP_Scan_Mirror_Encoder_Angle'
    CMIPSVM_ENCANGLE.units = 'Degrees'
    CMIPSVM_ENCANGLE[:] = s8_gen.encoder_angle
    # 
    CTIPSVM_TGTANGLE = ncfile.createVariable('TIP_SUVM_ENCODER_TARGET_ANGLE', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_TGTANGLE.long_name = 'TIP_Scan_Mirror_Encoder_Target_Angle'
    CTIPSVM_TGTANGLE.units = 'Degrees'
    CTIPSVM_TGTANGLE[:] = s6_gen.target_angle
    CMIPSVM_TGTANGLE = ncfile.createVariable('MIP_SUVM_ENCODER_TARGET_ANGLE', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_TGTANGLE.long_name = 'MIP_Scan_Mirror_Encoder_Target_Angle'
    CMIPSVM_TGTANGLE.units = 'Degrees'
    CMIPSVM_TGTANGLE[:] = s8_gen.target_angle
    # 
    print(ncfile)
    ncfile.close()
    
    print(' CTS File Complete: ' + outname)
    print('')
    
    """
    Unused SUVM bits                                        # Byte
    # self.header             = np.zeros(n, dtype='uintc')  #  0
    # self.apid               = np.zeros(n, dtype='ubyte')  #  4
    # self.length             = np.zeros(n, dtype='uint16') #  6
    # self.watchdog_counter   = np.zeros(n, dtype='uint32') # 24
    # self.version            = np.zeros(n, dtype='uint32') # 28
    # self.reset_status       = np.zeros(n, dtype='ubyte')  # 32
    # self.flash_last_op      = np.zeros(n, dtype='ubyte')  # 46
    # self.flash_status       = np.zeros(n, dtype='ubyte')  # 47
    # self.general_hk_flags   = np.zeros(n, dtype='uint32') # 48
    # self.ROM_SBE            = np.zeros(n, dtype='uint16') # 56
    # self.ROM_MBE            = np.zeros(n, dtype='uint16') # 58
    # self.RAM_SBE            = np.zeros(n, dtype='uint16') # 60
    # self.RAM_MBE            = np.zeros(n, dtype='uint16') # 62
    # self.GPIO_A             = np.zeros(n, dtype='uint32') # 64
    # self.GPIO_B             = np.zeros(n, dtype='uint32') # 68
    # self.launch_lock_flags  = np.zeros(n, dtype='uint32') # 72
    # self.VC_LIMIT_CHECK     = np.zeros(n, dtype='uint16') # 76
    # self.motor_flags        = np.zeros(n, dtype='uint16') # 104
    """
def main(fname):
    # import ECLIPSE_H9_ccsds as ehc
    # import ECLIPSE_telemetry_breakout as etb
    ccsds_byte = ehc.load_eclipse_bytes_from_ccsds(fname)
    ebyte = etb.breakout_hrt_packet(ccsds_byte)
    print(f'\n Processing {fname}\n')
    print(ebyte)
    print('')
    
    # ECL_L0_analog(fname, ebyte)
    ECL_L0_CTS(fname, ebyte)
    # ECL_L0_ALS(fname, ebyte)
    
if __name__ == "__main__":
    print(f"==== {__file__} ====")
    # main(fname)
