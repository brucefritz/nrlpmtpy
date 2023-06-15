"""
ECLIPSE GSE data parser, extracts instrument data from ECLIPSE HRT packets

Contents:
    output = load_hrt_bytes_from_gse(gse_in)
        "gse_in" is the .hrt file produced by ECLIPSE GSE
        
        output is a list of data bytes 
    
@author: bfritz
"""
# 
def load_hrt_bytes_from_gse(gse_in):
    """
    # This program reads in eclipse hrt packets and extracts data
    # HRT packets contain 644 words total --> 1288 bytes
    #           8 word header       16 bytes
    #               1 sync
    #               2 sync
    #               3 Data type (0x87) + ID (0x01)
    #               4 Packet counter
    #               5 Data type (0xe803 == 1000 --> ECLIPSE)
    #               6 Data lengh (0xf604 == 1270 bytes)
    #               7 Time upper half
    #               8 Time lower half
    #           635 words of data   1270 bytes
    #           1 word CRC          2 bytes
    ####
    # *** Note, the output flattens "outbyte" from a list of lists to a single list
    """
    fin = open(gse_in,"rb")		# open input file
    outbyte = []
    pkt = 0
    while 1:
        x = bytearray(fin.read(1288))	
        if len(x) < 1288:				# if 1300 bytes not read, end of file
            fin.close()
            break
        if x[0:6].hex() == "1acffc1d8701":
            outbyte.append(x[16:1286])	# extract the eclipse data
        # print(x[0:6].hex()) --> Shows 4 sync bytes, hrt byte, ID byte
        pkt += 1
    print('GSE File: ', gse_in)
    print('GSE File Contents: ', pkt, ' HRT packets\n')
    return [item for subset in outbyte for item in subset]
    # 
