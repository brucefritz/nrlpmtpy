"""
Routines to take Tri-XIP telemetry and parse into meaningful (decimal) values

Classes:
    IDC_M0() --> Data frame (length of n-records) to hold basic 1 Hz telemetry
                 from XIP IDC M0 output
    IDC_M1() --> Data frame (length of n-records) to hold high rate, 10 Hz,
                 telemetry from XIP IDC M1 output
        
Functions:
    convert_m0_hex2dec(m, xip) --> Primary function; parses ASCII M0 fromes 
                from IDC and fills "IDC_M0" class with decimal values
    convert_m1_hex2dec(m, xip) --> Primary function; parses ASCII M1 frames
                from IDC and fills "IDC_M1" class with decimal values
    IDC_DN_to_dec(DN) --> Algorithm for calculating decimal values from XIP
                IDC data numbers
    convert_m0_asc2dec(xip_file, xip) --> Wrapper to convert ascii Tri-XIP 
                files into the IDC_M0 data class above. Inputs are the ascii
                data file (xip_file) and the type of XIP ("TIP" or "MIP");
                output is the data class
    convert_m1_asc2dec(xip_file, xip) --> Wrapper to convert ascii Tri-XIP
                files into the IDC_M1 data class above. Same I/O as M0 version
    parse_ascii_packets(xip_file, style='M0') --> Convert ascii input files
                to a structure similar to how the data is parsed from the 
                binary HRT data files
    convert_m0_byt2dec(din,xip) --> Convert Python 'bytearray' of Tri-XIP 
                output from the binary HRT files to Python list; then
                convert to the IDC_M0() class described above
    convert_m1_byt2dec(din,xip) --> Same as above but for the M1 data class
    
@author: bfritz
"""
import numpy as np
# 
class IDC_M0():
    # Input: n -- Number of packets
    def __init__(self,n,xip):
        self.IDC_ID = np.zeros(n, dtype='U4')
        self.MET    = np.zeros(n, dtype='uint64')
        self.time   = np.zeros(n, dtype='uint64')
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
        self.HV_STATUS        = np.zeros(n, dtype='uint16')
    def __str__(self):
        a = f'Contents for IDC Serial Number: {self.IDC_ID}'
        c = 'Contains both MET and XIP instrument run time ("time")'
        t = f'Total packets converted :      {len(self.MET)}'
        return f'{a}\n{c}\n{t}\n\n'
# 
class IDC_M1():
    # Input: n -- Number of packets
    def __init__(self,n,xip):
        self.MET      = np.zeros(10*n, dtype='float')
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
        a = 'SUVM 10 Hz data Pakcet Contents for {self.IDC_ID}:'
        c = 'Contains both MET and XIP instrument run time ("time")'
        t = f'Total packets converted :      {len(self.MET)}'
        return f'{a}\n{c}\n{t}\n\n'
# 
def convert_m0_asc2dec(xip_file, xip):
    data_packets = parse_ascii_packets(xip_file, 'M0')
    return convert_m0_hex2dec(data_packets, xip)
# 
def convert_m1_asc2dec(xip_file, xip):
    data_packets = parse_ascii_packets(xip_file, 'M1')
    return convert_m1_hex2dec(data_packets, xip)
# 
def parse_ascii_packets(xip_file, style='M0'):
    """
    Formats XIP data flow to a format similar the output generated by binary 
    hrt files.
    Expects xip_file as a full path to the target ascii file
    Default is for M0 packet output, toggle "style" to return M1
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
# 
def convert_m0_byt2dec(din,xip):
    packet_list = []
    for i,p in enumerate(din):
        try:
            packet_list.append([p[0],p[1].decode('utf-8')])
        except UnicodeDecodeError:
            print(f'Error decoding bytes in M0 packet {i}\n')
    return convert_m0_hex2dec(packet_list,xip)
# 
def convert_m1_byt2dec(din,xip):
    packet_list = []
    for i,p in enumerate(din):
        try:
            packet_list.append([p[0],p[1].decode('utf-8')])
        except UnicodeDecodeError:
            print(f'Error decoding bytes in M1 packet {i}\n')
    return convert_m1_hex2dec(packet_list,xip)
# 
def convert_m0_hex2dec(m, xip):
    """
    Converts XIP M0 data frames from ASCII HEX to decimal values
    Expects m as a list of lists, with each element = [MET (long), 'HEX DATA']
    Expects "xip" as either "TIP" or "MIP"
    'HEX DATA' IDC M0 format:
    # 00 ØØ[zz zzzz] ØØ[zz zzzz]<CR>    PMT Dark Counts, PMT Red Counts
    # 04 ØØ[zz zzzz] Ø[xxx] Ø[xxx]<CR>  PMT UV Counts, HV Mon, HV Adj
    # 08 Ø[xxx] Øxxx Øxxx Øxxx<CR>      Sun Sensor, T[F1/LENS] T[F2/PMT] T_HV
    # 0C ØØ[zz zzzz] Ø[xxx] Ø[xxx]<CR>  Time Tag, 2.5 VREF Mon, IDC RTD
    # 10 [yyyy] [yyyy] [yyyy] FFFF<CR>  Discrete IDC & Sensor Flags, Error Status, IDC_ID
    # T<CR>
    """
    mout = IDC_M0(len(m), xip)
    for i, p in enumerate(m):
        mout.MET[i]    = p[0]
        mout.time[i]   = int(p[1][74:76] + p[1][77:81], 16)
        mout.dark[i]   = int(p[1][5:7]   + p[1][8:12], 16)
        if xip=='TIP':
            mout.red[i]  = int(p[1][15:17] + p[1][18:22], 16)
            mout.uv[i]   = int(p[1][28:30] + p[1][31:35], 16)
            mout.T_F1[i] = IDC_DN_to_dec(int(p[1][55:58], 16))
            mout.T_F2[i] = IDC_DN_to_dec(int(p[1][60:63], 16))
            mout.heater[i]  = int(p[1][100:104], 32)
        if xip=='MIP':
            mout.Mg[i]     = int(p[1][15:17] + p[1][18:22], 16)
            mout.VK[i]     = int(p[1][28:30] + p[1][31:35], 16)
            mout.T_LENS[i] = IDC_DN_to_dec(int(p[1][55:58], 16))
            mout.T_PMT[i]  = IDC_DN_to_dec(int(p[1][60:63], 16)) 
            mout.error[i]  = p[1][100:104]
        # 
        HV_V           = int(p[1][37:40], 16) * 3.3 / 4095
        mout.HV_mon[i] = (HV_V - 2.5)*(-1000) # Convert ADC V to HV
        mout.HV_adj[i] = int(p[1][42:45], 16) * 3.3 / 4095
        mout.sun[i]    = int(p[1][50:53], 16) * 3.3 / 4095
        mout.vref[i]   = int(p[1][83:86], 16) * 3.3 / 4095
        mout.T_IDC[i]  = IDC_DN_to_dec(int(p[1][88:91], 16))
        mout.T_HV[i]   = IDC_DN_to_dec(int(p[1][65:68], 16))
        mout.IDC_ID[i] = p[1][105:109]
        mout.discrete[i] = p[1][95:99]
        # 
        disc_bin = bin(int(p[1][95:99], 16))[2:].zfill(16)
        mout.MODE[i]             = disc_bin[-2:]
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
        mout.HV_STATUS[i]        = disc_bin[0:2]
    return mout
# 
def IDC_DN_to_dec(DN):
    DN_V = (DN / 4095) * 3.3
    DN_R = 4990 * (0.4)/(DN_V - 0.4)
    return (0.00001 * (DN_R * DN_R)) + (0.2355 * DN_R) - 245.65
# 
def convert_m1_hex2dec(m, xip):
    """
    Converts XIP 10 Hz M1 data frame from ASCII HEX to decimal values
    Expects m as a list of lists, with each element = [MET (long), 'HEX DATA']
    Expects "xip" as either "TIP" or "MIP"
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
    """
    mout = IDC_M1(len(m), xip)
    for i, p in enumerate(m):
        mout.IDC_ID    = p[1][3:7]
        try:
            mout.time[i*10:(i*10+10)] = [int(p[1][179:183],16) + k/10 for k in range(10)]
        except ValueError:
            print(f'Skipping M1 Time packet # {i}')
        mout.MET[i*10:(i*10+10)]  = [p[0] + k/10 for k in range(10)]
        dk = [p[1][8:12],   p[1][13:17],  p[1][18:22],  p[1][26:30],  p[1][31:35],
              p[1][36:40],  p[1][41:45],  p[1][49:53],  p[1][54:58],  p[1][59:63]]
        rd = [p[1][64:68],  p[1][72:76],  p[1][77:81],  p[1][82:86],  p[1][87:91],
              p[1][95:99],  p[1][100:104],p[1][105:109],p[1][110:114],p[1][118:122]]
        uv = [p[1][123:127],p[1][128:132],p[1][133:137],p[1][141:145],p[1][146:150],
              p[1][151:155],p[1][156:160],p[1][164:168],p[1][169:173],p[1][174:178]]
        try:
            mout.dark[i*10:(i*10+10)] = [int(x, 16) for x in dk]
        except ValueError:
            print(f'Skipping M1 Dark packet # {i}')
        if xip == 'TIP':
            try:
                mout.red[i*10:(i*10+10)] = [int(x, 16) for x in rd]
            except ValueError:
                print(f'Skipping M1 Red packet # {i}')
            try:
                mout.uv[i*10:(i*10+10)]  = [int(x, 16) for x in uv]
            except ValueError:
                print(f'Skipping M1 UV packet # {i}')
        if xip == 'MIP':
            try:
                mout.Mg[i*10:(i*10+10)] = [int(x, 16) for x in rd]
            except ValueError:
                print(f'Skipping M1 Mg+ packet # {i}')
            try:
                mout.VK[i*10:(i*10+10)] = [int(x, 16) for x in uv]
            except ValueError:
                print(f'Skipping M1 VK packet # {i}')
    # 
    return mout
