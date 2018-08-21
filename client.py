import socket
import struct
import sys

class DT_Request(object):
    """Creates an instance of a DT_Request packet"""
    def __init__(self, magic_no, packet_type, request_type):
        """initialize"""
        self.magic_no = magic_no
        self.packet_type = packet_type
        self.request_type = request_type
        self.packet = None
        self.check()  # check and then encode if valid
        self.encode()
        
    def check(self):
        """checks if the packet is valid"""
        if self.magic_no == 0x497E and self.packet_type == 0x0001 and (self.request_type == 0x0001 or self.request_type == 0x0002):
            return True
        else:
            print("Invalid packet...Terminating...\n")
            sys.exit()
            
    def encode(self):
        """packs all the bytes into a single packet"""
        if self.check:
            self.packet = struct.pack(">hhh", self.magic_no, self.packet_type, self.request_type)
            return self.packet
        else:
            return False # discard the packet without further action
        
def get_response(packet):
    """gets data from the packet and checks if it is a valid response packet"""
    header, body = packet[:13], packet[13:]
    text = body.decode("utf_8")
    
    magic_no, packet_type, language_code, year, month, day, hour, minute, length = struct.unpack(">hhhhbbbbb", header)
    length_of_header = len(header)
    length_of_packet = length_of_header + length
    
    return length_of_header, length_of_packet, magic_no, packet_type, language_code, year, month, day, hour, minute, length, text  

def check_response(length_of_header, length_of_packet, magic_no, packet_type, language_code, year, month, day, hour, minute, length):
    """ checking validity of header response packet. called in get response when 
    unpacking response from server"""
    while True:
        if length_of_header < 13:
            break
        if magic_no != 0x497E:
            break
        if packet_type != 0x0002:  # processes only DT_Response packets
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
    print("--------[packet Information]--------")
    print("Magic Number:", magic_no)
    print("packet Type:", packet_type)
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
    magic_number = 0x497E
    packet_type = 0x0001
    
    date_time = sys.argv[1]
    udp_ip = sys.argv[2]
    udp_port = sys.argv[3]

    # checking for valid date or time request
    if date_time != "date" and date_time != "time":
        print("Must enter either 'date' or 'time'!")
        sys.exit()
    
    # checking valid IP and hostname
    try:
        socket.inet_aton(udp_ip)
    except OSError:
        # if hostname like date_time.mydomain is entered, IP address of server
        # converted to dotted decimal notation
        try:
            info_list = socket.getaddrinfo(udp_ip, udp_port)
            udp_ip = info_list[0][4][0]
        except (OSError, socket.gaierror):  # checking if hostname exists
            print("Host name does not exist...terminating...\n")
            sys.exit()  
        except UnicodeError:  # checking for properly formed ip in DotDecimalNotation
            print("IP address not well formed...terminating...\n")
            sys.exit()

    # checks that port is an integer
    try:
        udp_port = int(udp_port)
    except:
        print("Port must be an integer!")
        sys.exit()

    if udp_port < 1024 or udp_port > 64000:  # checks the port is in range
        print("Port is out of range!")
        sys.exit()
        
    # sets user input of date / time to request type
    if date_time == "date":
        request_type = 0x0001
    elif date_time == "time":
        request_type = 0x0002
        
    # client tries opening up a udp socket
    try:
        sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # opens a UDP socket
        sock_out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # sock_out.bind((udp_ip, udp_port))
    except socket.error:
        print("Error opening port...Terminating...")
        sys.exit()

    running = True
    while running:
        packet = DT_Request(magic_number, packet_type, request_type)  # prepares DT-Request packet
        REQUEST = packet.packet  # returns the byte array of the packet header
        try:
            sock_out.sendto(REQUEST, (udp_ip, udp_port))  # packet request sent to server
            print("--------[Transmission Sent]---------\n")
        except:
            print("Error sending request to server...")
            break

        sock_out.settimeout(1) # wait for 1 second for a response packet.
        print("Waiting for response...\n")
        try:  # try to receive response from server
            data, addr = sock_out.recvfrom(1024)
            # response is unpacked in get_response and then checked if valid
            length_of_header, length_of_packet, magic_no, packet_type, language_code, year, month, day, hour, minute, length, text = get_response(data)
            if check_response(length_of_header, length_of_packet, magic_no, packet_type, language_code, year, month, day, hour, minute, length):
                print("Success: Relaying response...")
                print_results(magic_no, packet_type, language_code, year, month, day, hour, minute, length, text)
                running = False  # prints then exits                 
            else:
                print("Invalid packet...\n")
                running = False

        except socket.timeout:  # if client waits longer than a second; program exits
            print("Timeout error...\n")
            running = False
            
    print("-----[Transmission Terminated]------")
    sock_out.close()
    sys.exit()


if __name__ == "__main__":
    main()        
