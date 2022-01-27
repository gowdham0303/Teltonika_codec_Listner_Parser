from binascii import hexlify
import binascii
import struct


class Commands():
    def __init__(self):
        self.zero_byte= 4
        self.datasize= 4
        self.codec_id= 1
        self.command_qty_1= 1
        self.type= 1
        self.command_size= 4
        self.command_qty_2= 1
        self.crc= 4

        self.command_hex= ''

    def to_hexadecimal(self):
        pass

    def to_bytearray(self):
        pass

    def string_to_hex(self, command_string:str):
        # self.command_hex+= ("".join("{:02x}".format(ord(c)) for c in command_string))
        # print(self.command_hex)
        # self.command_hex+= "0x0A0D"
        # print(self.command_hex)

        # s= command_string.encode('utf-8')
        # self.command_hex+= binascii.hexlify(s)
        # self.command_hex+= bytes.hex(s)
        # print(s)
        # print(self.command_hex)
        for c in range(0, len(command_string) ):
            self.command_hex+= '\\'+"x%x"%ord(command_string[c])
        print(self.command_hex)


    def int_to_hex(self, value, number_of_byte):
        return 2*hex(value)[2:]  #To remove the "0x"

    def command_generation(self):
        self.string_to_hex("getstatus")
        zero_byte= struct.pack("!L", 0)
        codec_id= struct.pack("!B",12)
        types= struct.pack("!B",5)
        command_qty= struct.pack("!B",1)
        command= self.command_hex
        print(self.command_hex.encode('utf-8').decode('unicode_escape').encode("raw_unicode_escape"))
        print(binascii.a2b_hex(""))
        print(1)
        print(type(command))
        print(command_qty, type(command_qty))
        command_size= struct.pack("!L", int(len(command)/2))

        data_size= struct.pack("!L", int(len(codec_id + command_qty + types +  command_size + command + command_qty)/2))
        command_hex= zero_byte + data_size + codec_id + command_qty + types +  command_size + command + command_qty
        return command_hex

a= Commands()
print(a.command_generation())