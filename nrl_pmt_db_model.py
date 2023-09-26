# -*- coding: utf-8 -*-
"""
Classes for connecting to and loading data into an sqlite3 database

Initial tutorial from:
    https://www.sqlitetutorial.net/sqlite-python/creating-database/

Class Tutorial Video shown here:
    
    https://www.youtube.com/watch?v=LFG2Kx1m-Dc

@author: bfritz
"""
import sqlite3

class pmt_database:
    def __init__(self, dbname):
        """:param db_file: database file
        :return: Connection object or None
        """
        self.con = None
        try:
            self.con = sqlite3.connect(dbname)
            print(f'Running SQLite3 Version {sqlite3.version}')
            print(f'Connecting to ... {dbname} ...')
        except sqlite3.Error as e:
            print(e)
        self.cur = self.con.cursor()
        # self.create_muv_table()
        
    def create_muv_table(self):
        self.cur.execute("""DROP TABLE muv_pmt_frame""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS muv_pmt_frame(
            gpstime LONG PRIMARY KEY, julday REAL,
            ch1 LONG, ch2 INT, ch3 INT,
            hv REAL, sun REAL, mode TEXT, IDC_ERROR TEXT,
            t_lens REAL, t_pmt REAL, t_hv REAL, t_idc REAL,
            ch1_event INT, ch2_event INT, ch3_event INT, hv_event INT, sun_event INT,
            sg_geolat REAL, sg_geolon REAL, sg_altitude REAL,
            geolat REAL, geolon REAL, altitude REAL,
            maglat REAL, maglong REAL, MLT REAL,
            year INT, doy INT, hr INT, mm INT, ss INT, 
            gps_x_ecef REAL,  gps_y_ecef REAL,  gps_z_ecef REAL,
            gps_vx_ecef REAL, gps_vy_ecef REAL, gps_vz_ecef REAL,
            q1_body_eci REAL, q2_body_eci REAL, q3_body_eci REAL, q4_body_eci REAL,
            q1_ecef_eci REAL, q2_ecef_eci REAL, q3_ecef_eci REAL, q4_ecef_eci REAL,
            sln_x_eci REAL,   sln_y_eci REAL,   sln_z_eci REAL,
            sln_vx_eci REAL,  sln_vy_eci REAL,  sln_vz_eci REAL,
            sln_x_ecef REAL,  sln_y_ecef REAL,  sln_z ecef REAL,
            sln_vx_ecef REAL, sln_vy_ecef REAL, sln_vz ecef REAL,
            sln_nadir_x_body REAL, sln_nadir_y_body REAL, sln_nadir_z_body REAL,
            sln_sun_x_body REAL,  sln_sun_y_body REAL,  sln_sun_z_body REAL,
            sln_sun_x_eci REAL,   sln_sun_y_eci REAL,   sln_sun_z_eci REAL,
            sln_sun_model_x_eci REAL, sln_sun_model_y_eci REAL, sln_sun_model_z_eci REAL,
            sln_moon_x_body REAL, sln_moon_y_body REAL, sln_moon_z_body REAL,
            sln_moon_x_eci REAL,  sln_moon_y_eci REAL,  sln_moon_z_eci REAL,
            sln_moon_model_x_eci REAL, sln_moon_model_y_eci REAL, sln_moon_model_z_eci REAL,
            sln_mag_model_x_eci REAL,  sln_mag_model_y_eci REAL,  sln_mag_model_z_eci REAL,
            sln_mag_model_x_body REAL, sln_mag_model_y_body REAL, sln_mag_model_z_body REAL,
            ecl_look_x_eci REAL, ecl_look_y_eci REAL, ecl_look_z_eci REAL
            )""") # 88 total variables
        # 
    def create_summary_table(self):
        # self.cur.execute("""DROP TABLE muv_pmt_summary_frame""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS muv_pmt_summary_frame(
            gpstime_start LONG PRIMARY KEY, gpstime_stop LONG,
            julday_start REAL, julday_stop REAL,
            year_start INT,    year_stop INT,
            day_start INT,     day_stop INT,
            hour_start INT,    hour_stop INT,
            minute_start INT,  minute_stop INT,
            second_start INT,  second_stop INT
            )""") # 14 total variables
        # 
    def insert_sln_frame(self, ob):
        self.cur.execute("""INSERT OR IGNORE INTO muv_pmt_frame VALUES(
                         ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                         ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                         ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                         ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                         ?,?,?,?,?,?,?,?
                         )""", ob)
    
    def insert_sln_summary(self, summary):
        self.cur.execute("""INSERT OR IGNORE INTO muv_pmt_summary_frame VALUES(
                         ?,?,?,?,?,?,?,?,?,?,?,?,?,?
                         )""", summary)
    
    def commit_sln_frame(self):
        self.con.commit() 
    
    def read_all_data(self):
        self.cur.execute("""SELECT * FROM muv_pmt_frame""")
        rows = self.cur.fetchall()
        return rows
    
    def read_all_summary(self):
        self.cur.execute("""SELECT * FROM muv_pmt_summary_frame""")
        rows = self.cur.fetchall()
        return rows
    
    """
    Next function to write is to SELECT statement for specific values of GPS
    time in the database
    """
    
    def close(self,dbname):
        self.con.close()
        print(f'\n  Closing database ... {dbname}')
    
    

"""
# Legacy for template
"""
class observation:
    def __init__(self, dbname):
        self.con = sqlite3.connect(dbname)
        self.cur = self.con.cursor()
        self.create_table()
        
    def create_table(self):
        # self.cur.execute("""DROP TABLE observation""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS observation(
            met LONG PRIMARY KEY,
            uv INT,
            red INT,
            dark INT,
            hv REAL,
            date DATE
            )""")
        
    def insert(self, ob):
        self.cur.execute("""INSERT OR IGNORE INTO observation
                         VALUES(?,?,?,?,?,?)""", ob)
        self.con.commit() # Move to a different function in the class to commite after inserting
    
    def read(self):
        self.cur.execute("""SELECT * FROM observation""")
        rows = self.cur.fetchall()
        return rows
    
    