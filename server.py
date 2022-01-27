import socket
from threading import Thread
from time import strftime, gmtime
import struct
import binascii
from database import Database
from queueing import RawData, RedisListner
import configparser

config= configparser.ConfigParser()
config.read('config.ini')

database= Database(config= config['database'])
imei_list= database.fetch_imei()

# Start the redis Queue listners
for i in range(int(config['redis']['listners'])):
    RedisListner(channel="ParsedData", num_listner= i).start()
    RedisListner(channel="RawData", num_listner= i).start()

class ClientThread(Thread):
    def __init__(self, _socket) -> None:
        Thread.__init__(self)
        self.conn = _socket[0]
        self.addr = _socket[1]
        self.identifier = "None"
        self.logTime = strftime('%d %b %H:%M:%S', gmtime())
        self.step = 1
        self.imei = "unknown"

    def log(self, msg):
        print(f"{self.logTime}\t{self.identifier}\t{msg}")
        pass

    def extract_datalength(self, payload):
        result = payload[18:20] #Number of data 1 position
        if result!=b'': result= int(result,16)
        return result

    def run(self):
        client = self.conn
        if client:
            self.identifier = self.addr[0]
            for _ in range(2):
                try:
                    buff = self.conn.recv(8192)
                    received = binascii.hexlify(buff)
                    if len(received) > 2:
                        if self.step == 1:
                            self.step = 2
                            self.imei = (received[1::2][-15:])

                            if self.imei.decode('utf-8') in imei_list:
                                self.log("Device Authenticated | IMEI: {}".format(self.imei))
                                self.conn.send('\x01'.encode('utf-8'))
                            else:
                                self.conn.send('\x00'.encode('utf-8'))
                                break

                        elif self.step == 2:
                            len_records= self.extract_datalength(received) #For queue
                            received= self.imei+received

                            if len_records == 0:
                                self.conn.send('\x00'.encode('utf-8'))
                                self.conn.close()
                            else:
                                self.conn.send(struct.pack("!L", len_records))
                                RawData(data=received).start()
                                # a= '\x00\x00\x00\x00\x00\x00\x00\x0D\x0C\x01\x05\x00\x00\x00\x05676574696F\x01\x00\x00\x00\xCB'
                                # self.conn.send(a.encode('utf-8'))
                                # buff1 = self.conn.recv(1024)
                                # received1 = binascii.hexlify(buff1)
                                self.conn.close()
                            
                    else:
                        self.conn.send('\x00'.encode('utf-8'))
                except socket.error as err:
                    print(f"[+] Socket Error: {err}")
        else:
            self.log('Socket is null')


if __name__ == "__main__":
    print(f"VTS SERVER. {strftime('%d %b %H:%M:%S', gmtime())}")
    print(f"Server Started at port: {config['server']['port']}")
    server = None
    print()
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as e:
        print("[+] Socket Creation Error: {}".format(e))
        exit(0)

    try:
        server.bind((config['server']['host'], int(config['server']['port'])))
    except socket.error as e:
        print("[+] Socket Binding Error: {}".format(e))
        exit(0)

    try:
        server.listen(5)
    except socket.error as e:
        print("[+] Socket Listening Error: {}".format(e))
        exit(0)
    while True:
        ClientThread(server.accept()).start()

