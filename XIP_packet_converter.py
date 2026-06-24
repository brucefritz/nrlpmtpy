# -*- coding: utf-8 -*-
"""
Filename: XIP_packet_converter.py
Author: Bruce A. Fritz, NRL Code 7634
Description: Set of functions to load Tri-XIP telemetry and parse into
            meaningful (decimal) values

Date:   v1.0 2025-01-02, Created
Mods:   v1.1 2025-04-21, Modified class structure to add "sort_by" method
                         Create new GPS time based on internal XIP timer
        v1.2 2025-11-03, Modified M0/M1 classes to include additional time tags
        v1.3 2026-06-24, Fixed heater base-16 parsing, error field hex decode,
                         and MODE/HV_STATUS binary decode; vectorized the
                         timer-rollover correction loop

Classes:
    IDC_M0() --> Data frame (length of n-records) to hold basic 1 Hz telemetry
                 from XIP IDC M0 output
    IDC_M1() --> Data frame (length of n-records) to hold high rate, 10 Hz,
                 telemetry from XIP IDC M1 output

Functions:
    convert_m0_byt2dec(din,xip) --> Convert Python 'bytearray' of Tri-XIP
                output from the binary HRT files to Python list; then
                convert to the IDC_M0() class described above
    convert_m1_byt2dec(din,xip) --> Same as above but for the M1 data class
    convert_m0_hex2dec(m, xip) --> Primary function; parses ASCII M0 fromes
                from IDC and fills "IDC_M0" class with decimal values
    convert_m1_hex2dec(m, xip) --> Primary function; parses ASCII M1 frames
                from IDC and fills "IDC_M1" class with decimal values
    IDC_DN_to_dec(DN) --> Algorithm for calculating decimal values from XIP
                IDC data numbers
    convert_m0_asc2dec(xip_file, xip) --> Wrapper to convert ascii Tri-XIP
                files into the IDC_M0 data class above.
    convert_m1_asc2dec(xip_file, xip) --> Wrapper to convert ascii Tri-XIP
                files into the IDC_M1 data class above.
    parse_ascii_packets(xip_file, style='M0') --> Convert ascii input files
                to a structure similar to how the data is parsed from the
                binary HRT data files

"""
import numpy as np
import matplotlib.pyplot as plt
# import astropy.time as apt
#
class IDC_M0():
    # Input: n -- Number of packets
    def __init__(self, n: int, xip: str):
        self.IDC_ID = np.zeros(n, dtype='U4')
        self.H9_CCSDS_GPS_time = np.zeros(n, dtype='float')
        self.H9_CCSDS_ECL_time = np.zeros(n, dtype='uint64')
        self.ECL_MOE_GPS_time = np.zeros(n, dtype='uint64')
        self.time   = np.zeros(n, dtype='float')
        self.dark   = np.zeros(n, dtype='uint64')
        if xip=='TIP':
            self.red    = np.zeros(n, dtype='uint64')
            self.uv     = np.zeros(n, dtype='uint64')
            self.heater = np.zeros(n, dtype='uint32')
            self.T_F1   = np.zeros(n, dtype='float')
            self.T_F2   = np.zeros(n, dtype='float')
        if xip=='MIP':
            self.Mg     = np.zeros(n, dtype='uint64')
            self.VK     = np.zeros(n, dtype='uint64')
            self.error  = np.zeros(n, dtype='uint32')
            self.T_LENS = np.zeros(n, dtype='float')
            self.T_PMT  = np.zeros(n, dtype='float')
        self.HV_mon = np.zeros(n, dtype='float')
        self.HV_adj = np.zeros(n, dtype='float')
        self.sun    = np.zeros(n, dtype='float')
        self.vref   = np.zeros(n, dtype='float')
        self.T_IDC  = np.zeros(n, dtype='float')
        self.T_HV   = np.zeros(n, dtype='float')
        self.discrete = np.zeros(n, dtype='U4') #!!! Possibly no need?
        self.MODE             = np.zeros(n, dtype='uint16')
        self.HV_EVENT         = np.zeros(n, dtype='ubyte')
        self.SUN_EVENT        = np.zeros(n, dtype='ubyte')
        self.DK_EVENT         = np.zeros(n, dtype='ubyte')
        self.RD_EVENT         = np.zeros(n, dtype='ubyte')
        self.UV_EVENT         = np.zeros(n, dtype='ubyte')
        self.SUN_OVERRIDE     = np.zeros(n, dtype='ubyte')
        self.DK_OVERRIDE      = np.zeros(n, dtype='ubyte')
        self.RD_OVERRIDE      = np.zeros(n, dtype='ubyte')
        self.UV_OVERRIDE      = np.zeros(n, dtype='ubyte')
        self.HV_OVERRIDE      = np.zeros(n, dtype='ubyte')
        self.SHUTTER_OVERRIDE = np.zeros(n, dtype='ubyte')
        self.V5_OVERRIDE      = np.zeros(n, dtype='ubyte')
        self.HV_STATUS        = np.zeros(n, dtype='ubyte')
    def __str__(self):
        a = f'Contents for IDC Serial Number: {self.IDC_ID[0]}'
        c = 'Contains only XIP instrument run time ("time")'
        t = f'Total packets converted :      {len(self.dark)}'
        return f'{a}\n{c}\n{t}\n'
    def sort_by(self, key: str):
        """
        Sort all arrays by the values in the array named `key`.
        """
        if not hasattr(self, key):
            raise ValueError(f"No such field: {key}")

        sort_field = getattr(self, key)
        if not isinstance(sort_field, np.ndarray):
            raise TypeError(f"Field '{key}' is not a NumPy array and cannot be sorted.")

        sort_idx = np.argsort(sort_field)

        for attr, value in self.__dict__.items():
            if isinstance(value, np.ndarray) and len(value) == len(sort_field):
                setattr(self, attr, value[sort_idx])
    def remove_data_point(self, index_to_remove):
        """
        Removes a data point at the specified index from all arrays in class
        Args:  index_to_remove (int): The index of the data point to remove
        """
        if not (0 <= index_to_remove < len(self.header)):
            raise IndexError("Index out of bounds") #Throw an error if index is wrong.
        # Iterate through all attributes of the class
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, np.ndarray): #Check if it is a numpy array
                # Remove the element at the given index
                setattr(self, attr_name, np.delete(attr, index_to_remove))
#
class IDC_M1():
    # Input: n -- Number of packets
    def __init__(self, n: int, xip:str):
        self.H9_CCSDS_GPS_time = np.zeros(10*n, dtype='float')
        self.H9_CCSDS_ECL_time = np.zeros(10*n, dtype='uint64')
        self.ECL_MOE_GPS_time = np.zeros(10*n, dtype='uint64')
        self.time     = np.zeros(10*n, dtype='float')
        self.IDC_ID   = ''
        self.dark     = np.zeros(10*n, dtype='uint64')
        self.dark_chk = np.zeros(n, dtype='uint64')
        if xip=='TIP':
            self.red     = np.zeros(10*n, dtype='uint64')
            self.uv      = np.zeros(10*n, dtype='uint64')
            self.red_chk = np.zeros(n, dtype='uint64')
            self.uv_chk  = np.zeros(n, dtype='uint64')
        if xip=='MIP':
            self.Mg     = np.zeros(10*n, dtype='uint64')
            self.VK     = np.zeros(10*n, dtype='uint64')
            self.Mg_chk = np.zeros(n, dtype='uint64')
            self.VK_chk = np.zeros(n, dtype='uint64')
    def __str__(self):
        a = f'SUVM 10 Hz data Pakcet Contents for {self.IDC_ID[0]}:'
        c = 'Contains only XIP instrument run time ("time")'
        t = f'Total packets converted :      {len(self.dark)}'
        return f'{a}\n{c}\n{t}\n'
    def sort_by(self, key: str):
        """
        Sort all arrays by the values in the array named `key`.
        """
        if not hasattr(self, key): raise ValueError(f"No such field: {key}")

        sort_field = getattr(self, key)
        if not isinstance(sort_field, np.ndarray):
            raise TypeError(f"Field '{key}' is not a NumPy array and cannot be sorted.")

        sort_idx = np.argsort(sort_field)

        for attr, value in self.__dict__.items():
            if isinstance(value, np.ndarray) and len(value) == len(sort_field):
                setattr(self, attr, value[sort_idx])
    def remove_data_point(self, index_to_remove):
        """
        Removes a data point at the specified index from all arrays in class
        Args:  index_to_remove (int): The index of the data point to remove
        """
        if not (0 <= index_to_remove < len(self.header)):
            raise IndexError("Index out of bounds") #Throw an error if index is wrong.
        # Iterate through all attributes of the class
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, np.ndarray): #Check if it is a numpy array
                # Remove the element at the given index
                setattr(self, attr_name, np.delete(attr, index_to_remove))
#
def convert_m0_byt2dec(din: list[float, int, int, bytearray], xip: str) -> IDC_M0:
    """
    ECLIPSE-SPECIFIC !!!
    Convert Tri-XIP 1 Hz (M0) output from the binary HRT files to IDC_M0 class

    Parameters
    ----------
    din : list[float, int, int, bytearray]
        List of telemetry values with time tags and bytearray of data
    xip : str
        Designator for which instrument type to decode

    Returns
    -------
    IDC_M0
        Data class described above and calculated by convert_m1_hex2dec()

    """
    packet_list = []
    for i,p in enumerate(din):
        try:
            packet_list.append([p[0],p[1],p[2],p[3].decode('utf-8')])
        except UnicodeDecodeError:
            packet_list.append([p[0],p[1],p[2],'Unicode Decode Error'])
            print(f'Error decoding bytes in M0 packet {i}\n')
    return convert_m0_hex2dec(packet_list,xip)
#
def convert_m1_byt2dec(din: list[bytearray], xip: str) -> IDC_M1:
    """
    Convert Tri-XIP 10 Hz (M1) output from the binary HRT files to IDC_M1 class

    Parameters
    ----------
    din : list[bytearray]
        List of telemetry values with time tag and bytearray of data
    xip : str
        Designator for which instrument type to decode

    Returns
    -------
    IDC_M1
        Data class described above and calculated by convert_m1_hex2dec()

    """
    packet_list = []
    for i,p in enumerate(din):
        try:
            packet_list.append([p[0],p[1],p[2],p[3].decode('utf-8')])
        except UnicodeDecodeError:
            packet_list.append([p[0],p[1],p[2],'Unicode Decode Error'])
            print(f'Error decoding bytes in M1 packet {i}\n')
    return convert_m1_hex2dec(packet_list,xip)
#
def convert_m0_hex2dec(m: list[str], xip: str) -> IDC_M0:
    """
    Converts XIP M0 data frames from ASCII HEX to decimal values

    Parameters
    ----------
    m : list[str]
        List of data frames with ASCII data ('HEX': str)

        'HEX DATA' IDC M0 format:
        # 00 ØØ[zz zzzz] ØØ[zz zzzz]<CR>    PMT Dark Counts, PMT Red Counts
        # 04 ØØ[zz zzzz] Ø[xxx] Ø[xxx]<CR>  PMT UV Counts, HV Mon, HV Adj
        # 08 Ø[xxx] Øxxx Øxxx Øxxx<CR>      Sun Sensor, T[F1/LENS] T[F2/PMT] T_HV
        # 0C ØØ[zz zzzz] Ø[xxx] Ø[xxx]<CR>  Time Tag, 2.5 VREF Mon, IDC RTD
        # 10 [yyyy] [yyyy] [yyyy] FFFF<CR>  Discrete IDC & Sensor Flags, Error Status, IDC_ID
        # T<CR>

    xip : str
        Either "TIP" or "MIP"

    Returns
    -------
    IDC_M0
        Data class described above

    """
    mout = IDC_M0(len(m), xip)

    for i, p in enumerate(m):
        mout.H9_CCSDS_GPS_time[i] = p[0]
        mout.H9_CCSDS_ECL_time[i] = p[1]
        mout.ECL_MOE_GPS_time[i] = p[2]

        try:
            mout.time[i]   = int(p[-1][74:76] + p[-1][77:81], 16)
            mout.dark[i]   = int(p[-1][5:7]   + p[-1][8:12], 16)
            if xip=='TIP':
                mout.red[i]  = int(p[-1][15:17] + p[-1][18:22], 16)
                mout.uv[i]   = int(p[-1][28:30] + p[-1][31:35], 16)
                mout.T_F1[i] = IDC_DN_to_dec(int(p[-1][55:58], 16))
                mout.T_F2[i] = IDC_DN_to_dec(int(p[-1][60:63], 16))
                mout.heater[i]  = int(p[-1][100:104], 16)
            if xip=='MIP':
                mout.Mg[i]     = int(p[-1][15:17] + p[-1][18:22], 16)
                mout.VK[i]     = int(p[-1][28:30] + p[-1][31:35], 16)
                mout.T_LENS[i] = IDC_DN_to_dec(int(p[-1][55:58], 16))
                mout.T_PMT[i]  = IDC_DN_to_dec(int(p[-1][60:63], 16))
                mout.error[i]  = int(p[-1][100:104], 16)
            #
            HV_V           = int(p[-1][37:40], 16) * 3.3 / 4095
            mout.HV_mon[i] = (HV_V - 2.5)*(-1000) # Convert ADC V to HV
            mout.HV_adj[i] = int(p[-1][42:45], 16) * 3.3 / 4095
            mout.sun[i]    = int(p[-1][50:53], 16) * 3.3 / 4095
            mout.vref[i]   = int(p[-1][83:86], 16) * 3.3 / 4095
            mout.T_IDC[i]  = IDC_DN_to_dec(int(p[-1][88:91], 16))
            mout.T_HV[i]   = IDC_DN_to_dec(int(p[-1][65:68], 16))
            mout.IDC_ID[i] = p[-1][105:109]
            mout.discrete[i] = p[-1][95:99]
            #
            disc_bin = bin(int(p[-1][95:99], 16))[2:].zfill(16)
            mout.MODE[i]             = int(disc_bin[-2:], 2)
            mout.HV_EVENT[i]         = disc_bin[-3]
            mout.SUN_EVENT[i]        = disc_bin[-4]
            mout.DK_EVENT[i]         = disc_bin[-5]
            mout.RD_EVENT[i]         = disc_bin[-6]
            mout.UV_EVENT[i]         = disc_bin[-7]
            mout.SUN_OVERRIDE[i]     = disc_bin[-8]
            mout.DK_OVERRIDE[i]      = disc_bin[-9]
            mout.RD_OVERRIDE[i]      = disc_bin[-10]
            mout.UV_OVERRIDE[i]      = disc_bin[-11]
            mout.HV_OVERRIDE[i]      = disc_bin[-12]
            mout.SHUTTER_OVERRIDE[i] = disc_bin[-13]
            mout.V5_OVERRIDE[i]      = disc_bin[-14]
            mout.HV_STATUS[i]        = int(disc_bin[0:2], 2)
        except IndexError: print('Skipping empty packet')
        except ValueError:
            print(f'Invalid data: {p[-1]}')
    #
    try:
        if len(mout.time) < 2:
            raise IndexError
        dt = np.diff(mout.time.astype(float))
        rollover_mask = dt < -1000
        delta = np.where(rollover_mask, np.abs(dt), 0.0)
        rolltime = np.concatenate(([0.0], np.cumsum(delta)))
        for x in np.nonzero(rollover_mask)[0]:
            print(f'  XIP M0 Timer rollover correction at GPS time: {mout.H9_CCSDS_GPS_time[x]}')

        mout.time = mout.time.astype(float) + rolltime
        mout.sort_by('time')

    except IndexError: print(f'No {xip} time available\n')

    return mout
#
def IDC_DN_to_dec(DN: int) -> float:
    """
    Convert raw data numbers to decimal output

    Parameters
    ----------
    DN : int
        Data number

    Returns
    -------
    _ : float
        Converted decimal value

    """
    DN_V = (DN / 4095) * 3.3
    DN_R = 4990 * (0.4)/(DN_V - 0.4)
    return (0.00001 * (DN_R * DN_R)) + (0.2355 * DN_R) - 245.65
#
def convert_m1_hex2dec(m: list[str], xip: str) -> IDC_M1:
    """
    Converts XIP 10 Hz M1 data frame from ASCII HEX to decimal values

    Parameters
    ----------
    m : list[str]
        List of data frames, each itself a list with a timp tag (GPS_time : int)
        and ASCII data ('HEX': str)

        'HEX DATA' format is:
        # IDC M1
        # 00 IIII dddd dddd dddd<CR> IIII = IDC_ID
        # 04 dddd dddd dddd dddd<CR> ddd = Dark Counts (100 ms)
        # 08 dddd dddd dddd rrrr<CR> rrr = Red Counts (100 ms)
        # 0C rrrr rrrr rrrr rrrr<CR>
        # 10 rrrr rrrr rrrr rrrr<CR>
        # 14 rrrr uuuu uuuu uuuu<CR> uuu = UV Counts (100 ms)
        # 18 uuuu uuuu uuuu uuuu<CR>
        # 1C uuuu uuuu uuuu CCCC<CR> CCCC = Counter
        # T<CR>

    xip : str
        Either "TIP" or "MIP"

    Returns
    -------
    IDC_M1
        Data class described above

    """
    mout = IDC_M1(len(m), xip)
    for i, p in enumerate(m):
        mout.H9_CCSDS_GPS_time[i*10:(i*10+10)] = p[0]
        mout.H9_CCSDS_ECL_time[i*10:(i*10+10)] = p[1]
        mout.ECL_MOE_GPS_time[i*10:(i*10+10)] = p[2]

        try:
            mout.IDC_ID = p[-1][3:7]
            try:
                mout.time[i*10:(i*10+10)] = [int(p[-1][179:183],16) for k in range(10)]
                # mout.time[i*10:(i*10+10)] = [int(p[-1][179:183],16) + k/10 for k in range(10)]
            except ValueError: print(f'Skipping M1 Time packet # {i}')
            # mout.GPS_time[i*10:(i*10+10)]  = [p[-1][0] + k/10 for k in range(10)]
            dk = [p[-1][8:12],   p[-1][13:17],  p[-1][18:22],  p[-1][26:30],  p[-1][31:35],
                  p[-1][36:40],  p[-1][41:45],  p[-1][49:53],  p[-1][54:58],  p[-1][59:63]]
            rd = [p[-1][64:68],  p[-1][72:76],  p[-1][77:81],  p[-1][82:86],  p[-1][87:91],
                  p[-1][95:99],  p[-1][100:104],p[-1][105:109],p[-1][110:114],p[-1][118:122]]
            uv = [p[-1][123:127],p[-1][128:132],p[-1][133:137],p[-1][141:145],p[-1][146:150],
                  p[-1][151:155],p[-1][156:160],p[-1][164:168],p[-1][169:173],p[-1][174:178]]
            try: mout.dark[i*10:(i*10+10)] = [int(x, 16) for x in dk]
            except ValueError: print(f'Skipping M1 Dark packet # {i}')
            if xip == 'TIP':
                try: mout.red[i*10:(i*10+10)] = [int(x, 16) for x in rd]
                except ValueError: print(f'Skipping M1 Red packet # {i}')

                try: mout.uv[i*10:(i*10+10)]  = [int(x, 16) for x in uv]
                except ValueError: print(f'Skipping M1 UV packet # {i}')
            if xip == 'MIP':
                try: mout.Mg[i*10:(i*10+10)] = [int(x, 16) for x in rd]
                except ValueError: print(f'Skipping M1 Mg+ packet # {i}')

                try: mout.VK[i*10:(i*10+10)] = [int(x, 16) for x in uv]
                except ValueError: print(f'Skipping M1 VK packet # {i}')
        except IndexError: print('Skipping Empty Packet')
    #
    try:
        if len(mout.time) < 2:
            raise IndexError
        dt = np.diff(mout.time.astype(float))
        rollover_mask = dt < -1000
        delta = np.where(rollover_mask, np.abs(dt), 0.0)
        rolltime = np.concatenate(([0.0], np.cumsum(delta)))
        for x in np.nonzero(rollover_mask)[0]:
            print(f' {xip} M1 Time Rollover correction at GPS time: {mout.H9_CCSDS_GPS_time[x]}')

        mout.time = mout.time.astype(float) + rolltime
        mout.sort_by('time')

    except IndexError: print(f'No {xip} time available\n')

    # try:
    #     dt = np.abs(np.diff(mout.time))
    #     dt_idx = np.where(dt < 0.8)[0] #
    #     # Note the indices *should* be incremented by 1 to offset the np.diff change,
    #     # but because we're given 2 values per outlier, we can just use the 2nd idx
    #     rem_idx = [dt_idx[i] for i in range(1, len(dt_idx), 2)]
    #     for idx,val in enumerate(rem_idx):
    #         print(f'Removing bad encoder value at t = {gn.H9_CCSDS_GPS_time[val-idx]}')
    #         gn.remove_data_point(val-idx)
    # except:
    #     print(' Encoder data all good ... ')

    #

    return mout
#
def convert_m0_asc2dec(xip_file: str, xip: str) -> IDC_M0:
    """
    Wrapper to convert ascii Tri-XIP files into the IDC_M0 data class above.

    Parameters
    ----------
    xip_file : str
        Data file path and name
    xip : str
        Type of XIP ("TIP" or "MIP")

    Returns
    -------
    IDC_M0
        Data class described above

    """
    data_packets = parse_ascii_packets(xip_file, 'M0')
    return convert_m0_hex2dec(data_packets, xip)
#
def convert_m1_asc2dec(xip_file: str, xip: str) -> IDC_M1:
    """


    Parameters
    ----------
    xip_file : str
        DESCRIPTION.
    xip : str
        DESCRIPTION.

    Returns
    -------
    IDC_M1
        DESCRIPTION.

    """
    data_packets = parse_ascii_packets(xip_file, 'M1')
    return convert_m1_hex2dec(data_packets, xip)
#
def parse_ascii_packets(xip_file: str, style='M0') -> list[int, str]:
    """
    Convert ascii input files to a structure similar to how the data is parsed
    from the binary HRT data files

    Parameters
    ----------
    xip_file : str
        Full path and name for the target ascii file
    style: str
        Default is for M0 packet output, toggle "style" to return M1

    Returns
    -------
    m0 or m1 : list[str]
        List of lists that each include a time tag and ASCII hex output
    """
    m0 = []
    m1 = []
    with open(xip_file) as f:
        all_lines = f.readlines()
    time = 0
    packet = ''
    for line in all_lines:
        if line[0:2] == '13' or line[0:2] == '16': time = int(line)
        # NOTE the '13' times are the GPS epoch
        # NOTE the '16' times are the UNIX epoch
        # See the "ECL_plotmaker" suite for an algorithm to convert
        if line[0:2] == '00': packet += line
        if line[0:2] == '04': packet += line
        if line[0:2] == '08': packet += line
        if line[0:2] == '0C': packet += line
        if line[0:2] == '10': packet += line
        #
        if line[0:2] == '20': packet += line
        if line[0:2] == '24': packet += line
        if line[0:2] == '28': packet += line
        if line[0:2] == '2C': packet += line
        if line[0:2] == '30': packet += line
        if line[0:2] == '34': packet += line
        if line[0:2] == '38': packet += line
        if line[0:2] == '3C': packet += line
        #
        if line[0] == 'T':
            packet += line
            if len(packet) == 117: m0.append([time, packet])
            if len(packet) == 186: m1.append([time, packet])
            packet = ''
    #
    if style == 'M1': return m1
    return m0
