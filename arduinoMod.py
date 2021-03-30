import serial
import time
from colors import *

class arduino_Comm(object):
    def __init__(self):
        self.port = '/dev/ttyACM0'
        self.baurd_rate = 9600
        self.arduino_connected = False

    def arduino_is_connected(self):
        return self.arduino_connected
    
    def connect_arduino(self):
        while True:
            retry = False
            try:
                print('Establishing connection with Arduino..')
                self.ser = serial.Serial(self.port, self.baurd_rate)
                cprint(BOLD + GREEN, 'Successful Serial Connection with Arduino')
                self.arduino_connected = True
                retry = False
                
            except Exception as e:
                cprint(BOLD+RED,'[AR ERROR] Serial Connection Error: %s ' % str(e))
                retry = True

            if (not retry):
                break

    def disconnect_arduino(self):
        if self.ser:
            self.ser.close()
            self.arduino_connected = False

    def read_from_arduino(self):
        try:
            # self.ser.flush()
            ar_message = self.ser.readline().decode('utf-8').rstrip()
            #print("Message successfully received from Arduino: " + ar_message.rstrip())
            return ar_message

        except Exception as e:
            cprint(BOLD + RED,'[AR ERROR] Arduino Read Error: ' + str(e))

            if ('Input/output error' in str(e)):
                self.disconnect_arduino()
                cprint(BOLD + RED, 'Trying to reconnect Arduino..')
                self.connect_arduino()

    def write_to_arduino(self, ARmessage):
        try:
            if (not self.arduino_connected):
                cprint(BOLD + RED, '[AR ERROR] Arduino not connected: Unable to send message')
                return

            ARmessageEncode = ARmessage.encode('utf-8')
            self.ser.write(ARmessageEncode)
            #print('Message successfully sent to Arduino: ' + ARmessage)
            
        except Exception as e:
            cprint(BOLD + RED,'[AR ERROR] Arduino Write Error: ' + str(e))

if __name__ == "__main__":
    sr = arduino_Comm()
    sr.connect_arduino()
    print ('Connection Status: ' + str(sr.arduino_is_connected))

    sr.read_from_arduino()
    sr.write_to_arduino('31R2L6R6L7R4')

    sr.read_from_arduino()
    sr.write_to_arduino('ST')

    while True:
        sr.read_from_arduino()
    
