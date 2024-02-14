# -*- coding: utf-8 -*-
"""
Script to load Slingshot L1A NetCDF (.nc) files into a database

@author: bfritz
"""
import netCDF4
import glob
import numpy as np
from nrl_pmt_db_model import pmt_database
from astropy.time import Time
# from datetime import datetime

def summarize_nc(df,db):
    """
    Create tuple and insert into PMT Summary Table
    :param df: Dataframe (list of tuples) from Slingshot L1A file
    :param db: Pointer to database
    :return: n/a
    """
    print('  Summmarizing data')
    summary_tuple = (
        df[0][0], df[-1][0], # gpstime_start LONG PRIMARY KEY, gpstime_stop LONG,
        df[0][1], df[-1][1], # julday_start REAL, julday_stop REAL,
        
        df[0][27], df[-1][27], # year_start INT,    year_stop INT,
        df[0][28], df[-1][28], # day_start INT,     day_stop INT,
        df[0][29], df[-1][29], # hour_start INT,    hour_stop INT,
        df[0][30], df[-1][30], # minute_start INT,  minute_stop INT,
        df[0][31], df[-1][31], # second_start INT,  second_stop INT
        )
    db.insert_sln_summary(summary_tuple)
    return

def load_unmask_nc(ncfile, db):
    f = netCDF4.Dataset(ncfile)
    print(f'  Loading ... {ncfile}')
    # num_keys = len(f.variables.keys())
    # print(f'  Number of record keys = {num_keys}')
    # v01 = np.array(f['GPS_sec']) ### Currently empty field!!!
    v02 = np.array(f['JULDAY'])
    v03 = np.array(f['Mg_Counts'])
    v04 = np.array(f['VK_Counts'])
    v05 = np.array(f['Dark_Counts'])
    v06 = np.array(f['HV'])
    v07 = np.array(f['SUN'])
    v08 = np.array(f['MODE'])
    v09 = np.array(f['IDC_ERROR'])
    v10 = np.array(f['T_LENS'])
    v11 = np.array(f['T_PMT'])
    v12 = np.array(f['T_HV'])
    v13 = np.array(f['T_PMT'])
    v14 = np.array(f['MG_EVENT'])
    v15 = np.array(f['VK_EVENT'])
    v16 = np.array(f['DK_EVENT'])
    v17 = np.array(f['HV_EVENT'])
    v18 = np.array(f['SUN_EVENT'])
    v19 = np.array(f['SG_Geolat'])
    v20 = np.array(f['SG_Geolon'])
    v21 = np.array(f['SG_Altitude'])
    v22 = np.array(f['Geolat'])
    v23 = np.array(f['Geolon'])
    v24 = np.array(f['Altitude'])
    v25 = np.array(f['Maglat'])
    v26 = np.array(f['Maglon'])
    v27 = np.array(f['MLT'])
    v28 = np.array(f['Year'])
    v29 = np.array(f['DOY'])
    v30 = np.array(f['HR'])
    v31 = np.array(f['MM'])
    v32 = np.array(f['SS'])
    v33 = np.array(f['GPS_X_ECEF'])
    v34 = np.array(f['GPS_Y_ECEF'])
    v35 = np.array(f['GPS_Z_ECEF'])
    v36 = np.array(f['GPS_VX_ECEF'])
    v37 = np.array(f['GPS_VY_ECEF'])
    v38 = np.array(f['GPS_VZ_ECEF'])
    v39 = np.array(f['Q1_BODY_ECI'])
    v40 = np.array(f['Q2_BODY_ECI'])
    v41 = np.array(f['Q3_BODY_ECI'])
    v42 = np.array(f['Q4_BODY_ECI'])
    v43 = np.array(f['Q1_ECEF_wrt_ECI'])
    v44 = np.array(f['Q2_ECEF_wrt_ECI'])
    v45 = np.array(f['Q3_ECEF_wrt_ECI'])
    v46 = np.array(f['Q4_ECEF_wrt_ECI'])
    v47 = np.array(f['SLN_X_ECI'])
    v48 = np.array(f['SLN_Y_ECI'])
    v49 = np.array(f['SLN_Z_ECI'])
    v50 = np.array(f['SLN_VX_ECI'])
    v51 = np.array(f['SLN_VY_ECI'])
    v52 = np.array(f['SLN_VZ_ECI'])
    v53 = np.array(f['SLN_X_ECEF'])
    v54 = np.array(f['SLN_Y_ECEF'])
    v55 = np.array(f['SLN_Z_ECEF'])
    v56 = np.array(f['SLN_VX_ECEF'])
    v57 = np.array(f['SLN_VY_ECEF'])
    v58 = np.array(f['SLN_VZ_ECEF'])
    v59 = np.array(f['SLN_NADIR_X_BODY'])
    v60 = np.array(f['SLN_NADIR_Y_BODY'])
    v61 = np.array(f['SLN_NADIR_Z_BODY'])
    v62 = np.array(f['SLN_SUN_X_BODY'])
    v63 = np.array(f['SLN_SUN_Y_BODY'])
    v64 = np.array(f['SLN_SUN_Z_BODY'])
    v65 = np.array(f['SLN_SUN_X_ECI'])
    v66 = np.array(f['SLN_SUN_Y_ECI'])
    v67 = np.array(f['SLN_SUN_Z_ECI'])
    v68 = np.array(f['SLN_SUN_MODEL_X_ECI'])
    v69 = np.array(f['SLN_SUN_MODEL_Y_ECI'])
    v70 = np.array(f['SLN_SUN_MODEL_Z_ECI'])
    v71 = np.array(f['SLN_MOON_X_BODY'])
    v72 = np.array(f['SLN_MOON_Y_BODY'])
    v73 = np.array(f['SLN_MOON_Z_BODY'])
    v74 = np.array(f['SLN_MOON_X_ECI'])
    v75 = np.array(f['SLN_MOON_Y_ECI'])
    v76 = np.array(f['SLN_MOON_Z_ECI'])
    v77 = np.array(f['SLN_MOON_MODEL_X_ECI'])
    v78 = np.array(f['SLN_MOON_MODEL_Y_ECI'])
    v79 = np.array(f['SLN_MOON_MODEL_Z_ECI'])
    v80 = np.array(f['SLN_MAG_MODEL_X_ECI'])
    v81 = np.array(f['SLN_MAG_MODEL_Y_ECI'])
    v82 = np.array(f['SLN_MAG_MODEL_Z_ECI'])
    v83 = np.array(f['SLN_MAG_MODEL_X_body'])
    v84 = np.array(f['SLN_MAG_MODEL_Y_body'])
    v85 = np.array(f['SLN_MAG_MODEL_Z_body'])
    v86 = np.array(f['ECL_LOOK_X_ECI'])
    v87 = np.array(f['ECL_LOOK_Y_ECI'])
    v88 = np.array(f['ECL_LOOK_Z_ECI'])
    
    f.close()
    
    output = []
    
    for i,val in enumerate(v88):
        t_jd = Time(v02[i], format='jd')
        gps_int = round(float(str(Time(t_jd, format='gps'))))
        
        temp_tuple = (
            gps_int, v02[i], int(v03[i]),  int(v04[i]),  int(v05[i]), # Counts
            float(v06[i]),float(v07[i]),str(v08[i]),  str(v09[i]),
            float(v10[i]),float(v11[i]),float(v12[i]),float(v13[i]),
            int(v14[i]),  int(v15[i]),  int(v16[i]),  int(v17[i]),int(v18[i]),
            float(v19[i]),float(v20[i]),float(v21[i]),
            float(v22[i]),float(v23[i]),float(v24[i]),
            float(v25[i]),float(v26[i]),float(v27[i]),
            int(v28[i]),  int(v29[i]),  int(v30[i]),  int(v31[i]),int(v32[i]),
            float(v33[i]),float(v34[i]),float(v35[i]),
            float(v36[i]),float(v37[i]),float(v38[i]),
            float(v39[i]),float(v40[i]),float(v41[i]),float(v42[i]),
            float(v43[i]),float(v44[i]),float(v45[i]),float(v46[i]),
            float(v47[i]),float(v48[i]),float(v49[i]),
            float(v50[i]),float(v51[i]),float(v52[i]),
            float(v53[i]),float(v54[i]),float(v55[i]),
            float(v56[i]),float(v57[i]),float(v58[i]),
            float(v59[i]),float(v60[i]),float(v61[i]),
            float(v62[i]),float(v63[i]),float(v64[i]),
            float(v65[i]),float(v66[i]),float(v67[i]),
            float(v68[i]),float(v69[i]),float(v70[i]),
            float(v71[i]),float(v72[i]),float(v73[i]),
            float(v74[i]),float(v75[i]),float(v76[i]),
            float(v77[i]),float(v78[i]),float(v79[i]),
            float(v80[i]),float(v81[i]),float(v82[i]),
            float(v83[i]),float(v84[i]),float(v85[i]),
            float(v86[i]),float(v87[i]),float(v88[i]))
        # 
        output.append(temp_tuple)
        db.insert_sln_frame(temp_tuple)
    # 
    return output

def main():
    database_name = r"C:\data\SLINGSHOT\flt\l1A\SLN_ECLIPSE_RR_L1A.db"
    """
    Step 1 Connect to Database
    """
    db = pmt_database(database_name)
    pmt_database.create_muv_table(db)
    pmt_database.create_summary_table(db)
    """
    Step 2 Read File List
    """
    sln_L1A_dir = 'C:\\data\\SLINGSHOT\\flt\\L1A\\2308\\*.nc'
    file_list = glob.glob(sln_L1A_dir)
    """
    Step 3 Load data from file (function) and insert into table
    """
    for i,fname in enumerate(file_list):
        data_list = load_unmask_nc(fname,db)
        summarize_nc(data_list,db)
    
    # print(data_list[0])
    #     
    # 4 Insert data into the database (((moved to inside load_unmask_nc)))
    # db.insert_sln_frame(data_list)
    # 
    """
    Step 4 Commit data that has been inserted into the table
    """
    db.commit_sln_frame()
    # 5 Read back
    # for ob in db.read_all_data():
    #     print(ob)
    for smry in db.read_all_summary():
        print(smry)
    # df = db.read_all_data()
    # print(df[1])
    # 
    db.close(database_name)
    # 
    # 
if __name__ == '__main__':
    main()
