import socket
from colors import *
import time
from bluetoothMod import *
from arduinoMod import *

class pc_Comm(object):

    def __init__(self):
        self.ip_address = '192.168.4.4'
        self.port = 5050
        self.pc_is_connected = False

    def pc_is_connected(self):
        return self.pc_is_connected

    # to connect to pc via using sockets + port 5050 (working)
    def connect_pc(self):
        retry = True
        while (retry == True):
            try:
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conn.bind((self.ip_address, self.port))
                self.conn.listen(1)
                print('Listening for incoming PC connection on ', self.ip_address + ':' + str(self.port))

                self.client, self.addr = self.conn.accept()
                cprint(BOLD + GREEN, 'Successful PC Connection with IP Address: ' + str(self.addr))
                self.pc_is_connected = True
                retry = False

            except Exception as e:
                cprint(BOLD + RED, '[PC ERROR] PC Connection Error: ' + str(e))
                time.sleep(3)
                
            if (not retry):
                break

            print('Retrying PC Connection...')

    # to dsconnect connection with pc (working)
    def disconnect_pc(self):
        try:
            if self.conn:
                self.conn.close()
            if self.client:
                self.client.close()

            #cprint(BOLD + GREEN, 'PC disconnected successfully')
            self.pc_is_connected = False

        except Exception as e:
            pass


    # to read incoming messages from pc (working)
    def read_from_pc(self):
        try:
            pc_msg = self.client.recv(2048)
            pc_msg = pc_msg.decode('utf-8')
            #print('Message successfully received from PC: ' + pc_msg.rstrip())
            return pc_msg

        except Exception as e:
            cprint(BOLD + RED, '[PC ERROR] Message from PC cannot be read: ' + str(e))
            #if ('Connection reset by peer' in str(e)):
            self.disconnect_pc()
            cprint(BLUE, "Trying to reconnect PC...")
            self.connect_pc()
                

    # to write message to pc (working)
    def write_to_pc(self,PCmessage):
        try:
            if (not self.pc_is_connected):
                cprint(BOLD+RED, '[PC ERROR] PC not connected: Unable to send message')
                return

            messageEncode = PCmessage.encode('UTF-8')
            self.client.sendto(messageEncode, self.addr)
            #print('Message successfully sent to PC: ' + PCmessage.rstrip())
            
        except Exception as e:
            cprint(BOLD + RED, '[PC ERROR] Message not send to PC: ' + str(e))
                
if __name__ == "__main__":

    # testing of comms using fake exploration data
    
    bt = bluetooth_Comm()
    bt.connect_bluetooth()
    ar = arduino_Comm()
    ar.connect_arduino()
    pc = pc_Comm()
    pc.connect_pc()
    print ('Connection Status: ' + str(pc.pc_is_connected))

    
    f = open("ex_test3.txt","r")
    #pc.write_to_pc("ST\n")
    

    btmsg = bt.read_from_bluetooth()
    btmsg = btmsg[3:] + '\n'
    pc.write_to_pc(btmsg)

    pcmsg = pc.read_from_pc()
    pcmsg = pcmsg[3:]
    ar.write_to_arduino(pcmsg)
    
    while True:
        armsg = ar.read_from_arduino()
        pc.write_to_pc(armsg+"\n")

        line = f.readline().rstrip()
        line = (line.replace(' ', ''))
        line = (line.replace('[', ''))
        line = (line.replace(']', ''))
        #time.sleep(1)
        pc.write_to_pc(line+"\n")

        pcmsg = pc.read_from_pc()
        pcmsg = pcmsg[3:]
        bt.write_to_bluetooth(pcmsg)
        
        pcmsg = pc.read_from_pc()
        pcmsg = pcmsg[3:]
        ar.write_to_arduino(pcmsg)

        armsg = ar.read_from_arduino()
        pc.write_to_pc(armsg+"\n")
        
        if not line:
            break
        #print (line)

    '''message = input('Disconnect? y/n')
    if (message == 'y'):
        pc.disconnect_pc()
    elif (message == 'n'):
        lol = input ('LOL')'''

    # writing message to pc
    #message1 = input('enter message')
    #data = pc.read_from_pc()
    #pc.write_to_pc('10,20,10,20,10\n' )

    # reading message from pc
    #while True:
        #data = pc.read_from_pc()
                      

