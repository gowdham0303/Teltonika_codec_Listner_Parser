from datetime import datetime
from queueing import ParsedData
import threading


class Decoder(threading.Thread):
    def __init__(self, payload) -> None:
        threading.Thread.__init__(self)
        self.payload= payload
        self.imei= payload[:15].decode("utf-8")
        self.init= 15 # IMEI digits count

        #Bytes count for each data
        self.zero_bytes= 4
        self.data_field_length= 4
        self.codec_id= 1
        self.number_of_data_1= 1
        self.time_stamp= 8
        self.priority= 1
        self.longitude= 4
        self.latitude= 4
        self.altitude= 2
        self.angle= 2
        self.satellite= 1
        self.speed= 2
        self.event_io_id= 2
        self.number_of_io= 2
        self.io_id= 2
        self.n_byte= 2
        self.values_bytes=[1, 2, 4, 8]
        self.nx= 2
        self.crc= 4
        self.number_of_data_2= 1

    def run(self):
        # Should not change the flow of parsing
        self.values_zero_bytes= self.extract(self.zero_bytes)
        self.values_data_field_length= self.extract(self.data_field_length)
        self.values_codec_id= self.extract(self.codec_id)
        self.values_number_of_data_1= self.extract(self.number_of_data_1)
        self.gps_data= []
        self.complete_data={
            'imei':self.imei,
            'number_of_data':self.values_number_of_data_1,
        }
        
        self.avl_list=[]
        self.updatecomplete_data={}
        self.values_avl_data= {}

        def parse_io(byte):
            values_total= self.extract(self.n_byte)
            if values_total:
                for _ in range(values_total):
                    id= self.extract(self.io_id)
                    value= self.extract(byte)
                    self.values_avl_data.update({str(id):value})
        
        for _ in range(self.values_number_of_data_1):
            self.values_time_stamp= self.extract(self.time_stamp)
            self.values_priority= self.extract(self.priority)
            self.values_longitude= self.extract(self.longitude)
            self.values_latitude= self.extract(self.latitude)
            self.values_altitude= self.extract(self.altitude)
            self.values_angle= self.extract(self.angle)
            self.values_satellite= self.extract(self.satellite)
            self.values_speed= self.extract(self.speed)
            self.values_event_io_id= self.extract(self.event_io_id)
            self.values_number_of_io= self.extract(self.number_of_io)

            self.updatecomplete_data={
                'timestamp': self.values_time_stamp,
                'priority': self.values_priority,
                'longitude': self.values_longitude,
                'latitude': self.values_latitude,
                'altitude': self.values_altitude,
                'angle': self.values_angle,
                'satellite': self.values_satellite,
                'speed': self.values_speed,
                'event_io_id': self.values_event_io_id,
                'number_of_io': self.values_number_of_io
            }
            for byte in self.values_bytes:
                parse_io(byte)

            self.values_total_nx= self.extract(self.nx)


            self.updatecomplete_data.update({'avl_data':self.values_avl_data})
            self.gps_data.append(self.updatecomplete_data)
            self.complete_data.update({'data':self.gps_data})

            self.values_avl_data={}
            self.updatecomplete_data=[]

        #send the parsed data to the Queue
        ParsedData(data= self.complete_data).start()
    
    def extract(self, length):
        length= length*2
        result = self.payload[ self.init : (self.init + length) ]
        self.init += length
        if result!=b'': result= int(result,16)
        return result
