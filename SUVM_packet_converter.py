# -*- coding: utf-8 -*-
"""
suvm_packet_converter

Classes:
    suvm_bootloader_packet()
    suvm_command_packet()
    suvm_encoder_packet()
    suvm_general_packet()

Functions:
    suvm_converter(input_array):
        
        Parses each packet type produced by SUVM during normal operation

@author: bfritz
"""
import numpy as np
# 
class suvm_bootloader_packet():
    def __init__(self, n):
        self.time               = np.zeros(n, dtype='uint32')
        self.header             = np.zeros(n, dtype='uintc')  #  0
        self.apid               = np.zeros(n, dtype='ubyte')  #  4
        self.sequence_count     = np.zeros(n, dtype='ubyte')  #  5
        self.length             = np.zeros(n, dtype='uint16') #  6
        self.system_counter     = np.zeros(n, dtype='uint64') #  8, 1/1000 s
        self.gps_pps            = np.zeros(n, dtype='uint64') # 16, 1/1000 s
        self.watchdog_counter   = np.zeros(n, dtype='uint32') # 24, 1/50,000,000 s
        self.version            = np.zeros(n, dtype='uint32') # 28
        self.reset_status       = np.zeros(n, dtype='ubyte')  # 32
        self.last_cmd_status    = np.zeros(n, dtype='ubyte')  # 33
        self.last_cmd_id        = np.zeros(n, dtype='ubyte')  # 34
        self.last_cmd_opcode    = np.zeros(n, dtype='ubyte')  # 35
        self.last_cmd_time      = np.zeros(n, dtype='uint64') # 36, 1/1000 s
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
    
class suvm_general_packet():
    # Input: n -- Number of packets
    def __init__(self,n):
        self.time               = np.zeros(n, dtype='uint32')
        self.header             = np.zeros(n, dtype='uintc')  #  0
        self.apid               = np.zeros(n, dtype='ubyte')  #  4
        self.sequence_count     = np.zeros(n, dtype='ubyte')  #  5
        self.length             = np.zeros(n, dtype='uint16') #  6
        self.system_counter     = np.zeros(n, dtype='uint64') #  8
        self.gps_pps            = np.zeros(n, dtype='uint64') # 16
        self.watchdog_counter   = np.zeros(n, dtype='uint32') # 24
        self.version            = np.zeros(n, dtype='uint32') # 28
        self.reset_status       = np.zeros(n, dtype='ubyte')  # 32
        self.last_cmd_status    = np.zeros(n, dtype='ubyte')  # 33
        self.last_cmd_id        = np.zeros(n, dtype='ubyte')  # 34
        self.last_cmd_opcode    = np.zeros(n, dtype='ubyte')  # 35
        self.last_cmd_time      = np.zeros(n, dtype='uint64') # 36
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
    # 
class suvm_command_packet():
    def __init__(self, n):
        self.time               = np.zeros(n, dtype='uint32')
        self.header             = np.zeros(n, dtype='uintc')  #  0
        self.apid               = np.zeros(n, dtype='ubyte')  #  4
        self.sequence_count     = np.zeros(n, dtype='ubyte')  #  5
        self.length             = np.zeros(n, dtype='uint16') #  6
        self.system_counter     = np.zeros(n, dtype='uint64') #  8, 1/1000 s
        self.last_command       = np.zeros(n, dtype='S50') # Sufficient bytes for any cmd
        self.crc                = np.zeros(n, dtype='uint32') # 64
    # def __repr__(self):
    #     return f"<Test a:{self.a} b:{self.b}>"
    def __str__(self):
        t1 = f"SUVM Command Packets: {len(self.header)}"
        return f'{t1}\n'
    # 
class suvm_memory_packet():
    def __init__(self, n):
        self.time               = np.zeros(n, dtype='uint32')
        self.header             = np.zeros(n, dtype='uintc')  #  0
        self.apid               = np.zeros(n, dtype='ubyte')  #  4
        self.sequence_count     = np.zeros(n, dtype='ubyte')  #  5
        self.length             = np.zeros(n, dtype='uint16') #  6
        self.system_counter     = np.zeros(n, dtype='uint64') #  8, 1/1000 s
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
        self.time               = np.zeros(n, dtype='uint32')
        self.header             = np.zeros(n, dtype='uintc')  #  0
        self.apid               = np.zeros(n, dtype='ubyte')  #  4
        self.sequence_count     = np.zeros(n, dtype='ubyte')  #  5
        self.length             = np.zeros(n, dtype='uint16') #  6
        self.system_counter     = np.zeros(n, dtype='uint64') #  8, 1/1000 s
        self.time_first_element = np.zeros(n, dtype='uint64') #  16, 1/1000 s
        self.encoder_counts     = np.zeros(n*125, dtype='int16')
        self.padding            = np.zeros(n, dtype='uint16')
        self.crc                = np.zeros(n, dtype='uint32')
    # def __repr__(self):
    #     return f"<Test a:{self.a} b:{self.b}>"
    def __str__(self):
        t1 = f"SUVM Encoder Packets: {len(self.header)}"
        return f'{t1}\n'
    # 
def suvm_bootloader_converter(s):
    bt = suvm_bootloader_packet(len(s.boot))
    for i,p in enumerate(s.boot):
        bt.time[i]              = s.boot_time[i]
        bt.header[i]            = int.from_bytes(p[0:4],'big')
        bt.apid[i]              = p[4] # 0
        bt.sequence_count[i]    = p[5]
        bt.length[i]            = int.from_bytes(p[6:8],'little')
        bt.system_counter[i]    = int.from_bytes(p[8:16],'little')
        bt.gps_pps[i]           = int.from_bytes(p[16:24],'little')
        bt.watchdog_counter[i]  = int.from_bytes(p[24:28],'little')
        bt.version[i]           = int.from_bytes(p[28:32],'little')
        bt.reset_status[i]      = p[32]
        bt.last_cmd_status[i]   = p[33]
        bt.last_cmd_id[i]       = p[34]
        bt.last_cmd_opcode[i]   = p[35]
        bt.last_cmd_time[i]     = int.from_bytes(p[36:44],'little')
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
    return bt

def suvm_command_converter(s):
    cm = suvm_command_packet(len(s.command))
    for i,p in enumerate(s.command):
        cm.time[i]              = s.command_time[i]
        cm.header[i]            = int.from_bytes(p[0:4],'big')
        cm.apid[i]              = p[4] # 2
        cm.sequence_count[i]    = p[5]
        cm.length[i]            = int.from_bytes(p[6:8],'little')
        cm.system_counter[i]    = int.from_bytes(p[8:16],'little')
        # cm.last_command[i]      = hex(int.from_bytes(p[16:cm.length[i]], 'little'))
        cm.last_command[i]      = p[16:cm.length[i]].hex()
        cm.crc[i]               = int.from_bytes(p[cm.length[i]:cm.length[i]+4], 'big')
    # 
    return cm

def suvm_encoder_converter(s):
    en = suvm_encoder_packet(len(s.encoder))
    for i,p in enumerate(s.encoder):
        en.time[i]              = s.encoder_time[i]
        en.header[i]            = int.from_bytes(p[0:4],'big')
        en.apid[i]              = p[4] # 4
        en.sequence_count[i]    = p[5]
        en.length[i]            = int.from_bytes(p[6:8],'little')
        en.system_counter[i]    = int.from_bytes(p[8:16],'little')
        en.time_first_element[i]= int.from_bytes(p[16:24],'little')
        j = i*125
        for z in range(0,250,2):
            en.encoder_counts[int(j+z/2)] = int.from_bytes(p[24+z:24+z+2],'little') - 2**15
        en.padding[i]           = 0
        en.crc[i]               = int.from_bytes(p[276:280], 'little')
    # 
    return en

def suvm_general_converter(s):
    gn = suvm_general_packet(len(s.general))
    # me = suvm_encoder_packet(len(s.memory))
    
    for i,p in enumerate(s.general):
        if len(p) < 120: continue
        gn.time[i]              = s.general_time[i]
        gn.header[i]            = int.from_bytes(p[0:4],'big')
        gn.apid[i]              = p[4] # 1
        gn.sequence_count[i]    = p[5]
        gn.length[i]            = int.from_bytes(p[6:8],'little')
        gn.system_counter[i]    = int.from_bytes(p[8:16],'little')
        gn.gps_pps[i]            = int.from_bytes(p[16:24],'little')
        gn.watchdog_counter[i]   = int.from_bytes(p[24:28],'little')
        gn.version[i]            = int.from_bytes(p[28:32],'little')
        gn.reset_status[i]       = p[33]
        gn.last_cmd_status[i]    = p[34]
        gn.last_cmd_id[i]        = p[35]
        gn.last_cmd_opcode[i]    = p[36]
        gn.last_cmd_time[i]      = int.from_bytes(p[36:44],'little')
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
    return gn    