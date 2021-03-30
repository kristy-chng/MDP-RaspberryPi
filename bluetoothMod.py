from bluetooth import *
from colors import *
import time
import os

class bluetooth_Comm(object):

    def __init__(self):
        self.server_socket = None
        self.client_socket = None
        self.bt_is_connected = False

    # to check if bluetooth is connected
    def bt_is_connected(self):
        return self.bt_is_connected

    # to connect to android using bluetooth (working)
    def connect_bluetooth(self):
        while True:
            btPort = 4
            retry = False

            # creating the server socket and attempting to bind to the port
            try:
                self.server_sock = BluetoothSocket(RFCOMM)
                self.server_sock.bind(('', btPort))
                self.server_sock.listen(1)
                self.port = self.server_sock.getsockname()[1]
                uuid = '00001101-0000-1000-8000-00805f9b34fb'

                advertise_service(self.server_sock, 'rpiGrp4',
                                  service_id = uuid,
                                  service_classes = [uuid, SERIAL_PORT_CLASS],
                                  profiles = [SERIAL_PORT_PROFILE])
                print('Establishing Bluetooth connection on RFCOMM channel %d' % self.port)

                self.client_socket, client_address = self.server_sock.accept()
                cprint(BOLD + GREEN, 'Successful Bluetooth connection with ' + str(client_address))
                self.bt_is_connected = True
                retry = False

            except Exception as e:
                cprint(BOLD + RED, '[BT ERROR] Bluetooth Connection Error: ' + str(e))
                if ('Address already in use' in str(e)):
                    os.system("sudo service bluetooth stop")
                    os.system("sudo /etc/init.d/bluetooth stop")
                elif ('no advertisable device' in str(e)):
                    os.system("sudo service bluetooth start")
                    os.system("sudo hciconfig hci0 piscan")
                retry = True
                #time.sleep(5)

            if (not retry):
                break

    # to disconnect connection with android (working)
    def disconnect_bluetooth(self):
        try:
            if self.client_socket is not None:
                self.client_socket.close()
                self.client_sock = None

            if self.server_socket is not None:
                self.server_socket.close()
                self.server_sock = None

            #cprint(BOLD+ GREEN, "Android disconnected Successfully")
            self.bt_is_connected = False

        except Exception as e:
            pass

    # to read incoming messages from android (working)
    def read_from_bluetooth(self):
        try:
            bluetooth_msg = self.client_socket.recv(2048)
            bluetooth_msg = bluetooth_msg.decode('utf-8') #bytes to string
            #print("Message successfully received from Android: " + bluetooth_msg.rstrip())
            return bluetooth_msg
        
        except BluetoothError as e:
            cprint(BOLD + RED, '[BT ERROR] Message from Android cannot be read: ' + str(e))
            if ('Connection reset by peer' in str(e)):
                self.disconnect_bluetooth()
                cprint(BLUE, "Trying to reconnect bluetooth...")
                self.connect_bluetooth()

    # to write message to android (working)
    def write_to_bluetooth(self, BTmessage):
        try:
            if (not self.bt_is_connected):
                cprint(BOLD + RED,'[BT ERROR] Bluetooth not connected: Unable to send message')
                return
            
            self.client_socket.send(BTmessage)
            #print('Message successfully sent to Android: ' + BTmessage)

        except BluetoothError as e:
            cprint(BOLD + RED,'[BT ERROR] Message not sent to Android: ' + str(e))


if __name__ == "__main__":

    # tested using serial bt term |& android app

    # testing of connection & disconnection
    bt = bluetooth_Comm()
    bt.connect_bluetooth()
    print ('Connection Status: ' + str(bt.bt_is_connected))

   # message = input('Disconnect? y/n')
    #if (message == 'y'):
       # bt.disconnect_bluetooth()
    #elif (message == 'n'):
        #lol = input ('LOL')

    # testing of writing to android
    #message1 = input("Enter message: ")
    #bt.write_to_bluetooth(message1)

    # testing of reading from android  
    #message2 = bt.read_from_bluetooth()

    
    
            
            
            

            
                

            
            
            
            
    
