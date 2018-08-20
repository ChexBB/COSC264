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
    """gets data from the packet and checks if it is a valid response packet"""
    header, body = packet[:13], packet[13:]
    text = body.decode("utf_8")
    #print(header)
    #print(body)
    
    magic_no, packet_type, language_code, year, month, day, hour, minute, length = struct.unpack(">hhhhbbbbb", header)
    length_of_header = len(header)
    length_of_packet = length_of_header + length
    
    valid = check_response(length_of_header, length_of_packet, magic_no, packet_type, language_code, year, month, day, hour, minute, length)
    if valid:
        return magic_no, packet_type, language_code, year, month, day, hour, minute, length, text  
    else:
        print("Invalid packet...Terminating...")
        sys.exit()

def check_response(length_of_header, length_of_packet, magic_no, packet_type, language_code, year, month, day, hour, minute, length):
    """ checking validity of header response packet. called in get response when 
    unpacking response from server"""
    while True:
        if length_of_header < 13: # need to check, at least 13? or should be 13 exact
            break
        if magic_no != 0x497E:
            break
        if packet_type != 0x0002: # processes only DT_Response packets
            break
        if language_code != 0x0001 and language_code != 0x0002 and language_code != 0x0003:
            break
        if year > 2100:
            break
        if month < 1 and month > 12:
            break
        if day < 1 and day > 31:
            break
        if hour < 0 and hour > 23:
            break
        if minute < 0 and minute > 59:
            break
        if length_of_packet != (13 + length):  
            break
        else:
            return True # passes all checks!
    return False
    
def print_results(magic_no, packet_type, language_code, year, month, day, hour, minute, length, text):
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
    dateTime = sys.argv[1]
    UDP_IP = sys.argv[2]
    UDP_PORT = sys.argv[3]

    # checking for valid date or time request
    if dateTime != "date" and dateTime != "time":
        print("Must enter either 'date' or 'time'!")
        sys.exit()
    
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
            sys.exit()

    # checks that port is an integer
    try:
        UDP_PORT = int(UDP_PORT)
    except:
        print("Port must be an integer!")
        sys.exit()

    if UDP_PORT < 1024 or UDP_PORT > 64000:
        print("Port is out of range!")
        sys.exit()

    if dateTime == "date":
        request_type = 0x0001
    elif dateTime == "time":
        request_type = 0x0002

    ## https://docs.python.org/3/library/socket.html#socket.SOCK_DGRAM
    sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # opens a UDP socket
    sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # sock_out.bind((UDP_IP, UDP_PORT))

    running = True
    while running:
        packet = DT_Request(0x497E, 0x0001, request_type)  # prepares DT-Request packet
        REQUEST = packet.Packet  # returns the byte array of the packet
        try:
            sock_out.sendto(REQUEST, (UDP_IP, UDP_PORT))
            print("Request sent...\n")
        except:  # need to be more specific with socket errors?
            print("Error sending request to server...")
            break

        sock_out.settimeout(1) # wait for 1 second for a response packet.
        try:
            data, addr = sock_out.recvfrom(1024)
            # print("Received from server:", data)
            # response is unpacked and validated in get_response
            magic_no, packet_type, language_code, year, month, day, hour, minute, length, text = get_response(data)
            print_results(magic_no, packet_type, language_code, year, month, day, hour, minute, length, text)
            running = False  # prints then exits

        except socket.timeout:
            print("Timeout error...\n")
            running = False
            
    print("Transmission terminated...\n")
    sock_out.close()
    sys.exit()
    
if __name__ == "__main__":
    main()        

