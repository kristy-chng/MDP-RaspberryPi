# MDP-RaspberryPi

NTU School of Computer Science and Engineering (AY2020/21 S2)
CZ3004 Multidisciplinary Design Project

## Role of the RPi
The main idea is to allow messages to be passed around between the 3 devices via its corresponding medium, with the RPI acting as the bridge. The mediums for which each devices uses:
- Arduino: Serial via USB
- Android: RFCOMM Protocol via Bluetooth
- PC: IP Protocol with RPi configured as a WAP

## Initial Set up 
- Booting up the RPI with a fresh copy of Raspbian Jessie
- Establishing a SSH connection to enable remote connection to the RPI
- Establishing the RPI as a Wireless Access Point with gateway to the Internet
- Setting up RPI Bluetooth link with Android
- Setting up USB Interface with Arduino board

## Running of Program
```sudo python3 multiProcessMod.py```

## Use of Multi-threading
To ensure that RPi is able to handle simultaneous communication with all 3 devices.
- Every read function (for each of the 3 devices) will be run on separate threads.
- A 4th thread is also created for the purpose of the RPI’s Image Recognition capabilities.

## Misc
- explorationTestData1/2/3.txt contains fake sensor data to test out robot's algorithm
