# -*- coding: utf-8 -*-
"""
ECLIPSE_telemetry_breakout -- contains procedures to parse data packets into 
individual instrument values

Contents:
    
    Classes:
        eclipse_packet()
        suvm_packet()
        
    Routines:
        breakout_hrt_packet()
        breakout_suvm_packet()

@author: bfritz
"""
import numpy as np

class eclipse_packet():
    def __init__(self):
        self.tip1_m0 = []
        self.tip1_m1 = []
        self.mip3_m0 = []
        self.mip3_m1 = []
        self.tip5_m0 = []
        self.tip5_m1 = []
        self.mip7_m0 = []
        self.mip7_m1 = []
        self.suvm2   = []
        self.suvm4   = []
        self.suvm6   = []
        self.suvm8   = []
        self.analog1 = []
        self.analog2 = []
#     def __repr__(self):
#         return f"<Test a:{self.a} b:{self.b}>"
    def __str__(self):
        a1 = f"ALS Housekeeping Packets: out.ana1 = {len(self.analog1)}"
        a2 = f"CTS Housekeeping Packets: out.ana2 = {len(self.analog2)}"
        x1 = f"TIP1 Packets: out.tip1_m0 = {len(self.tip1_m0)}, out.tip1_m1 = {len(self.tip1_m1)}"
        x3 = f"MIP3 Packets: out.mip3_m0 = {len(self.mip3_m0)}, out.mip3_m1 = {len(self.mip3_m1)}"
        x5 = f"TIP5 Packets: out.tip5_m0 = {len(self.tip5_m0)}, out.tip5_m1 = {len(self.tip5_m1)}"
        x7 = f"MIP7 Packets: out.mip7_m0 = {len(self.mip7_m0)}, out.mip7_m1 = {len(self.mip7_m1)}"
        s2 = f"SUVM2 Packets: out.suvm2 = {len(self.suvm2)}"
        s4 = f"SUVM4 Packets: out.suvm4 = {len(self.suvm4)}"
        s6 = f"SUVM6 Packets: out.suvm6 = {len(self.suvm6)}"
        s8 = f"SUVM8 Packets: out.suvm8 = {len(self.suvm8)}"
        return f'{a1}\n{a2}\n\n{x1}\n{x3}\n{x5}\n{x7}\n\n{s2}\n{s4}\n{s6}\n{s8}\n'
    # 
class suvm_packet():
    def __init__(self):
        self.general = []
        self.encoder = []
        self.boot    = []
        self.command = []
        self.memory  = []
        self.general_time = []
        self.encoder_time = []
        self.boot_time    = []
        self.command_time = []
        self.memory_time  = []
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
def breakout_suvm_packet(sin):
    out = suvm_packet()
    for x in sin:
        if int.from_bytes(x[1][0:4],'big') == 0x352ef853:
            apid    = x[1][4]
            # sequence= x[1][5]
            # length  = int.from_bytes(x[1][6:7],"big")
            if apid == 0:
                out.boot_time.append(x[0])
                out.boot.append(x[1])
            elif apid == 1:
                out.general_time.append(x[0])
                out.general.append(x[1])
            elif apid == 2:
                out.command_time.append(x[0])
                out.command.append(x[1])
            elif apid == 3:
                out.memory_time.append(x[0])
                out.memory.append(x[1])
            elif apid == 4:
                out.encoder_time.append(x[0])
                out.encoder.append(x[1])
        else:
            print('Invalid SUVM Packet APID at time ', x[0])
    return out
# 
def breakout_hrt_packet(fd):
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
                print('Faulty instrument HRT Packet ID: {fault_bytes}')
        # 
        if sync_word == '0x1acffc1d':
            pkt_length  = np.ushort(hdr[6] | hdr[7] << 8)
            time_tag    = np.uint(int.from_bytes(hdr[8:12],'little'))
            i += 12
            #
            data_packet = bytearray(fd[i:i+pkt_length])
            try:
                if inst_id == '01007500' and data_packet[105:109].decode('utf-8') == 'AF09':
                    out.tip1_m0.append([time_tag, data_packet])  # XIP 1 M0 (117b)
            except UnicodeDecodeError:
                print(f'Error decoding bytes in ATIP HRT packet {i}\n')
            if inst_id == '0100ba00':   # XIP 1 M1  (186 bytes)
                out.tip1_m1.append([time_tag, data_packet])
            if inst_id[0:4] == '0200':   # SUVM 2
                out.suvm2.append([time_tag, data_packet])
            try:
                if inst_id == '03007500' and data_packet[105:109].decode('utf-8') == 'BF02':
                    out.mip3_m0.append([time_tag, data_packet])  # XIP 3 M0 (117b)
            except UnicodeDecodeError:
                print(f'Error decoding bytes in AMIP HRT packet {i}\n')
            if inst_id == '0300ba00':   # XIP 3 M1  (186 bytes)
                out.mip3_m1.append([time_tag, data_packet])
            if inst_id[0:4] == '0400':   # SUVM 4
                out.suvm4.append([time_tag, data_packet])
            try:
                if inst_id == '05007500' and data_packet[105:109].decode('utf-8') == 'AF08':
                    out.tip5_m0.append([time_tag, data_packet])  # XIP 5 M0 (117b)
            except UnicodeDecodeError:
                print(f'Error decoding bytes in CTIP HRT packet {i}\n')
            if inst_id == '0500ba00':   # XIP 5 M1  (186 bytes)
                out.tip5_m1.append([time_tag, data_packet])
            if inst_id[0:4] == '0600':   # SUVM 6
                out.suvm6.append([time_tag, data_packet])
            try:
                if inst_id == '07007500' and data_packet[105:109].decode('utf-8') == 'BF03':
                    out.mip7_m0.append([time_tag, data_packet])   # XIP7 M0 (117b)
            except UnicodeDecodeError:
                print(f'Error decoding bytes in CMIP HRT packet {i}\n')
            if inst_id == '0700ba00':   # XIP 7 M1  (186 bytes)
                out.mip7_m1.append([time_tag, data_packet])
            if inst_id[0:4] == '0800':   # SUVM 8
                out.suvm8.append([time_tag, data_packet])
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
