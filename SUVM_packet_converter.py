# -*- coding: utf-8 -*-
"""
Filename: suvm_packet_converter.py
Author: Bruce A. Fritz, NRL Code 7634
Description: Set of functions to load SUVM telemetry and parse into
            meaningful (decimal) values
Date:   v1.0 2025-01-02, Created
Mods:   v1.1 2025-04-22, Modified class structure to add "sort_by" method
                         Create new GPS time based on internal XIP timer
        v1.2 2025-11-03, Reverted back to basic time keeping, no interpolation
                         Added time from all headers at CCSDS and MOE levels
        v1.3 2026-06-24, Removed bogus en.time/s.encoder_time assignment
                         (neither field exists, raised AttributeError);
                         fixed off-by-one byte offsets in
                         suvm_general_converter's reset_status/last_cmd_*
                         fields to match the bootloader header layout;
                         vectorized the encoder_counts unpacking loop
        v1.4 2026-07-01, Changed sequence_count dtype from ubyte to uint32
                         in all packet classes; added sort_by to bootloader,
                         command, and encoder packet classes; added
                         _suvm_time_checks() helper to all converters to
                         apply sequence_count rollover correction,
                         system_counter correction, and warn on zero or 
                         anomalous time-tag entries

Classes:
    suvm_bootloader_packet()
    suvm_command_packet()
    suvm_encoder_packet()
    suvm_memory_packet
    suvm_general_packet()

Functions:
    suvm_bootloader_converter(input_array)
    suvm_command_converter(input_array)
    suvm_encoder_converter(input_array)
    suvm_general_converter(input_array)

"""
import numpy as np
# import matplotlib.pyplot as plt
# import astropy.time as apt
#
class suvm_bootloader_packet():
    def __init__(self, n):
        self.H9_CCSDS_GPS_time  = np.zeros(n, dtype='float')
        self.H9_CCSDS_ECL_time  = np.zeros(n, dtype='uint64')
        self.ECL_MOE_GPS_time   = np.zeros(n, dtype='uint64')
        self.header             = np.zeros(n, dtype='uintc')  #  0
        self.apid               = np.zeros(n, dtype='ubyte')  #  4
        self.sequence_count     = np.zeros(n, dtype='uint32') #  5
        self.length             = np.zeros(n, dtype='uint16') #  6
        self.system_counter     = np.zeros(n, dtype='float64')#  8, 1/1000 s
        self.gps_pps            = np.zeros(n, dtype='float64')# 16, 1/1000 s
        self.watchdog_counter   = np.zeros(n, dtype='uint32') # 24, 1/50,000 s
        self.version            = np.zeros(n, dtype='uint32') # 28
        self.reset_status       = np.zeros(n, dtype='ubyte')  # 32
        self.last_cmd_status    = np.zeros(n, dtype='ubyte')  # 33
        self.last_cmd_id        = np.zeros(n, dtype='ubyte')  # 34
        self.last_cmd_opcode    = np.zeros(n, dtype='ubyte')  # 35
        self.last_cmd_time      = np.zeros(n, dtype='float64')# 36, 1/1000 s
        self.cmd_success        = np.zeros(n, dtype='ubyte')  # 44
        self.cmd_fail           = np.zeros(n, dtype='ubyte')  # 45
        self.flash_last_op      = np.zeros(n, dtype='ubyte')  # 46
        self.flash_status       = np.zeros(n, dtype='ubyte')  # 47
        self.general_hk_flags   = np.zeros(n, dtype='uint32')  # 48
        self.last_crc           = np.zeros(n, dtype='uint32') # 52
        self.ROM_SBE            = np.zeros(n, dtype='uint16') # 56
        self.ROM_MBE            = np.zeros(n, dtype='uint16') # 58
        self.RAM_SBE            = np.zeros(n, dtype='uint16') # 60
        self.RAM_MBE            = np.zeros(n, dtype='uint16') # 62
        self.crc                = np.zeros(n, dtype='uint32') # 64
    # def __repr__(self):
    #     return f"<Test a:{self.a} b:{self.b}>"
    def __str__(self):
        t1 = f"SUVM Bootloader Packets: {len(self.header)}"
        return f'{t1}\n'
    def sort_by(self, key: str):
        if not hasattr(self, key): raise ValueError(f"No such field: {key}")
        sort_field = getattr(self, key)
        if not isinstance(sort_field, np.ndarray):
            raise TypeError(f"Field '{key}' is not a NumPy array and cannot be sorted.")
        sort_idx = np.argsort(sort_field)
        for attr, value in self.__dict__.items():
            if isinstance(value, np.ndarray) and len(value) == len(sort_field):
                setattr(self, attr, value[sort_idx])

class suvm_general_packet():
    # Input: n -- Number of packets
    def __init__(self,n):
        self.H9_CCSDS_GPS_time  = np.zeros(n, dtype='float')
        self.H9_CCSDS_ECL_time  = np.zeros(n, dtype='uint64')
        self.ECL_MOE_GPS_time   = np.zeros(n, dtype='uint64')
        self.header             = np.zeros(n, dtype='uintc')  #  0
        self.apid               = np.zeros(n, dtype='ubyte')  #  4
        self.sequence_count     = np.zeros(n, dtype='uint32') #  5
        self.length             = np.zeros(n, dtype='uint16') #  6
        self.system_counter     = np.zeros(n, dtype='float64') #  8, 1/1000 s
        self.gps_pps            = np.zeros(n, dtype='float64') # 16, 1/1000 s
        self.watchdog_counter   = np.zeros(n, dtype='uint32') # 24
        self.version            = np.zeros(n, dtype='uint32') # 28
        self.reset_status       = np.zeros(n, dtype='ubyte')  # 32
        self.last_cmd_status    = np.zeros(n, dtype='ubyte')  # 33
        self.last_cmd_id        = np.zeros(n, dtype='ubyte')  # 34
        self.last_cmd_opcode    = np.zeros(n, dtype='ubyte')  # 35
        self.last_cmd_time      = np.zeros(n, dtype='float64') # 36, 1/1000 s
        self.cmd_success        = np.zeros(n, dtype='ubyte')  # 44
        self.cmd_fail           = np.zeros(n, dtype='ubyte')  # 45
        self.flash_last_op      = np.zeros(n, dtype='ubyte')  # 46
        self.flash_status       = np.zeros(n, dtype='ubyte')  # 47
        self.general_hk_flags   = np.zeros(n, dtype='uint32') # 48
        self.last_crc           = np.zeros(n, dtype='uint32') # 52
        self.ROM_SBE            = np.zeros(n, dtype='uint16') # 56
        self.ROM_MBE            = np.zeros(n, dtype='uint16') # 58
        self.RAM_SBE            = np.zeros(n, dtype='uint16') # 60
        self.RAM_MBE            = np.zeros(n, dtype='uint16') # 62
        self.GPIO_A             = np.zeros(n, dtype='uint32') # 64
        self.GPIO_B             = np.zeros(n, dtype='uint32') # 68
        self.launch_lock_flags  = np.zeros(n, dtype='uint32') # 72
        self.VC_LIMIT_CHECK     = np.zeros(n, dtype='uint16') # 76
        self.V5_IMON            = np.zeros(n, dtype='float') # 78
        self.V5_VMON            = np.zeros(n, dtype='float') # 80
        self.V3_IMON            = np.zeros(n, dtype='float') # 82
        self.V3_VMON            = np.zeros(n, dtype='float') # 84
        self.V22_IMON           = np.zeros(n, dtype='float') # 86
        self.V22_VMON           = np.zeros(n, dtype='float') # 88
        self.MOTOR_IMON         = np.zeros(n, dtype='float') # 90
        self.MOTOR_VMON         = np.zeros(n, dtype='float') # 92
        self.temperature        = np.zeros(n, dtype='float') # 94
        self.encoder_zero_offset= np.zeros(n, dtype='short') # 96
        self.encoder_current_ct = np.zeros(n, dtype='short')  # 98
        self.encoder_target     = np.zeros(n, dtype='short')  # 100
        # 2 bytes padding
        self.motor_flags        = np.zeros(n, dtype='uint16') # 104
        self.profile_index      = np.zeros(n, dtype='uint16') # 106
        self.pwm_rate           = np.zeros(n, dtype='uint32') # 108
        self.pwm_counts_remain  = np.zeros(n, dtype='uint32') # 112
        self.crc                = np.zeros(n, dtype='uint32') # 116
        self.encoder_angle      = np.zeros(n, dtype='float')
        self.target_angle       = np.zeros(n, dtype='float')
    # def __repr__(self):
    #     return f"<Test a:{self.a} b:{self.b}>"
    def __str__(self):
        t1 = f"SUVM General Packets: {len(self.header)}"
        return f'{t1}\n'
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
    #
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
class suvm_command_packet():
    def __init__(self, n):
        self.H9_CCSDS_GPS_time  = np.zeros(n, dtype='float')
        self.H9_CCSDS_ECL_time  = np.zeros(n, dtype='uint64')
        self.ECL_MOE_GPS_time   = np.zeros(n, dtype='uint64')
        self.header             = np.zeros(n, dtype='uintc')  #  0
        self.apid               = np.zeros(n, dtype='ubyte')  #  4
        self.sequence_count     = np.zeros(n, dtype='uint32') #  5
        self.length             = np.zeros(n, dtype='uint16') #  6
        self.system_counter     = np.zeros(n, dtype='float64') # 8, 1/1000 s
        self.last_command       = np.zeros(n, dtype='S50') # Sufficient bytes for any cmd
        self.crc                = np.zeros(n, dtype='uint32') # 64
    # def __repr__(self):
    #     return f"<Test a:{self.a} b:{self.b}>"
    def __str__(self):
        t1 = f"SUVM Command Packets: {len(self.header)}"
        return f'{t1}\n'
    def sort_by(self, key: str):
        if not hasattr(self, key): raise ValueError(f"No such field: {key}")
        sort_field = getattr(self, key)
        if not isinstance(sort_field, np.ndarray):
            raise TypeError(f"Field '{key}' is not a NumPy array and cannot be sorted.")
        sort_idx = np.argsort(sort_field)
        for attr, value in self.__dict__.items():
            if isinstance(value, np.ndarray) and len(value) == len(sort_field):
                setattr(self, attr, value[sort_idx])
    #
class suvm_memory_packet():
    def __init__(self, n):
        self.H9_CCSDS_GPS_time  = np.zeros(n, dtype='float')
        self.H9_CCSDS_ECL_time  = np.zeros(n, dtype='uint64')
        self.ECL_MOE_GPS_time   = np.zeros(n, dtype='uint64')
        self.time               = np.zeros(n, dtype='uint32')
        self.header             = np.zeros(n, dtype='uintc')  #  0
        self.apid               = np.zeros(n, dtype='ubyte')  #  4
        self.sequence_count     = np.zeros(n, dtype='ubyte')  #  5
        self.length             = np.zeros(n, dtype='uint16') #  6
        self.system_counter     = np.zeros(n, dtype='float64') #  8, 1/1000 s
        self.address            = np.zeros(n, dtype='uint32') #  16
        self.last_command       = np.zeros(n, dtype='str')  #, 20 Sufficient bytes for any cmd
        self.crc                = np.zeros(n, dtype='uint32') # 21-276
    # def __repr__(self):
    #     return f"<Test a:{self.a} b:{self.b}>"
    def __str__(self):
        t1 = f"SUVM Memory Packets: {len(self.header)}"
        return f'{t1}\n'
    #
class suvm_encoder_packet():
    def __init__(self, n):
        self.H9_CCSDS_GPS_time  = np.zeros(n, dtype='float')
        self.H9_CCSDS_ECL_time  = np.zeros(n, dtype='uint64')
        self.ECL_MOE_GPS_time   = np.zeros(n, dtype='uint64')
        self.header             = np.zeros(n, dtype='uintc')  #  0
        self.apid               = np.zeros(n, dtype='ubyte')  #  4
        self.sequence_count     = np.zeros(n, dtype='uint32') #  5
        self.length             = np.zeros(n, dtype='uint16') #  6
        self.system_counter     = np.zeros(n, dtype='float64') #  8, 1/1000 s
        self.time_first_element = np.zeros(n, dtype='float64') #  16, 1/1000 s
        self.encoder_counts     = np.zeros(n*125, dtype='int16')
        self.padding            = np.zeros(n, dtype='uint16')
        self.crc                = np.zeros(n, dtype='uint32')
    # def __repr__(self):
    #     return f"<Test a:{self.a} b:{self.b}>"
    def __str__(self):
        t1 = f"SUVM Encoder Packets: {len(self.header)}"
        return f'{t1}\n'
    def sort_by(self, key: str):
        if not hasattr(self, key): raise ValueError(f"No such field: {key}")
        sort_field = getattr(self, key)
        if not isinstance(sort_field, np.ndarray):
            raise TypeError(f"Field '{key}' is not a NumPy array and cannot be sorted.")
        sort_idx = np.argsort(sort_field)
        n = len(sort_field)
        for attr, value in self.__dict__.items():
            if isinstance(value, np.ndarray):
                if len(value) == n:
                    setattr(self, attr, value[sort_idx])
                elif len(value) == n * 125 and attr == 'encoder_counts':
                    self.encoder_counts = value.reshape(n, 125)[sort_idx].reshape(-1)
    def remove_data_point(self, index_to_remove):
        """
        Removes a data point at the specified index from all arrays in class
        Args:     index_to_remove (int): The index of the data point to remove
        """
        if not (0 <= index_to_remove < len(self.header)):
            raise IndexError("Index out of bounds")
        # Iterate through all attributes of the class
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, np.ndarray): #Check if it is a numpy array
                # Reshape encoder_counts to remove appropriate elements
                if attr_name == 'encoder_counts':
                    num_packets = len(self.header)
                    attr = attr.reshape(num_packets, 125)
                    attr = np.delete(attr, index_to_remove, axis=0)
                    self.encoder_counts = attr.reshape(-1)
                else:
                    # Remove the element at the given index
                    setattr(self, attr_name, np.delete(attr, index_to_remove))
    #
def _suvm_time_checks(pkt, name: str):
    """
    Post-processing applied to every SUVM packet object after its parse loop:
      1. sequence_count rollover correction (ubyte counter wraps at 256)
      2. system_counter reset correction (reboot drops counter back to ~0)
      3. sort all arrays by H9_CCSDS_GPS_time
      4. warn on zero-valued time-tag entries and anomalous GPS time gaps
    """
    n = len(pkt.H9_CCSDS_GPS_time)
    if n < 2:
        return
    # --- sequence_count rollover (in packet-arrival order) ---
    dt_seq = np.diff(pkt.sequence_count.astype(np.int32))
    ro = dt_seq < 0
    if np.any(ro):
        offsets = np.concatenate(([0], np.cumsum(np.where(ro, 256, 0)))).astype(np.uint32)
        pkt.sequence_count = pkt.sequence_count.astype(np.uint32) + offsets
        print(f'  [SUVM {name}] sequence_count rollover: {int(np.count_nonzero(ro))} event(s)')
    # --- system_counter spike-cluster removal and interpolation ---
    # A cluster of anomalous values is bounded by a large positive jump (entry)
    # and a large negative jump (exit). Clusters may span more than one point.
    # Bad values are replaced in-place with linear interpolation between the
    # last good sample before the cluster and the first good sample after it;
    # dt_sys is then recomputed so genuine firmware resets are still caught.
    dt_sys = np.diff(pkt.system_counter)
    up_events   = np.nonzero(dt_sys >  100.)[0]
    down_events = np.nonzero(dt_sys < -100.)[0]
    if len(up_events) > 0 and len(down_events) > 0:
        for x in down_events:
            preceding_up = up_events[up_events < x]
            if len(preceding_up) > 0:
                i0 = int(preceding_up[-1])   # last good index before cluster
                i1 = int(x) + 1              # first good index after cluster
                n_cluster = i1 - i0 - 1
                if i1 < n:
                    y0 = pkt.system_counter[i0]
                    y1 = pkt.system_counter[i1]
                    idx = np.arange(i0 + 1, i1)
                    pkt.system_counter[i0+1:i1] = y0 + (y1 - y0) * (idx - i0) / (i1 - i0)
                    print(f'  [SUVM {name}] Removed and interpolated system_counter '
                          f'over {n_cluster} bad point(s) at indices {i0+1}–{i1-1}')
                else:
                    print(f'  [SUVM {name}] system_counter spike cluster at end of '
                          f'array (indices {i0+1}+): cannot interpolate forward')
    # --- system_counter reset (large negative jump = firmware reboot) ---
    # Recompute after interpolation so genuine resets are still corrected.
    dt_sys = np.diff(pkt.system_counter)
    rs = dt_sys < -100.
    if np.any(rs):
        delta = np.where(rs, np.abs(dt_sys), 0.)
        pkt.system_counter = pkt.system_counter + np.concatenate(([0.], np.cumsum(delta)))
        print(f'  [SUVM {name}] system_counter reset: {int(np.count_nonzero(rs))} event(s)')
    # --- zero-valued time entries (skipped/missing packets leave init zeros) ---
    for field in ('H9_CCSDS_GPS_time', 'H9_CCSDS_ECL_time', 'ECL_MOE_GPS_time'):
        z = int(np.count_nonzero(getattr(pkt, field) == 0))
        if z:
            print(f'  [SUVM {name}] Warning: {z} zero-valued {field} entries')
    # --- anomalous GPS time gaps (out-of-order or missing > 10 s) ---
    dt_gps = np.diff(pkt.H9_CCSDS_GPS_time)
    for x in np.nonzero((dt_gps < -10) | (dt_gps > 10.))[0]:
        print(f'  [SUVM {name}] H9_CCSDS_GPS_time anomaly: {dt_gps[x]:+.3f}s at index {x+1}')
#
def suvm_bootloader_converter(s: list) -> suvm_bootloader_packet:
    """
    Converts SUVM bootloader frames to decimal values

    Parameters
    ----------
    s : list
        Input data array with time tags and byte values of data
        See "suvm_packet" class in "ECLIPSE_telemetry_breakout.py"

    Returns
    -------
    suvm_bootloader_packet
        Data class as described above

    """
    bt = suvm_bootloader_packet(len(s.boot))
    for i,p in enumerate(s.boot):
        bt.H9_CCSDS_GPS_time[i] = s.boot_ccsds_time[i]
        bt.H9_CCSDS_ECL_time[i] = s.boot_ccsds_ecl_time[i]
        bt.ECL_MOE_GPS_time[i]  = s.boot_ecl_moe_time[i]
        bt.header[i]            = int.from_bytes(p[0:4],'big')
        bt.apid[i]              = p[4] # 0
        bt.sequence_count[i]    = p[5]
        bt.length[i]            = int.from_bytes(p[6:8],'little')
        bt.system_counter[i]    = float(int.from_bytes(p[8:16],'little')) / 1000.
        bt.gps_pps[i]           = float(int.from_bytes(p[16:24],'little')) / 1000.
        bt.watchdog_counter[i]  = int.from_bytes(p[24:28],'little')
        bt.version[i]           = int.from_bytes(p[28:32],'little')
        bt.reset_status[i]      = p[32]
        bt.last_cmd_status[i]   = p[33]
        bt.last_cmd_id[i]       = p[34]
        bt.last_cmd_opcode[i]   = p[35]
        bt.last_cmd_time[i]     = float(int.from_bytes(p[36:44],'little')) / 1000.
        bt.cmd_success[i]       = p[44]
        bt.cmd_fail[i]          = p[45]
        bt.flash_last_op[i]     = p[46]
        bt.flash_status[i]      = p[47]
        bt.general_hk_flags[i]  = int.from_bytes(p[48:52],'little')
        bt.last_crc[i]          = int.from_bytes(p[52:56],'little')
        bt.ROM_SBE[i]           = int.from_bytes(p[56:58],'little')
        bt.ROM_MBE[i]           = int.from_bytes(p[58:60],'little')
        bt.RAM_SBE[i]           = int.from_bytes(p[60:62],'little')
        bt.RAM_MBE[i]           = int.from_bytes(p[62:64],'little')
        bt.crc[i]               = int.from_bytes(p[64:68],'little')
    #
    _suvm_time_checks(bt, 'bootloader')
    return bt
#
def suvm_command_converter(s: list) -> suvm_command_packet:
    """
    Converts SUVM command frames to decimal values

    Parameters
    ----------
    s : list
        Input data array with time tags and byte values of data
        See "suvm_packet" class in "ECLIPSE_telemetry_breakout.py"

    Returns
    -------
    suvm_command_packet
        Data class as described above

    """
    cm = suvm_command_packet(len(s.command))
    for i,p in enumerate(s.command):
        cm.H9_CCSDS_GPS_time[i] = s.command_ccsds_time[i]
        cm.H9_CCSDS_ECL_time[i] = s.command_ccsds_ecl_time[i]
        cm.ECL_MOE_GPS_time[i]  = s.command_ecl_moe_time[i]
        cm.header[i]            = int.from_bytes(p[0:4],'big')
        cm.apid[i]              = p[4] # 2
        cm.sequence_count[i]    = p[5]
        cm.length[i]            = int.from_bytes(p[6:8],'little')
        cm.system_counter[i]    = float(int.from_bytes(p[8:16],'little')) / 1000.
        # cm.last_command[i]      = hex(int.from_bytes(p[16:cm.length[i]], 'little'))
        cm.last_command[i]      = p[16:cm.length[i]].hex()
        cm.crc[i]               = int.from_bytes(p[cm.length[i]:cm.length[i]+4], 'big')
    #
    _suvm_time_checks(cm, 'command')
    return cm

def suvm_encoder_converter(s: list) -> suvm_encoder_packet:
    """
    Converts SUVM encoder frames to decimal values

    Parameters
    ----------
    s : list
        Input data array with time tags and byte values of data
        See "suvm_packet" class in "ECLIPSE_telemetry_breakout.py"

    Returns
    -------
    suvm_encoder_packet
        Data class as described above

    """
    en = suvm_encoder_packet(len(s.encoder))
    for i,p in enumerate(s.encoder):
        en.H9_CCSDS_GPS_time[i] = s.encoder_ccsds_time[i]
        en.H9_CCSDS_ECL_time[i] = s.encoder_ccsds_ecl_time[i]
        en.ECL_MOE_GPS_time[i]  = s.encoder_ecl_moe_time[i]
        en.header[i]            = int.from_bytes(p[0:4],'big')
        en.apid[i]              = p[4] # 4
        en.sequence_count[i]    = p[5]
        en.length[i]            = int.from_bytes(p[6:8],'little')
        en.system_counter[i]    = float(int.from_bytes(p[8:16],'little')) / 1000.
        en.time_first_element[i]= float(int.from_bytes(p[16:24],'little')) / 1000.
        j = i*125
        raw = np.frombuffer(bytes(p[24:24+250]), dtype='<u2', count=125)
        en.encoder_counts[j:j+125] = raw.astype(np.int32) - 2**15
        en.padding[i]           = 0
        en.crc[i]               = int.from_bytes(p[276:280], 'little')
    #
    _suvm_time_checks(en, 'encoder')
    return en

def suvm_general_converter(s: list) -> suvm_general_packet:
    """
    Converts SUVM general frames to decimal values

    Parameters
    ----------
    s : list
        Input data array with time tags and byte values of data
        See "suvm_packet" class in "ECLIPSE_telemetry_breakout.py"

    Returns
    -------
    suvm_general_packet
        Data class as described above

    """
    print('Busting bits n bytes from SUVM General Packet')
    gn = suvm_general_packet(len(s.general))

    for i,p in enumerate(s.general):
        if len(p) < 120: continue
        gn.H9_CCSDS_GPS_time[i] = s.gen_ccsds_time[i]
        gn.H9_CCSDS_ECL_time[i] = s.gen_ccsds_ecl_time[i]
        gn.ECL_MOE_GPS_time[i]  = s.gen_ecl_moe_time[i]
        gn.header[i]            = int.from_bytes(p[0:4],'big')
        gn.apid[i]              = p[4] # 1
        gn.sequence_count[i]    = p[5]
        gn.length[i]            = int.from_bytes(p[6:8],'little')
        gn.system_counter[i]    = float(int.from_bytes(p[8:16],'little'))/1000.
        gn.gps_pps[i]            = float(int.from_bytes(p[16:24],'little'))/1000.
        gn.watchdog_counter[i]   = int.from_bytes(p[24:28],'little')
        gn.version[i]            = int.from_bytes(p[28:32],'little')
        gn.reset_status[i]       = p[32]
        gn.last_cmd_status[i]    = p[33]
        gn.last_cmd_id[i]        = p[34]
        gn.last_cmd_opcode[i]    = p[35]
        gn.last_cmd_time[i]      = float(int.from_bytes(p[36:44],'little'))/1000.
        gn.cmd_success[i]        = p[44]
        gn.cmd_fail[i]           = p[45]
        gn.flash_last_op[i]      = p[46]
        gn.flash_status[i]       = p[47]
        gn.general_hk_flags[i]   = int.from_bytes(p[48:52],'little')
        gn.last_crc[i]           = int.from_bytes(p[52:56],'little')
        gn.ROM_SBE[i]            = int.from_bytes(p[56:58],'little')
        gn.ROM_MBE[i]            = int.from_bytes(p[58:60],'little')
        gn.RAM_SBE[i]            = int.from_bytes(p[60:62],'little')
        gn.RAM_MBE[i]            = int.from_bytes(p[62:64],'little')
        gn.GPIO_A[i]             = int.from_bytes(p[64:68],'little')
        gn.GPIO_B[i]             = int.from_bytes(p[68:72],'little')
        gn.launch_lock_flags[i]  = int.from_bytes(p[72:76],'little')
        gn.VC_LIMIT_CHECK[i]     = int.from_bytes(p[76:78],'little')
        gn.V5_IMON[i]     = int.from_bytes(p[78:80],'little') * 0.0000152587891 #A
        gn.V5_VMON[i]     = int.from_bytes(p[80:82],'little') * 0.0001530036926 #V
        gn.V3_IMON[i]     = int.from_bytes(p[82:84],'little') * 0.0000152587891 #A
        gn.V3_VMON[i]     = int.from_bytes(p[84:86],'little') * 0.0001011924744 #V
        gn.V22_IMON[i]    = int.from_bytes(p[86:88],'little') * 0.0000076293945 #A
        gn.V22_VMON[i]    = int.from_bytes(p[88:90],'little') * 0.0008576316834 #V
        gn.MOTOR_IMON[i]  = int.from_bytes(p[90:92],'little') * 0.0000152587891 #A
        gn.MOTOR_VMON[i]  = int.from_bytes(p[92:94],'little') * 0.0002425041199 #V
        gn.temperature[i] = int.from_bytes(p[94:96],'little') / 256 # C
        gn.encoder_zero_offset[i] = int.from_bytes(p[96:98],'little')
        gn.encoder_current_ct[i]  = int.from_bytes(p[98:100],'little')
        gn.encoder_target[i]      = int.from_bytes(p[100:102],'little')
        # Padding
        gn.motor_flags[i]         = int.from_bytes(p[104:106],'little')
        gn.profile_index[i]       = int.from_bytes(p[106:108],'little')
        gn.pwm_rate[i]            = int.from_bytes(p[108:112],'little')
        gn.pwm_counts_remain[i]   = int.from_bytes(p[112:116],'little')
        gn.crc[i]                 = int.from_bytes(p[116:120],'little')
        gn.encoder_angle[i]       = (gn.encoder_current_ct[i] - gn.encoder_zero_offset[i]) * 360 / 2**13
        gn.target_angle[i]        = (gn.encoder_target[i] - gn.encoder_zero_offset[i]) * 360 / 2**13
    #
    _suvm_time_checks(gn, 'general')
    try:
        d_enc = np.abs(np.diff(gn.encoder_angle))
        d_enc_idx = np.where(d_enc > 2.5)[0] #
        # Note the indices *should* be incremented by 1 to offset the np.diff change,
        # but because we're given 2 values per outlier, we can just use the 2nd idx
        rem_idx = [d_enc_idx[i] for i in range(1, len(d_enc_idx), 2)]
        for idx,val in enumerate(rem_idx):
            print(f'Removing bad encoder value at t = {gn.H9_CCSDS_GPS_time[val-idx]}')
            gn.remove_data_point(val-idx)
    except:
        print(' Encoder data all good ... ')

    return gn