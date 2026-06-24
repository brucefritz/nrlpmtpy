#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: ECLIPSE_H9_ccsds.py
Author: Bruce A. Fritz, NRL Code 7634
Date:   2024-01-10, 0.0 Created
        2024-12-17, 1.0 Updated Header for git upload
        2026-06-24, 1.1 Moved decryption to separate file
Version: 1.1
Description: Set of functions that will load an ISS telemetry STP-H9 ECLIPSE 
    CCSDS file and load the bytes into appropriately sized frames for processing
Functions:
    1) load_eclipse_bytes_from_ccsds(ccsds_in) --> reads in *decrypted* CCSDS
            packets and extracts HRT data
            Inputs: decrypted CCSDS file, e.g. "NRL_1729_2023249.out"
            Output: Python list of byte-frames containing ECLIPSE data

    2) load_iss_hs_bytes_from_ccsds(ccsds_in) --> reads in *decrypted* CCSDS
            packets and extracts HS data
            Inputs: decrypted CCSDS file, e.g. "NRL_1729_2023249.out"
            Output: Python list of byte-frames containing ISS H&S data

"""
def load_eclipse_bytes_from_ccsds(ccsds_in) -> list[bytes]:
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
      6   [0:7] -- Fine Time (1/256 resolution)
      6  [8:15] -- Time ID, etc.
      7   [1:4] -- STP-H9 Element ID
      7  [5:15] -- STP-H9 Packet ID #1
      8            STP-H9 Packet ID #2
      9            Additional Fine Time Precision (1/65535 resolution, overkill)
      --- Start ECLIPSE Header info
      10 Sequence Counter ?
      11 ECLIPSE data type (0xE803 == 1000 --> ECLIPSE HRT)
      12 ECLIPSE packet length (0xF604 == 1270d packets)
      13 GPS Time, Big end
      14 GPS Time, Little end
    """
    outbyte = []
    outtime = []
    gpstime = []
    pkt = 0
    with open(ccsds_in, "rb") as fin:
        while 1:
            x = bytearray(fin.read(1300))	# read in full CCSDS packet assuming it starts at first byte
            if len(x) < 1300:				# if 1300 bytes not read, end of file
                break
            apid = int.from_bytes(x[0:2], 'big') & 0x07FF
            ecid = x[20:22].hex()

            if apid == 1729 and ecid == 'e803':
                finetime = x[10] / 256.
                pkt_len = int.from_bytes(x[22:24], 'little') # def. 0xf604-->1270
                outbyte.append(x[28:(28 + pkt_len)])	# extract the eclipse data
                outtime.append(int.from_bytes(x[6:10], 'big') + finetime)
                gpstime.append(int.from_bytes(x[24:28], 'little'))
                pkt += 1
            else:
                print('Anomalous packet')
    print('CCSDS File: ', ccsds_in)
    print('CCSDS File Contents: ', pkt, ' HRT packets')
    return b''.join(bytes(b) for b in outbyte), outtime, gpstime
#
def load_iss_hs_bytes_from_ccsds(ccsds_in) -> list[bytearray]:
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
    outbyte = []
    gps_list = []
    pkt_ctr = 0
    bad_packet = 0
    with open(ccsds_in, "rb") as fin:
        while 1:
            packet = bytearray(fin.read(453)) # Read in a full packet at a time
            if len(packet) < 453:			  # if 453 bytes not read, end of file
                break
            try:
                apid = int.from_bytes(packet[22:24], 'big') & 0x07FF
                gpstime = int.from_bytes(packet[48:52], 'big')
                if apid == 674 and gpstime > 1362875400:
                    outbyte.append(packet)
                    gps_list.append(gpstime)
                    pkt_ctr += 1
                else:
                    bad_packet += 1
                    print('Anomalous packet')
            except ValueError:
                bad_packet += 1
                print('Bad Packet Value')
    #
    print('STP-H9 H&S File: ', ccsds_in)
    print('STP-H9 H&S File Contents: ', pkt_ctr, ' packets')
    print('                 skipped: ', bad_packet, ' bad packets\n')
    #
    return outbyte, gps_list