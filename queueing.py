import threading
import json
import redis
from database import Database
import configparser

config= configparser.ConfigParser()
config.read('config.ini')


class ParsedData(threading.Thread):
    def __init__(self, data:dict or list):
        threading.Thread.__init__(self)
        self.r_cli = redis.Redis(host='localhost', port=6379, db=0)
        self.channels = 'ParsedData'
        self.gps_data= data

    def run(self):
        self.r_cli.rpush(self.channels, json.dumps(self.gps_data))


class RawData(threading.Thread):
    def __init__(self, data:bytes):
        threading.Thread.__init__(self)
        self.r_cli = redis.Redis(host='localhost', port=6379, db=1)
        self.channels = 'RawData'
        self.raw_data= data
    
    def run(self):
        self.r_cli.rpush(self.channels, self.raw_data)

class RedisListner(threading.Thread):
    def __init__(self, channel:str, num_listner:int):
        threading.Thread.__init__(self)        
        self.identifier = num_listner
        self.channels = channel
        
        if self.channels=='ParsedData':
            self.r_db= 0
        elif self.channels=='RawData':
            self.r_db= 1
        else:
            raise ValueError("Incorrect Channel name")

        self.r_cli = redis.Redis(host='localhost', port=6379, db=self.r_db)

    def run(self):
        print(f"Started listener {self.identifier} at channel: {self.channels}")
        if self.channels=="ParsedData":
            while True:
                item= self.r_cli.blpop(self.channels, 0)[1]
                item= item.decode('utf-8') 
                if item == "KILL":
                    break
                else:
                    database= Database(config= config['database'])
                    database.to_database(eval(item))

        elif self.channels=='RawData':
            from decoder import Decoder
            while True:
                item= self.r_cli.blpop(self.channels, 0)[1]
                if item == "KILL":
                    break
                else:
                    Decoder(payload=item).start()
        print(f"{self} {self.identifier} unsubscribed and finished")

