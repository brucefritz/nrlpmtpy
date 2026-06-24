#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: ECL_make_nc0.py
Author: Bruce A. Fritz, NRL Code 7634
Version: 1.1
Date:   v1.0  2023-03-20, Created
        v1.1  2024-12-17, Updated Header for git upload
Description: Executable main() script to process ECLIPSE TLM CCSDS files into
    separated L0 files

Classes:
    None
        
Functions:
    ECL_global_attributes() sets global attributes in the L0 file
    ECL_L0_analog() creats a .nc file that contains 1 day of IIB analog data
    generate_aux_logfile() creates a .txt file containing all AUX messages
    ECL_L0_ALS()
    ECL_L0_CTS()
    ECL_L0_ISS()
    
NetCDF exmample to follow at
https://unidata.github.io/python-training/workshop/Bonus/netcdf-writing/

External Python package dependencies:
    netCDF4
    astropy

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
import STPH9_usgnc_converter as h9gnc
import astropy.time as apt
import ECL0_nc_survey as L0_plot

def ECL_global_attributes(ncfile: Dataset) -> None:
    """
    Adds the common list of Global Attibutes to each NetCDF file being generated
    for each data type (ALS, CTS, Analog)

    Parameters
    ----------
    ncfile : Dataset
        Pointer to netCDF4 Dataset that requires addition of Global Parameters
    
    Returns
    -------
    None
        netCDF4 object does not require return to accept the update

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
    ncfile.time_resolution = '1 second'
    ncfile.data_type = "H0>Photometer_Counts"
    
    ncfile.generated_by = 'Bruce A. Fritz'
    ncfile.generation_date = time.asctime(time.localtime(time.time()))
    
    # ncfile.logical_file_id = "ECL_H0_MIP_20220801_V01 [TBR]"
    # ncfile.logical_source  = "SLN_H0_MIP [TBR]"
    # ncfile.logical_source_description = "Tri-MIP Photometer Counts"
    # ncfile.mods = "Initial Release"

    eclipse_text = """See Dymond et al. (2023) for an ECLIPSE description,
                      https://doi.org/10.5281/zenodo.8092594"""
    ACK_TEXT   = """Tri-TIP development was funded by the Office of Naval Research.
                Tri-MIP development was funded by DARPA, data archival is 
                supported by the Chief of Naval Research"""
    RULES_TEXT = """    ECLIPSE is led by the U. S. Naval Research Laboratory 
    (NRL). The ‘Rules of the Road’ help ensure that the use of any data and 
    analysis results includes the proper inherent uncertainties and limitations 
    in the data and data products, and that the time, effort, and expertise of 
    the ECLIPSE team, as well as their sponsors, are properly recognized. Users 
    of ECLIPSE data must agree to adhere to the following:
        1.	The user should contact a listed team member at NRL (Ken Dymond or 
            Bruce Fritz) prior to any investigation to discuss intended usage 
            and possible data limitations.    
        2.	Data will only be shared with other users with direct approval of 
            an ECLIPSE team member, and with agreement from the user to abide 
            by these Rules of the Road.
        3.	Before they are formally submitted or presented, draft copies of 
            all reports, publications, and presentations must be sent to an 
            ECLIPSE team member along with an offer of co-authorship to all key 
            ECLIPSE instrument scientists at NRL listed above. The user should 
            coordinate this as early as possible, since publications and reports 
            that include NRL co-authors may require up to four weeks for internal 
            review and approval.
        4.	Users should heed the caveats of instrument scientists as to the 
            interpretation and limitations of data or model results. Investigators 
            supplying data or models may insist that such caveats be published, 
            even if co-authorship is declined. Data and model version numbers 
            should also be specified, as relevant.
        5.	Acknowledgment to institutions, personnel, and funding agencies must 
            be given for all uses of ECLIPSE data regardless of whether co-
            authorship is accepted, including at least the following statement 
            The STP-H9 payload was integrated and flown under the direction of 
            the Department of Defense Space Test Program (DoD STP). Support for 
            the ECLIPSE experiment by the DARPA SEE Program and the Office of 
            Naval Research. 
        6.	Copies of all reports, papers, and presentations that use ECLIPSE 
            data and results will be forwarded to Bruce Fritz, bruce.a.fritz4.civ@us.navy.mil, 
            so that a Bibliography of productivity from ECLIPSE can be maintained.
    """ 

    ncfile.text = eclipse_text
    ncfile.acknowledgement = ACK_TEXT
    ncfile.rules_of_use = RULES_TEXT
    # ncfile.project = "SPDS>Space Physics Data System"
    # ;; See ISTP exchangeable data products for more info
    # ;; Additional optional Global attributes .... 
    #       see https://spdf.gsfc.nasa.gov/istp_guide/gattributes.html
    # ncfile.doi = "DOI: [TBD]" # contact SPASE to register
    # ncfile.spase_DatasetResourceID = "TBD", # * Recommended
    # ncfile.software_version = 'TBD'
    

def ECL_L0_analog(fname: str, ebyte: list) -> str:
    """
    Generate netCDF L0 file for a given ECLIPSE telemetry input

    Parameters
    ----------
    fname : str
        File name + path for input, used to generate output string
    ebyte : list
        eclipse_packet object of ECLIPSE_telemetry_breakout module

    Returns
    -------
    outname : str
        .nc file created

    """
    (fpath, fbase_ext) = path.split(fname)
    (fbase, f_ext) = path.splitext(fbase_ext)
    # 
    fnew_ext = f"{fbase}_ECLIPSE_L0_analog.nc"
    outname = path.join(fpath, 'L0_analog', fnew_ext)
    print(f'Starting to generate the file ... \n ... {outname} \n')
    # 
    ncfile = Dataset(outname,mode='w',format='NETCDF4') 
    # 
    analog1 = eic.eclipse_iib_converter(ebyte.analog1)
    analog2 = eic.eclipse_iib_converter(ebyte.analog2)
    
    # Define Dimensions
    ncfile.createDimension('ALS_time', len(analog1.GPS_time))
    ncfile.createDimension('CTS_time', len(analog2.GPS_time))
    # 
    # Create Attributes
    # 
    ### GLOBAL ATTRIBUTES specific to this file type
    ncfile.source_1 = fbase_ext
    # ncfile.source_2 = 'TBD - Will be ISS telemetry file' # No ISS data here
    ncfile.filename = outname
    ncfile.data_version = 'v1.0'
    ### REQUIRED GLOBAL ATTRIBUTES
    ECL_global_attributes(ncfile)
    # 
    # Create Variables
    ALS_GPSt = ncfile.createVariable('ALS_GPS_time', np.uint32, ('ALS_time',), zlib=True)
    ALS_GPSt.units = 'seconds'
    ALS_GPSt.long_name = 'ALS_analog_GPS_time'
    ALS_GPSt[:] = analog1.GPS_time
    # 
    CTS_GPSt = ncfile.createVariable('CTS_GPS_time', np.uint32, ('CTS_time',), zlib=True)
    CTS_GPSt.units = 'seconds'
    CTS_GPSt.long_name = 'ALS_analog_GPS_time'
    CTS_GPSt[:] = analog2.GPS_time
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
    # print(ncfile)
    ncfile.close()
    
    print(' Analog File Complete: ' + outname)
    print('')
    
    return outname
    
def generate_aux_logfile(aux: list[int, bytearray], auxname: str) -> None:
    """
    Generates .txt log file from TIP telemetry

    Parameters
    ----------
    aux : list[int, bytearray]
        Input data from HRT file
    auxname : str
        Name used to generate output file

    Returns
    -------
    None
        File created externally

    """
    print(f'Generating AUX logfile: {auxname}')
    with open(auxname, 'w') as fp:
        fp.write('Time                    Command\n')
        for i, c in enumerate(aux):
            iso_t = apt.Time(c[0], format='gps')
            time = iso_t.fits
            command = c[1].decode('utf-8')
            fp.write(f'{time} {command[0:4]}\n')
    return 

def ECL_L0_ALS(fname: str, ebyte: list) -> str:
    """
    Generates daily ECLIPSE ALS L0 file

    Parameters
    ----------
    fname : str
        Input filename
    ebyte : list
        eclipse_packet object of ECLIPSE_telemetry_breakout module

    Returns
    -------
    None
        .nc L0 file created

    """
    (fpath, fbase_ext) = path.split(fname)
    (fbase, f_ext) = path.splitext(fbase_ext)
    # 
    fnew_ext = f"{fbase}_ECLIPSE_L0_ALS.nc"
    outname = path.join(fpath, 'L0_ALS', fnew_ext)
    #
    print(f'Starting to generate the file(s) ... \n ... {outname}\n')
    # 
    if len(ebyte.tip1_aux) > 0:
        print(f' ... {fbase}_ALS_TIP_aux_log.txt\n')
        generate_aux_logfile(ebyte.tip1_aux, path.join(fpath,'L0_ALS',f'{fbase}_ALS_TIP_aux_log.txt'))
    if len(ebyte.mip3_aux) > 0:
        print(f' ... {fbase}_ALS_TIP_aux_log.txt\n')
        generate_aux_logfile(ebyte.mip3_aux, path.join(fpath,'L0_ALS',f'{fbase}_ALS_MIP_aux_log.txt'))
    # 
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
    
    ncfile.createDimension('TIP_M0_TIME', len(tip0.time))
    ncfile.createDimension('TIP_M1_TIME', len(tip1.time))
    ncfile.createDimension('TIP_SUVM_TIME', len(s2_gen.system_counter))
    ncfile.createDimension('MIP_M0_TIME', len(mip0.time))
    ncfile.createDimension('MIP_M1_TIME', len(mip1.time))
    ncfile.createDimension('MIP_SUVM_TIME', len(s4_gen.system_counter))
    # 
    # Create Attributes
    # 
    ### GLOBAL ATTRIBUTES specific to this file type
    ncfile.source_1 = fbase_ext
    ncfile.filename = outname
    ncfile.data_version = 'v1.0'
    ### REQUIRED GLOBAL ATTRIBUTES
    ECL_global_attributes(ncfile)
    """ 
    # XIP Variables
    
    M0 Vlues Not included:
    #         self.IDC_ID = np.zeros(n, dtype='U4')
    #         self.MODE             = np.zeros(n, dtype='U2')
    """
    # 
    ATIP0_GPSt1 = ncfile.createVariable('TIP_M0_CCSDS_GPS_TIME', np.float64, ('TIP_M0_TIME',), zlib=True)
    ATIP0_GPSt1.units = 'seconds'
    ATIP0_GPSt1.long_name = 'ALS_TIP_M0_H9_CCSDS_GPS_time'
    ATIP0_GPSt1[:] = tip0.H9_CCSDS_GPS_time
    AMIP0_GPSt1 = ncfile.createVariable('MIP_M0_CCSDS_GPS_TIME', np.float64, ('MIP_M0_TIME',), zlib=True)
    AMIP0_GPSt1.units = 'seconds'
    AMIP0_GPSt1.long_name = 'ALS_MIP_M0_H9_CCSDS_GPS_time'
    AMIP0_GPSt1[:] = mip0.H9_CCSDS_GPS_time
    # 
    ATIP0_GPSt2 = ncfile.createVariable('TIP_M0_CCSDS_ECL_TIME', np.float64, ('TIP_M0_TIME',), zlib=True)
    ATIP0_GPSt2.units = 'seconds'
    ATIP0_GPSt2.long_name = 'ALS_TIP_M0_CCSDS_ECLIPSE_GPS_time'
    ATIP0_GPSt2[:] = tip0.H9_CCSDS_ECL_time
    AMIP0_GPSt2 = ncfile.createVariable('MIP_M0_CCSDS_ECL_TIME', np.float64, ('MIP_M0_TIME',), zlib=True)
    AMIP0_GPSt2.units = 'seconds'
    AMIP0_GPSt2.long_name = 'ALS_MIP_M0_CCSDS_ECLIPSE_GPS_time'
    AMIP0_GPSt2[:] = mip0.H9_CCSDS_ECL_time
    # 
    ATIP0_GPSt3 = ncfile.createVariable('TIP_M0_ECL_MOE_GPS_TIME', np.float64, ('TIP_M0_TIME',), zlib=True)
    ATIP0_GPSt3.units = 'seconds'
    ATIP0_GPSt3.long_name = 'ALS_TIP_M0_ECLIPSE_MOE_GPS_time'
    ATIP0_GPSt3[:] = tip0.ECL_MOE_GPS_time
    AMIP0_GPSt3 = ncfile.createVariable('MIP_M0_ECL_MOE_GPS_TIME', np.float64, ('MIP_M0_TIME',), zlib=True)
    AMIP0_GPSt3.units = 'seconds'
    AMIP0_GPSt3.long_name = 'ALS_MIP_M0_ECLIPSE_MOE_GPS_time'
    AMIP0_GPSt3[:] = mip0.ECL_MOE_GPS_time
    # 
    ATIP0_TIME = ncfile.createVariable('TIP_M0_RUNTIME', np.uint64, ('TIP_M0_TIME',), zlib=True)
    ATIP0_TIME.units = 'seconds'
    ATIP0_TIME.long_name = 'system_run_time'
    ATIP0_TIME[:] = tip0.time
    AMIP0_TIME = ncfile.createVariable('MIP_M0_RUNTIME', np.uint64, ('MIP_M0_TIME',), zlib=True)
    AMIP0_TIME.units = 'seconds'
    AMIP0_TIME.long_name = 'system_run_time'
    AMIP0_TIME[:] = mip0.time
    # 
    ATIP0_DARK = ncfile.createVariable('TIP_M0_DARK', np.uint64, ('TIP_M0_TIME',), zlib=True)
    ATIP0_DARK.units = 'counts/sec'
    ATIP0_DARK.long_name = 'dark_PMT_counts'
    ATIP0_DARK[:] = tip0.dark
    AMIP0_DARK = ncfile.createVariable('MIP_M0_DARK', np.uint64, ('MIP_M0_TIME',), zlib=True)
    AMIP0_DARK.units = 'counts/sec'
    AMIP0_DARK.long_name = 'dark_PMT_counts'
    AMIP0_DARK[:] = mip0.dark
    # 
    ATIP0_RED = ncfile.createVariable('TIP_M0_RED', np.uint64, ('TIP_M0_TIME',), zlib=True)
    ATIP0_RED.units = 'counts/sec'
    ATIP0_RED.long_name = 'red_PMT_counts'
    ATIP0_RED[:] = tip0.red
    # 
    AMIP0_MG = ncfile.createVariable('MIP_M0_MG', np.uint64, ('MIP_M0_TIME',), zlib=True)
    AMIP0_MG.units = 'counts/sec'
    AMIP0_MG.long_name = 'Mg_PMT_counts'
    AMIP0_MG[:] = mip0.Mg
    # 
    ATIP0_UV = ncfile.createVariable('TIP_M0_UV', np.uint64, ('TIP_M0_TIME',), zlib=True)
    ATIP0_UV.units = 'counts/sec'
    ATIP0_UV.long_name = 'uv_PMT_counts'
    ATIP0_UV[:] = tip0.uv
    # 
    AMIP0_VK = ncfile.createVariable('MIP_M0_VK', np.uint64, ('MIP_M0_TIME',), zlib=True)
    AMIP0_VK.units = 'counts/sec'
    AMIP0_VK.long_name = 'VK_PMT_counts'
    AMIP0_VK[:] = mip0.VK
    # 
    ATIP0_HEATER = ncfile.createVariable('TIP_M0_HEATER', np.uint32, ('TIP_M0_TIME',), zlib=True)
    ATIP0_HEATER.long_name = 'heater_duty_cycle'
    ATIP0_HEATER[:] = tip0.heater
    # 
    # AMIP0_ERROR = ncfile.createVariable('MIP_M0_ERROR', np.uint32, ('MIP_M0_TIME',), zlib=True)
    # AMIP0_ERROR.long_name = 'error'
    # AMIP0_ERROR[:] = mip0.error
    # 
    ATIP0_TF1 = ncfile.createVariable('TIP_M0_TF1', np.float32, ('TIP_M0_TIME',), zlib=True)
    ATIP0_TF1.units = 'Celsius'
    ATIP0_TF1.long_name = 'filter_temperature_1'
    ATIP0_TF1[:] = tip0.T_F1
    # 
    AMIP0_TLENS = ncfile.createVariable('MIP_M0_TLENS', np.float32, ('MIP_M0_TIME',), zlib=True)
    AMIP0_TLENS.units = 'Celsius'
    AMIP0_TLENS.long_name = 'Lens_temperature'
    AMIP0_TLENS[:] = mip0.T_LENS
    # 
    ATIP0_TF2 = ncfile.createVariable('TIP_M0_TF2', np.float32, ('TIP_M0_TIME',), zlib=True)
    ATIP0_TF2.units = 'Celsius'
    ATIP0_TF2.long_name = 'filter_temperature_2'
    ATIP0_TF2[:] = tip0.T_F2
    #
    AMIP0_TPMT = ncfile.createVariable('MIP_M0_TPMT', np.float32, ('MIP_M0_TIME',), zlib=True)
    AMIP0_TPMT.units = 'Celsius'
    AMIP0_TPMT.long_name = 'PMT_block_temperature'
    AMIP0_TPMT[:] = mip0.T_PMT
    #
    ATIP0_HVMON = ncfile.createVariable('TIP_M0_HV_mon', np.float32, ('TIP_M0_TIME',), zlib=True)
    ATIP0_HVMON.units = 'Volts'
    ATIP0_HVMON.long_name = 'High_voltage_monitor'
    ATIP0_HVMON[:] = tip0.HV_mon
    AMIP0_HVMON = ncfile.createVariable('MIP_M0_HV_mon', np.float32, ('MIP_M0_TIME',), zlib=True)
    AMIP0_HVMON.units = 'Volts'
    AMIP0_HVMON.long_name = 'High_voltage_monitor'
    AMIP0_HVMON[:] = mip0.HV_mon
    #
    ATIP0_HVADJ = ncfile.createVariable('TIP_M0_HV_adj', np.float32, ('TIP_M0_TIME',), zlib=True)
    ATIP0_HVADJ.units = 'Volts'
    ATIP0_HVADJ.long_name = 'High_voltage_adjust'
    ATIP0_HVADJ[:] = tip0.HV_adj
    AMIP0_HVADJ = ncfile.createVariable('MIP_M0_HV_adj', np.float32, ('MIP_M0_TIME',), zlib=True)
    AMIP0_HVADJ.units = 'Volts'
    AMIP0_HVADJ.long_name = 'High_voltage_adjust'
    AMIP0_HVADJ[:] = mip0.HV_adj
    #
    ATIP0_SUN = ncfile.createVariable('TIP_M0_sun', np.float32, ('TIP_M0_TIME',), zlib=True)
    ATIP0_SUN.units = 'Volts'
    ATIP0_SUN.long_name = 'sun_sensor'
    ATIP0_SUN[:] = tip0.sun
    AMIP0_SUN = ncfile.createVariable('MIP_M0_sun', np.float32, ('MIP_M0_TIME',), zlib=True)
    AMIP0_SUN.units = 'Volts'
    AMIP0_SUN.long_name = 'sun_sensor'
    AMIP0_SUN[:] = mip0.sun
    #
    ATIP0_VREF = ncfile.createVariable('TIP_M0_VREF', np.float32, ('TIP_M0_TIME',), zlib=True)
    ATIP0_VREF.units = 'Volts'
    ATIP0_VREF.long_name = 'reference_voltage_2p5V'
    ATIP0_VREF[:] = tip0.vref
    AMIP0_VREF = ncfile.createVariable('MIP_M0_VREF', np.float32, ('MIP_M0_TIME',), zlib=True)
    AMIP0_VREF.units = 'Volts'
    AMIP0_VREF.long_name = 'reference_voltage_2p5V'
    AMIP0_VREF[:] = mip0.vref
    #
    ATIP0_TIDC = ncfile.createVariable('TIP_M0_TIDC', np.float32, ('TIP_M0_TIME',), zlib=True)
    ATIP0_TIDC.units = 'Celsius'
    ATIP0_TIDC.long_name = 'IDC_temperature'
    ATIP0_TIDC[:] = tip0.T_IDC
    AMIP0_TIDC = ncfile.createVariable('MIP_M0_TIDC', np.float32, ('MIP_M0_TIME',), zlib=True)
    AMIP0_TIDC.units = 'Celsius'
    AMIP0_TIDC.long_name = 'IDC_temperature'
    AMIP0_TIDC[:] = mip0.T_IDC
    #
    ATIP0_THV = ncfile.createVariable('TIP_M0_THV', np.float32, ('TIP_M0_TIME',), zlib=True)
    ATIP0_THV.units = 'Celsius'
    ATIP0_THV.long_name = 'high_voltage_temperature'
    ATIP0_THV[:] = tip0.T_HV
    AMIP0_THV = ncfile.createVariable('MIP_M0_THV', np.float32, ('MIP_M0_TIME',), zlib=True)
    AMIP0_THV.units = 'Celsius'
    AMIP0_THV.long_name = 'high_voltage_temperature'
    AMIP0_THV[:] = mip0.T_HV
    #
    # ATIP0_DISCRETE = ncfile.createVariable('TIP_M0_DISCRETE', np.str, ('TIP_M0_TIME',), zlib=True)
    # ATIP0_DISCRETE.long_name = 'discrete'
    # ATIP0_DISCRETE[:] = tip0.discrete
    # AMIP0_DISCRETE = ncfile.createVariable('MIP_M0_DISCRETE', np.str, ('MIP_M0_TIME',), zlib=True)
    # AMIP0_DISCRETE.long_name = 'discrete'
    # AMIP0_DISCRETE[:] = mip0.discrete
    #
    ATIP0_HVSTAT = ncfile.createVariable('TIP_M0_HV_Status', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    ATIP0_HVSTAT.long_name = 'High_Voltage_Status'
    ATIP0_HVSTAT[:] = tip0.HV_STATUS
    AMIP0_HVSTAT = ncfile.createVariable('MIP_M0_HV_Status', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    AMIP0_HVSTAT.long_name = 'High_Voltage_Status'
    AMIP0_HVSTAT[:] = mip0.HV_STATUS
    # 
    ATIP0_HVEVENT = ncfile.createVariable('TIP_M0_HV_Event', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    ATIP0_HVEVENT.long_name = 'High_Voltage_Exceed_Threshold'
    ATIP0_HVEVENT[:] = tip0.HV_EVENT
    AMIP0_HVEVENT = ncfile.createVariable('MIP_M0_HV_Event', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    AMIP0_HVEVENT.long_name = 'High_Voltage_Exceed_Threshold'
    AMIP0_HVEVENT[:] = mip0.HV_EVENT
    # 
    ATIP0_SUNEVENT = ncfile.createVariable('TIP_M0_Sun_Event', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    ATIP0_SUNEVENT.long_name = 'Sun_Sensor_Exceed_Threshold'
    ATIP0_SUNEVENT[:] = tip0.SUN_EVENT
    AMIP0_SUNEVENT = ncfile.createVariable('MIP_M0_Sun_Event', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    AMIP0_SUNEVENT.long_name = 'Sun_Sensor_Exceed_Threshold'
    AMIP0_SUNEVENT[:] = mip0.SUN_EVENT
    # 
    ATIP0_DKEVENT = ncfile.createVariable('TIP_M0_DK_EVENT', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    ATIP0_DKEVENT.long_name = 'PMT_Dark_Pad_Exceed_Threshold'
    ATIP0_DKEVENT[:] = tip0.DK_EVENT
    AMIP0_DKEVENT = ncfile.createVariable('MIP_M0_DK_EVENT', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    AMIP0_DKEVENT.long_name = 'PMT_Dark_Pad_Exceed_Threshold'
    AMIP0_DKEVENT[:] = mip0.DK_EVENT
    # 
    ATIP0_RDEVENT = ncfile.createVariable('TIP_M0_RD_EVENT', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    ATIP0_RDEVENT.long_name = 'PMT_Red_Pad_Exceed_Threshold'
    ATIP0_RDEVENT[:] = tip0.RD_EVENT
    AMIP0_RDEVENT = ncfile.createVariable('MIP_M0_RD_EVENT', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    AMIP0_RDEVENT.long_name = 'PMT_Red_Pad_Exceed_Threshold'
    AMIP0_RDEVENT[:] = mip0.RD_EVENT
    # 
    ATIP0_UVEVENT = ncfile.createVariable('TIP_M0_UV_EVENT', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    ATIP0_UVEVENT.long_name = 'PMT_UV_Pad_Exceed_Threshold'
    ATIP0_UVEVENT[:] = tip0.UV_EVENT
    AMIP0_UVEVENT = ncfile.createVariable('MIP_M0_UV_EVENT', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    AMIP0_UVEVENT.long_name = 'PMT_UV_Pad_Exceed_Threshold'
    AMIP0_UVEVENT[:] = mip0.UV_EVENT
    # 
    ATIP0_SUNOVERRIDE = ncfile.createVariable('TIP_M0_Sun_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    ATIP0_SUNOVERRIDE.long_name = 'Sun_Sensor_Override'
    ATIP0_SUNOVERRIDE[:] = tip0.SUN_OVERRIDE
    AMIP0_SUNOVERRIDE = ncfile.createVariable('MIP_M0_Sun_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    AMIP0_SUNOVERRIDE.long_name = 'Sun_Sensor_Override'
    AMIP0_SUNOVERRIDE[:] = mip0.SUN_OVERRIDE
    # 
    ATIP0_DKOVERRIDE = ncfile.createVariable('TIP_M0_Dark_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    ATIP0_DKOVERRIDE.long_name = 'Dark_Count_Override'
    ATIP0_DKOVERRIDE[:] = tip0.DK_OVERRIDE
    AMIP0_DKOVERRIDE = ncfile.createVariable('MIP_M0_Dark_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    AMIP0_DKOVERRIDE.long_name = 'Dark_Count_Override'
    AMIP0_DKOVERRIDE[:] = mip0.DK_OVERRIDE
    # 
    ATIP0_RD_OVERRIDE = ncfile.createVariable('TIP_M0_Red_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    ATIP0_RD_OVERRIDE.long_name = 'Red_Count_Override'
    ATIP0_RD_OVERRIDE[:] = tip0.RD_OVERRIDE
    AMIP0_RD_OVERRIDE = ncfile.createVariable('MIP_M0_Red_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    AMIP0_RD_OVERRIDE.long_name = 'Red_Count_Override'
    AMIP0_RD_OVERRIDE[:] = mip0.RD_OVERRIDE
    # 
    ATIP0_UVOVERRIDE = ncfile.createVariable('TIP_M0_UV_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    ATIP0_UVOVERRIDE.long_name = 'UV_Count_Override'
    ATIP0_UVOVERRIDE[:] = tip0.UV_OVERRIDE
    AMIP0_UVOVERRIDE = ncfile.createVariable('MIP_M0_UV_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    AMIP0_UVOVERRIDE.long_name = 'UV_Count_Override'
    AMIP0_UVOVERRIDE[:] = mip0.UV_OVERRIDE
    # 
    ATIP0_HVOVERRIDE = ncfile.createVariable('TIP_M0_HV_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    ATIP0_HVOVERRIDE.long_name = 'High_Voltage_Override'
    ATIP0_HVOVERRIDE[:] = tip0.HV_OVERRIDE
    AMIP0_HVOVERRIDE = ncfile.createVariable('MIP_M0_HV_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    AMIP0_HVOVERRIDE.long_name = 'High_Voltage_Override'
    AMIP0_HVOVERRIDE[:] = mip0.HV_OVERRIDE
    # 
    ATIP0_SHUTTEROVERRIDE = ncfile.createVariable('TIP_M0_Shutter_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    ATIP0_SHUTTEROVERRIDE.long_name = 'Shutter_Override'
    ATIP0_SHUTTEROVERRIDE[:] = tip0.SHUTTER_OVERRIDE
    AMIP0_SHUTTEROVERRIDE = ncfile.createVariable('MIP_M0_Shutter_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    AMIP0_SHUTTEROVERRIDE.long_name = 'Shutter_Override'
    AMIP0_SHUTTEROVERRIDE[:] = mip0.SHUTTER_OVERRIDE
    # 
    ATIP0_V5OVERRIDE = ncfile.createVariable('TIP_M0_5V_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    ATIP0_V5OVERRIDE.long_name = '5V_Override'
    ATIP0_V5OVERRIDE[:] = tip0.V5_OVERRIDE
    AMIP0_V5OVERRIDE = ncfile.createVariable('MIP_M0_5V_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
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
    # 
    ATIP1_GPSt1 = ncfile.createVariable('TIP_M1_CCSDS_GPS_TIME', np.float64, ('TIP_M1_TIME',), zlib=True)
    ATIP1_GPSt1.long_name = 'ALS_TIP_CCSDS_GPS_time_10Hz'
    ATIP1_GPSt1.units = 'Seconds'
    ATIP1_GPSt1[:] = tip1.H9_CCSDS_GPS_time
    AMIP1_GPSt1 = ncfile.createVariable('MIP_M1_CCSDS_GPS_TIME', np.float64, ('MIP_M1_TIME',), zlib=True)
    AMIP1_GPSt1.long_name = 'ALS_MIP_CCSDS_GPS_time_10Hz'
    AMIP1_GPSt1.units = 'Seconds'
    AMIP1_GPSt1[:] = mip1.H9_CCSDS_GPS_time
    # 
    ATIP1_GPSt2 = ncfile.createVariable('TIP_M1_CCSDS_ECL_TIME', np.float64, ('TIP_M1_TIME',), zlib=True)
    ATIP1_GPSt2.long_name = 'ALS_TIP_CCSDS_ECLIPSE_GPS_time_10Hz'
    ATIP1_GPSt2.units = 'Seconds'
    ATIP1_GPSt2[:] = tip1.H9_CCSDS_ECL_time
    AMIP1_GPSt2 = ncfile.createVariable('MIP_M1_CCSDS_ECL_TIME', np.float64, ('MIP_M1_TIME',), zlib=True)
    AMIP1_GPSt2.long_name = 'ALS_MIP_CCSDS_ECLIPSE_GPS_time_10Hz'
    AMIP1_GPSt2.units = 'Seconds'
    AMIP1_GPSt2[:] = mip1.H9_CCSDS_ECL_time
    # 
    ATIP1_GPSt3 = ncfile.createVariable('TIP_M1_ECL_MOE_GPS_TIME', np.float64, ('TIP_M1_TIME',), zlib=True)
    ATIP1_GPSt3.long_name = 'ALS_TIP_ECLIPSE_MOE_GPS_time_10Hz'
    ATIP1_GPSt3.units = 'Seconds'
    ATIP1_GPSt3[:] = tip1.ECL_MOE_GPS_time
    AMIP1_GPSt3 = ncfile.createVariable('MIP_M1_ECL_MOE_GPS_TIME', np.float64, ('MIP_M1_TIME',), zlib=True)
    AMIP1_GPSt3.long_name = 'ALS_MIP_ECLIPSE_MOE_GPS_time_10Hz'
    AMIP1_GPSt3.units = 'Seconds'
    AMIP1_GPSt3[:] = mip1.ECL_MOE_GPS_time
    # 
    ATIP1_TIME = ncfile.createVariable('TIP_M1_RUNTIME', np.float64, ('TIP_M1_TIME',), zlib=True)
    ATIP1_TIME.long_name = 'System_Run_Time_10Hz'
    ATIP1_TIME.units = 'Seconds'
    ATIP1_TIME[:] = tip1.time
    AMIP1_TIME = ncfile.createVariable('MIP_M1_RUNTIME', np.float64, ('MIP_M1_TIME',), zlib=True)
    AMIP1_TIME.long_name = 'System_Run_Time_10Hz'
    AMIP1_TIME.units = 'Seconds'
    AMIP1_TIME[:] = mip1.time
    # 
    ATIP1_DARK = ncfile.createVariable('TIP_M1_DARK', np.uint16, ('TIP_M1_TIME',), zlib=True)
    ATIP1_DARK.long_name = 'Dark_Count_10Hz'
    ATIP1_DARK.units = 'Cts/sec'
    ATIP1_DARK[:] = tip1.dark
    
    AMIP1_DARK = ncfile.createVariable('MIP_M1_DARK', np.uint16, ('MIP_M1_TIME',), zlib=True)
    AMIP1_DARK.long_name = 'Dark_Count_10Hz'
    AMIP1_DARK.units = 'Cts/sec'
    AMIP1_DARK[:] = mip1.dark
    # 
    ATIP1_RED = ncfile.createVariable('TIP_M1_RED', np.uint16, ('TIP_M1_TIME',), zlib=True)
    ATIP1_RED.long_name = 'Red_Count_10Hz'
    ATIP1_RED.units = 'Cts/sec'
    ATIP1_RED[:] = tip1.red
    # 
    AMIP1_MG = ncfile.createVariable('MIP_M1_MG', np.uint16, ('MIP_M1_TIME',), zlib=True)
    AMIP1_MG.long_name = 'Mg_Count_10Hz'
    AMIP1_MG.units = 'Cts/sec'
    AMIP1_MG[:] = mip1.Mg
    # 
    ATIP1_UV = ncfile.createVariable('TIP_M1_UV', np.uint16, ('TIP_M1_TIME',), zlib=True)
    ATIP1_UV.long_name = 'UV_Count_10Hz'
    ATIP1_UV.units = 'Cts/sec'
    ATIP1_UV[:] = tip1.uv
    # 
    AMIP1_VK = ncfile.createVariable('MIP_M1_VK', np.uint16, ('MIP_M1_TIME',), zlib=True)
    AMIP1_VK.long_name = 'VK_Count_10Hz'
    AMIP1_VK.units = 'Cts/sec'
    AMIP1_VK[:] = mip1.VK
    # 
    """
    SUVM Variables
    """
    # 
    ATIPSVM_TIME1 = ncfile.createVariable('TIP_SUVM_CCSDS_GPS_TIME', np.float64, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_TIME1.long_name = 'TIP_Scan_Mirror_CCSDS_GPS_time'
    ATIPSVM_TIME1.units = 'seconds'
    ATIPSVM_TIME1[:] = s2_gen.H9_CCSDS_GPS_time
    AMIPSVM_TIME1 = ncfile.createVariable('MIP_SUVM_CCSDS_GPS_TIME', np.float64, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_TIME1.long_name = 'MIP_Scan_Mirror_CCSDS_GPS_time'
    AMIPSVM_TIME1.units = 'seconds'
    AMIPSVM_TIME1[:] = s4_gen.H9_CCSDS_GPS_time
    # 
    ATIPSVM_TIME2 = ncfile.createVariable('TIP_SUVM_CCSDS_ECL_TIME', np.float64, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_TIME2.long_name = 'TIP_Scan_Mirror_CCSDS_ECLIPSE_GPS_time'
    ATIPSVM_TIME2.units = 'seconds'
    ATIPSVM_TIME2[:] = s2_gen.H9_CCSDS_ECL_time
    AMIPSVM_TIME2 = ncfile.createVariable('MIP_SUVM_CCSDS_ECL_TIME', np.float64, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_TIME2.long_name = 'MIP_Scan_Mirror_CCSDS_ECLIPSE_GPS_time'
    AMIPSVM_TIME2.units = 'seconds'
    AMIPSVM_TIME2[:] = s4_gen.H9_CCSDS_ECL_time
    # 
    ATIPSVM_TIME3 = ncfile.createVariable('TIP_SUVM_ECL_MOE_GPS_TIME', np.float64, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_TIME3.long_name = 'TIP_Scan_Mirror_ECLIPSE_MOE_GPS_time'
    ATIPSVM_TIME3.units = 'seconds'
    ATIPSVM_TIME3[:] = s2_gen.ECL_MOE_GPS_time
    AMIPSVM_TIME3 = ncfile.createVariable('MIP_SUVM_ECL_MOE_GPS_TIME', np.float64, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_TIME3.long_name = 'MIP_Scan_Mirror_ECLIPSE_MOE_GPS_time'
    AMIPSVM_TIME3.units = 'seconds'
    AMIPSVM_TIME3[:] = s4_gen.ECL_MOE_GPS_time
    # 
    ATIPSVM_SEQ = ncfile.createVariable('TIP_SUVM_SEQUENCE', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_SEQ.long_name = 'TIP_Scan_Mirror_Sequence_Count'
    ATIPSVM_SEQ[:] = s2_gen.sequence_count
    AMIPSVM_SEQ = ncfile.createVariable('MIP_SUVM_SEQUENCE', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_SEQ.long_name = 'MIP_Scan_Mirror_Sequence_Count'
    AMIPSVM_SEQ[:] = s4_gen.sequence_count
    # 
    ATIPSVM_SYSCT = ncfile.createVariable('TIP_SUVM_System_Counter', np.float64, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_SYSCT.long_name = 'TIP_Scan_Mirror_System_Counter'
    ATIPSVM_SYSCT.units = 'seconds'
    ATIPSVM_SYSCT[:] = s2_gen.system_counter
    AMIPSVM_SYSCT = ncfile.createVariable('MIP_SUVM_System_Counter', np.float64, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_SYSCT.long_name = 'MIP_Scan_Mirror_System_Counter'
    AMIPSVM_SYSCT.units = 'seconds'
    AMIPSVM_SYSCT[:] = s4_gen.system_counter
    # 
    ATIPSVM_GPSPPS = ncfile.createVariable('TIP_SUVM_GPS_PPS', np.float64, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_GPSPPS.long_name = 'TIP_Scan_Mirror_GPS_PPS'
    ATIPSVM_GPSPPS.units = 'seconds'
    ATIPSVM_GPSPPS[:] = s2_gen.gps_pps
    AMIPSVM_GPSPPS = ncfile.createVariable('MIP_SUVM_GPS_PPS', np.float64, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_GPSPPS.long_name = 'MIP_Scan_Mirror_GPS_PPS'
    AMIPSVM_GPSPPS.units = 'seconds'
    AMIPSVM_GPSPPS[:] = s4_gen.gps_pps
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
    ATIPSVM_LASTCMD_TIME = ncfile.createVariable('TIP_SUVM_LAST_CMD_TIME', np.float64, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_LASTCMD_TIME.long_name = 'TIP_Scan_Mirror_Last_Command_Time'
    ATIPSVM_LASTCMD_TIME.units = 'seconds'
    ATIPSVM_LASTCMD_TIME[:] = s2_gen.last_cmd_time
    AMIPSVM_LASTCMD_TIME = ncfile.createVariable('MIP_SUVM_LAST_CMD_TIME', np.float64, ('MIP_SUVM_TIME',), zlib=True)
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
    ATIPSVM_V5IMON = ncfile.createVariable('TIP_SUVM_V5_IMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_V5IMON.long_name = 'TIP_Scan_Mirror_5V_Current_Monitor'
    ATIPSVM_V5IMON.units = 'Amperes'
    ATIPSVM_V5IMON[:] = s2_gen.V5_IMON
    AMIPSVM_V5IMON = ncfile.createVariable('MIP_SUVM_V5_IMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_V5IMON.long_name = 'MIP_Scan_Mirror_5V_Current_Monitor'
    AMIPSVM_V5IMON.units = 'Amperes'
    AMIPSVM_V5IMON[:] = s4_gen.V5_IMON
    # 
    ATIPSVM_V5VMON = ncfile.createVariable('TIP_SUVM_V5_VMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_V5VMON.long_name = 'TIP_Scan_Mirror_5V_Voltage_Monitor'
    ATIPSVM_V5VMON.units = 'Volts'
    ATIPSVM_V5VMON[:] = s2_gen.V5_VMON
    AMIPSVM_V5VMON = ncfile.createVariable('MIP_SUVM_V5_VMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_V5VMON.long_name = 'MIP_Scan_Mirror_5V_Voltage_Monitor'
    AMIPSVM_V5VMON.units = 'Volts'
    AMIPSVM_V5VMON[:] = s4_gen.V5_VMON
    # 
    ATIPSVM_V3IMON = ncfile.createVariable('TIP_SUVM_V3_IMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_V3IMON.long_name = 'TIP_Scan_Mirror_3V_Current_Monitor'
    ATIPSVM_V3IMON.units = 'Amperes'
    ATIPSVM_V3IMON[:] = s2_gen.V3_IMON
    AMIPSVM_V3IMON = ncfile.createVariable('MIP_SUVM_V3_IMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_V3IMON.long_name = 'MIP_Scan_Mirror_3V_Current_Monitor'
    AMIPSVM_V3IMON.units = 'Amperes'
    AMIPSVM_V3IMON[:] = s4_gen.V3_IMON
    # 
    ATIPSVM_V3VMON = ncfile.createVariable('TIP_SUVM_V3_VMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_V3VMON.long_name = 'TIP_Scan_Mirror_3V_Voltage_Monitor'
    ATIPSVM_V3VMON.units = 'Volts'
    ATIPSVM_V3VMON[:] = s2_gen.V3_VMON
    AMIPSVM_V3VMON = ncfile.createVariable('MIP_SUVM_V3_VMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_V3VMON.long_name = 'MIP_Scan_Mirror_3V_Voltage_Monitor'
    AMIPSVM_V3VMON.units = 'Volts'
    AMIPSVM_V3VMON[:] = s4_gen.V3_VMON
    # 
    ATIPSVM_V22IMON = ncfile.createVariable('TIP_SUVM_V22_IMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_V22IMON.long_name = 'TIP_Scan_Mirror_22V_Current_Monitor'
    ATIPSVM_V22IMON.units = 'Amperes'
    ATIPSVM_V22IMON[:] = s2_gen.V22_IMON
    AMIPSVM_V22IMON = ncfile.createVariable('MIP_SUVM_V22_IMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_V22IMON.long_name = 'MIP_Scan_Mirror_22V_Current_Monitor'
    AMIPSVM_V22IMON.units = 'Amperes'
    AMIPSVM_V22IMON[:] = s4_gen.V22_IMON
    # 
    ATIPSVM_V22VMON = ncfile.createVariable('TIP_SUVM_V22_VMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_V22VMON.long_name = 'TIP_Scan_Mirror_22V_Voltage_Monitor'
    ATIPSVM_V22VMON.units = 'Volts'
    ATIPSVM_V22VMON[:] = s2_gen.V22_VMON
    AMIPSVM_V22VMON = ncfile.createVariable('MIP_SUVM_V22_VMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_V22VMON.long_name = 'MIP_Scan_Mirror_22V_Voltage_Monitor'
    AMIPSVM_V22VMON.units = 'Volts'
    AMIPSVM_V22VMON[:] = s4_gen.V22_VMON
    # 
    ATIPSVM_MOTORIMON = ncfile.createVariable('TIP_SUVM_MOTOR_IMON', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_MOTORIMON.long_name = 'TIP_Scan_Mirror_Motor_Current_Monitor'
    ATIPSVM_MOTORIMON.units = 'Amperes'
    ATIPSVM_MOTORIMON[:] = s2_gen.MOTOR_IMON
    AMIPSVM_MOTORIMON = ncfile.createVariable('MIP_SUVM_MOTOR_IMON', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_MOTORIMON.long_name = 'MIP_Scan_Mirror_Motor_Current_Monitor'
    AMIPSVM_MOTORIMON.units = 'Amperes'
    AMIPSVM_MOTORIMON[:] = s4_gen.MOTOR_IMON
    # 
    ATIPSVM_TEMP = ncfile.createVariable('TIP_SUVM_TEMP', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_TEMP.long_name = 'TIP_Scan_Mirror_Temperature'
    ATIPSVM_TEMP.units = 'Celsius'
    ATIPSVM_TEMP[:] = s2_gen.temperature
    AMIPSVM_TEMP = ncfile.createVariable('MIP_SUVM_TEMP', np.float32, ('MIP_SUVM_TIME',), zlib=True)
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
    ATIPSVM_ENCANGLE = ncfile.createVariable('TIP_SUVM_ENCODER_ANGLE', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_ENCANGLE.long_name = 'TIP_Scan_Mirror_Encoder_Angle'
    ATIPSVM_ENCANGLE.units = 'Degrees'
    ATIPSVM_ENCANGLE[:] = s2_gen.encoder_angle
    AMIPSVM_ENCANGLE = ncfile.createVariable('MIP_SUVM_ENCODER_ANGLE', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_ENCANGLE.long_name = 'MIP_Scan_Mirror_Encoder_Angle'
    AMIPSVM_ENCANGLE.units = 'Degrees'
    AMIPSVM_ENCANGLE[:] = s4_gen.encoder_angle
    # 
    ATIPSVM_TGTANGLE = ncfile.createVariable('TIP_SUVM_ENCODER_TARGET_ANGLE', np.float32, ('TIP_SUVM_TIME',), zlib=True)
    ATIPSVM_TGTANGLE.long_name = 'TIP_Scan_Mirror_Encoder_Target_Angle'
    ATIPSVM_TGTANGLE.units = 'Degrees'
    ATIPSVM_TGTANGLE[:] = s2_gen.target_angle
    AMIPSVM_TGTANGLE = ncfile.createVariable('MIP_SUVM_ENCODER_TARGET_ANGLE', np.float32, ('MIP_SUVM_TIME',), zlib=True)
    AMIPSVM_TGTANGLE.long_name = 'MIP_Scan_Mirror_Encoder_Target_Angle'
    AMIPSVM_TGTANGLE.units = 'Degrees'
    AMIPSVM_TGTANGLE[:] = s4_gen.target_angle
    # 
    
    # print(ncfile)
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
    
    return outname

def ECL_L0_CTS(fname: str, ebyte: list) -> str:
    """
    Generates .nc L0 file for daily ECLIPSE CTS data

    Parameters
    ----------
    fname : str
        Filename + path for input file
    ebyte : list
        eclipse_packet object of ECLIPSE_telemetry_breakout module
    
    Returns
    -------
    outname : str
        .nc L0 file created

    """
    (fpath, fbase_ext) = path.split(fname)
    (fbase, f_ext) = path.splitext(fbase_ext)
    
    fnew_ext = f"{fbase}_ECLIPSE_L0_CTS.nc"
    outname = path.join(fpath, 'L0_CTS', fnew_ext)
    # 
    print('Starting to generate the file(s) ... ')
    # 
    if len(ebyte.tip5_aux) > 0:
        print(f' ... {fbase}_CTS_TIP_aux_log.txt')
        generate_aux_logfile(ebyte.tip5_aux, path.join(fpath,'L0_CTS',f'{fbase}_CTS_TIP_aux_log.txt'))
    if len(ebyte.mip7_aux) > 0:
        print(f' ... {fbase}_CTS_MIP_aux_log.txt')
        generate_aux_logfile(ebyte.mip7_aux, path.join(fpath,'L0_CTS',f'{fbase}_CTS_MIP_aux_log.txt'))
    #
    print(' ... ' + outname)
    print('')
    # 
    tip0 = xpc.convert_m0_byt2dec(ebyte.tip5_m0, 'TIP')
    tip1 = xpc.convert_m1_byt2dec(ebyte.tip5_m1, 'TIP')
    mip0 = xpc.convert_m0_byt2dec(ebyte.mip7_m0, 'MIP')
    mip1 = xpc.convert_m1_byt2dec(ebyte.mip7_m1, 'MIP')
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
    ncfile.createDimension('TIP_M0_TIME', len(tip0.time))
    ncfile.createDimension('TIP_M1_TIME', len(tip1.time))
    ncfile.createDimension('TIP_SUVM_TIME', len(s6_gen.system_counter))
    ncfile.createDimension('MIP_M0_TIME', len(mip0.time))
    ncfile.createDimension('MIP_M1_TIME', len(mip1.time))
    ncfile.createDimension('MIP_SUVM_TIME', len(s8_gen.system_counter))
    # 
    # Create Attributes
    # 
    ### GLOBAL ATTRIBUTES specific to this file type
    ncfile.source_1 = fbase_ext
    ncfile.filename = outname
    ncfile.data_version = 'v1.1'
    ### REQUIRED GLOBAL ATTRIBUTES
    ECL_global_attributes(ncfile)
    """ 
    # XIP Variables
    
    M0 Vlues Not included:
    #         self.IDC_ID = np.zeros(n, dtype='U4')
    #         self.MODE             = np.zeros(n, dtype='U2')
    """
    # 
    CTIP0_GPSt1 = ncfile.createVariable('TIP_M0_CCSDS_GPS_TIME', np.float64, ('TIP_M0_TIME',), zlib=True)
    CTIP0_GPSt1.units = 'seconds'
    CTIP0_GPSt1.long_name = 'CTS_TIP_M0_H9_CCSDS_GPS_time'
    CTIP0_GPSt1[:] = tip0.H9_CCSDS_GPS_time
    CMIP0_GPSt1 = ncfile.createVariable('MIP_M0_CCSDS_GPS_TIME', np.float64, ('MIP_M0_TIME',), zlib=True)
    CMIP0_GPSt1.units = 'seconds'
    CMIP0_GPSt1.long_name = 'CTS_MIP_M0_H9_CCSDS_GPS_time'
    CMIP0_GPSt1[:] = mip0.H9_CCSDS_GPS_time
    #
    CTIP0_GPSt2 = ncfile.createVariable('TIP_M0_CCSDS_ECL_TIME', np.float64, ('TIP_M0_TIME',), zlib=True)
    CTIP0_GPSt2.units = 'seconds'
    CTIP0_GPSt2.long_name = 'CTS_TIP_M0_H9_CCSDS_ECLIPSE_GPS_time'
    CTIP0_GPSt2[:] = tip0.H9_CCSDS_ECL_time
    CMIP0_GPSt2 = ncfile.createVariable('MIP_M0_CCSDS_ECL_TIME', np.float64, ('MIP_M0_TIME',), zlib=True)
    CMIP0_GPSt2.units = 'seconds'
    CMIP0_GPSt2.long_name = 'CTS_MIP_M0_H9_CCSDS_ECLIPSE_GPS_time'
    CMIP0_GPSt2[:] = mip0.H9_CCSDS_ECL_time
    #
    CTIP0_GPSt3 = ncfile.createVariable('TIP_M0_ECL_MOE_GPS_TIME', np.float64, ('TIP_M0_TIME',), zlib=True)
    CTIP0_GPSt3.units = 'seconds'
    CTIP0_GPSt3.long_name = 'CTS_TIP_M0_ECLIPSE_MOE_GPS_time'
    CTIP0_GPSt3[:] = tip0.ECL_MOE_GPS_time
    CMIP0_GPSt3 = ncfile.createVariable('MIP_M0_ECL_MOE_GPS_TIME', np.float64, ('MIP_M0_TIME',), zlib=True)
    CMIP0_GPSt3.units = 'seconds'
    CMIP0_GPSt3.long_name = 'CTS_MIP_M0_ECLIPSE_MOE_GPS_time'
    CMIP0_GPSt3[:] = mip0.ECL_MOE_GPS_time
    # 
    CTIP0_TIME = ncfile.createVariable('TIP_M0_RUNTIME', np.uint64, ('TIP_M0_TIME',), zlib=True)
    CTIP0_TIME.units = 'seconds'
    CTIP0_TIME.long_name = 'system_run_time'
    CTIP0_TIME[:] = tip0.time
    CMIP0_TIME = ncfile.createVariable('MIP_M0_RUNTIME', np.uint64, ('MIP_M0_TIME',), zlib=True)
    CMIP0_TIME.units = 'seconds'
    CMIP0_TIME.long_name = 'system_run_time'
    CMIP0_TIME[:] = mip0.time
    # 
    CTIP0_DARK = ncfile.createVariable('TIP_M0_DARK', np.uint64, ('TIP_M0_TIME',), zlib=True)
    CTIP0_DARK.units = 'counts/sec'
    CTIP0_DARK.long_name = 'dark_PMT_counts'
    CTIP0_DARK[:] = tip0.dark
    CMIP0_DARK = ncfile.createVariable('MIP_M0_DARK', np.uint64, ('MIP_M0_TIME',), zlib=True)
    CMIP0_DARK.units = 'counts/sec'
    CMIP0_DARK.long_name = 'dark_PMT_counts'
    CMIP0_DARK[:] = mip0.dark
    # 
    CTIP0_RED = ncfile.createVariable('TIP_M0_RED', np.uint64, ('TIP_M0_TIME',), zlib=True)
    CTIP0_RED.units = 'counts/sec'
    CTIP0_RED.long_name = 'red_PMT_counts'
    CTIP0_RED[:] = tip0.red
    # 
    CMIP0_MG = ncfile.createVariable('MIP_M0_MG', np.uint64, ('MIP_M0_TIME',), zlib=True)
    CMIP0_MG.units = 'counts/sec'
    CMIP0_MG.long_name = 'Mg_PMT_counts'
    CMIP0_MG[:] = mip0.Mg
    # 
    CTIP0_UV = ncfile.createVariable('TIP_M0_UV', np.uint64, ('TIP_M0_TIME',), zlib=True)
    CTIP0_UV.units = 'counts/sec'
    CTIP0_UV.long_name = 'uv_PMT_counts'
    CTIP0_UV[:] = tip0.uv
    # 
    CMIP0_VK = ncfile.createVariable('MIP_M0_VK', np.uint64, ('MIP_M0_TIME',), zlib=True)
    CMIP0_VK.units = 'counts/sec'
    CMIP0_VK.long_name = 'VK_PMT_counts'
    CMIP0_VK[:] = mip0.VK
    # 
    CTIP0_HEATER = ncfile.createVariable('TIP_M0_HEATER', np.uint32, ('TIP_M0_TIME',), zlib=True)
    CTIP0_HEATER.long_name = 'heater_duty_cycle'
    CTIP0_HEATER[:] = tip0.heater
    # 
    # CMIP0_ERROR = ncfile.createVariable('MIP_M0_ERROR', np.uint32, ('MIP_M0_TIME',), zlib=True)
    # CMIP0_ERROR.long_name = 'error'
    # CMIP0_ERROR[:] = mip0.error
    # 
    CTIP0_TF1 = ncfile.createVariable('TIP_M0_TF1', np.float32, ('TIP_M0_TIME',), zlib=True)
    CTIP0_TF1.units = 'Celsius'
    CTIP0_TF1.long_name = 'filter_temperature_1'
    CTIP0_TF1[:] = tip0.T_F1
    # 
    CMIP0_TLENS = ncfile.createVariable('MIP_M0_TLENS', np.float32, ('MIP_M0_TIME',), zlib=True)
    CMIP0_TLENS.units = 'Celsius'
    CMIP0_TLENS.long_name = 'Lens_temperature'
    CMIP0_TLENS[:] = mip0.T_LENS
    # 
    CTIP0_TF2 = ncfile.createVariable('TIP_M0_TF2', np.float32, ('TIP_M0_TIME',), zlib=True)
    CTIP0_TF2.units = 'Celsius'
    CTIP0_TF2.long_name = 'filter_temperature_2'
    CTIP0_TF2[:] = tip0.T_F2
    #
    CMIP0_TPMT = ncfile.createVariable('MIP_M0_TPMT', np.float32, ('MIP_M0_TIME',), zlib=True)
    CMIP0_TPMT.units = 'Celsius'
    CMIP0_TPMT.long_name = 'PMT_block_temperature'
    CMIP0_TPMT[:] = mip0.T_PMT
    #
    CTIP0_HVMON = ncfile.createVariable('TIP_M0_HV_mon', np.float32, ('TIP_M0_TIME',), zlib=True)
    CTIP0_HVMON.units = 'Volts'
    CTIP0_HVMON.long_name = 'High_voltage_monitor'
    CTIP0_HVMON[:] = tip0.HV_mon
    CMIP0_HVMON = ncfile.createVariable('MIP_M0_HV_mon', np.float32, ('MIP_M0_TIME',), zlib=True)
    CMIP0_HVMON.units = 'Volts'
    CMIP0_HVMON.long_name = 'High_voltage_monitor'
    CMIP0_HVMON[:] = mip0.HV_mon
    #
    CTIP0_HVADJ = ncfile.createVariable('TIP_M0_HV_adj', np.float32, ('TIP_M0_TIME',), zlib=True)
    CTIP0_HVADJ.units = 'Volts'
    CTIP0_HVADJ.long_name = 'High_voltage_adjust'
    CTIP0_HVADJ[:] = tip0.HV_adj
    CMIP0_HVADJ = ncfile.createVariable('MIP_M0_HV_adj', np.float32, ('MIP_M0_TIME',), zlib=True)
    CMIP0_HVADJ.units = 'Volts'
    CMIP0_HVADJ.long_name = 'High_voltage_adjust'
    CMIP0_HVADJ[:] = mip0.HV_adj
    #
    CTIP0_SUN = ncfile.createVariable('TIP_M0_sun', np.float32, ('TIP_M0_TIME',), zlib=True)
    CTIP0_SUN.units = 'Volts'
    CTIP0_SUN.long_name = 'sun_sensor'
    CTIP0_SUN[:] = tip0.sun
    CMIP0_SUN = ncfile.createVariable('MIP_M0_sun', np.float32, ('MIP_M0_TIME',), zlib=True)
    CMIP0_SUN.units = 'Volts'
    CMIP0_SUN.long_name = 'sun_sensor'
    CMIP0_SUN[:] = mip0.sun
    #
    CTIP0_VREF = ncfile.createVariable('TIP_M0_VREF', np.float32, ('TIP_M0_TIME',), zlib=True)
    CTIP0_VREF.units = 'Volts'
    CTIP0_VREF.long_name = 'reference_voltage_2p5V'
    CTIP0_VREF[:] = tip0.vref
    CMIP0_VREF = ncfile.createVariable('MIP_M0_VREF', np.float32, ('MIP_M0_TIME',), zlib=True)
    CMIP0_VREF.units = 'Volts'
    CMIP0_VREF.long_name = 'reference_voltage_2p5V'
    CMIP0_VREF[:] = mip0.vref
    #
    CTIP0_TIDC = ncfile.createVariable('TIP_M0_TIDC', np.float32, ('TIP_M0_TIME',), zlib=True)
    CTIP0_TIDC.units = 'Celsius'
    CTIP0_TIDC.long_name = 'IDC_temperature'
    CTIP0_TIDC[:] = tip0.T_IDC
    CMIP0_TIDC = ncfile.createVariable('MIP_M0_TIDC', np.float32, ('MIP_M0_TIME',), zlib=True)
    CMIP0_TIDC.units = 'Celsius'
    CMIP0_TIDC.long_name = 'IDC_temperature'
    CMIP0_TIDC[:] = mip0.T_IDC
    #
    CTIP0_THV = ncfile.createVariable('TIP_M0_THV', np.float32, ('TIP_M0_TIME',), zlib=True)
    CTIP0_THV.units = 'Celsius'
    CTIP0_THV.long_name = 'high_voltage_temperature'
    CTIP0_THV[:] = tip0.T_HV
    CMIP0_THV = ncfile.createVariable('MIP_M0_THV', np.float32, ('MIP_M0_TIME',), zlib=True)
    CMIP0_THV.units = 'Celsius'
    CMIP0_THV.long_name = 'high_voltage_temperature'
    CMIP0_THV[:] = mip0.T_HV
    #
    # CTIP0_DISCRETE = ncfile.createVariable('TIP_M0_DISCRETE', np.str, ('TIP_M0_TIME',), zlib=True)
    # CTIP0_DISCRETE.long_name = 'discrete'
    # CTIP0_DISCRETE[:] = tip0.discrete
    # CMIP0_DISCRETE = ncfile.createVariable('MIP_M0_DISCRETE', np.str, ('MIP_M0_TIME',), zlib=True)
    # CMIP0_DISCRETE.long_name = 'discrete'
    # CMIP0_DISCRETE[:] = mip0.discrete
    #
    CTIP0_HVSTAT = ncfile.createVariable('TIP_M0_HV_Status', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    CTIP0_HVSTAT.long_name = 'High_Voltage_Status'
    CTIP0_HVSTAT[:] = tip0.HV_STATUS
    CMIP0_HVSTAT = ncfile.createVariable('MIP_M0_HV_Status', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    CMIP0_HVSTAT.long_name = 'High_Voltage_Status'
    CMIP0_HVSTAT[:] = mip0.HV_STATUS
    # 
    CTIP0_HVEVENT = ncfile.createVariable('TIP_M0_HV_Event', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    CTIP0_HVEVENT.long_name = 'High_Voltage_Exceed_Threshold'
    CTIP0_HVEVENT[:] = tip0.HV_EVENT
    CMIP0_HVEVENT = ncfile.createVariable('MIP_M0_HV_Event', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    CMIP0_HVEVENT.long_name = 'High_Voltage_Exceed_Threshold'
    CMIP0_HVEVENT[:] = mip0.HV_EVENT
    # 
    CTIP0_SUNEVENT = ncfile.createVariable('TIP_M0_Sun_Event', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    CTIP0_SUNEVENT.long_name = 'Sun_Sensor_Exceed_Threshold'
    CTIP0_SUNEVENT[:] = tip0.SUN_EVENT
    CMIP0_SUNEVENT = ncfile.createVariable('MIP_M0_Sun_Event', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    CMIP0_SUNEVENT.long_name = 'Sun_Sensor_Exceed_Threshold'
    CMIP0_SUNEVENT[:] = mip0.SUN_EVENT
    # 
    CTIP0_DKEVENT = ncfile.createVariable('TIP_M0_DK_EVENT', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    CTIP0_DKEVENT.long_name = 'PMT_Dark_Pad_Exceed_Threshold'
    CTIP0_DKEVENT[:] = tip0.DK_EVENT
    CMIP0_DKEVENT = ncfile.createVariable('MIP_M0_DK_EVENT', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    CMIP0_DKEVENT.long_name = 'PMT_Dark_Pad_Exceed_Threshold'
    CMIP0_DKEVENT[:] = mip0.DK_EVENT
    # 
    CTIP0_RDEVENT = ncfile.createVariable('TIP_M0_RD_EVENT', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    CTIP0_RDEVENT.long_name = 'PMT_Red_Pad_Exceed_Threshold'
    CTIP0_RDEVENT[:] = tip0.RD_EVENT
    CMIP0_RDEVENT = ncfile.createVariable('MIP_M0_RD_EVENT', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    CMIP0_RDEVENT.long_name = 'PMT_Red_Pad_Exceed_Threshold'
    CMIP0_RDEVENT[:] = mip0.RD_EVENT
    # 
    CTIP0_UVEVENT = ncfile.createVariable('TIP_M0_UV_EVENT', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    CTIP0_UVEVENT.long_name = 'PMT_UV_Pad_Exceed_Threshold'
    CTIP0_UVEVENT[:] = tip0.UV_EVENT
    CMIP0_UVEVENT = ncfile.createVariable('MIP_M0_UV_EVENT', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    CMIP0_UVEVENT.long_name = 'PMT_UV_Pad_Exceed_Threshold'
    CMIP0_UVEVENT[:] = mip0.UV_EVENT
    # 
    CTIP0_SUNOVERRIDE = ncfile.createVariable('TIP_M0_Sun_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    CTIP0_SUNOVERRIDE.long_name = 'Sun_Sensor_Override'
    CTIP0_SUNOVERRIDE[:] = tip0.SUN_OVERRIDE
    CMIP0_SUNOVERRIDE = ncfile.createVariable('MIP_M0_Sun_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    CMIP0_SUNOVERRIDE.long_name = 'Sun_Sensor_Override'
    CMIP0_SUNOVERRIDE[:] = mip0.SUN_OVERRIDE
    # 
    CTIP0_DKOVERRIDE = ncfile.createVariable('TIP_M0_Dark_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    CTIP0_DKOVERRIDE.long_name = 'Dark_Count_Override'
    CTIP0_DKOVERRIDE[:] = tip0.DK_OVERRIDE
    CMIP0_DKOVERRIDE = ncfile.createVariable('MIP_M0_Dark_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    CMIP0_DKOVERRIDE.long_name = 'Dark_Count_Override'
    CMIP0_DKOVERRIDE[:] = mip0.DK_OVERRIDE
    # 
    CTIP0_RD_OVERRIDE = ncfile.createVariable('TIP_M0_Red_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    CTIP0_RD_OVERRIDE.long_name = 'Red_Count_Override'
    CTIP0_RD_OVERRIDE[:] = tip0.RD_OVERRIDE
    CMIP0_RD_OVERRIDE = ncfile.createVariable('MIP_M0_Red_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    CMIP0_RD_OVERRIDE.long_name = 'Red_Count_Override'
    CMIP0_RD_OVERRIDE[:] = mip0.RD_OVERRIDE
    # 
    CTIP0_UVOVERRIDE = ncfile.createVariable('TIP_M0_UV_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    CTIP0_UVOVERRIDE.long_name = 'UV_Count_Override'
    CTIP0_UVOVERRIDE[:] = tip0.UV_OVERRIDE
    CMIP0_UVOVERRIDE = ncfile.createVariable('MIP_M0_UV_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    CMIP0_UVOVERRIDE.long_name = 'UV_Count_Override'
    CMIP0_UVOVERRIDE[:] = mip0.UV_OVERRIDE
    # 
    CTIP0_HVOVERRIDE = ncfile.createVariable('TIP_M0_HV_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    CTIP0_HVOVERRIDE.long_name = 'High_Voltage_Override'
    CTIP0_HVOVERRIDE[:] = tip0.HV_OVERRIDE
    CMIP0_HVOVERRIDE = ncfile.createVariable('MIP_M0_HV_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    CMIP0_HVOVERRIDE.long_name = 'High_Voltage_Override'
    CMIP0_HVOVERRIDE[:] = mip0.HV_OVERRIDE
    # 
    CTIP0_SHUTTEROVERRIDE = ncfile.createVariable('TIP_M0_Shutter_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    CTIP0_SHUTTEROVERRIDE.long_name = 'Shutter_Override'
    CTIP0_SHUTTEROVERRIDE[:] = tip0.SHUTTER_OVERRIDE
    CMIP0_SHUTTEROVERRIDE = ncfile.createVariable('MIP_M0_Shutter_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    CMIP0_SHUTTEROVERRIDE.long_name = 'Shutter_Override'
    CMIP0_SHUTTEROVERRIDE[:] = mip0.SHUTTER_OVERRIDE
    # 
    CTIP0_V5OVERRIDE = ncfile.createVariable('TIP_M0_5V_Override', np.ubyte, ('TIP_M0_TIME',), zlib=True)
    CTIP0_V5OVERRIDE.long_name = '5V_Override'
    CTIP0_V5OVERRIDE[:] = tip0.V5_OVERRIDE
    CMIP0_V5OVERRIDE = ncfile.createVariable('MIP_M0_5V_Override', np.ubyte, ('MIP_M0_TIME',), zlib=True)
    CMIP0_V5OVERRIDE.long_name = '5V_Override'
    CMIP0_V5OVERRIDE[:] = mip0.V5_OVERRIDE
    # 
    CTIP1_GPSt1 = ncfile.createVariable('TIP_M1_CCSDS_GPS_TIME', np.float64, ('TIP_M1_TIME',), zlib=True)
    CTIP1_GPSt1.long_name = 'CTS_TIP_CCSDS_GPS_time_10Hz'
    CTIP1_GPSt1.units = 'Seconds'
    CTIP1_GPSt1[:] = tip1.H9_CCSDS_GPS_time
    CMIP1_GPSt1 = ncfile.createVariable('MIP_M1_CCSDS_GPS_TIME', np.float64, ('MIP_M1_TIME',), zlib=True)
    CMIP1_GPSt1.long_name = 'CTS_MIP_CCSDS_GPS_time_10Hz'
    CMIP1_GPSt1.units = 'Seconds'
    CMIP1_GPSt1[:] = mip1.H9_CCSDS_GPS_time
    # 
    CTIP1_GPSt2 = ncfile.createVariable('TIP_M1_CCSDS_ECL_TIME', np.float64, ('TIP_M1_TIME',), zlib=True)
    CTIP1_GPSt2.long_name = 'CTS_TIP_CCSDS_ECLIPSE_GPS_time_10Hz'
    CTIP1_GPSt2.units = 'Seconds'
    CTIP1_GPSt2[:] = tip1.H9_CCSDS_ECL_time
    CMIP1_GPSt2 = ncfile.createVariable('MIP_M1_CCSDS_ECL_TIME', np.float64, ('MIP_M1_TIME',), zlib=True)
    CMIP1_GPSt2.long_name = 'CTS_MIP_CCSDS_ECLIPSE_GPS_time_10Hz'
    CMIP1_GPSt2.units = 'Seconds'
    CMIP1_GPSt2[:] = mip1.H9_CCSDS_ECL_time
    # 
    CTIP1_GPSt3 = ncfile.createVariable('TIP_M1_ECL_MOE_GPS_TIME', np.float64, ('TIP_M1_TIME',), zlib=True)
    CTIP1_GPSt3.long_name = 'CTS_TIP_ECLIPSE_MOE_GPS_time_10Hz'
    CTIP1_GPSt3.units = 'Seconds'
    CTIP1_GPSt3[:] = tip1.ECL_MOE_GPS_time
    CMIP1_GPSt3 = ncfile.createVariable('MIP_M1_ECL_MOE_GPS_TIME', np.float64, ('MIP_M1_TIME',), zlib=True)
    CMIP1_GPSt3.long_name = 'CTS_MIP_ECLIPSE_MOE_GPS_time_10Hz'
    CMIP1_GPSt3.units = 'Seconds'
    CMIP1_GPSt3[:] = mip1.ECL_MOE_GPS_time
    # 
    CTIP1_TIME = ncfile.createVariable('TIP_M1_RUNTIME', np.float64, ('TIP_M1_TIME',), zlib=True)
    CTIP1_TIME.long_name = 'System_Run_Time_10Hz'
    CTIP1_TIME.units = 'Seconds'
    CTIP1_TIME[:] = tip1.time
    
    CMIP1_TIME = ncfile.createVariable('MIP_M1_RUNTIME', np.float64, ('MIP_M1_TIME',), zlib=True)
    CMIP1_TIME.long_name = 'System_Run_Time_10Hz'
    CMIP1_TIME.units = 'Seconds'
    CMIP1_TIME[:] = mip1.time
    # 
    CTIP1_DARK = ncfile.createVariable('TIP_M1_DARK', np.uint16, ('TIP_M1_TIME',), zlib=True)
    CTIP1_DARK.long_name = 'Dark_Count_10Hz'
    CTIP1_DARK.units = 'Cts/sec'
    CTIP1_DARK[:] = tip1.dark
    CMIP1_DARK = ncfile.createVariable('MIP_M1_DARK', np.uint16, ('MIP_M1_TIME',), zlib=True)
    CMIP1_DARK.long_name = 'Dark_Count_10Hz'
    CMIP1_DARK.units = 'Cts/sec'
    CMIP1_DARK[:] = mip1.dark
    # 
    CTIP1_RED = ncfile.createVariable('TIP_M1_RED', np.uint16, ('TIP_M1_TIME',), zlib=True)
    CTIP1_RED.long_name = 'Red_Count_10Hz'
    CTIP1_RED.units = 'Cts/sec'
    CTIP1_RED[:] = tip1.red
    # 
    CMIP1_MG = ncfile.createVariable('MIP_M1_MG', np.uint16, ('MIP_M1_TIME',), zlib=True)
    CMIP1_MG.long_name = 'Mg_Count_10Hz'
    CMIP1_MG.units = 'Cts/sec'
    CMIP1_MG[:] = mip1.Mg
    # 
    CTIP1_UV = ncfile.createVariable('TIP_M1_UV', np.uint16, ('TIP_M1_TIME',), zlib=True)
    CTIP1_UV.long_name = 'UV_Count_10Hz'
    CTIP1_UV.units = 'Cts/sec'
    CTIP1_UV[:] = tip1.uv
    # 
    CMIP1_VK = ncfile.createVariable('MIP_M1_VK', np.uint16, ('MIP_M1_TIME',), zlib=True)
    CMIP1_VK.long_name = 'VK_Count_10Hz'
    CMIP1_VK.units = 'Cts/sec'
    CMIP1_VK[:] = mip1.VK
    # 
    """
    SUVM Variables
    """
    #
    CTIPSVM_TIME1 = ncfile.createVariable('TIP_SUVM_CCSDS_GPS_TIME', np.float64, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_TIME1.long_name = 'TIP_Scan_Mirror_CCSDS_GPS_time'
    CTIPSVM_TIME1.units = 'seconds'
    CTIPSVM_TIME1[:] = s6_gen.H9_CCSDS_GPS_time
    CMIPSVM_TIME1 = ncfile.createVariable('MIP_SUVM_CCSDS_GPS_TIME', np.float64, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_TIME1.long_name = 'MIP_Scan_Mirror_CCSDS_GPS_time'
    CMIPSVM_TIME1.units = 'seconds'
    CMIPSVM_TIME1[:] = s8_gen.H9_CCSDS_GPS_time
    # 
    CTIPSVM_TIME2 = ncfile.createVariable('TIP_SUVM_CCSDS_ECL_TIME', np.float64, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_TIME2.long_name = 'TIP_Scan_Mirror_CCSDS_ECLIPSE_GPS_time'
    CTIPSVM_TIME2.units = 'seconds'
    CTIPSVM_TIME2[:] = s6_gen.H9_CCSDS_ECL_time
    CMIPSVM_TIME2 = ncfile.createVariable('MIP_SUVM_CCSDS_ECL_TIME', np.float64, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_TIME2.long_name = 'MIP_Scan_Mirror_CCSDS_ECLIPSE_GPS_time'
    CMIPSVM_TIME2.units = 'seconds'
    CMIPSVM_TIME2[:] = s8_gen.H9_CCSDS_ECL_time
    # 
    CTIPSVM_TIME3 = ncfile.createVariable('TIP_SUVM_ECL_MOE_GPS_TIME', np.float64, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_TIME3.long_name = 'TIP_Scan_Mirror_ECLIPSE_MOE_GPS_time'
    CTIPSVM_TIME3.units = 'seconds'
    CTIPSVM_TIME3[:] = s6_gen.ECL_MOE_GPS_time
    CMIPSVM_TIME3 = ncfile.createVariable('MIP_SUVM_ECL_MOE_GPS_TIME', np.float64, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_TIME3.long_name = 'MIP_Scan_Mirror_ECLIPSE_MOE_GPS_time'
    CMIPSVM_TIME3.units = 'seconds'
    CMIPSVM_TIME3[:] = s8_gen.ECL_MOE_GPS_time
    # 
    CTIPSVM_SEQ = ncfile.createVariable('TIP_SUVM_SEQUENCE', np.ubyte, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_SEQ.long_name = 'TIP_Scan_Mirror_Sequence_Count'
    CTIPSVM_SEQ[:] = s6_gen.sequence_count
    CMIPSVM_SEQ = ncfile.createVariable('MIP_SUVM_SEQUENCE', np.ubyte, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_SEQ.long_name = 'MIP_Scan_Mirror_Sequence_Count'
    CMIPSVM_SEQ[:] = s8_gen.sequence_count
    # 
    CTIPSVM_SYSCT = ncfile.createVariable('TIP_SUVM_System_Counter', np.float64, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_SYSCT.long_name = 'TIP_Scan_Mirror_System_Counter'
    CTIPSVM_SYSCT.units = 'seconds'
    CTIPSVM_SYSCT[:] = s6_gen.system_counter
    CMIPSVM_SYSCT = ncfile.createVariable('MIP_SUVM_System_Counter', np.float64, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_SYSCT.long_name = 'MIP_Scan_Mirror_System_Counter'
    CMIPSVM_SYSCT.units = 'seconds'
    CMIPSVM_SYSCT[:] = s8_gen.system_counter
    # 
    CTIPSVM_GPSPPS = ncfile.createVariable('TIP_SUVM_GPS_PPS', np.float64, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_GPSPPS.long_name = 'TIP_Scan_Mirror_GPS_PPS'
    CTIPSVM_GPSPPS.units = 'seconds'
    CTIPSVM_GPSPPS[:] = s6_gen.gps_pps
    CMIPSVM_GPSPPS = ncfile.createVariable('MIP_SUVM_GPS_PPS', np.float64, ('MIP_SUVM_TIME',), zlib=True)
    CMIPSVM_GPSPPS.long_name = 'MIP_Scan_Mirror_GPS_PPS'
    CMIPSVM_GPSPPS.units = 'seconds'
    CMIPSVM_GPSPPS[:] = s8_gen.gps_pps
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
    CTIPSVM_LASTCMD_TIME = ncfile.createVariable('TIP_SUVM_LAST_CMD_TIME', np.float64, ('TIP_SUVM_TIME',), zlib=True)
    CTIPSVM_LASTCMD_TIME.long_name = 'TIP_Scan_Mirror_Last_Command_Time'
    CTIPSVM_LASTCMD_TIME.units = 'seconds'
    CTIPSVM_LASTCMD_TIME[:] = s6_gen.last_cmd_time
    CMIPSVM_LASTCMD_TIME = ncfile.createVariable('MIP_SUVM_LAST_CMD_TIME', np.float64, ('MIP_SUVM_TIME',), zlib=True)
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
    ncfile.close()
    # 
    print(f' CTS File Complete: {outname}\n')
    # 
    """
    Unused SUVM data (Byte #):
    header (0-3); apid (4-5); length (6-7); watchdog_counter (24-27)
    version (28-31); reset_status (32); flash_last_op (46)
    flash_status (47);  general_hk_flags (48-51)
    ROM_SBE (56-57); ROM_MBE (58-59); RAM_SBE (60-61); RAM_MBE (62-63)
    GPIO_A (64-67); GPIO_B (68-71)
    launch_lock_flags (72-75); VC_LIMIT_CHECK (76-77); motor_flags (104-105)
    """
    
    return outname

def ECL_L0_ISS(fname: str, iss_name: str, iss_byte: list[bytearray]) -> str:
    """
    Generates .nc L0 file for ISS position information related to ECLIPSE mssn

    Parameters
    ----------
    fname : str
        Filename + path for input file for ECLIPSE data
    iss_name : str
        Filename + path for input file for ISS data
    iss_byte : list[bytearray]
        List of byte values for ISS data created by eclipse_h9_ccsds module

    Returns
    -------
    outname : str
        .nc L0 file created

    """
    (fpath, fbase_ext) = path.split(fname)
    (ipath, ibase_ext) = path.split(iss_name)
    (fbase, f_ext) = path.splitext(fbase_ext)
    # 
    fnew_ext = f"{fbase}_ECLIPSE_L0_ISS.nc"
    outname = path.join(fpath, 'L0_ISS', fnew_ext)
    # 
    print(f'Starting to generate the file ... \n ... {outname}\n')
    # 
    iss_df = h9gnc.load_stph9_hs_packet_674f6(iss_byte)
    iss    = h9gnc.convert_stph9_hs_df_to_dataclass(iss_df)
    # _______________________
    # Generate a NetCDF File
    ncfile = Dataset(outname,mode='w',format='NETCDF4') 
    # __________________
    # Define Dimensions
    ncfile.createDimension('nRec', len(iss_df))
    ncfile.createDimension('nVec', 3)
    ncfile.createDimension('nQuat', 4)
    # __________________
    # Create Attributes
    ### GLOBAL ATTRIBUTES specific to this file type
    ncfile.source_1 = ibase_ext
    ncfile.filename = outname
    ncfile.title    = 'ISS Time + Position Info'
    ncfile.data_version = 'v1.0'
    ncfile.APID     = '674f6'
    ### REQUIRED GLOBAL ATTRIBUTES
    ECL_global_attributes(ncfile)
    # 
    # ncfile.logical_file_id = "ECL_H0_MIP_20220801_V01 [TBR]"
    # ncfile.logical_source  = "SLN_H0_MIP [TBR]"
    # ncfile.logical_source_description = "ISS H&S Data"
    ncfile.mods = "v0 - Initial Release"
    # 
    v00 = ncfile.createVariable('Year', np.uint16, ('nRec',), zlib=True)
    v00[:] = iss.yyyy
    v01 = ncfile.createVariable('Month', np.ubyte, ('nRec',), zlib=True)
    v01[:] = iss.mm
    v02 = ncfile.createVariable('Day', np.ubyte, ('nRec',), zlib=True)
    v02[:] = iss.dd
    v03 = ncfile.createVariable('Hour', np.ubyte, ('nRec',), zlib=True)
    v03[:] = iss.hh
    v04 = ncfile.createVariable('Minute', np.ubyte, ('nRec',), zlib=True)
    v04[:] = iss.mn
    v05 = ncfile.createVariable('Second', np.ubyte, ('nRec',), zlib=True)
    v05[:] = iss.ss
    v06 = ncfile.createVariable('Sec_of_day', np.float64, ('nRec',), zlib=True)
    v06[:] = iss.secondofday
    v07 = ncfile.createVariable('Sec_of_week', np.float64, ('nRec',), zlib=True)
    v07[:] = iss.secondofweek
    v08 = ncfile.createVariable('Day_of_week', np.ubyte, ('nRec',), zlib=True)
    v08[:] = iss.dayofweek
    # v09 = ncfile.createVariable('Day_name', 'S1', ('nRec',), zlib=True)
    # v09[:] = np.zeros(86400, dtype='str') #### Currently no support for strings
    
    v10 = ncfile.createVariable('DOY', np.float64, ('nRec',), zlib=True)
    v10.long_name = 'Day of Year'
    v10[:] = iss.doy
    v11 = ncfile.createVariable('Julian', np.float64, ('nRec',), zlib=True)
    v11.long_name = 'Julian Day'
    v11[:] = iss.jd
    v12 = ncfile.createVariable('MET', np.uint32, ('nRec',), zlib=True)
    v12.units = 'Seconds'
    v12.long_name = 'Mission Elapsed Time'
    v12[:] = iss.met
    v13 = ncfile.createVariable('GPS', np.uint32, ('nRec',), zlib=True)
    v13.units = 'Seconds'
    v13.long_name = 'GPS Time'
    v13[:] = iss.gpssec
    v20 = ncfile.createVariable('GPS_cumul', np.uint32, ('nRec',), zlib=True)
    v20.units = 'Seconds'
    v20.long_name = 'GPS Cumulative Time'
    v20[:] = iss.gpscumul
    v21 = ncfile.createVariable('GPS_WEEK', np.uint32, ('nRec',), zlib=True)
    v21.long_name = 'GPS Weeks'
    v21[:] = iss.gpsweek
    v22 = ncfile.createVariable('GPS_SEC', np.uint32, ('nRec',), zlib=True)
    v22.long_name = 'GPS Seconds'
    v22[:] = iss.gpssec
    
    v23 = ncfile.createVariable('USGNC_SEC', 'f8', ('nRec',), zlib=True)
    v23.units     = 'Seconds'
    v23.long_name = 'U.S. Guidance, Navigation and Control Time'
    v23[:] = iss.usgnc_sec
    
    v24 = ncfile.createVariable('USGNC_POSN_INERT', 'f4', ('nRec','nVec'), zlib=True)
    v24.units     = 'km'
    v24.long_name = 'U.S. Guidance, Navigation and Control Position (ECI)'
    v24[:] = iss.posn_inert
    v25 = ncfile.createVariable('Radius', 'f8', ('nRec',), zlib=True)
    v25.units     = 'km'
    v25.long_name = 'Radial distance to ISS'
    v25[:] = iss.radius
    v26 = ncfile.createVariable('Rhat', 'f8', ('nRec','nVec'), zlib=True)
    v26.long_name = 'Unit radial vector pointing to ISS'
    v26[:] = iss.rhat
    
    v27 = ncfile.createVariable('USGNC_VEL_INERT', 'f4', ('nRec','nVec'), zlib=True)
    v27.units     = 'km/s'
    v27.long_name = 'U.S. Guidance, Navigation and Control Inertial Velocity'
    v27[:] = iss.velc_inert
    v28 = ncfile.createVariable('Speed', 'f8', ('nRec',), zlib=True)
    v28.units     = 'km/s'
    v28.long_name = 'Scalar speed of ISS'
    v28[:] = iss.speed
    v29 = ncfile.createVariable('Vhat', 'f8', ('nRec','nVec'), zlib=True)
    v29.long_name = 'ISS Velocity Unit Vector'
    v29[:] = iss.vhat
    
    v30 = ncfile.createVariable('USGNC_RATE_INERT', 'f4', ('nRec','nVec'), zlib=True)
    v30.long_name = 'U.S. Guidance, Navigation and Control Rate'
    v30[:] = iss.rate_inert
    v31 = ncfile.createVariable('USGNC_QUAT_INERT', 'f4', ('nRec','nQuat'), zlib=True)
    v31.long_name = 'U.S. Guidance, Navigation and Control Quaternion'
    v31[:] = iss.quat_inert
    
    v32 = ncfile.createVariable('USGNC_QUAT_LVLH', 'f4', ('nRec','nQuat'), zlib=True)
    v32.long_name = 'U.S. Guidance, Navigation and Control Quaternion (LVLH)'
    v32[:] = iss.quat_lvlh
    
    v33 = ncfile.createVariable('USGNC_POSN_CTRS', 'f4', ('nRec','nVec'), zlib=True)
    v33.units     = 'km'
    v33.long_name = 'U.S. Guidance, Navigation and Control Position'
    v33[:] = iss.posn_ctrs
    v34 = ncfile.createVariable('USGNC_VEL_CTRS', 'f4', ('nRec','nVec'), zlib=True)
    v34.units     = 'km/sec'
    v34.long_name = 'U.S. Guidance, Navigation and Control Velocity'
    v34[:] = iss.velc_ctrs
    v35 = ncfile.createVariable('USGNC_QUAT_CTRS', 'f4', ('nRec','nQuat'), zlib=True)
    v35.long_name = 'U.S. Guidance, Navigation and Control Quaternion'
    v35[:] = iss.quat_ctrs
    
    ncfile.close()
    return outname
    # print(iss.quat_ctrs[0:10][:])
    # 
def print_L0_ECLIPSE_summary(ebyte: list, iss_byte: list[bytearray], rtdir: str) -> None:
    """
    
    Parameters
    ----------
    ebyte : list
        DESCRIPTION.
    iss_byte : list[bytearray]
        DESCRIPTION.
    rtdir : str
        Path to the directory where the file should be placed

    Returns
    -------
    None
        DESCRIPTION.
    
    """
    iss_df = h9gnc.load_stph9_hs_packet_674f6(iss_byte)
    iss    = h9gnc.convert_stph9_hs_df_to_dataclass(iss_df)
    
    atip0 = xpc.convert_m0_byt2dec(ebyte.tip1_m0,'TIP')
    amip0 = xpc.convert_m0_byt2dec(ebyte.mip3_m0,'MIP')
    ctip0 = xpc.convert_m0_byt2dec(ebyte.tip5_m0,'TIP')
    cmip0 = xpc.convert_m0_byt2dec(ebyte.mip7_m0,'MIP')
    
    ymd = f'{int(np.median(iss.yyyy))}/{int(np.median(iss.mm)):02}/{int(np.median(iss.dd)):02}'
    doy = f'{int(np.median(iss.doy))}'
    n_iiba = f'{len(ebyte.analog1):>6}'
    n_iibc = f'{len(ebyte.analog2):>6}'
    #___TIP_ALS
    n_lrt_ta = f'{len(ebyte.tip1_m0):>8}'
    n_hrt_ta = f'{len(ebyte.tip1_m1):>8}'
    n_aux_ta = f'{len(ebyte.tip1_aux):>8}'
    n_svm_ta = f'{len(ebyte.suvm2):>8}'
    try:
        hvv_ta = f'{round(max(atip0.HV_mon)):>6}'
    except ValueError:
        hvv_ta = f'{0:>6}'
    #___MIP_ALS
    n_lrt_ma = f'{len(ebyte.mip3_m0):>8}'
    n_hrt_ma = f'{len(ebyte.mip3_m1):>8}'
    n_aux_ma = f'{len(ebyte.mip3_aux):>8}'
    n_svm_ma = f'{len(ebyte.suvm4):>8}'
    try:
        hvv_ma = f'{round(max(amip0.HV_mon)):>6}'
    except ValueError:
        hvv_ma = f'{0:>6}'
    #___TIP_CTS
    n_lrt_tc = f'{len(ebyte.tip5_m0):>8}'
    n_hrt_tc = f'{len(ebyte.tip5_m1):>8}'
    n_aux_tc = f'{len(ebyte.tip5_aux):>8}'
    n_svm_tc = f'{len(ebyte.suvm6):>8}'
    try:
        hvv_tc = f'{round(max(ctip0.HV_mon)):>6}'
    except ValueError:
        hvv_tc = f'{0:>6}'
    #___MIP_CTS
    n_lrt_mc = f'{len(ebyte.mip7_m0):>8}'
    n_hrt_mc = f'{len(ebyte.mip7_m1):>8}'
    n_aux_mc = f'{len(ebyte.mip7_aux):>8}'
    n_svm_mc = f'{len(ebyte.suvm8):>8}'
    try:
        hvv_mc = f'{round(max(cmip0.HV_mon)):>6}'
    except ValueError:
        hvv_mc = f'{0:>6}'
    
    filename = f'{rtdir}{int(np.median(iss.yyyy))}{int(np.median(iss.doy)):03}_eclipse_daily_status.txt'
    
    print(f'Generating L0 logfile: ... {filename}')
    
    header = 'YYYY/MM/DD DOY n_iiba n_iibc \
n_lrt_ta n_hrt_ta n_aux_ta hvv_ta n_svm_ta \
n_lrt_ma n_hrt_ma n_aux_ma hvv_ma n_svm_ma \
n_lrt_tc n_hrt_tc n_aux_tc hvv_tc n_svm_tc \
n_lrt_mc n_hrt_mc n_aux_mc hvv_mc n_svm_mc\n'
    print(header)
    
    dout = f'{ymd} {doy} {n_iiba} {n_iibc} \
{n_lrt_ta} {n_hrt_ta} {n_aux_ta} {hvv_ta} {n_svm_ta} \
{n_lrt_ma} {n_hrt_ma} {n_aux_ma} {hvv_ma} {n_svm_ma} \
{n_lrt_tc} {n_hrt_tc} {n_aux_tc} {hvv_tc} {n_svm_tc} \
{n_lrt_mc} {n_hrt_mc} {n_aux_mc} {hvv_mc} {n_svm_mc}'
    print(dout)
    
    with open(filename, 'w') as fp:
        fp.write(header)
        fp.write(dout)
        # for i, c in enumerate(aux):
        #     time = iso_t.fits
        #     fp.write(f'{time} {command[0:4]}\n')
    
    return
    # 
def main() -> None:
    eclpath = 'D:/ECLIPSE/flt/'
    YYYY = 2026
    for DOY in range(174, 175):
        tic = time.time()
        # Change f-string to f'{DOY:03}' to make a 3 char string with 0-padding
        ecl_load = f'{eclpath}RAW_OUT/NRL_1729_{YYYY}{DOY:03}.out'
        ecl_name = f'D:/ECLIPSE/flt/NRL_1729_{YYYY}{DOY:03}.out'
        iss_name = f'D:/STPH9/flt/NRL_674f6_{YYYY}{DOY:03}'
        # Load / parse the binary data
        iss_byte, iss_ccsds_time = ehc.load_iss_hs_bytes_from_ccsds(iss_name)
        ecl_ccsds_byte, h9_ccsds_time, ecl_ccsds_time = ehc.load_eclipse_bytes_from_ccsds(ecl_load)
        ebyte = etb.breakout_hrt_packet(ecl_ccsds_byte, h9_ccsds_time, ecl_ccsds_time)
        # 
        print(f'\n Loading {ecl_name} ...\n Loading {iss_name} ...\n{ebyte}\n')
        ### Convert the binary data
        iss_file    = ECL_L0_ISS(ecl_name, iss_name, iss_byte)
        analog_file = ECL_L0_analog(ecl_name, ebyte)
        cts_file    = ECL_L0_CTS(ecl_name, ebyte)
        als_file    = ECL_L0_ALS(ecl_name, ebyte)
        toc = time.time()
        
        print_L0_ECLIPSE_summary(ebyte, iss_byte, f'{eclpath}L0_log/')
        
        print(f' Completed for {DOY = } in {(toc-tic):.2f} seconds\n')
        
        sv = 1
        L0_plot.ecl0_iss_data_plot(iss_file, save=sv)
        L0_plot.ecl0_analog_survey_plot(analog_file, save=sv)
        
        L0_plot.ecl0_survey_plot(cts_file, unit='CTS', content='TIP_HK', save=sv)
        L0_plot.ecl0_survey_plot(cts_file, unit='CTS', content='MIP_HK', save=sv)
        L0_plot.ecl0_survey_plot(cts_file, unit='CTS', content='SUVM_HK', save=sv)
        
        L0_plot.ecl0_survey_plot(als_file, unit='ALS', content='TIP_HK', save=sv)
        L0_plot.ecl0_survey_plot(als_file, unit='ALS', content='MIP_HK', save=sv)
        L0_plot.ecl0_survey_plot(als_file, unit='ALS', content='SUVM_HK', save=sv)
        
    
    # import netCDF4 as nc

    # # Open the NetCDF file
    # dataset = nc.Dataset('your_file.nc', 'r')

    # # Access and print global attributes
    # print("Global attributes:")
    # for attr_name in dataset.ncattrs():
    #     print(f"{attr_name}: {dataset.getncattr(attr_name)}")
    
    
if __name__ == "__main__":
    print(f"==== {__file__} ====")
    main()
