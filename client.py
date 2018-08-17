import socket
import struct
import sys

class DT_Request(object):
    """Creates an instance of a DT_Request packet"""
    def __init__(self, magic_no, packet_type, request_type):
        """initializes the bytes"""
        self.Magic_No = magic_no
        self.Packet_Type = packet_type
        self.Request_Type = request_type
        self.Packet = None
        self.valid_packet = False
        
        self.check()
        self.encode()
        
    def check(self):
        """checks if the packet is valid"""
        if self.Magic_No == 0x497E and self.Packet_Type == 0x0001 and (self.Request_Type == 0x0001 or self.Request_Type == 0x0002):
            self.valid_packet = True
            return self.valid_packet
        else:
            raise Exception("Invalid packet")
            
    def encode(self):
        """packs all the bytes into a single packet"""
        if self.valid_packet == True:
            self.Packet = struct.pack(">hhh", self.Magic_No, self.Packet_Type, self.Request_Type)
            return self.Packet
        else:
            return False # discard the packet without further action'
        
def get_response(packet):
    """gets data from the packet"""
    header, body = packet[:13], packet[14:]
    text = body.rstrip(b'\x00').decode("utf_8")
    
    magic_no, packet_type, language_code, year, month, day, hour, minute, length = struct.unpack(">hhhhbbbbb", header)
    return magic_no, packet_type, language_code, year, month, day, hour, minute, length, text    

def print_results(magic_no, packet_type, language_code, year, month, day, hour, minute, length, text):
    print()
    print("--------[Packet Information]--------")
    print("Magic Number:", magic_no)
    print("Packet Type:", packet_type)
    print("Language Code:", language_code)
    print("------------------------------------")
    print()
    print("-----------[Current Time]-----------")
    print("Year:", year)
    print("Month:", month)
    print("Day:", day)
    print("Hour", hour)
    print("Minute:", minute)
    print("------------------------------------")
    print()
    print("-------------[Message]--------------")
    print("Length:", length)
    print("Text:", text)    
    print("------------------------------------")
    print()
    

def main():
    # might need to restructure main into try catch format?
    running_flag = True
    dateTime = sys.argv[1]
    UDP_IP = sys.argv[2]
    UDP_PORT = int(sys.argv[3])
    
    # checking for valid hostname (need to fix!)
    try:
        socket.inet_aton(UDP_IP)
    except socket.error:
        info_list = socket.getaddrinfo(UDP_IP, 'www')
        UDP_IP = info_list[0][4][0]
        try:
            socket.inet_aton(UDP_IP)
        except (socket.error, socket.gaierror):
            print("Invalid Host name address, quiting...")
            sleep(5)
            quit()
            
    ## https://docs.python.org/3/library/socket.html#socket.SOCK_DGRAM
    sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # opens a UDP socket
    
    while running_flag: 
        if dateTime == "date" or dateTime == "time":
            if dateTime == "date":
                request_type = 0x0001
            elif dateTime == "time":
                request_type = 0x0002
            # need some processing here?
            
            if UDP_PORT >= 1024 and UDP_PORT <= 64000:
                # valid request
                print("Valid request...")
                
                packet = DT_Request(0x497E, 0x0001, request_type) # prepares DT-Request
                REQUEST = packet.Packet # returns the bytearray of the packet
                #print(REQUEST)                
                
                #sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # opens a UDP socket
                sock_out.sendto(REQUEST, (UDP_IP, UDP_PORT))
                
                sock_out.settimeout(1) # wait for 1 second for a response packet.
                try:
                    data, addr = sock_out.recvfrom(1024)
                    print("Received from server:", data)
                    magic_no, packet_type, language_code, year, month, day, hour, minute, length, text = get_response(data)
                    
                    print_results(magic_no, packet_type, language_code, year, month, day, hour, minute, length, text)
                    
                except socket.timeout:
                    print("Waited too long...")
                    
                running_flag = False
            else:
                print("Invalid port...")
                running_flag = False
        else:
            print("Error, closing...")
            running_flag = False
            
        print("Transmission terminated...")
        sock_out.close()

    
if __name__ == "__main__":
    main()        

