"""
Script to process data from *decrypted STP-H9 ECLIPSE CCSDS files

Functions:
    decrypt_eclipse_hrt_from_ccsds(ccsds_in) --> 
    
    load_eclipse_bytes_from_ccsds(ccsds_in) --> reads in *decrypted* CCSDS 
            packets and extracts HRT data
    
* Requires decrypted CCSDS files. To decrypt in Spyder (Windows) IDE:
In [1]: runfile('C:/code/py/stp/dice_decrypt_v2_0/decrypt.py', args=EncCCSDS, 
                                    wdir='C:/code/py/stp/dice_decrypt_v2_0/')

where EncCCSDS is the encrypted data file, e.g. 
    'C:/data/ECLIPSE/gnd/220907-TVAC/IssCcsds.1729_2022-09-07_20_19_06'

@author: bfritz
"""
import sys
import os
import pandas as pd
import numpy as np
# 
def decrypt_eclipse_hrt_from_ccsds(ccsds_in):
    print('Prodecure only fit to run from Sypder IDE (Windows)')
    # Pointer to decyprtion working directory
    decrypt_dir = 'C:/code/py/stp/dice_decrypt_v2_0/'
    # Pointer to decryption script
    decrypt_file = f'{decrypt_dir}/decrypt.py'
    isExist = os.path.exists(decrypt_dir)
    if isExist == False:
        print("STP decrypt tool not found, please fix the directory")
        sys.exit()
    # !!! Only works in Windwos-based Spyder IDE
    runfile(decrypt_file, args=ccsds_in, wdir=decrypt_dir)
    return
# 
def load_eclipse_bytes_from_ccsds(ccsds_in):
    """
    # CCSDS packets are fixed length of 1300 bytes
    # 18 bytes CCSDS header
    # 10 bytes ECLIPSE header
    # 1270 bytes ECLIPSE HRT data
    # 2 byte CRC-16
    # 
    # The ouput is expected to feed into "breakout_hrt_packet()"
    # from ECLIPSE_telemetry_breakout.py
    # *** Note, the output flattens "outbyte" from a list of lists, to a single list
    
    CCSDS Header
    Word [Bits] -- Description
      1   [0:2] -- Version number (0 == Version 1)
      1   [ 3 ] -- Header type, Core (0) or Payload (1)
      1   [ 4 ] -- Secondary header (1 for ECLIPSE)
      1  [5:15] -- Payload APID (1729 == 0x06C1 for ECLIPSE)
        Ver.=0 + Head.=1 + Second. head. = 1 + APID = 1729 --> Word 1 = 0x1EC1
      2   [0:1] -- Sequence flag, Commands (11'b) or Telemetry (00'b)
      2  [2:15] -- Packet Sequence Count
      3  [0:15] -- Packet length --> 1293 for ECLIPSE = # bytes after header - 1
      4            Coarse Time MSW
      5            Coarse Time LSW
      6   [0:7] -- Fine Time
      6  [8:15] -- Time ID, etc.
      7   [1:4] -- STP-H9 Element ID
      7  [5:15] -- STP-H9 Packet ID #1
      8            STP-H9 Packet ID #2
      9            Additional Fine Time Precision
      --- Start ECLIPSE Header info
      10 Sequence Counter ?
      11 ECLIPSE data type (0xE803 == 1000 --> ECLIPSE HRT)
      12 ECLIPSE packet length (0xF604 == 1270d packets)
      13 GPS Time, Big end
      14 GPS Time, Little end
    """
    fin = open(ccsds_in,"rb")		# open input file
    outbyte = []
    pkt = 0
    while 1:
        x = bytearray(fin.read(1300))	# read in full CCSDS packet assuming it starts at first byte
        if len(x) < 1300:				# if 1300 bytes not read, end of file
            fin.close()
            break
        abin = bin(int(x[0:2].hex(), 16))
        apid = int(abin[-11:], 2)
        ecid = x[20:22].hex()
        if apid == 1729 and ecid == 'e803':
            # print(x[22:24].hex(), int.from_bytes(x[22:24], 'little'))
            pkt_len = int.from_bytes(x[22:24], 'little') # def. 0xf604-->1270
            outbyte.append(x[28:(28 + pkt_len)])	# extract the eclipse data
            pkt += 1
        else:
            print('Anomalous packet')
    print('CCSDS File: ', ccsds_in)
    print('CCSDS File Contents: ', pkt, ' HRT packets\n')
    return [item for subset in outbyte for item in subset]
# 
def load_iss_hs_bytes_from_ccsds(ccsds_in):
    """
    This routine reads a STP-H9 GSE nbinary file, format 6
    This is a customized GSE packet that includes only the ISS USGNC parameters
    
    # H&S packets are fixed length of 453 bytes
    
    Header (known, relevant parameters)
    Bytes [Bits] -- Description
      0- 38        -- Total Header
     22- 23  [0:2] -- Version number (0 == Version 1)
     22- 23  [ 3 ] -- Header type, Core (0) or Payload (1)
     22- 23  [ 4 ] -- Secondary header (0 for H9)
     22- 23 [5:15] -- Payload APID (674 == 0x02A2 for STP-H9)
        Ver.=1 + Head.=1 + Second. head. = 0 + APID = 674 --> Word 11 = 0x1AA2
     35- 36 Packet Counter (little endian)
     48- 51                  - GPS Time (uint)
         61                  - GPS Time (byte, 1/256.)
      71- 74, 84- 87, 97-100 - Inertial Position (float, ft)
     110-113,123-126,136-139 - Inertial Velocity (float, ft/s)
     149-152,162-165,175-178 - Inertial Rate (float)
     188-191,201-204,214-217,227-230 - Inertial Quaternion (float)
     240-243,253-256,266-269,279-282 - LVLH Quaternion (float)
        -292                 - State Vector Quality Flag (byte)
        -302                 - Attitude Quaternion Quality Flag (byte)
        -312                 - Solar LOS Quality Flag (byte)
        -322                 - Attitude Rate Quality Flag (byte)
     332-335,345-348,358-361 - CTRS Position (float, ft)
     371-374,384-387,397-400 - CTRS Velocity (float, ft/s)
     410-413,423-426,436-439,449-452 - CTRS Quaternion (float)
    """
    fin = open(ccsds_in,"rb")
    outbyte = []
    pkt_ctr = 0
    bad_packet = 0
    while 1:
        packet = bytearray(fin.read(453)) # Read in a full packet at a time
        if len(packet) < 453:			  # if 453 bytes not read, end of file
            fin.close()
            break
        abin = bin(int(packet[22:24].hex(), 16))
        apid = int(abin[-11:], 2)
        gpstime = int.from_bytes(packet[48:52], 'big')
        if apid == 674 and gpstime > 1362875400:
            outbyte.append(packet)
            pkt_ctr += 1
        else:
            bad_packet += 1
            print('Anomalous packet')
    # 
    print('STP-H9 H&S File: ', ccsds_in)
    print('STP-H9 H&S File Contents: ', pkt_ctr, ' packets')
    print('                 skipped: ', bad_packet, ' bad packets\n')
    # 
    return outbyte
    
# 
# def main():
    ### Debug test for decrypt
    # dfile = 'C:/data/ECLIPSE/gnd/06-H9_integration/221128-H9_KSC/IssCcsds.1729_2022-11-28_10~29~19'
    # decrypt_eclipse_hrt_from_ccsds(dfile)
    # 
    ### Debug test for CCSDS loader
    # ccsds_file_in = 'C:/data/ECLIPSE/gnd/08-H9_TVAC/220909-TVAC/IssCcsds.1729_2022-09-09_22_54_13.out'
    # ccsds_byte = load_eclipse_bytes_from_ccsds(ccsds_file_in)
    # 
    ### Debug test for ISS CCSDS loader
    # iss_file_in = 'C:/data/STPH9/flt/2312/NRL_674f6_2023361'
    # iss_byte = load_iss_hs_bytes_from_ccsds(iss_file_in)
    
# if __name__ == "__main__":
#     print(f"==== {__file__} ====")
#     main()