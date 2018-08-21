import socket
import struct
import sys
import select
import datetime

class DT_Response(object):
    """Creates an instance of a DT_Request packet"""
    def __init__(self, language):
        """initialize"""
        self.magic_no = 0x497E
        self.packet_type = 0x0002
        self.language_code = language
        self.year = None
        self.month = None
        self.day = None
        self.hour = None
        self.minute = None
        self.length = None
        self.text = None
        self.packet = None
        self.header = None
        self.body = None
        self.english = {1:"January",
                        2:"February", 
                        3:"March", 
                        4:"April",
                        5:"May",
                        6:"June",
                        7:"July",
                        8:"August",
                        9:"September",
                        10:"October",
                        11:"November",
                        12:"December"}
        
        self.maori = {1:"Kohitātea",
                      2:"Hui-tanguru", 
                      3:"Poutū-te-rangi", 
                      4:"Paenga-whāwhā",
                      5:"Haratua",
                      6:"Pipiri",
                      7:"Hōngongoi",
                      8:"Here-turi-koka", # Here-turi-kōkā
                      9:"Mahuru",
                      10:"Whiringa-ā-nuku",
                      11:"Whiringa-ā-rangi",
                      12:"Hakihea"}        
        
        self.german = {1:"Januar",
                      2:"Februar", 
                      3:"März", 
                      4:"April",
                      5:"Mai",
                      6:"Juni",
                      7:"Juli",
                      8:"August",
                      9:"September",
                      10:"Oktober",
                      11:"November",
                      12:"Dezember"}    
        
    def check(self):
        """checks if the packet is valid"""
        if self.magic_no == 0x497E and self.packet_type == 0x0002:
            return True
        else:
            print("Invalid packet...Terminating...\n")
            return False
            
    def encode(self):
        """packs all the bytes into a single packet"""
        if self.check:
            self.header = struct.pack(">hhhhbbbbb", self.magic_no, self.packet_type, 
                                      self.language_code, self.year, self.month,
                                      self.day, self.hour, self.minute, self.length)
            self.body = struct.pack("%ds" % (self.length,), self.text)
            self.packet = self.header + self.body
            return self.packet
        else:
            return False # discard the packet without further action
        
    def textual_representation(self, request):
        """returns a date or time representation based on the request made"""
        now = datetime.datetime.now()
        self.year = now.year
        self.month = now.month
        self.day = now.day
        self.hour = now.hour
        self.minute = now.minute
        
        if self.language_code == 0x0001:
            if request == 1:
                proper_month = self.convert_month()
                self.text = "Today's date is " + proper_month + ' ' + str(self.day) + ', ' + str(self.year)
            elif request == 2:
                self.text = "The current time is " + str(self.hour) + ':' + str(self.minute)
        elif self.language_code == 0x0002:
            if request == 1:
                proper_month = self.convert_month()
                self.text = "Ko te ra o tenei ra ko " + proper_month + ' ' + str(self.day) + ', ' + str(self.year)
            elif request == 2:
                self.text = "Ko te wa o tenei wa " + str(self.hour) + ':' + str(self.minute)          
        elif self.language_code == 0x0003:
            if request == 1:
                proper_month = self.convert_month()
                self.text = "Heute ist der " + proper_month + ' ' + str(self.day) + ', ' + str(self.year)
            elif request == 2:
                self.text = "Die Uhrzeit ist " + str(self.hour) + ':' + str(self.minute)     
                
        self.text = self.text.encode('utf-8')
        self.length = len(self.text)
        if self.length <= 255:  # checking for valid text length
            return True
        else:
            print("Text is too long...")
            return False
        
    def convert_month(self):
        """returns the proper name of a month in the specified language"""
        if self.language_code == 0x0001:
            return self.english[self.month]
        
        elif self.language_code == 0x0002:
            return self.maori[self.month]   
        
        elif self.language_code == 0x0003:
            return self.german[self.month]
           
def request_check(packet):
    """checks if the request packet is valid"""
    magic_no, packet_type, request_type = get_request(packet)
    length_of_packet = struct.calcsize('>hhh')
    # checks if packet is 6 bytes and valid magic no, packet type and request type
    if length_of_packet == 6 and magic_no == 0x497E and packet_type == 0x0001 and (request_type == 0x0001 or request_type == 0x0002):
        return True
    else:
        return False
    
def get_request(packet):
    """gets data from the packet"""
    magic_no, packet_type, request_type = struct.unpack('>hhh', packet)
    return magic_no, packet_type, request_type

    
def main():
    udp_ip = "127.0.0.1"
    
    udp_ip_1 = sys.argv[1]
    udp_ip_2 = sys.argv[2]
    udp_ip_3 = sys.argv[3]

    try:
        udp_ip_1 = int(udp_ip_1)
        udp_ip_2 = int(udp_ip_2)
        udp_ip_3 = int(udp_ip_3)
    except:
        # all ports must be an integer
        print("All ports must be integers!")
        sys.exit()

    # port in range checks
    if udp_ip_1 < 1024 or udp_ip_1 > 64000:
        print("Port 1 out of range!")
        sys.exit()

    if udp_ip_2 < 1024 or udp_ip_2 > 64000:
        print("Port 2 out of range!")
        sys.exit()

    if udp_ip_3 < 1024 or udp_ip_3 > 64000:
        print("Port 3 out of range!")
        sys.exit()

    # checks for port uniqueness
    if len({udp_ip_1, udp_ip_2, udp_ip_3}) != 3:
        print("All port numbers must be unique!")
        sys.exit()

    try:
        # opening three sockets for each language request
        sock_eng = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # English
        sock_mao = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Te reo Maori
        sock_ger = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # German

        # set each socket
        sock_eng.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_mao.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_ger.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # binding each socket to a port
        sock_eng.bind((udp_ip, udp_ip_1))
        sock_mao.bind((udp_ip, udp_ip_2))
        sock_ger.bind((udp_ip, udp_ip_3))
    except socket.error:
        print("Error opening / binding ports...Terminating...")
        sys.exit()

    running = True
    while running:
        # block until at least one socket is ready
        ready_sockets, _, _ = select.select([sock_eng, sock_mao, sock_ger], [], [])
        for sock in ready_sockets:
            data, addr = sock.recvfrom(1024)

            print("-"*40)
            print("received message:", data)
            print("Sender IP:", sock.getsockname()[0])
            print("Sender port:", sock.getsockname()[1]) # gets the senders port to determine language
            print("-"*40)
            
            if request_check(data): # DT_Request being checked for validity
                magic_no, packet_type, date_time_code = get_request(data)
                sender_port = sock.getsockname()[1]  # gets the port of the sender
                
                # assigns the language for the response based on senders port
                if sender_port == udp_ip_1:
                    language_code = 0x0001
                elif sender_port == udp_ip_2:
                    language_code = 0x0002
                elif sender_port == udp_ip_3:
                    language_code = 0x0003
                    
                # preparing a DT_Response 
                response = DT_Response(language_code)
                # checking if response is valid
                if response.check() and response.textual_representation(date_time_code):
                    response.encode()  # encode header and text into byte array
                    RESPONSE = response.packet
                    
                    try: # attempting to send response packet back to client
                        sock.sendto(RESPONSE, (addr[0], addr[1]))
                        print("Transmission sent...")
                    except:
                        print("Error sending request to client...")
                        continue 
                else:
                    print("Invalid response packet...")
                    continue
            else:
                print("Received packet is not valid...")
                continue # continue at start of loop
                
    # close all 3 sockets before exiting program
    sock_eng.close()
    sock_mao.close()
    sock_ger.close()
    print("Goodbye!")
    sys.exit()
        

if __name__ == "__main__":
    main()
