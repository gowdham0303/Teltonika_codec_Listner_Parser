import traceback
import mysql.connector
from datetime import datetime
import json



class Database:
    def __init__(self, config):

        self.mydb = mysql.connector.connect(
            host= config['host'],
            user= config['username'],
            password= config['password'],
            database=  config['database'],
            auth_plugin='mysql_native_password'
            )

    def fetch_imei(self):
        self.conn= self.mydb.cursor()
        sql= "SELECT * FROM IMEI"
        self.conn.execute(sql)
        result= self.conn.fetchall()
        imei_list=[]
        for row in result:
            imei_list.append(row[1])
        return tuple(imei_list)

    def to_database(self, value: dict):
        try:
            self.conn= self.mydb.cursor()
            imei= value['imei']
            value_list=[]
            for data in value['data']:
                timestamp= datetime.utcfromtimestamp(data['timestamp']/1000.0).isoformat()
                latitude= data['latitude']/10000000
                longitude= data['longitude']/10000000
                altitude= data['altitude']
                speed= data['speed']
                priority= data['priority']
                avldata= json.dumps(data['avl_data'])
                value_list.append((imei, timestamp, latitude, longitude, altitude, speed, avldata, priority)) 

            sql= "INSERT INTO locationInfo (imei, time_stamp, latitude, longitude, altitude, speed, avlData, priority) VALUES (%s, %s ,%s, %s, %s, %s, %s, %s)"
            
            self.conn.executemany(sql, value_list)
            self.mydb.commit()

        except:
            print(data['altitude'])
            traceback.print_exc()