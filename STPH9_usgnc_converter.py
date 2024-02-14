# -*- coding: utf-8 -*-
"""
Routines to convert STP-H9 byte-level telemetry to decimal values

Classes:
    IDC_M0() --> 
        
Functions:
    convert_m0_hex2dec(m, xip) --> 

@author: bfritz
"""
import struct
import numpy as np
import pandas as pd
import astropy.time as aptime
import spacepy as sp
import datetime
# 
class ISS_USGNC_TLM():
    # Input: n -- Number of packets
    def __init__(self,n):
        self.pktnum      = np.zeros(n, dtype='uint16')
        self.yyyy        = np.zeros(n, dtype='uint16')
        self.mm          = np.zeros(n, dtype='uint8')
        self.dd          = np.zeros(n, dtype='uint8')
        self.hh          = np.zeros(n, dtype='uint8')
        self.mn          = np.zeros(n, dtype='uint8')
        self.ss          = np.zeros(n, dtype='uint8')
        self.jd          = np.zeros(n, dtype='double')
        self.secondofday = np.zeros(n, dtype='double')
        self.gpscumul    = np.zeros(n, dtype='uint64')
        self.gpsweek     = np.zeros(n, dtype='uint32')
        self.gpssec_crs  = np.zeros(n, dtype='uint32')
        self.gpssec      = np.zeros(n, dtype='double')
        self.apid        = np.zeros(n, dtype='uint16')
        self.radius      = np.zeros(n, dtype='double')
        self.rhat        = np.zeros((n,3), dtype='double')
        self.speed       = np.zeros(n, dtype='double')
        self.vhat        = np.zeros((n,3), dtype='double')
        self.usgnc_sec  = np.zeros(n, dtype='double')
        self.posn_inert = np.zeros((n,3), dtype='float')
        self.velc_inert = np.zeros((n,3), dtype='float')
        self.rate_inert = np.zeros((n,3), dtype='float')
        self.quat_inert = np.zeros((n,4), dtype='float')
        self.quat_lvlh  = np.zeros((n,4), dtype='float')
        self.posn_ctrs  = np.zeros((n,3), dtype='float')
        self.velc_ctrs  = np.zeros((n,3), dtype='float')
        self.quat_ctrs  = np.zeros((n,4), dtype='float')
        self.statvec_qual  = np.zeros(n, dtype='ubyte')
        self.attquat_qual  = np.zeros(n, dtype='ubyte')
        self.solarlos_qual = np.zeros(n, dtype='ubyte')
        self.attrate_qual  = np.zeros(n, dtype='ubyte')
        self.met           = np.zeros(n, dtype='double')
        self.doy           = np.zeros(n, dtype='uint16')
        self.dayofweek     = np.zeros(n, dtype='ubyte')
        self.secondofweek  = np.zeros(n, dtype='uint32')
        # self.sxyz_quats       = np.zeros(n, dtype='')
        # self.xyzs_quats       = np.zeros(n, dtype='')
    def __str__(self):
        a = f'Contents for ISS USGNC'
        b = f'Total packets :      {len(self.pktnum)}'
        return f'{a}\n{b}\n'


def load_stph9_hs_packet_674f6_pd_only(infile):
    """
    Template for loading data using only pandas and numpy (no data class)
    Currently not functional, mismatch between endian-ness of the system
    """
    apid_674_data_template = np.dtype([
        ('hdr_a','S22'), ('apid_plus','>u2'),                       #   0- 23
        ('hdr_b','S10'), ('pnuma', 'B'),                            #  24- 34
        ('pnumb', 'B'), ('hdrc','S3'),                              #  35- 38
        ('msid_LADP06MD2378W','S9'), ('gpssec_crs','>u4'),          #  39- 51
        ('LADP06MD2380W','S9'), ('gpssec_dec','B'),                 #  52- 61
        ('LADP06MD2395H','S9'), ('posn_inert_X','>f4'),             #  62- 74
        ('LADP06MD2396H','S9'), ('posn_inert_Y','>f4'),             #  75- 87
        ('LADP06MD2397H','S9'), ('posn_inert_Z','>f4'),             #  88-100
        ('LADP06MD2399R','S9'), ('velc_inert_X','>f4'),             # 101-113
        ('LADP06MD2400R','S9'), ('velc_inert_Y','>f4'),             # 114-126
        ('LADP06MD2401R','S9'), ('velc_inert_Z','>f4'),             # 127-139
        ('LADP06MD2391R','S9'), ('rate_inert_X','>f4'),             # 140-152
        ('LADP06MD2392R','S9'), ('rate_inert_Y','>f4'),             # 153-165
        ('LADP06MD2393R','S9'), ('rate_inert_Z','>f4'),             # 166-178
        ('LADP06MD2382U','S9'), ('quat_inert_0','>f4'),             # 179-191
        ('LADP06MD2383U','S9'), ('quat_inert_1','>f4'),             # 192-204
        ('LADP06MD2384U','S9'), ('quat_inert_2','>f4'),             # 205-217
        ('LADP06MD2385U','S9'), ('quat_inert_3','>f4'),             # 218-230
        ('LADP06MD2416U','S9'), ('quat_lvlh_0','>f4'),              # 231-243
        ('LADP06MD2417U','S9'), ('quat_lvlh_1','>f4'),              # 244-256
        ('LADP06MD2418U','S9'), ('quat_lvlh_2','>f4'),              # 257-269
        ('LADP06MD2419U','S9'), ('quat_lvlh_3','>f4'),              # 270-282
        ('LADP06MD2429U','S9'), ('statvec_qual','B'),               # 283-292
        ('LADP06MD2430U','S9'), ('attquat_qual','B'),               # 293-302
        ('LADP06MD2431U','S9'), ('solarlos_qual','B'),              # 303-312
        ('LADP06MD2432U','S9'), ('attrate_qual','B'),               # 313-322
        ('LADP06MD2403H','S9'), ('posn_ctrs_X','>f4'),              # 323-335
        ('LADP06MD2404H','S9'), ('posn_ctrs_Y','>f4'),              # 336-348
        ('LADP06MD2405H','S9'), ('posn_ctrs_Z','>f4'),              # 349-361
        ('LADP06MD2407R','S9'), ('velc_ctrs_X','>f4'),              # 362-374
        ('LADP06MD2408R','S9'), ('velc_ctrs_Y','>f4'),              # 375-387
        ('LADP06MD2409R','S9'), ('velc_ctrs_Z','>f4'),              # 388-400
        ('LADP06MD2411U','S9'), ('quat_ctrs_0','>f4'),              # 401-413
        ('LADP06MD2412U','S9'), ('quat_ctrs_1','>f4'),              # 414-426
        ('LADP06MD2413U','S9'), ('quat_ctrs_2','>f4'),              # 427-439
        ('LADP06MD2414U','S9'), ('quat_ctrs_3','>f4'),              # 440-452
        ])
    
    with open(infile, 'rb') as f: byte_data = f.read()
    
    if (len(byte_data) % 453) != 0:
        print('Byte Array not even multiple of 453, returning...')
        return
    else:
        np_data = np.frombuffer(byte_data, apid_674_data_template)
        df = pd.DataFrame(np_data)
    print(len(df))
    df = df[df['gpssec_crs'] > 1000]
    print(len(df))
    df = df.drop_duplicates(subset=['gpssec_crs'])
    print(len(df))
    
    """
    ValueError: Big-endian buffer not supported on little-endian compiler
    """
    return df

def load_stph9_hs_packet_674f6(byte_data):
    print(f'Loading APID 674 HS Format 6 File to Pandas DataFrame ... ')
    """
    STP-H9 FMT6 Custom GSE Packet for NRL VVIPRE & ECLIPSE
    GSE APID 674
    Format 6
    Packet Length: 453 bytes
    Output Rate 1
    Revision 2
    """
    # Load the data class
    iss = ISS_USGNC_TLM(len(byte_data))     # Use the class here to load data
    ft_to_km = 1.609344/5280.0
    # 
    ### "pkt_num" Bit-wise operator likely unnecessary but remains consistent with S.A.B. IDL source
    for i,p in enumerate(byte_data):
        abin = bin(int(p[22:24].hex(), 16))
        iss.apid[i]         = int(abin[-11:], 2)
        iss.pktnum[i]       = int(p[34] & 3)*256 + int(p[35])
        iss.gpssec_crs[i]   = int.from_bytes(p[48:52], 'big')
        iss.gpssec[i]       = float(iss.gpssec_crs[i]) + int(p[61])/256.0
        iss.posn_inert[i,0] = struct.unpack('>f',bytes(p[ 71: 75]))[0]*ft_to_km
        iss.posn_inert[i,1] = struct.unpack('>f',bytes(p[ 84: 88]))[0]*ft_to_km
        iss.posn_inert[i,2] = struct.unpack('>f',bytes(p[ 97:101]))[0]*ft_to_km
        iss.velc_inert[i,0] = struct.unpack('>f',bytes(p[110:114]))[0]*ft_to_km
        iss.velc_inert[i,1] = struct.unpack('>f',bytes(p[123:127]))[0]*ft_to_km
        iss.velc_inert[i,2] = struct.unpack('>f',bytes(p[136:140]))[0]*ft_to_km
        iss.rate_inert[i,0] = struct.unpack('>f',bytes(p[149:153]))[0]
        iss.rate_inert[i,1] = struct.unpack('>f',bytes(p[162:166]))[0]
        iss.rate_inert[i,2] = struct.unpack('>f',bytes(p[175:179]))[0]
        iss.quat_inert[i,0] = struct.unpack('>f',bytes(p[188:192]))[0]
        iss.quat_inert[i,1] = struct.unpack('>f',bytes(p[201:205]))[0]
        iss.quat_inert[i,2] = struct.unpack('>f',bytes(p[214:218]))[0]
        iss.quat_inert[i,3] = struct.unpack('>f',bytes(p[227:231]))[0]
        iss.quat_lvlh[i,0]  = struct.unpack('>f',bytes(p[240:244]))[0]
        iss.quat_lvlh[i,1]  = struct.unpack('>f',bytes(p[253:257]))[0]
        iss.quat_lvlh[i,2]  = struct.unpack('>f',bytes(p[266:270]))[0]
        iss.quat_lvlh[i,3]  = struct.unpack('>f',bytes(p[279:283]))[0]
        iss.statvec_qual[i] = int(p[292])
        iss.attquat_qual[i] = int(p[302])
        iss.solarlos_qual[i]= int(p[312])
        iss.attrate_qual[i] = int(p[322])
        iss.posn_ctrs[i,0]  = struct.unpack('>f',bytes(p[332:336]))[0]*ft_to_km
        iss.posn_ctrs[i,1]  = struct.unpack('>f',bytes(p[345:349]))[0]*ft_to_km
        iss.posn_ctrs[i,2]  = struct.unpack('>f',bytes(p[358:362]))[0]*ft_to_km
        iss.velc_ctrs[i,0]  = struct.unpack('>f',bytes(p[371:375]))[0]*ft_to_km
        iss.velc_ctrs[i,1]  = struct.unpack('>f',bytes(p[384:388]))[0]*ft_to_km
        iss.velc_ctrs[i,2]  = struct.unpack('>f',bytes(p[397:401]))[0]*ft_to_km
        iss.quat_ctrs[i,0]  = struct.unpack('>f',bytes(p[410:414]))[0]
        iss.quat_ctrs[i,1]  = struct.unpack('>f',bytes(p[423:427]))[0]
        iss.quat_ctrs[i,2]  = struct.unpack('>f',bytes(p[436:440]))[0]
        iss.quat_ctrs[i,3]  = struct.unpack('>f',bytes(p[449:453]))[0]
        
    print(f'Reading in total entries:        {len(byte_data)}')
    df = pd.DataFrame()
    # 
    # Put data into Pandas Dataframe to enable array manipulation (sort,drop)
    df['APID']          = iss.apid
    df['packet_number'] = iss.pktnum
    df['gpssec_crs']    = iss.gpssec_crs
    df['usgnc_sec']     = iss.gpssec
    df['posn_inert_X']  = iss.posn_inert[:,0]
    df['posn_inert_Y']  = iss.posn_inert[:,1]
    df['posn_inert_Z']  = iss.posn_inert[:,2]
    df['velc_inert_X']  = iss.velc_inert[:,0]
    df['velc_inert_Y']  = iss.velc_inert[:,1]
    df['velc_inert_Z']  = iss.velc_inert[:,2]
    df['rate_inert_X']  = iss.rate_inert[:,0]
    df['rate_inert_Y']  = iss.rate_inert[:,1]
    df['rate_inert_Z']  = iss.rate_inert[:,2]
    df['quat_inert_0']  = iss.quat_inert[:,0]
    df['quat_inert_1']  = iss.quat_inert[:,1]
    df['quat_inert_2']  = iss.quat_inert[:,2]
    df['quat_inert_3']  = iss.quat_inert[:,3]
    df['quat_lvlh_0']   = iss.quat_lvlh[:,0]
    df['quat_lvlh_1']   = iss.quat_lvlh[:,1]
    df['quat_lvlh_2']   = iss.quat_lvlh[:,2]
    df['quat_lvlh_3']   = iss.quat_lvlh[:,3]
    df['statvec_qual']  = iss.statvec_qual
    df['attquat_qual']  = iss.attquat_qual
    df['solarlos_qual'] = iss.solarlos_qual
    df['attrate_qual']  = iss.attrate_qual
    df['posn_ctrs_X']   = iss.posn_ctrs[:,0]
    df['posn_ctrs_Y']   = iss.posn_ctrs[:,1]
    df['posn_ctrs_Z']   = iss.posn_ctrs[:,2]
    df['velc_ctrs_X']   = iss.velc_ctrs[:,0]
    df['velc_ctrs_Y']   = iss.velc_ctrs[:,1]
    df['velc_ctrs_Z']   = iss.velc_ctrs[:,2]
    df['quat_ctrs_0']   = iss.quat_ctrs[:,0]
    df['quat_ctrs_1']   = iss.quat_ctrs[:,1]
    df['quat_ctrs_2']   = iss.quat_ctrs[:,2]
    df['quat_ctrs_3']   = iss.quat_ctrs[:,3]
    # 
    # Remove any potentially bad times
    df = df[df['gpssec_crs'] > 1362875000]
    print(f'             valid times:        {len(df)}')
    # 
    df = df.drop_duplicates(subset=['gpssec_crs'])
    df = df.sort_values(by=['gpssec_crs'])
    print(f'Returning unique entries:        {len(df)}\n')
    # 
    # Quality check not implemented, not sure it has desired effect (per SAB)
    # df = df[(df['statvec_qual'] == 1) | (df['attquat_qual'] == 1)]
    # print(f'Selecting quality data points:   {len(df)}')
    # 
    # print(df['vhat_Y'][0:5])
    # for number in iss.gpssec[100:115]: print(f'{number:10.7f}')
    return df

def convert_stph9_hs_df_to_dataclass(df):
    iss = ISS_USGNC_TLM(len(df))
    
    iss.apid            = np.array(df['APID'])
    iss.pktnum          = np.array(df['packet_number'])
    iss.gpssec_crs      = np.array(df['gpssec_crs'])
    iss.gpscumul        = np.array(df['usgnc_sec'])
    iss.posn_inert[:,0] = np.array(df['posn_inert_X'])
    iss.posn_inert[:,1] = np.array(df['posn_inert_Y'])
    iss.posn_inert[:,2] = np.array(df['posn_inert_Z'])
    iss.velc_inert[:,0] = np.array(df['velc_inert_X'])
    iss.velc_inert[:,1] = np.array(df['velc_inert_Y'])
    iss.velc_inert[:,2] = np.array(df['velc_inert_Z'])
    iss.rate_inert[:,0] = np.array(df['rate_inert_X'])
    iss.rate_inert[:,1] = np.array(df['rate_inert_Y'])
    iss.rate_inert[:,2] = np.array(df['rate_inert_Z'])
    iss.quat_inert[:,0] = np.array(df['quat_inert_0'])
    iss.quat_inert[:,1] = np.array(df['quat_inert_1'])
    iss.quat_inert[:,2] = np.array(df['quat_inert_2'])
    iss.quat_inert[:,3] = np.array(df['quat_inert_3'])
    iss.quat_lvlh[:,0]  = np.array(df['quat_lvlh_0'])
    iss.quat_lvlh[:,1]  = np.array(df['quat_lvlh_1'])
    iss.quat_lvlh[:,2]  = np.array(df['quat_lvlh_2'])
    iss.quat_lvlh[:,3]  = np.array(df['quat_lvlh_3'])
    iss.statvec_qual    = np.array(df['statvec_qual'])
    iss.attquat_qual    = np.array(df['attquat_qual'])
    iss.solarlos_qual   = np.array(df['solarlos_qual'])
    iss.attrate_qual    = np.array(df['attrate_qual'])
    iss.posn_ctrs[:,0]  = np.array(df['posn_ctrs_X'])
    iss.posn_ctrs[:,1]  = np.array(df['posn_ctrs_Y'])
    iss.posn_ctrs[:,2]  = np.array(df['posn_ctrs_Z'])
    iss.velc_ctrs[:,0]  = np.array(df['velc_ctrs_X'])
    iss.velc_ctrs[:,1]  = np.array(df['velc_ctrs_Y'])
    iss.velc_ctrs[:,2]  = np.array(df['velc_ctrs_Z'])
    iss.quat_ctrs[:,0]  = np.array(df['quat_ctrs_0'])
    iss.quat_ctrs[:,1]  = np.array(df['quat_ctrs_1'])
    iss.quat_ctrs[:,2]  = np.array(df['quat_ctrs_2'])
    iss.quat_ctrs[:,3]  = np.array(df['quat_ctrs_3'])
    # 
    # Add derived parameters
    iss.usgnc_sec       = np.array(df['usgnc_sec'])
      # NRT GPS seconds for legacy purposes
    iss.gpsweek         = [int(x / 604800) for x in iss.gpscumul]
    iss.gpssec          = [int(x % 604800) for x in iss.gpscumul]
    # 
    t_gnc = aptime.Time(iss.gpscumul, format='gps')
    iss.jd              = t_gnc.jd
    iss.yyyy            = [int(x[0:4]) for x in t_gnc.iso]
    iss.mm              = [int(x[5:7]) for x in t_gnc.iso]
    iss.dd              = [int(x[8:10]) for x in t_gnc.iso]
    iss.hh              = [int(x[11:13]) for x in t_gnc.iso]
    iss.mn              = [int(x[14:16]) for x in t_gnc.iso]
    iss.ss              = [float(x[17:23]) for x in t_gnc.iso]
    iss.secondofday = [x*3600.0 + y*60.0 + z for x,y,z in 
                       zip(iss.hh,iss.mn,iss.ss)]
    iss.doy = [datetime.datetime(x,y,z,a,b,int(c)).timetuple().tm_yday for
               x,y,z,a,b,c in zip(iss.yyyy,iss.mm,iss.dd,iss.hh,iss.mn,iss.ss)]
    # 
    iss.radius          = [np.sqrt(x*x + y*y + z*z) for x,y,z in 
                    zip(iss.posn_inert[:,0],iss.posn_inert[:,1],iss.posn_inert[:,2])]
    iss.rhat[:,0]       = [x/y for x,y in zip(iss.posn_inert[:,0],iss.radius)]
    iss.rhat[:,1]       = [x/y for x,y in zip(iss.posn_inert[:,1],iss.radius)]
    iss.rhat[:,2]       = [x/y for x,y in zip(iss.posn_inert[:,2],iss.radius)]
    iss.speed           = [np.sqrt(x*x + y*y + z*z) for x,y,z in 
                    zip(iss.velc_inert[:,0],iss.velc_inert[:,1],iss.velc_inert[:,2])]
    iss.vhat[:,0]       = [x/y for x,y in zip(iss.velc_inert[:,0],iss.speed)]
    iss.vhat[:,1]       = [x/y for x,y in zip(iss.velc_inert[:,1],iss.speed)]
    iss.vhat[:,2]       = [x/y for x,y in zip(iss.velc_inert[:,2],iss.speed)]
    # 
    # NOTE: launchtimes takes out leap seconds, so is not a true GPS time, 
    # but used for UT timing calcuations 
    h9_t0_yy = 2023
    h9_t0_mm = 3
    h9_t0_dd = 15
    h9_t0_hh = 00 # UT
    h9_t0_mn = 30
    h9_t0_ss = 00
    h9_t0_gpsweek = 2253
    h9_t0_gpssecofweek = 261000
    ticksperday = 86400
    # Note, to find MET, adding back in leap seconds that are subtracted in
    # launchtimes values = 18 as of the launch date for H9
    leap_sec=18
    launch_gps_met0 = h9_t0_gpsweek*86400.*7 + h9_t0_gpssecofweek + leap_sec 
    # MET is mission elapsed time, in seconds; usgnc_sec is gps time and does not remove leap seconds
    iss.met = [x - float(launch_gps_met0) for x in iss.usgnc_sec]
    
    iss.secondofweek = [(((h9_t0_gpssecofweek + x) % 604800.) + 604800.) % 604800.  for x in iss.met]
    iss.dayofweek = [int(x/86400) + 1 for x in iss.secondofweek]
    
    return iss

def main():
    import ECLIPSE_H9_ccsds as ehc
    iss_file_in = 'C:/data/STPH9/flt/2401/NRL_674f6_2024001'
    ## Debug test for decrypt
    
    iss_byte = ehc.load_iss_hs_bytes_from_ccsds(iss_file_in)
    iss_df = load_stph9_hs_packet_674f6(iss_byte)
    iss = convert_stph9_hs_df_to_dataclass(iss_df)
    
    # df = load_stph9_hs_packet_674f6_pd(iss_file_in)
    
    # 
if __name__ == "__main__":
    print(f"==== {__file__} ====")
    main()