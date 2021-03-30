# MDP - Raspberry Pi (Communication)

NTU School of Computer Science and Engineering (AY2020/21 S2)
CZ3004 Multidisciplinary Design Project

### Role of the RPi
![alt text](https://github.com/kristy-chng/MDP-RaspberryPi/blob/main/high-level-architecture.png?raw=true)

The main idea is to allow messages to be passed around between the 3 devices via its corresponding medium, with the RPI acting as the bridge. The mediums for which each devices uses:
- **Arduino**: Serial via USB
- **Android**: RFCOMM Protocol via Bluetooth
- **PC**: IP Protocol with RPi configured as a WAP

### Initial Set up 
- Booting up the RPI with a fresh copy of Raspbian Jessie
- Establishing a SSH connection to enable remote connection to the RPI
- Establishing the RPI as a Wireless Access Point with gateway to the Internet
- Setting up RPI Bluetooth link with Android
- Setting up USB Interface with Arduino board

### Data Exchange Protocol
- For every message that is sent to the RPI, a 2-character header, which indicates the destination device, is attached to the front of the message – e.g. ‘AR’ = Arduino, ‘AN’ = Android, ‘PC’ = PC
- RPi simply peeks at the 2-character header, remove the header,  and send the rest of the message to the intended destination.

### Use of Multi-threading
To ensure that RPi is able to handle simultaneous communication with all 3 devices.
- Every read function (for each of the 3 devices) will be run on separate threads.
- Threads are not neccessary for write functions as writing can only be done after reading 

### Running of Program
```sudo python3 multiProcessMod.py```

### Misc
- explorationTestData1/2/3.txt contains fake sensor data to test out robot's algorithm
