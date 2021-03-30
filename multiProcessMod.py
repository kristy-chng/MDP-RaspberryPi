import sys
import time
import threading
import os
import picamera
import shutil
from pcMod import *
from bluetoothMod import *
from arduinoMod import *

class MultiProcess(threading.Thread):
    
######################### Multithreading ###############################    

    def __init__(self):
        threading.Thread.__init__(self)
        self.debug = False

        self.pc_thread = pc_Comm()
        self.bluetooth_thread = bluetooth_Comm()
        self.arduino_thread = arduino_Comm()

        # initialize connection threads
        init_pcThread = threading.Thread(target = self.pc_thread.connect_pc, name = "pc_init_thread")
        init_bluetoothThread = threading.Thread(target = self.bluetooth_thread.connect_bluetooth, name = "bt_init_thread")
        init_arduinoThread = threading.Thread(target = self.arduino_thread.connect_arduino, name = "ar_init_thread")

        # set threads as daemon
        init_pcThread.daemon = True
        init_bluetoothThread.daemon = True
        init_arduinoThread.daemon = True

        # start threads
        init_pcThread.start()
        init_bluetoothThread.start()
        init_arduinoThread.start()
        
        #self.camera = picamera.PiCamera()
        #self.camera.resolution = (720, 480)
        #self.camera.zoom = (0.1, 0.45, 0.8, 0.8)
        #self.camera.exposure_mode = 'sports'

        # counter used to stop IR process after 5 pictures have been taken
        self.counter = 0

        while not (self.pc_thread.pc_is_connected and self.arduino_thread.arduino_is_connected): #and self.bluetooth_thread.bt_is_connected):
            time.sleep(0.1)

    def initialize_threads(self):
        
        # initialize threads
        self.readBTThread = threading.Thread(target=self.readBluetooth, name = "bt_read_thread")
        self.readPCThread = threading.Thread(target=self.readPC, name = "pc_read_thread")
        self.readARThread = threading.Thread(target=self.readArduino, name = "ar_read_thread")
        self.IRThread = threading.Thread(target=self.checkImageFolder, name = "ir_thread")

        # set threads as daemon
        self.readPCThread.daemon = True
        self.readBTThread.daemon = True
        self.readARThread.daemon = True
        self.IRThread.daemon = True
        print("All daemon threads initialized successfully")

        # start threads
        self.readPCThread.start()
        self.readBTThread.start()
        self.readARThread.start()
        self.IRThread.start()
        print("All daemon threads started successfully")
        

######################### Android Communication ###############################

    def writeBluetooth(self, msgToBT):
        self.bluetooth_thread.write_to_bluetooth(msgToBT)

    def readBluetooth(self):
        while True:
            retry = False
            try:
                while True:
                    readBTMessage = self.bluetooth_thread.read_from_bluetooth()
                    if (readBTMessage is None):
                        continue
                    readBTMessage = readBTMessage.lstrip()
                    if (len(readBTMessage) == 0):
                        continue
                    if (readBTMessage[:2].upper() == ('PC')):
                        self.writePC(readBTMessage[3:]+ '\n')
                        cprint(BOLD+GREEN,"[BT -> PC] Successful: %s" % readBTMessage[3:].rstrip())
                    elif (readBTMessage[:2].upper() == ('AR')):
                        self.writeArduino(readBTMessage[3:])
                        cprint(BOLD+GREEN,"[BT -> AR] Successful: %s" % readBTMessage[3:].rstrip())
                    else:
                        cprint(BOLD+RED, "[HEADER ERROR] Incorrect header from Bluetooth: [%s]" % readBTMessage[:2])

            except Exception as e:
                print("main/BT-Recv Error %s" % str(e))
                retry = True

            if (not retry):
                break

############################# PC Communication ###############################
                
    def writePC(self, msgToPC):
        self.pc_thread.write_to_pc(msgToPC)

    def processPCMsg(self, readPCMessage):
        if (readPCMessage is None):
            return
        readPCMessage = readPCMessage.lstrip()
        if (len(readPCMessage) == 0):
            return
        if (readPCMessage[:2].upper() == 'AN'):
            self.writeBluetooth(readPCMessage[3:])
            cprint(BOLD+GREEN,"[PC -> BT] Successful: %s" % readPCMessage[3:].rstrip())
        elif (readPCMessage[:2].upper() == 'AR'):
            self.writeArduino(readPCMessage[3:])
            cprint(BOLD+GREEN,"[PC -> AR] Successful: %s" % readPCMessage[3:].rstrip())
        elif (readPCMessage[:2].upper() == 'IR'):
            coordinates = readPCMessage[3:].rstrip()
            self.imageTaking(coordinates) # takes the picture
            self.writePC('PC,Go\n') # algo wants a signal once photo is taken
            
        else:
            cprint(BOLD + RED, "[HEADER ERROR] Incorrect header from PC: [%s]" % readPCMessage[:2])

    def readPC(self):
        try:
            while True:
                readPCMessage = self.pc_thread.read_from_pc()
                if (readPCMessage is None):
                    continue
                readPCMessage = readPCMessage.split('\n')
                for msg in readPCMessage:
                    self.processPCMsg(msg)

        except Exception as e:
            print("main/PC-Recv Error: %s" % str(e))

########################### Arduino Communication ##############################

    def writeArduino(self,msgToARD):
        self.arduino_thread.write_to_arduino(msgToARD)

    def readArduino(self):
        try:
            while True:
                readArduinoMsg = self.arduino_thread.read_from_arduino()
                if (readArduinoMsg is None):
                    continue
                readArduinoMsg = readArduinoMsg.lstrip()
                if (len(readArduinoMsg) == 0):
                    continue
                if (readArduinoMsg[:2].upper() == 'AN'):
                    self.writeBluetooth(readArduinoMsg[3:]+ "\r\n")
                    cprint(BOLD+GREEN,"[AR -> BT] Successful: %s" % readArduinoMsg[3:].rstrip())
                elif (readArduinoMsg[:2].upper() == 'PC'):
                    self.writePC(readArduinoMsg[3:] + '\n')
                    cprint(BOLD+GREEN,"[AR -> PC] Successful: %s" % readArduinoMsg[3:].rstrip())
                else:
                    cprint(BOLD + RED, "[HEADER ERROR] Incorrect header from Arduino: [%s]" % readArduinoMsg[:2])

        except socket.error as e:
            print("main/ARD-Recv Error:Socket Disconnected")
        
########################### Image Recognition ##############################
            
    def imageTaking(self,coordinates):
        start_time = time.time()
        timestr = time.strftime("%d-%m-%Y-%H:%M:%S")
        self.camera.capture('/home/pi/Desktop/RawImage/'+coordinates+'.jpg')
        print("--- %s seconds ---" % (time.time() - start_time))
        
    def checkImageFolder(self):
        while True:
            if (self.bluetooth_thread.bt_is_connected):
                path = '/home/pi/Desktop/Detected2'
                searchPath='/home/pi/Desktop/DetectedImages'
                files = os.listdir(path)
                containedFile=os.listdir(searchPath)
                firstFile=""
                compareFile=""
                msg= ''
                if len(files) != 0:
                    for filename in files:
                        filename_split = filename.split(",")
                        firstFile=filename_split[0]
                        
                        contained = []
                        for compare in containedFile:
                            compare_split = compare.split(",")
                            contained.append(compare_split[0])
                            
                        
                        if(firstFile not in contained):
                            msg = filename.replace('.jpg.JPG', '')
                            msg = 'IR,'+ msg
                            shutil.move('/home/pi/Desktop/Detected2/'+filename, '/home/pi/Desktop/DetectedImages')
                            self.writeBluetooth(msg)
                            print('[IR->BT] Successful: %s' % msg.rstrip())
                            self.counter = self.counter+1
                            msg = ''
                        else:
                            os.remove('/home/pi/Desktop/Detected2/'+filename)
                        #self.counter = self.counter+1
            
                if (self.counter == 5): # to disconnect and exit program once robot takes all 5 pictures
                    time.sleep(2)
                    self.disconnect_all()
                    quit()

########################### Others ##############################
                    
    def keep_alive(self):
        while(1):
            time.sleep(1)

    def disconnect_all(self):
        self.pc_thread.disconnect_pc()
        self.bluetooth_thread.disconnect_bluetooth()
        self.arduino_thread.disconnect_arduino()
        cprint(BOLD+GREEN, 'Disconnected all devices')
                    
            
if __name__ == "__main__":
    mainThread = MultiProcess()
    mainThread.initialize_threads()
    mainThread.keep_alive()

    
                        
                        
        

        
