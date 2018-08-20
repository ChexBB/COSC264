import socket
import struct
import sys
import select
import datetime

class DT_Response(object):
    """Creates an instance of a DT_Request packet"""
    def __init__(self, language):
        """initializes the bytes"""
        self.Magic_No = 0x497E
        self.Packet_Type = 0x0002
        self.Language_Code = language
        self.Year = None
        self.Day = None
        self.Hour = None
        self.Minute = None
        self.Length = None
        self.Text = None
        self.Packet = None
        self.Header = None
        self.Body = None
        self.valid_packet = False
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
        
        # checks the validity of the packt on initialization
        self.check()
        
    def check(self):
        """checks if the packet is valid"""
        if self.Magic_No == 0x497E and self.Packet_Type == 0x0002:
            self.valid_packet = True
            return self.valid_packet
        else:
            raise Exception("Invalid packet")
            
    def encode(self):
        """packs all the bytes into a single packet"""
        if self.valid_packet == True:
            self.Header = struct.pack(">hhhhbbbbb", self.Magic_No, self.Packet_Type, 
                                      self.Language_Code, self.Year, self.Month,
                                      self.Day, self.Hour, self.Minute, self.Length)
            self.Body = struct.pack("%ds" % (self.Length,), self.Text)
            self.Packet = self.Header + self.Body
            #print(self.Header)
            #print(self.Body)
            #print(self.Packet)
            return self.Packet
        else:
            return False # discard the packet without further action
        
    def textual_representation(self, request):
        """returns a date or time representation based on the request made"""
        now = datetime.datetime.now()
        self.Year = now.year
        self.Month = now.month
        self.Day = now.day
        self.Hour = now.hour
        self.Minute = now.minute
        
        #print("Language", self.Language_Code)
        #print("Request", request)
        if self.Language_Code == 0x0001:
            if request == 1:
                proper_month = self.convert_month()
                self.Text = "Today's date is " + proper_month + ' ' + str(self.Day) + ', ' + str(self.Year)
            elif request == 2:
                self.Text = "The current time is " + str(self.Hour) + ':' + str(self.Minute)
        elif self.Language_Code == 0x0002:
            if request == 1:
                proper_month = self.convert_month()
                self.Text = "Ko te ra o tenei ra ko " + proper_month + ' ' + str(self.Day) + ', ' + str(self.Year)
            elif request == 2:
                self.Text = "Ko te wa o tenei wa " + str(self.Hour) + ':' + str(self.Minute)          
        elif self.Language_Code == 0x0003:
            if request == 1:
                proper_month = self.convert_month()
                self.Text = "Heute ist der " + proper_month + ' ' + str(self.Day) + ', ' + str(self.Year)
            elif request == 2:
                self.Text = "Die Uhrzeit ist " + str(self.Hour) + ':' + str(self.Minute)     
                
        self.Text = self.Text.encode('utf-8')
        self.Length = len(self.Text)
        if self.Length > 255:
            print("Text is too long...Terminating...")  # return to the start of the loop??
        #print(self.Text)
        
    def convert_month(self):
        """returns the proper name of a month in the specified language"""
        if self.Language_Code == 0x0001:
            return self.english[self.Month]
        
        elif self.Language_Code == 0x0002:
            return self.maori[self.Month]   
        
        elif self.Language_Code == 0x0003:
            return self.german[self.Month]
           
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
    
    UDP_IP = "127.0.0.1"
    
    UDP_PORT_1 = sys.argv[1]
    UDP_PORT_2 = sys.argv[2]
    UDP_PORT_3 = sys.argv[3]

    try:
        UDP_PORT_1 = int(UDP_PORT_1)
        UDP_PORT_2 = int(UDP_PORT_2)
        UDP_PORT_3 = int(UDP_PORT_3)
    except:
        # all ports must be an integer
        print("All ports must be integers!")
        sys.exit()

    # port in range checks
    if UDP_PORT_1 < 1024 or UDP_PORT_1 > 64000:
        print("Port 1 out of range!")
        sys.exit()

    if UDP_PORT_2 < 1024 or UDP_PORT_2 > 64000:
        print("Port 2 out of range!")
        sys.exit()

    if UDP_PORT_3 < 1024 or UDP_PORT_3 > 64000:
        print("Port 3 out of range!")
        sys.exit()

    # checks for port uniqueness
    if len({UDP_PORT_1, UDP_PORT_2, UDP_PORT_3}) != 3:
        print("All port numbers must be unique!")
        sys.exit()

    # opening three sockets for each language request
    sock_eng = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # English
    sock_mao = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Te reo Maori
    sock_ger = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # German

    # set each socket
    sock_eng.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_mao.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_ger.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # binding each socket to a port
    sock_eng.bind((UDP_IP, UDP_PORT_1))
    sock_mao.bind((UDP_IP, UDP_PORT_2))
    sock_ger.bind((UDP_IP, UDP_PORT_3))

    running = True
    while running:
        # block until at least one socket is ready
        ready_sockets, _, _ = select.select([sock_eng, sock_mao, sock_ger], [], [])
        for sock in ready_sockets:
            data, addr = sock.recvfrom(1024)

            print("-"*40)
            print("received message:", data)
            print("received IP:", addr[0]) # need to be senders IP or this one?
            print("Sender port:", sock.getsockname()[1]) # gets the senders port to determine language
            print("-"*40)
            
            if request_check(data): # DT_Request being checked for validity
                magic_no, packet_type, date_time_code = get_request(data)
                sender_port = sock.getsockname()[1]
                
                if sender_port == UDP_PORT_1:
                    language_code = 0x0001
                elif sender_port == UDP_PORT_2:
                    language_code = 0x0002
                elif sender_port == UDP_PORT_3:
                    language_code = 0x0003
                    
                response = DT_Response(language_code)
                response.textual_representation(date_time_code)
                response.encode()
                RESPONSE = response.Packet
                #print("Full response to be sent:", RESPONSE)

                # sending response packet back to client
                try:
                    sock.sendto(RESPONSE, (addr[0], addr[1]))
                    print("Transmission sent...")
                except:
                    print("Error sending request to client...")
                    # running = False
                    continue

            else:
                print("Received packet is not valid... Terminating... ")
                # running = False
                continue
                
    # close all 3 sockets before exiting program
    sock_eng.close()
    sock_mao.close()
    sock_ger.close()
    print("Goodbye!")
    sys.exit()
        

if __name__ == "__main__":
    main()   
