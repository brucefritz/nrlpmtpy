# -*- coding: utf-8 -*-
"""
ECLIPSE_iib_converter
    Class:
        iib_records()
    
    Function:
        eclipse_iib_converter()
        Takes input as n-length list of [n x MET, n x bytearray(IIB data)]

@author: bfritz
"""
class iib_records():
    def __init__(self):
        self.MET = []
        self.I_mip12V = []
        self.I_mip3V = []
        self.V_mip12V = []
        self.V_mip3V = []
        self.I_tsm5V = []
        self.I_tsm3V = []
        self.V_tsm5V = []
        self.V_tsm3V = []
        self.V_tsm28V = []
        self.I_tip12V = []
        self.V_tip12V = []
        self.I_tip3V = []
        self.V_tip3V = []
        self.I_msm5V = []
        self.I_msm3V = []
        self.V_msm28V = []
        self.V_msm3V = []
        self.V_msm5V = []
    def __str__(self):
        a1 = "Number of IIB Records: "
        a2 = f"Time: {len(self.MET)}"
        x1 = f"Tri-MIP: I_12V = {len(self.I_mip12V)}, I_3.3V = {len(self.I_mip3V)}"
        x3 = f"Tri-TIP: I_12V = {len(self.I_tip12V)}, I_3.3V = {len(self.I_tip3V)}"
        s2 = f"Tri-MIP SUVM: I_5V = {len(self.I_msm5V)}, I_3.3V = {len(self.I_msm3V)}"
        s4 = f"Tri-TIP SUVM: I_5V = {len(self.I_tsm5V)}, I_3.3V = {len(self.I_tsm3V)}"
        return f'{a1}\n{a2}\n\n{x1}\n{x3}\n\n{s2}\n{s4}\n'
    # 
def eclipse_iib_converter(din):
    # ALS (unit = 1) CTS (unit = 2)
    out = iib_records()
    for x in din:
        if len(din) == 0:
            break
        if len(x[1]) < 64:
            break
        if float(x[0]) - float(din[0][0]) > 1000000:
            break # Identify anomalous time tags at end of files
        rec = []
        for i in range(0,len(x[1]),2):   # Convert bytes to floats
            val = float(int.from_bytes(bytearray(x[1][i:i+2]),'little'))
            val = val / 4095. * 5.
            rec.append(val)
        # 
        out.MET.append(x[0])
        out.I_mip12V.append(0.1  * rec[0])
        out.I_mip3V.append( 0.1  * rec[1])
        out.V_mip12V.append(2.47 * rec[2])
        out.V_mip3V.append( 1.0  * rec[3])
        out.I_tsm5V.append( 0.1  * rec[16])
        out.I_tsm3V.append( 0.1  * rec[17])
        out.V_tsm5V.append(2.47  * rec[18])
        out.V_tsm3V.append( 1.0  * rec[19])
        out.V_tsm28V.append(7.67 * rec[21])
        out.I_tip12V.append(0.1  * rec[22])
        out.V_tip12V.append(2.47 * rec[23])
        out.I_tip3V.append( 0.1  * rec[24])
        out.V_tip3V.append( 1.0  * rec[25])
        out.I_msm5V.append( 0.1  * rec[26])
        out.I_msm3V.append( 0.1  * rec[27])
        out.V_msm28V.append(7.67 * rec[28])
        out.V_msm3V.append( 1.0  * rec[30])
        out.V_msm5V.append(2.47  * rec[31])
    # 
    return out

