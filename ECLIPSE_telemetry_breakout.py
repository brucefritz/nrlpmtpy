#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: ECLIPSE_telemetry_breakout.py
Author: Bruce A. Fritz, NRL Code 7634
Date:   2024-01-02, Created
        2024-12-27, Updated Header for git upload, included function I/O detail
Version: 1.0
Description: Contains functions to parse the asynchronous ECLIPSE TLM data 
packets into individual instrument packet types

Classes:
    eclipse_packet() -- Class for each of the ECLIPSE packet types
    suvm_packet() -- Class for the individual SUVM packet types
        
Functions:
    breakout_hrt_packet()
        Input: List of ECLIPSE telemetry bytes from "ECLIPSE_H9_ccsds.py"
        Output: Data class filled with all ECLIPSE data, including PMTs, SUVMs
            and IIB health and status information 
            
    breakout_suvm_packet()
        Input: HRT Data Class of SUVM telemetry bytes from breakout_hrt_packet()
        Output: Data class filled with SUVM data broken down by data type

"""
import numpy as np

class eclipse_packet():
    def __init__(self):
        self.tip1_m0  = []
        self.tip1_m1  = []
        self.tip1_aux = []
        self.mip3_m0  = []
        self.mip3_m1  = []
        self.mip3_aux = []
        self.tip5_m0  = []
        self.tip5_m1  = []
        self.tip5_aux = []
        self.mip7_m0  = []
        self.mip7_m1  = []
        self.mip7_aux = []
        self.suvm2    = []
        self.suvm4    = []
        self.suvm6    = []
        self.suvm8    = []
        self.analog1  = []
        self.analog2  = []
#     def __repr__(self):
#         return f"<Test a:{self.a} b:{self.b}>"
    def __str__(self):
        a1 = f"ALS Housekeeping Packets: out.ana1 = {len(self.analog1)}"
        a2 = f"CTS Housekeeping Packets: out.ana2 = {len(self.analog2)}"
        x1 = f"TIP1 Pkts: m0 = {len(self.tip1_m0)}, m1 = {len(self.tip1_m1)}, Aux = {len(self.tip1_aux)}"
        x3 = f"MIP3 Pkts: m0 = {len(self.mip3_m0)}, m1 = {len(self.mip3_m1)}, Aux = {len(self.mip3_aux)}"
        x5 = f"TIP5 Pkts: m0 = {len(self.tip5_m0)}, m1 = {len(self.tip5_m1)}, Aux = {len(self.tip5_aux)}"
        x7 = f"MIP7 Pkts: m0 = {len(self.mip7_m0)}, m1 = {len(self.mip7_m1)}, Aux = {len(self.mip7_aux)}"
        s2 = f"SUVM2 Pkts: suvm2 = {len(self.suvm2)}"
        s4 = f"SUVM4 Pkts: suvm4 = {len(self.suvm4)}"
        s6 = f"SUVM6 Pkts: suvm6 = {len(self.suvm6)}"
        s8 = f"SUVM8 Pkts: suvm8 = {len(self.suvm8)}"
        return f'{a1}\n{a2}\n\n{x1}\n{x3}\n{x5}\n{x7}\n\n{s2}\n{s4}\n{s6}\n{s8}\n'
    # 
class suvm_packet():
    def __init__(self):
        self.boot = []
        self.boot_ccsds_time = []
        self.boot_ccsds_ecl_time = []
        self.boot_ecl_moe_time = []
        self.general = []
        self.gen_ccsds_time = []
        self.gen_ccsds_ecl_time = []
        self.gen_ecl_moe_time = []
        self.encoder = []
        self.encoder_ccsds_time = []
        self.encoder_ccsds_ecl_time = []
        self.encoder_ecl_moe_time = []
        self.command = []
        self.command_ccsds_time = []
        self.command_ccsds_ecl_time = []
        self.command_ecl_moe_time = []
        self.memory  = []
        self.memory_ccsds_time  = []
        self.memory_ccsds_ecl_time  = []
        self.memory_ecl_moe_time  = []
    # def __repr__(self):
    #     return f"<Test a:{self.a} b:{self.b}>"
    def __str__(self):
        z = 'SUVM Contents:'
        a = f"     General Packets:     {len(self.general)}"
        b = f"     Encoder Packets:     {len(self.encoder)}"
        c = f"     Boot Packets:        {len(self.boot)}"
        d = f"     Command Packets:     {len(self.command)}"
        e = f"     Memory Packets:      {len(self.memory)}"
        byte_sum = len(self.boot)+len(self.general)+len(self.command)+len(self.encoder)+len(self.memory)
        s = f"Total SUVM Packets: {byte_sum}"
        return f'{z}\n{a}\n{b}\n{c}\n{d}\n{e}\n\n{s}\n'
# 
def breakout_suvm_packet(sin: list[bytearray]) -> list[suvm_packet()]:
    out = suvm_packet()
    for x in sin:
        if int.from_bytes(x[-1][0:4],'big') == 0x352ef853:
            try:
                apid    = x[-1][4]
            except IndexError:
                print(f'SUVM packet {x[0]} incomplete!\n')
            # sequence= x[1][5]
            # length  = int.from_bytes(x[1][6:7],"big")
            if apid == 0:
                out.boot_ccsds_time.append(x[0])
                out.boot_ccsds_ecl_time.append(x[1])
                out.boot_ecl_moe_time.append(x[2])
                out.boot.append(x[3])
            elif apid == 1:
                out.gen_ccsds_time.append(x[0])
                out.gen_ccsds_ecl_time.append(x[1])
                out.gen_ecl_moe_time.append(x[2])
                out.general.append(x[3])
            elif apid == 2:
                out.command_ccsds_time.append(x[0])
                out.command_ccsds_ecl_time.append(x[1])
                out.command_ecl_moe_time.append(x[2])
                out.command.append(x[3])
            elif apid == 3:
                out.memory_ccsds_time.append(x[0])
                out.memory_ccsds_ecl_time.append(x[1])
                out.memory_ecl_moe_time.append(x[2])
                out.memory.append(x[3])
            elif apid == 4:
                out.encoder_ccsds_time.append(x[0])
                out.encoder_ccsds_ecl_time.append(x[1])
                out.encoder_ecl_moe_time.append(x[2])
                out.encoder.append(x[3])
        else:
            print('Invalid SUVM Packet APID at time ', x[0])
    return out
# 
def breakout_hrt_packet(fd: list[bytes], tc: list[float], te: list[float]) -> list[eclipse_packet()]:
    """
    Splits ECLIPSE HRT Packets apart into individual instrument frames
    
    Parameters
    ----------
    fd : list[bytes]
        List of ECLIPSE HRT telemetry bytes
    tc : list[float]
        GPS Time from CCSDS Header
    te : list[float]
        GPS Time from CCSDS-ECLIPSE Header

    Returns
    -------
    list[eclipse_packet()]
        See above

    """
    out = eclipse_packet()
    i=0
    while 1:
        if i > len(fd):
            break
        hdr = fd[i:i+12]
        if len(hdr) < 12:
            break
        sync_word = hex(int.from_bytes(bytearray(hdr[0:4]), 'little'))
        # inst_num  = hex(int.from_bytes(bytearray(hdr[4:6]), 'little'))
        # pkt_len   = hex(int.from_bytes(bytearray(hdr[6:8]), 'little'))
        inst_id   = bytearray(hdr[4:8]).hex()
        if inst_id[0:4] == '0900':
            if bytearray(hdr[6:8]).hex() != '4000':
                fault_bytes = bytearray(hdr[6:8]).hex()
                print(f'Faulty instrument HRT Packet ID: {fault_bytes}')
        # 
        if sync_word == '0x1acffc1d':
            pkt_length  = np.ushort(hdr[6] | hdr[7] << 8)
            time_tag_moe = np.uint(int.from_bytes(hdr[8:12],'little')) # Integer GPS time tag in HRT Frame, currently unused
            tidx = int(np.floor(i/1270))
            # if tc[tidx] > 1366847998:
            #     print(f'moe: {time_tag_moe}, ccsds: {tc[tidx]}')
            # time_tag = tc[tidx]
            time_tag = time_tag_moe
            i += 12
            #
            data_packet = bytearray(fd[i:i+pkt_length])
            try:
                if inst_id == '01007500' and data_packet[105:109].decode('utf-8') == 'AF09':
                    out.tip1_m0.append([tc[tidx], te[tidx], time_tag, data_packet])  # XIP 1 M0 (117b)
            except UnicodeDecodeError:
                print(f'Error decoding bytes in ATIP HRT packet at GPS time {time_tag}')
            if inst_id == '01000500':   # XIP 1 Aux (5 bytes)
                out.tip1_aux.append([time_tag, data_packet])
            if inst_id == '0100ba00':   # XIP 1 M1  (186 bytes)
                out.tip1_m1.append([tc[tidx], te[tidx], time_tag, data_packet])
            if inst_id[0:4] == '0200':   # SUVM 2
                out.suvm2.append([tc[tidx], te[tidx], time_tag, data_packet])
            try:
                if inst_id == '03007500' and data_packet[105:109].decode('utf-8') == 'BF02':
                    out.mip3_m0.append([tc[tidx], te[tidx], time_tag, data_packet])  # XIP 3 M0 (117b)
            except UnicodeDecodeError:
                print(f'Error decoding bytes in AMIP HRT packet at GPS time {time_tag}')
            if inst_id == '03000500':   # XIP 3 Aux (5 bytes)
                out.mip3_aux.append([time_tag, data_packet])
            if inst_id == '0300ba00':   # XIP 3 M1  (186 bytes)
                out.mip3_m1.append([tc[tidx], te[tidx], time_tag, data_packet])
            if inst_id[0:4] == '0400':   # SUVM 4
                out.suvm4.append([tc[tidx], te[tidx], time_tag, data_packet])
            try:
                if inst_id == '05007500' and data_packet[105:109].decode('utf-8') == 'AF08':
                    out.tip5_m0.append([tc[tidx], te[tidx], time_tag, data_packet])  # XIP 5 M0 (117b)
            except UnicodeDecodeError:
                print(f'Error decoding bytes in CTIP HRT packet at GPS time {time_tag}')
            if inst_id == '05000500':   # XIP 5 Aux (5 bytes)
                out.tip5_aux.append([time_tag, data_packet])
            if inst_id == '0500ba00':   # XIP 5 M1  (186 bytes)
                out.tip5_m1.append([tc[tidx], te[tidx], time_tag, data_packet])
            if inst_id[0:4] == '0600':   # SUVM 6
                out.suvm6.append([tc[tidx], te[tidx], time_tag, data_packet])
            try:
                if inst_id == '07007500' and data_packet[105:109].decode('utf-8') == 'BF03':
                    out.mip7_m0.append([tc[tidx], te[tidx], time_tag, data_packet])   # XIP7 M0 (117b)
            except UnicodeDecodeError:
                print(f'Error decoding bytes in CMIP HRT packet at GPS time {time_tag}')
            if inst_id == '07000500':   # XIP 7 Aux (5 bytes)
                out.mip7_aux.append([time_tag, data_packet])
            if inst_id == '0700ba00':   # XIP 7 M1  (186 bytes)
                out.mip7_m1.append([tc[tidx], te[tidx], time_tag, data_packet])
            if inst_id[0:4] == '0800':   # SUVM 8
                out.suvm8.append([tc[tidx], te[tidx], time_tag, data_packet])
                # 
            if inst_id == '09004000':   # Analog 1  (64 bytes)
                out.analog1.append([time_tag, data_packet])
            if inst_id == '0a004000':   # Analog 2  (64 bytes)
                out.analog2.append([time_tag, data_packet])
            i += pkt_length
        else:
            i += 1
        # 
    return out
    # 
