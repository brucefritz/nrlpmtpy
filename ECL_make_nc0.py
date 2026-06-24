#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: ECL_make_nc0.py
Author: Bruce A. Fritz, NRL Code 7634
Version: 1.1
Date:   v1.0  2023-03-20, Created
        v1.1  2024-12-17, Updated Header for git upload
        v2.0  2026-06-24, Major refactor 
Description: Executable main() script to process ECLIPSE TLM CCSDS files into
    separated L0 files

Classes:
    None

Functions:
    ECL_global_attributes() sets global attributes in the L0 file
    ECL_L0_analog() creats a .nc file that contains 1 day of IIB analog data
    generate_aux_logfile() creates a .txt file containing all AUX messages
    ECL_L0_survey() generates the daily ALS or CTS survey L0 file
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
            be willing to grant the same to the ECLIPSE team in similar circumstances.
        4.	Users that wish to publish results derived from ECLIPSE data should
            coordinate with the ECLIPSE team to assure that the data are not
            being used in a way that is contrary to or duplicative of ongoing
            ECLIPSE team efforts. This is especially important because ECLIPSE
            scientists are still deriving the optimal techniques for processing
            the data.
        5.	Users are required to include a brief acknowledgement of NRL and
            ECLIPSE sponsors in any published results.
    """
    ncfile.acknowledgement = ACK_TEXT
    ncfile.rules_of_the_road = RULES_TEXT
    ncfile.eclipse_description = eclipse_text
    return

def _create_var(ncfile: Dataset, name: str, dtype, dim: str, data,
                 units: str = None, long_name: str = None):
    """
    Creates a netCDF4 variable, optionally sets its 'units'/'long_name'
    attributes, and fills it with data.
    """
    var = ncfile.createVariable(name, dtype, (dim,), zlib=True)
    if units is not None:
        var.units = units
    if long_name is not None:
        var.long_name = long_name
    var[:] = data
    return var

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
    # Each entry: (suffix, dtype, units, long_name, analog1_attr, analog2_attr)
    analog_vars = [
        ('GPS_time',          np.uint32,  'seconds', 'analog_GPS_time',        'GPS_time', 'GPS_time'),
        ('MIP_I_12V',         np.float32, 'Amps',     'MIP_12V_current',        'I_mip12V', 'I_mip12V'),
        ('MIP_V_12V',         np.float32, 'Volts',    'MIP_12V_voltage',        'V_mip12V', 'V_mip12V'),
        ('MIP_I_3V',          np.float32, 'Amps',     'MIP_3V_current',         'I_mip3V',  'I_mip3V'),
        ('MIP_V_3V',          np.float32, 'Volts',    'MIP_3V_voltage',         'V_mip3V',  'V_mip3V'),
        ('TIP_I_12V',         np.float32, 'Amps',     'TIP_12V_current',        'I_tip12V', 'I_tip12V'),
        ('TIP_V_12V',         np.float32, 'Volts',    'TIP_12V_voltage',        'V_tip12V', 'V_tip12V'),
        ('TIP_I_3V',          np.float32, 'Amps',     'TIP_3V_current',         'I_tip3V',  'I_tip3V'),
        ('TIP_V_3V',          np.float32, 'Volts',    'TIP_3V_voltage',         'V_tip3V',  'V_tip3V'),
        ('TIP_SUVM_I_5V',     np.float32, 'Amps',     'TIP_SUVM_5V_current',    'I_tsm5V',  'I_tsm5V'),
        ('TIP_SUVM_V_5V',     np.float32, 'Volts',    'TIP_SUVM_5V_voltage',    'V_tsm5V',  'V_tsm5V'),
        ('TIP_SUVM_I_3V',     np.float32, 'Amps',     'TIP_SUVM_3V_current',    'I_tsm3V',  'I_tsm3V'),
        ('TIP_SUVM_V_3V',     np.float32, 'Volts',    'TIP_SUVM_3V_voltage',    'V_tsm3V',  'V_tsm3V'),
        ('MIP_SUVM_I_5V',     np.float32, 'Amps',     'MIP_SUVM_5V_current',    'I_msm5V',  'I_msm5V'),
        ('MIP_SUVM_V_5V',     np.float32, 'Volts',    'MIP_SUVM_5V_voltage',    'V_msm5V',  'V_msm5V'),
        ('MIP_SUVM_I_3V',     np.float32, 'Amps',     'MIP_SUVM_3V_current',    'I_msm3V',  'I_msm3V'),
        ('MIP_SUVM_V_3V',     np.float32, 'Volts',    'MIP_SUVM_3V_voltage',    'V_msm3V',  'V_msm3V'),
        ('TIP_SUVM_V_28V',    np.float32, 'Volts',    'TIP_SUVM_28V_voltage',   'V_tsm28V', 'V_tsm28V'),
        ('MIP_SUVM_V_28V',    np.float32, 'Volts',    'MIP_SUVM_28V_voltage',   'V_msm28V', 'V_msm28V'),
    ]
    for suffix, dtype, units, lname_tag, attr1, attr2 in analog_vars:
        _create_var(ncfile, f'ALS_{suffix}', dtype, 'ALS_time',
                    getattr(analog1, attr1), units=units, long_name=f'ALS_{lname_tag}')
        _create_var(ncfile, f'CTS_{suffix}', dtype, 'CTS_time',
                    getattr(analog2, attr2), units=units, long_name=f'CTS_{lname_tag}')
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

# Per-unit configuration distinguishing ALS vs CTS survey files.
_SURVEY_CONFIG = {
    'ALS': dict(out_subdir='L0_ALS', data_version='v1.0',
                tip_m0='tip1_m0', tip_m1='tip1_m1', tip_aux='tip1_aux',
                mip_m0='mip3_m0', mip_m1='mip3_m1', mip_aux='mip3_aux',
                suvm_tip='suvm2', suvm_mip='suvm4'),
    'CTS': dict(out_subdir='L0_CTS', data_version='v1.1',
                tip_m0='tip5_m0', tip_m1='tip5_m1', tip_aux='tip5_aux',
                mip_m0='mip7_m0', mip_m1='mip7_m1', mip_aux='mip7_aux',
                suvm_tip='suvm6', suvm_mip='suvm8'),
}

def ECL_L0_survey(fname: str, ebyte: list, unit: str) -> str:
    """
    Generates daily ECLIPSE survey (ALS or CTS) L0 file

    Parameters
    ----------
    fname : str
        Input filename
    ebyte : list
        eclipse_packet object of ECLIPSE_telemetry_breakout module
    unit : str
        Which survey unit to generate, 'ALS' or 'CTS'

    Returns
    -------
    outname : str
        .nc L0 file created

    """
    cfg = _SURVEY_CONFIG[unit]
    (fpath, fbase_ext) = path.split(fname)
    (fbase, f_ext) = path.splitext(fbase_ext)
    #
    fnew_ext = f"{fbase}_ECLIPSE_L0_{unit}.nc"
    outname = path.join(fpath, cfg['out_subdir'], fnew_ext)
    #
    print(f'Starting to generate the file(s) ... \n ... {outname}\n')
    #
    tip_aux = getattr(ebyte, cfg['tip_aux'])
    mip_aux = getattr(ebyte, cfg['mip_aux'])
    if len(tip_aux) > 0:
        print(f' ... {fbase}_{unit}_TIP_aux_log.txt\n')
        generate_aux_logfile(tip_aux, path.join(fpath, cfg['out_subdir'], f'{fbase}_{unit}_TIP_aux_log.txt'))
    if len(mip_aux) > 0:
        print(f' ... {fbase}_{unit}_MIP_aux_log.txt\n')
        generate_aux_logfile(mip_aux, path.join(fpath, cfg['out_subdir'], f'{fbase}_{unit}_MIP_aux_log.txt'))
    #
    ncfile = Dataset(outname,mode='w',format='NETCDF4')
    #
    tip0 = xpc.convert_m0_byt2dec(getattr(ebyte, cfg['tip_m0']), 'TIP')
    tip1 = xpc.convert_m1_byt2dec(getattr(ebyte, cfg['tip_m1']), 'TIP')
    mip0 = xpc.convert_m0_byt2dec(getattr(ebyte, cfg['mip_m0']), 'MIP')
    mip1 = xpc.convert_m1_byt2dec(getattr(ebyte, cfg['mip_m1']), 'MIP')
    #
    s_tip_byte = etb.breakout_suvm_packet(getattr(ebyte, cfg['suvm_tip']))
    s_tip = spc.suvm_general_converter(s_tip_byte)
    s_mip_byte = etb.breakout_suvm_packet(getattr(ebyte, cfg['suvm_mip']))
    s_mip = spc.suvm_general_converter(s_mip_byte)
    #
    # Define Dimensions
    ncfile.createDimension('TIP_M0_TIME', len(tip0.time))
    ncfile.createDimension('TIP_M1_TIME', len(tip1.time))
    ncfile.createDimension('TIP_SUVM_TIME', len(s_tip.system_counter))
    ncfile.createDimension('MIP_M0_TIME', len(mip0.time))
    ncfile.createDimension('MIP_M1_TIME', len(mip1.time))
    ncfile.createDimension('MIP_SUVM_TIME', len(s_mip.system_counter))
    #
    # Create Attributes
    #
    ### GLOBAL ATTRIBUTES specific to this file type
    ncfile.source_1 = fbase_ext
    ncfile.filename = outname
    ncfile.data_version = cfg['data_version']
    ### REQUIRED GLOBAL ATTRIBUTES
    ECL_global_attributes(ncfile)
    """
    # XIP Variables

    M0 Vlues Not included:
    #         self.IDC_ID = np.zeros(n, dtype='U4')
    #         self.MODE             = np.zeros(n, dtype='U2')
    """
    # M0 variables shared by TIP and MIP
    _create_var(ncfile, 'TIP_M0_CCSDS_GPS_TIME', np.float64, 'TIP_M0_TIME', tip0.H9_CCSDS_GPS_time, units='seconds', long_name=f'{unit}_TIP_M0_H9_CCSDS_GPS_time')
    _create_var(ncfile, 'MIP_M0_CCSDS_GPS_TIME', np.float64, 'MIP_M0_TIME', mip0.H9_CCSDS_GPS_time, units='seconds', long_name=f'{unit}_MIP_M0_H9_CCSDS_GPS_time')
    _create_var(ncfile, 'TIP_M0_CCSDS_ECL_TIME', np.float64, 'TIP_M0_TIME', tip0.H9_CCSDS_ECL_time, units='seconds', long_name=f'{unit}_TIP_M0_CCSDS_ECLIPSE_GPS_time')
    _create_var(ncfile, 'MIP_M0_CCSDS_ECL_TIME', np.float64, 'MIP_M0_TIME', mip0.H9_CCSDS_ECL_time, units='seconds', long_name=f'{unit}_MIP_M0_CCSDS_ECLIPSE_GPS_time')
    _create_var(ncfile, 'TIP_M0_ECL_MOE_GPS_TIME', np.float64, 'TIP_M0_TIME', tip0.ECL_MOE_GPS_time, units='seconds', long_name=f'{unit}_TIP_M0_ECLIPSE_MOE_GPS_time')
    _create_var(ncfile, 'MIP_M0_ECL_MOE_GPS_TIME', np.float64, 'MIP_M0_TIME', mip0.ECL_MOE_GPS_time, units='seconds', long_name=f'{unit}_MIP_M0_ECLIPSE_MOE_GPS_time')
    _create_var(ncfile, 'TIP_M0_RUNTIME', np.uint64, 'TIP_M0_TIME', tip0.time, units='seconds', long_name='system_run_time')
    _create_var(ncfile, 'MIP_M0_RUNTIME', np.uint64, 'MIP_M0_TIME', mip0.time, units='seconds', long_name='system_run_time')
    _create_var(ncfile, 'TIP_M0_DARK', np.uint64, 'TIP_M0_TIME', tip0.dark, units='counts/sec', long_name='dark_PMT_counts')
    _create_var(ncfile, 'MIP_M0_DARK', np.uint64, 'MIP_M0_TIME', mip0.dark, units='counts/sec', long_name='dark_PMT_counts')
    # TIP-only / MIP-only M0 channels
    _create_var(ncfile, 'TIP_M0_RED', np.uint64, 'TIP_M0_TIME', tip0.red, units='counts/sec', long_name='red_PMT_counts')
    _create_var(ncfile, 'MIP_M0_MG', np.uint64, 'MIP_M0_TIME', mip0.Mg, units='counts/sec', long_name='Mg_PMT_counts')
    _create_var(ncfile, 'TIP_M0_UV', np.uint64, 'TIP_M0_TIME', tip0.uv, units='counts/sec', long_name='uv_PMT_counts')
    _create_var(ncfile, 'MIP_M0_VK', np.uint64, 'MIP_M0_TIME', mip0.VK, units='counts/sec', long_name='VK_PMT_counts')
    _create_var(ncfile, 'TIP_M0_HEATER', np.uint32, 'TIP_M0_TIME', tip0.heater, long_name='heater_duty_cycle')
    # AMIP0_ERROR not currently populated upstream
    _create_var(ncfile, 'TIP_M0_TF1', np.float32, 'TIP_M0_TIME', tip0.T_F1, units='Celsius', long_name='filter_temperature_1')
    _create_var(ncfile, 'MIP_M0_TLENS', np.float32, 'MIP_M0_TIME', mip0.T_LENS, units='Celsius', long_name='Lens_temperature')
    _create_var(ncfile, 'TIP_M0_TF2', np.float32, 'TIP_M0_TIME', tip0.T_F2, units='Celsius', long_name='filter_temperature_2')
    _create_var(ncfile, 'MIP_M0_TPMT', np.float32, 'MIP_M0_TIME', mip0.T_PMT, units='Celsius', long_name='PMT_block_temperature')
    _create_var(ncfile, 'TIP_M0_HV_mon', np.float32, 'TIP_M0_TIME', tip0.HV_mon, units='Volts', long_name='High_voltage_monitor')
    _create_var(ncfile, 'MIP_M0_HV_mon', np.float32, 'MIP_M0_TIME', mip0.HV_mon, units='Volts', long_name='High_voltage_monitor')
    _create_var(ncfile, 'TIP_M0_HV_adj', np.float32, 'TIP_M0_TIME', tip0.HV_adj, units='Volts', long_name='High_voltage_adjust')
    _create_var(ncfile, 'MIP_M0_HV_adj', np.float32, 'MIP_M0_TIME', mip0.HV_adj, units='Volts', long_name='High_voltage_adjust')
    _create_var(ncfile, 'TIP_M0_sun', np.float32, 'TIP_M0_TIME', tip0.sun, units='Volts', long_name='sun_sensor')
    _create_var(ncfile, 'MIP_M0_sun', np.float32, 'MIP_M0_TIME', mip0.sun, units='Volts', long_name='sun_sensor')
    _create_var(ncfile, 'TIP_M0_VREF', np.float32, 'TIP_M0_TIME', tip0.vref, units='Volts', long_name='reference_voltage_2p5V')
    _create_var(ncfile, 'MIP_M0_VREF', np.float32, 'MIP_M0_TIME', mip0.vref, units='Volts', long_name='reference_voltage_2p5V')
    _create_var(ncfile, 'TIP_M0_TIDC', np.float32, 'TIP_M0_TIME', tip0.T_IDC, units='Celsius', long_name='IDC_temperature')
    _create_var(ncfile, 'MIP_M0_TIDC', np.float32, 'MIP_M0_TIME', mip0.T_IDC, units='Celsius', long_name='IDC_temperature')
    _create_var(ncfile, 'TIP_M0_THV', np.float32, 'TIP_M0_TIME', tip0.T_HV, units='Celsius', long_name='high_voltage_temperature')
    _create_var(ncfile, 'MIP_M0_THV', np.float32, 'MIP_M0_TIME', mip0.T_HV, units='Celsius', long_name='high_voltage_temperature')
    # ATIP0_DISCRETE / AMIP0_DISCRETE not currently populated upstream (np.str unsupported)
    _create_var(ncfile, 'TIP_M0_HV_Status', np.ubyte, 'TIP_M0_TIME', tip0.HV_STATUS, long_name='High_Voltage_Status')
    _create_var(ncfile, 'MIP_M0_HV_Status', np.ubyte, 'MIP_M0_TIME', mip0.HV_STATUS, long_name='High_Voltage_Status')
    _create_var(ncfile, 'TIP_M0_HV_Event', np.ubyte, 'TIP_M0_TIME', tip0.HV_EVENT, long_name='High_Voltage_Exceed_Threshold')
    _create_var(ncfile, 'MIP_M0_HV_Event', np.ubyte, 'MIP_M0_TIME', mip0.HV_EVENT, long_name='High_Voltage_Exceed_Threshold')
    _create_var(ncfile, 'TIP_M0_Sun_Event', np.ubyte, 'TIP_M0_TIME', tip0.SUN_EVENT, long_name='Sun_Sensor_Exceed_Threshold')
    _create_var(ncfile, 'MIP_M0_Sun_Event', np.ubyte, 'MIP_M0_TIME', mip0.SUN_EVENT, long_name='Sun_Sensor_Exceed_Threshold')
    _create_var(ncfile, 'TIP_M0_DK_EVENT', np.ubyte, 'TIP_M0_TIME', tip0.DK_EVENT, long_name='PMT_Dark_Pad_Exceed_Threshold')
    _create_var(ncfile, 'MIP_M0_DK_EVENT', np.ubyte, 'MIP_M0_TIME', mip0.DK_EVENT, long_name='PMT_Dark_Pad_Exceed_Threshold')
    _create_var(ncfile, 'TIP_M0_RD_EVENT', np.ubyte, 'TIP_M0_TIME', tip0.RD_EVENT, long_name='PMT_Red_Pad_Exceed_Threshold')
    _create_var(ncfile, 'MIP_M0_RD_EVENT', np.ubyte, 'MIP_M0_TIME', mip0.RD_EVENT, long_name='PMT_Red_Pad_Exceed_Threshold')
    _create_var(ncfile, 'TIP_M0_UV_EVENT', np.ubyte, 'TIP_M0_TIME', tip0.UV_EVENT, long_name='PMT_UV_Pad_Exceed_Threshold')
    _create_var(ncfile, 'MIP_M0_UV_EVENT', np.ubyte, 'MIP_M0_TIME', mip0.UV_EVENT, long_name='PMT_UV_Pad_Exceed_Threshold')
    _create_var(ncfile, 'TIP_M0_Sun_Override', np.ubyte, 'TIP_M0_TIME', tip0.SUN_OVERRIDE, long_name='Sun_Sensor_Override')
    _create_var(ncfile, 'MIP_M0_Sun_Override', np.ubyte, 'MIP_M0_TIME', mip0.SUN_OVERRIDE, long_name='Sun_Sensor_Override')
    _create_var(ncfile, 'TIP_M0_Dark_Override', np.ubyte, 'TIP_M0_TIME', tip0.DK_OVERRIDE, long_name='Dark_Count_Override')
    _create_var(ncfile, 'MIP_M0_Dark_Override', np.ubyte, 'MIP_M0_TIME', mip0.DK_OVERRIDE, long_name='Dark_Count_Override')
    _create_var(ncfile, 'TIP_M0_Red_Override', np.ubyte, 'TIP_M0_TIME', tip0.RD_OVERRIDE, long_name='Red_Count_Override')
    _create_var(ncfile, 'MIP_M0_Red_Override', np.ubyte, 'MIP_M0_TIME', mip0.RD_OVERRIDE, long_name='Red_Count_Override')
    _create_var(ncfile, 'TIP_M0_UV_Override', np.ubyte, 'TIP_M0_TIME', tip0.UV_OVERRIDE, long_name='UV_Count_Override')
    _create_var(ncfile, 'MIP_M0_UV_Override', np.ubyte, 'MIP_M0_TIME', mip0.UV_OVERRIDE, long_name='UV_Count_Override')
    _create_var(ncfile, 'TIP_M0_HV_Override', np.ubyte, 'TIP_M0_TIME', tip0.HV_OVERRIDE, long_name='High_Voltage_Override')
    _create_var(ncfile, 'MIP_M0_HV_Override', np.ubyte, 'MIP_M0_TIME', mip0.HV_OVERRIDE, long_name='High_Voltage_Override')
    _create_var(ncfile, 'TIP_M0_Shutter_Override', np.ubyte, 'TIP_M0_TIME', tip0.SHUTTER_OVERRIDE, long_name='Shutter_Override')
    _create_var(ncfile, 'MIP_M0_Shutter_Override', np.ubyte, 'MIP_M0_TIME', mip0.SHUTTER_OVERRIDE, long_name='Shutter_Override')
    _create_var(ncfile, 'TIP_M0_5V_Override', np.ubyte, 'TIP_M0_TIME', tip0.V5_OVERRIDE, long_name='5V_Override')
    _create_var(ncfile, 'MIP_M0_5V_Override', np.ubyte, 'MIP_M0_TIME', mip0.V5_OVERRIDE, long_name='5V_Override')
    """
    # M1 Variables

    Not included:
        # tip1 / mip1 .dark_chk = np.zeros(10*n, dtype='uint64')
        # tip1        .red_chk = np.zeros(n, dtype='uint64')
        # tip1        .uv_chk  = np.zeros(n, dtype='uint64')
        # mip1        .Mg_chk = np.zeros(n, dtype='uint64')
        # mip1        .VK_chk = np.zeros(n, dtype='uint64')

    """
    _create_var(ncfile, 'TIP_M1_CCSDS_GPS_TIME', np.float64, 'TIP_M1_TIME', tip1.H9_CCSDS_GPS_time, units='Seconds', long_name=f'{unit}_TIP_CCSDS_GPS_time_10Hz')
    _create_var(ncfile, 'MIP_M1_CCSDS_GPS_TIME', np.float64, 'MIP_M1_TIME', mip1.H9_CCSDS_GPS_time, units='Seconds', long_name=f'{unit}_MIP_CCSDS_GPS_time_10Hz')
    _create_var(ncfile, 'TIP_M1_CCSDS_ECL_TIME', np.float64, 'TIP_M1_TIME', tip1.H9_CCSDS_ECL_time, units='Seconds', long_name=f'{unit}_TIP_CCSDS_ECLIPSE_GPS_time_10Hz')
    _create_var(ncfile, 'MIP_M1_CCSDS_ECL_TIME', np.float64, 'MIP_M1_TIME', mip1.H9_CCSDS_ECL_time, units='Seconds', long_name=f'{unit}_MIP_CCSDS_ECLIPSE_GPS_time_10Hz')
    _create_var(ncfile, 'TIP_M1_ECL_MOE_GPS_TIME', np.float64, 'TIP_M1_TIME', tip1.ECL_MOE_GPS_time, units='Seconds', long_name=f'{unit}_TIP_ECLIPSE_MOE_GPS_time_10Hz')
    _create_var(ncfile, 'MIP_M1_ECL_MOE_GPS_TIME', np.float64, 'MIP_M1_TIME', mip1.ECL_MOE_GPS_time, units='Seconds', long_name=f'{unit}_MIP_ECLIPSE_MOE_GPS_time_10Hz')
    _create_var(ncfile, 'TIP_M1_RUNTIME', np.float64, 'TIP_M1_TIME', tip1.time, units='Seconds', long_name='System_Run_Time_10Hz')
    _create_var(ncfile, 'MIP_M1_RUNTIME', np.float64, 'MIP_M1_TIME', mip1.time, units='Seconds', long_name='System_Run_Time_10Hz')
    _create_var(ncfile, 'TIP_M1_DARK', np.uint16, 'TIP_M1_TIME', tip1.dark, units='Cts/sec', long_name='Dark_Count_10Hz')
    _create_var(ncfile, 'MIP_M1_DARK', np.uint16, 'MIP_M1_TIME', mip1.dark, units='Cts/sec', long_name='Dark_Count_10Hz')
    _create_var(ncfile, 'TIP_M1_RED', np.uint16, 'TIP_M1_TIME', tip1.red, units='Cts/sec', long_name='Red_Count_10Hz')
    _create_var(ncfile, 'MIP_M1_MG', np.uint16, 'MIP_M1_TIME', mip1.Mg, units='Cts/sec', long_name='Mg_Count_10Hz')
    _create_var(ncfile, 'TIP_M1_UV', np.uint16, 'TIP_M1_TIME', tip1.uv, units='Cts/sec', long_name='UV_Count_10Hz')
    _create_var(ncfile, 'MIP_M1_VK', np.uint16, 'MIP_M1_TIME', mip1.VK, units='Cts/sec', long_name='VK_Count_10Hz')
    """
    SUVM Variables
    """
    _create_var(ncfile, 'TIP_SUVM_CCSDS_GPS_TIME', np.float64, 'TIP_SUVM_TIME', s_tip.H9_CCSDS_GPS_time, units='seconds', long_name='TIP_Scan_Mirror_CCSDS_GPS_time')
    _create_var(ncfile, 'MIP_SUVM_CCSDS_GPS_TIME', np.float64, 'MIP_SUVM_TIME', s_mip.H9_CCSDS_GPS_time, units='seconds', long_name='MIP_Scan_Mirror_CCSDS_GPS_time')
    _create_var(ncfile, 'TIP_SUVM_CCSDS_ECL_TIME', np.float64, 'TIP_SUVM_TIME', s_tip.H9_CCSDS_ECL_time, units='seconds', long_name='TIP_Scan_Mirror_CCSDS_ECLIPSE_GPS_time')
    _create_var(ncfile, 'MIP_SUVM_CCSDS_ECL_TIME', np.float64, 'MIP_SUVM_TIME', s_mip.H9_CCSDS_ECL_time, units='seconds', long_name='MIP_Scan_Mirror_CCSDS_ECLIPSE_GPS_time')
    _create_var(ncfile, 'TIP_SUVM_ECL_MOE_GPS_TIME', np.float64, 'TIP_SUVM_TIME', s_tip.ECL_MOE_GPS_time, units='seconds', long_name='TIP_Scan_Mirror_ECLIPSE_MOE_GPS_time')
    _create_var(ncfile, 'MIP_SUVM_ECL_MOE_GPS_TIME', np.float64, 'MIP_SUVM_TIME', s_mip.ECL_MOE_GPS_time, units='seconds', long_name='MIP_Scan_Mirror_ECLIPSE_MOE_GPS_time')
    _create_var(ncfile, 'TIP_SUVM_SEQUENCE', np.ubyte, 'TIP_SUVM_TIME', s_tip.sequence_count, long_name='TIP_Scan_Mirror_Sequence_Count')
    _create_var(ncfile, 'MIP_SUVM_SEQUENCE', np.ubyte, 'MIP_SUVM_TIME', s_mip.sequence_count, long_name='MIP_Scan_Mirror_Sequence_Count')
    _create_var(ncfile, 'TIP_SUVM_System_Counter', np.float64, 'TIP_SUVM_TIME', s_tip.system_counter, units='seconds', long_name='TIP_Scan_Mirror_System_Counter')
    _create_var(ncfile, 'MIP_SUVM_System_Counter', np.float64, 'MIP_SUVM_TIME', s_mip.system_counter, units='seconds', long_name='MIP_Scan_Mirror_System_Counter')
    _create_var(ncfile, 'TIP_SUVM_GPS_PPS', np.float64, 'TIP_SUVM_TIME', s_tip.gps_pps, units='seconds', long_name='TIP_Scan_Mirror_GPS_PPS')
    _create_var(ncfile, 'MIP_SUVM_GPS_PPS', np.float64, 'MIP_SUVM_TIME', s_mip.gps_pps, units='seconds', long_name='MIP_Scan_Mirror_GPS_PPS')
    _create_var(ncfile, 'TIP_SUVM_LAST_COMMAND_STATUS', np.ubyte, 'TIP_SUVM_TIME', s_tip.last_cmd_status, long_name='TIP_Scan_Mirror_Last_Command_Status')
    _create_var(ncfile, 'MIP_SUVM_LAST_COMMAND_STATUS', np.ubyte, 'MIP_SUVM_TIME', s_mip.last_cmd_status, long_name='MIP_Scan_Mirror_Last_Command_Status')
    _create_var(ncfile, 'TIP_SUVM_LAST_COMMAND_ID', np.ubyte, 'TIP_SUVM_TIME', s_tip.last_cmd_id, long_name='TIP_Scan_Mirror_Last_Command_ID')
    _create_var(ncfile, 'MIP_SUVM_LAST_COMMAND_ID', np.ubyte, 'MIP_SUVM_TIME', s_mip.last_cmd_id, long_name='MIP_Scan_Mirror_Last_Command_ID')
    _create_var(ncfile, 'TIP_SUVM_LAST_OP_CODE', np.ubyte, 'TIP_SUVM_TIME', s_tip.last_cmd_opcode, long_name='TIP_Scan_Mirror_Last_Command_Op_Code')
    _create_var(ncfile, 'MIP_SUVM_LAST_OP_CODE', np.ubyte, 'MIP_SUVM_TIME', s_mip.last_cmd_opcode, long_name='MIP_Scan_Mirror_Last_Command_Op_Code')
    _create_var(ncfile, 'TIP_SUVM_LAST_CMD_TIME', np.float64, 'TIP_SUVM_TIME', s_tip.last_cmd_time, units='seconds', long_name='TIP_Scan_Mirror_Last_Command_Time')
    _create_var(ncfile, 'MIP_SUVM_LAST_CMD_TIME', np.float64, 'MIP_SUVM_TIME', s_mip.last_cmd_time, units='seconds', long_name='MIP_Scan_Mirror_Last_Command_Time')
    _create_var(ncfile, 'TIP_SUVM_LAST_CMD_SUCCESS', np.ubyte, 'TIP_SUVM_TIME', s_tip.cmd_success, long_name='TIP_Scan_Mirror_Last_Command_Success')
    _create_var(ncfile, 'MIP_SUVM_LAST_CMD_SUCCESS', np.ubyte, 'MIP_SUVM_TIME', s_mip.cmd_success, long_name='MIP_Scan_Mirror_Last_Command_Success')
    _create_var(ncfile, 'TIP_SUVM_LAST_CMD_FAIL', np.ubyte, 'TIP_SUVM_TIME', s_tip.cmd_fail, long_name='TIP_Scan_Mirror_Last_Command_Fail')
    _create_var(ncfile, 'MIP_SUVM_LAST_CMD_FAIL', np.ubyte, 'MIP_SUVM_TIME', s_mip.cmd_fail, long_name='MIP_Scan_Mirror_Last_Command_Fail')
    _create_var(ncfile, 'TIP_SUVM_LAST_CRC', np.uint32, 'TIP_SUVM_TIME', s_tip.last_crc, long_name='TIP_Scan_Mirror_Last_CRC')
    _create_var(ncfile, 'MIP_SUVM_LAST_CRC', np.uint32, 'MIP_SUVM_TIME', s_mip.last_crc, long_name='MIP_Scan_Mirror_Last_CRC')
    _create_var(ncfile, 'TIP_SUVM_V5_IMON', np.float32, 'TIP_SUVM_TIME', s_tip.V5_IMON, units='Amperes', long_name='TIP_Scan_Mirror_5V_Current_Monitor')
    _create_var(ncfile, 'MIP_SUVM_V5_IMON', np.float32, 'MIP_SUVM_TIME', s_mip.V5_IMON, units='Amperes', long_name='MIP_Scan_Mirror_5V_Current_Monitor')
    _create_var(ncfile, 'TIP_SUVM_V5_VMON', np.float32, 'TIP_SUVM_TIME', s_tip.V5_VMON, units='Volts', long_name='TIP_Scan_Mirror_5V_Voltage_Monitor')
    _create_var(ncfile, 'MIP_SUVM_V5_VMON', np.float32, 'MIP_SUVM_TIME', s_mip.V5_VMON, units='Volts', long_name='MIP_Scan_Mirror_5V_Voltage_Monitor')
    _create_var(ncfile, 'TIP_SUVM_V3_IMON', np.float32, 'TIP_SUVM_TIME', s_tip.V3_IMON, units='Amperes', long_name='TIP_Scan_Mirror_3V_Current_Monitor')
    _create_var(ncfile, 'MIP_SUVM_V3_IMON', np.float32, 'MIP_SUVM_TIME', s_mip.V3_IMON, units='Amperes', long_name='MIP_Scan_Mirror_3V_Current_Monitor')
    _create_var(ncfile, 'TIP_SUVM_V3_VMON', np.float32, 'TIP_SUVM_TIME', s_tip.V3_VMON, units='Volts', long_name='TIP_Scan_Mirror_3V_Voltage_Monitor')
    _create_var(ncfile, 'MIP_SUVM_V3_VMON', np.float32, 'MIP_SUVM_TIME', s_mip.V3_VMON, units='Volts', long_name='MIP_Scan_Mirror_3V_Voltage_Monitor')
    _create_var(ncfile, 'TIP_SUVM_V22_IMON', np.float32, 'TIP_SUVM_TIME', s_tip.V22_IMON, units='Amperes', long_name='TIP_Scan_Mirror_22V_Current_Monitor')
    _create_var(ncfile, 'MIP_SUVM_V22_IMON', np.float32, 'MIP_SUVM_TIME', s_mip.V22_IMON, units='Amperes', long_name='MIP_Scan_Mirror_22V_Current_Monitor')
    _create_var(ncfile, 'TIP_SUVM_V22_VMON', np.float32, 'TIP_SUVM_TIME', s_tip.V22_VMON, units='Volts', long_name='TIP_Scan_Mirror_22V_Voltage_Monitor')
    _create_var(ncfile, 'MIP_SUVM_V22_VMON', np.float32, 'MIP_SUVM_TIME', s_mip.V22_VMON, units='Volts', long_name='MIP_Scan_Mirror_22V_Voltage_Monitor')
    _create_var(ncfile, 'TIP_SUVM_MOTOR_IMON', np.float32, 'TIP_SUVM_TIME', s_tip.MOTOR_IMON, units='Amperes', long_name='TIP_Scan_Mirror_Motor_Current_Monitor')
    _create_var(ncfile, 'MIP_SUVM_MOTOR_IMON', np.float32, 'MIP_SUVM_TIME', s_mip.MOTOR_IMON, units='Amperes', long_name='MIP_Scan_Mirror_Motor_Current_Monitor')
    _create_var(ncfile, 'TIP_SUVM_TEMP', np.float32, 'TIP_SUVM_TIME', s_tip.temperature, units='Celsius', long_name='TIP_Scan_Mirror_Temperature')
    _create_var(ncfile, 'MIP_SUVM_TEMP', np.float32, 'MIP_SUVM_TIME', s_mip.temperature, units='Celsius', long_name='MIP_Scan_Mirror_Temperature')
    _create_var(ncfile, 'TIP_SUVM_ENCODER_ZERO_OFFSET', np.short, 'TIP_SUVM_TIME', s_tip.encoder_zero_offset, long_name='TIP_Scan_Mirror_Encoder_Zero_Offset')
    _create_var(ncfile, 'MIP_SUVM_ENCODER_ZERO_OFFSET', np.short, 'MIP_SUVM_TIME', s_mip.encoder_zero_offset, long_name='MIP_Scan_Mirror_Encoder_Zero_Offset')
    _create_var(ncfile, 'TIP_SUVM_ENCODER_CURRENT_CT', np.short, 'TIP_SUVM_TIME', s_tip.encoder_current_ct, long_name='TIP_Scan_Mirror_Encoder_Current_Count')
    _create_var(ncfile, 'MIP_SUVM_ENCODER_CURRENT_CT', np.short, 'MIP_SUVM_TIME', s_mip.encoder_current_ct, long_name='MIP_Scan_Mirror_Encoder_Current_Count')
    _create_var(ncfile, 'TIP_SUVM_ENCODER_TARGET', np.short, 'TIP_SUVM_TIME', s_tip.encoder_target, long_name='TIP_Scan_Mirror_Encoder_Target')
    _create_var(ncfile, 'MIP_SUVM_ENCODER_TARGET', np.short, 'MIP_SUVM_TIME', s_mip.encoder_target, long_name='MIP_Scan_Mirror_Encoder_Target')
    _create_var(ncfile, 'TIP_SUVM_ENCODER_PROFILE_INDEX', np.uint16, 'TIP_SUVM_TIME', s_tip.profile_index, long_name='TIP_Scan_Mirror_Encoder_Profile_Index')
    _create_var(ncfile, 'MIP_SUVM_ENCODER_PROFILE_INDEX', np.uint16, 'MIP_SUVM_TIME', s_mip.profile_index, long_name='MIP_Scan_Mirror_Encoder_Profile_Index')
    _create_var(ncfile, 'TIP_SUVM_PWM_RATE', np.uint32, 'TIP_SUVM_TIME', s_tip.pwm_rate, units='Hz', long_name='TIP_Scan_Mirror_Motor_PWM_Rate')
    _create_var(ncfile, 'MIP_SUVM_PWM_RATE', np.uint32, 'MIP_SUVM_TIME', s_mip.pwm_rate, units='Hz', long_name='MIP_Scan_Mirror_Motor_PWM_Rate')
    _create_var(ncfile, 'TIP_SUVM_PWM_CTS_REMAIN', np.uint32, 'TIP_SUVM_TIME', s_tip.pwm_counts_remain, long_name='TIP_Scan_Mirror_Motor_PWM_Counts_Remain')
    _create_var(ncfile, 'MIP_SUVM_PWM_CTS_REMAIN', np.uint32, 'MIP_SUVM_TIME', s_mip.pwm_counts_remain, long_name='MIP_Scan_Mirror_Motor_PWM_Counts_Remain')
    _create_var(ncfile, 'TIP_SUVM_CRC', np.uint32, 'TIP_SUVM_TIME', s_tip.crc, long_name='TIP_Scan_Mirror_CRC')
    _create_var(ncfile, 'MIP_SUVM_CRC', np.uint32, 'MIP_SUVM_TIME', s_mip.crc, long_name='MIP_Scan_Mirror_CRC')
    _create_var(ncfile, 'TIP_SUVM_ENCODER_ANGLE', np.float32, 'TIP_SUVM_TIME', s_tip.encoder_angle, units='Degrees', long_name='TIP_Scan_Mirror_Encoder_Angle')
    _create_var(ncfile, 'MIP_SUVM_ENCODER_ANGLE', np.float32, 'MIP_SUVM_TIME', s_mip.encoder_angle, units='Degrees', long_name='MIP_Scan_Mirror_Encoder_Angle')
    _create_var(ncfile, 'TIP_SUVM_ENCODER_TARGET_ANGLE', np.float32, 'TIP_SUVM_TIME', s_tip.target_angle, units='Degrees', long_name='TIP_Scan_Mirror_Encoder_Target_Angle')
    _create_var(ncfile, 'MIP_SUVM_ENCODER_TARGET_ANGLE', np.float32, 'MIP_SUVM_TIME', s_mip.target_angle, units='Degrees', long_name='MIP_Scan_Mirror_Encoder_Target_Angle')
    #
    # print(ncfile)
    ncfile.close()

    print(f' {unit} File Complete: ' + outname)
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
        cts_file    = ECL_L0_survey(ecl_name, ebyte, 'CTS')
        als_file    = ECL_L0_survey(ecl_name, ebyte, 'ALS')
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
