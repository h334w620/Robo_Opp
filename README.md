# Robo_Opp
![image](https://github.com/h334w620/Robo_Opp/assets/123573593/b5e64647-80f4-420c-9fe2-906f9cd6907c)

## Overview

Robo Opp is a new and novel way to secure any perimeter. It identifies nearby targets and neutralizes them using a precision designed Nerf Gun.

The code here is for the two devices that were principally used to control Robo Opp: an Orange Pi, and an Arduino. The Orange Pi was used for vision processing. It communicates with the Arduino over serial to tell it how to actuate things on Robo Opp. The Arduino controls two things: the motors at the base and the Nerf Gun trigger.

## Setup

### Vision

#### Prerequistes

Before any further actions could be taken, the Orange Pi was flashed with the latest Armbian image. From there, necessary software was installed.

Since it is necessary to be able to communicate using serial, we decided to use pyserial. To install pyserial, run `sudo apt install python-serial`.

To do the actual vision processing, we used OpenCV. To install OpenCV, run `sudo apt install python-opencv`.

If these wouldn't install, you may want to make sure the date was set correctly. TLS (and hence https) tends not to work well with incorrect times.

#### Installing the Code

There needs to be a place to store the code on the device. We decided to make a folder called `/scripts`. To make this folder, run `mkdir /scripts` and `chmod 1777 /scripts`. Then move `haarcascade_frontalface_default.xml`, `startvision.sh`, and `vision.py` to this folder. To make sure the script is executable, run `chmod u+x startvision.sh`.

Finally, install the service. Move `vision.service` to `/usr/lib/systemd/system/vision.service` and run `systemctl enable vision`.

Vision should be active upon reboot. Make sure the camera index is set correctly in `vision.py`.

### Hardware Control
#### Prerequistes

Before any further actions could be taken, download the latest version of PlatformIO and mount the project in VScode or, using CLI, go to the project Arduino_uno directory. 

Since it is necessary to be able to communicate using serial, make sure the correct USB to Serial drivers are installed on the Orange PI 5.

#### Bill Of Materials
Pieces | Parts
------ | ------
1   | Arduino UNO
2  | L298n H-bridge
1 | 5 volt Relay
2 | NEMA 17 Stepper Motors
1 | Logitech camera
1 | Motorized NERF Gun
1 | Orange PI 5
1 | 32 GB SD card

#### Allocated Pins
PIN | Desc.
------ | ------
12   | Trigger Relay Pin
4, 5, 6 ,7   | Stepper Motor A Pin
8, 9, 10, 11 | Stepper Motor B Pin

#### (Rough) schematics
##### WARNING
- The NPN transistor is a stand in for a optocoupler controlled relay.
- The DC motor is a stand in for Nerf Gun
- The L298d is a stand in for the L298n
- The Green wire repersents the stepper motor windings
- The USB is directly connected to the OrangePI 5 for serial
![image](https://github.com/h334w620/Robo_Opp/assets/123573593/86343e01-ca8c-4af9-87bd-a3e8b8e7e63c)

#### Installing the Code

Within the project Arduino_uno directory:
Build project and upload firmware to the all devices specified
> pio run --target upload

Clean project (delete compiled objects)
> pio run --target clean

Process only uno environment
> pio run -e uno

Build project only for uno and upload firmware
> pio run -e uno -t upload

