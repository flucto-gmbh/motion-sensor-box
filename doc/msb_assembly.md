# Hardware assembly

The Motion-Sensor-Box may be subdivided into the cybercube and all the other inner components within the housing. 
Those components need to be assembled first before starting the main assembly.


## Assembly guide for the msb rev8´s cybercube

### The cybercube consists of the following electronic components:

   1. Raspberry Pi Zero W V 1.1
   
        <img src="doc/assembly_cybercube/IMG_1264.JPG" width="250"/> <img src="doc/assembly_cybercube/IMG_1266.JPG" width="250"/> 
   2. StromPi 3
   
        <img src="doc/assembly_cybercube/IMG_1261.JPG" width="250"/> <img src="doc/assembly_cybercube/IMG_1260.JPG" width="250"/> 
   3. Waveshare Ethernet/USB Hub-Hat
   
        <img src="doc/assembly_cybercube/IMG_1270.JPG" width="250"/> <img src="doc/assembly_cybercube/IMG_1271.JPG" width="250"/> 
   4. LoRa-Hat
   
        <img src="doc/assembly_cybercube/IMG_1262.JPG" width="250"/> <img src="doc/assembly_cybercube/IMG_1263.JPG" width="250"/> 
   5. GPS-Module
   
        <img src="doc/assembly_cybercube/IMG_1272.JPG" width="250"/> <img src="doc/assembly_cybercube/IMG_1273.JPG" width="250"/> 
   6. Sense-Hat
   
        <img src="doc/assembly_cybercube/IMG_1267.JPG" width="250"/> <img src="doc/assembly_cybercube/IMG_1269.JPG" width="250"/> 
        
   7. SD-Card
   
        <img src="doc/assembly_cybercube/sd_card_front.JPG" width="250"/> <img src="doc/assembly_cybercube/sd_card_back.JPG" width="250"/> 
  
   8. Fan
   
        <img src="doc/assembly_cybercube/fan_front.JPG" width="250"/> <img src="doc/assembly_cybercube/fan_back.JPG" width="250"/> 

Before you assemble the main components it is higly recommended to prepare the components first, this includes the cybercube power supply and the GPS cable.

# 1. GPS-cable:

First, you need a USB-A cable, a GNSS connector, and cables as well as soldering equipment. 
You start by cutting the USB-A cable to a length of 4-5cm. After cutting you prepare the USB cable for soldering. 
This preparation includes pulling the cable cover (about 1cm) and removing the aluminum protection as well as the small copper cables. Additionally,
you cut off the glass fiber and remove the cable cover from each cable. 

To prepare the cables coming from the GNSS connector you only have to remove the individual cable covers, cut the 
cables coming from the middle of the connector and cut the other cables to a length of 4-6cm. 

Before soldering the two ends together it is highly recommended to twist the cable ends and to apply tin on each cable. **Be aware of the cable order.** You should also use a shrinking tube for each cable to prevent any unwanted interferences between the different cables. 

If you are using a 5-PIN connector you need to follow the cable order shown below. 

|GNSS side   | A     | B     | C   | D     | E    | 
|---         | :---: |:---:  |:---:|:---:  |:---: | 
|USB side    | white | green |*cut*| black | red  |

<img src="doc/assembly_cybercube/GNSS_Wires.png"/>  

If you are using a 6-PIN connector you need to solder the cables together according to the order below.

|GNSS side   | clock     | A     | B   | C     | D    |  E    |
|---         | :---: |:---:  |:---:|:---:  |:---: | :---: |
|USB side    | - | white |green| *cut* | black  |  red  |

The clock cable does not need to be connected to the USB cable and can therefore be ignored.

After soldering all necessary cables together it is recommended to form a small loop with the cables coming from the GNSS connector and use a larger shrinking tube. This prevents any strain on a specific cable and protects the connection. 
The 6-PIN connector can only be oriented the right way,  **if you are using the 5-PIN connector, make sure that the connector is correctly oriented (black / "E", aligned left)**


# 2. Power supply
The power supply consists of two cable branches. Prepare them seperately.

## **Positive branch**

Front             |  TOP
:-------------------------:|:-------------------------:
<img src="doc/assembly_cybercube/positive_branch_front.png" width="500"/>  |  <img src="doc/assembly_cybercube/positive_branch_top.png" width="500"/>





You start by cutting the cable (red, 1mm^2) to an appropriate length (about 20 - 25 cm). After that, you remove about 1 cm of the cable cover on both sides and apply tin on **one** of these ends. 

<img src="doc/assembly_cybercube/IMG_1325.JPG" width="400"/>

The end **with** the pre-applied tin needs to be soldered to a sleeve connector.

<img src="doc/assembly_cybercube/cable_red_sleeve.JPG" width="400"/>

After soldering, you may test the connection by pulling on the cable. 
Now you start to prepare the other cable of the branch which is used for the cybercube. First, you assemble a small fuse (this prevents high currents from destroying the cybercube´s components).

<img src="doc/assembly_cybercube/IMG_1347.JPG" width="400"/>

The fuse is connected with two black cables. On one end you need to twist the cable end, apply tin, and solder the end to a small connecting pin. 

<img src="doc/assembly_cybercube/IMG_1328.JPG" width="400"/>

The small pin connector will later be part of the power supply for the cybercube. 
To connect the black cable with the fuse and the red cable with the pin attached we space out the little cables peeking out of the cable ends. 

<img src="doc/assembly_cybercube/IMG_1344.JPG" width="400"/>

We then twist them into each other. 

<img src="doc/assembly_cybercube/IMG_1345.JPG" width="400"/>  |  <img src="doc/assembly_cybercube/IMG_1346.JPG" width="400"/>

After that, we connect the cables permanently with a ferrule. 

<img src="doc/assembly_cybercube/IMG_1356.JPG" width="400"/>

To prevent any damage to the connection, we use a small shrinking tube to protect the cables.

<img src="doc/assembly_cybercube/IMG_1357.JPG" width="400"/>

## **Negative branch**

Front             |  TOP
:-------------------------:|:-------------------------:
<img src="doc/assembly_cybercube/negative_branch_front.png" width="500"/>  |  <img src="doc/assembly_cybercube/negative_branch_top.png" width="500"/>

The negative cable is much more straightforward. You start by preparing one black cable (1 mm^2). Cut the cable to the same length as the red cable before. Follow by removing the cable cover on both sides (about 1 cm). 

<img src="doc/assembly_cybercube/IMG_1321.JPG" width="400"/>

Twist the small cables on one of the ends and apply tin as you did on the first cable. You then solder this end to a sleeve connector.

<img src="doc/assembly_cybercube/cable_black_sleeve.JPG" width="400"/>

After that, you need a second black cable which you cut to an appropriate length (14 - 16 cm) (power supply for the cybercube, about the same length as the cable with the fuse). You remove the cable covers on both ends (1 cm), then apply tin on one side and solder a small pin connector to the end. 

<img src="doc/assembly_cybercube/IMG_1328.JPG" width="400"/>

As the last step, you need to space out the little cables coming from the loose ends of the cables and twist them into each other. 

<img src="doc/assembly_cybercube/IMG_1364.JPG" width="400"/>  |  <img src="doc/assembly_cybercube/IMG_1366.JPG" width="400"/>

You then connect them, using once again a ferrule. 

<img src="doc/assembly_cybercube/IMG_1367.JPG" width="400"/>

To prevent any damage to the connection, we use a small shrinking tube to protect the cables.

<img src="doc/assembly_cybercube/IMG_1369.JPG" width="400"/>

After preparing both branches, you may connect the long red cable and the long black cable to the Bulgin connector. For an example of the assembly of the Bulgin connector, see table below. 

|1| 2    | 3   | 4   | 5     | 6    | 
|:----:| :---: |:---:  |:---:|:---:  |:---: | 
| <img src="doc/assembly_cybercube/bulgin_1.JPG" width="250"/> | <img src="doc/assembly_cybercube/bulgin_2.JPG" width="250"/> |<img src="doc/assembly_cybercube/bulgin_3.JPG" width="250"/>| <img src="doc/assembly_cybercube/bulgin_4.JPG" width="250"/> | <img src="doc/assembly_cybercube/bulgin_5.JPG" width="250"/>  | <img src="doc/assembly_cybercube/bulgin_6.JPG" width="250"/>


|7| 8    | 9   | 10  |11     | 12    | 
|:---:| :---: |:---:  |:---:|:---:  |:---: | 
| <img src="doc/assembly_cybercube/bulgin_7.JPG" width="250"/> | <img src="doc/assembly_cybercube/bulgin_8.JPG" width="250"/> |<img src="doc/assembly_cybercube/bulgin_9.JPG" width="250"/>| <img src="doc/assembly_cybercube/bulgin_10.JPG" width="250"/> | <img src="doc/assembly_cybercube/bulgin_11.JPG" width="250"/>  | <img src="doc/assembly_cybercube/bulgin_12.JPG" width="250"/>


<img src="doc/assembly_cybercube/MSB_power_supply.png" width="400"/>

After that, you may plug in the small pin connector of the two remaining cables into the connector for the cybercube´s power supply. 

<img src="doc/assembly_cybercube/cybercube_power_supply.png" width="400"/> | <img src="doc/assembly_cybercube/power_supply.png" width="400"/>



# 3. Electronic stack

After preparing the necessary parts you may start by screwing the four spacers into the Raspberry Pi. 

<img src="doc/assembly_cybercube/IMG_1277.JPG" width="500"/>

You continue by connecting the StromPi with the Raspberry Pi through the 40-Pin connector. Then you attach the power supply cable to the StromPi. 

<img src="doc/assembly_cybercube/IMG_1290.JPG" width="500"/>

On top of the StromPi you put the LoRa-Hat, also connected through the 40-Pin connector.

<img src="doc/assembly_cybercube/IMG_1292.JPG" width="500"/>

Now you need to use a 40-Pin extension which is plugged into the 40-Pin connector of the LoRa-Hat. 

<img src="doc/assembly_cybercube/IMG_1293.JPG" width="500"/>

After that, you connect the Sense-Hat to the 40-Pin Adapter.

<img src="doc/assembly_cybercube/IMG_1294.JPG" width="500"/>

Now you put 4 bolts (M2,5) into the spacings of the stack sides (top).

<img src="doc/assembly_cybercube/Stack_seite_links.PNG" width="400"/> <img src="doc/assembly_cybercube/Stack_seite_rechts.PNG" width="400"/>

As the last step, you connect the antenna with the approriate connector on the LoRa-Hat. To connect the USB-Hat, hold the USB-Hat against the underside of the Raspberry Pi and put one side of the stack into the 
stack attachment. Then you attach the other side attachment to the stack and start by screwing in the 4 screws at the 
bottom. 

<img src="doc/assembly_cybercube/IMG_1296.JPG" width="500"/>

You follow with the 4 screws on the top and connect the USB-A cable with the USB-A port of the StromPi. 

<img src="doc/assembly_cybercube/IMG_1298.JPG" width="500"/>

Before you can put the electronic stack into the cybercube housing, you need to first screw in the bulgin connector into the cybercube´s side.

<img src="doc/assembly_cybercube/cybercube_housing.png" width="500"/>

After that, you connect the cables (power supply) with the bulgin connector. Now, you may put the electronic stack into the cybercube´s housing. Put the GPS-module into it´s recess and connect the GPS-module with it´s specific connector. Put the end of the antenna cable into the hole of the cybercube´s lid. For better cooling it is also possible to attach a little fan to the inner side of the lid.

<img src="doc/assembly_cybercube/fan.png" width="500"/>

Now you may close the cybercube´s lid with four screws and connect a ethernet cable with the ethernet port (The GPS-module is partly hold in place by the cybercube´s lid. The GPS-Module must be placed above the litte support structure.)

<img src="doc/assembly_cybercube/gps_cut.jpg" width="500"/>

Connect a short camera cable to the port of the cybercube by using the small slit on the cybercube´s side. Place the end of the short cable into the small 3D-Printed support piece.

<img src="doc/assembly_cybercube/assembly_10.JPG" width="400"/>  <img src="doc/assembly_cybercube/assembly_11.JPG" width="400"/>

You have now completed the cybercube assembly and may now start with the assembly of the inner components.

<img src="doc/assembly_cybercube/cybercube_assembly.png" width="800"/>

## Assembly of inner components

### The inner components are:

   1. base-Plate (3D-Print)

<img src="doc/assembly_cybercube/baseplate.png" width="400"/>
   
   2. coverplate (3D-Print)

<img src="doc/assembly_cybercube/coverplate.png" width="400"/>

   3. case 

<img src="doc/assembly_cybercube/case_iso.jpg" width="400"/>
   
   4. case lid

<img src="doc/assembly_cybercube/case_lid_iso.jpg" width="400"/>

   6. 6x spacer bolds

<img src="doc/assembly_cybercube/spacer_iso.jpg" width="400"/>

   7. camera (glass, cable, lens)

<img src="doc/assembly_cybercube/camera_iso.jpg" width="400"/>

   8. battery

<img src="doc/assembly_cybercube/battery_iso.jpg" width="400"/>

   9. power supply

<img src="doc/assembly_cybercube/positive_branch_top.png" width="400"/> <img src="doc/assembly_cybercube/negative_branch_top.png" width="400"/>

   10. 2x antennas

<img src="doc/assembly_cybercube/antennas.jpg" width="400"/>

   11. internet stick

<img src="doc/assembly_cybercube/usb.jpg" width="400"/>

   12. ethernet extension

<img src="doc/assembly_cybercube/ethernet.jpg" width="400"/>

   13. LoRa-Antenna

<img src="doc/assembly_cybercube/LoRa-Antenna.jpg" width="400"/>

   14. screws and nuts

   15. short camera cable

   16. long camera cable 

   17. cybercube

<img src="doc/assembly_cybercube/cybercube_assembly.png" width="400"/>

   18. USB-cable and Ethernet-cable
### Assembly:

1. Drill a hole into the case, for the ethernet port.

<img src="doc/assembly_cybercube/assembly_0.png" width="400"/>

2. You start by mounting the camera glass and the camera holder. 

<img src="doc/assembly_cybercube/assembly_1.jpg" width="400"/>

3. Then you mount the camera on the camera holder. 

<img src="doc/assembly_cybercube/assembly_2.jpg" width="400"/>

4. You place the camera cable into the camera cable channel of the baseplate.

<img src="doc/assembly_cybercube/assembly_3.jpg" width="400"/>

5. Prepare the case by screwing in the camera glass

<img src="doc/assembly_cybercube/assembly_4.jpg" width="400"/>

6. After that, you follow by putting the baseplate into the case and connect the camera with the cable 

<img src="doc/assembly_cybercube/assembly_5.jpg" width="400"/>

7. Install the ethernet extension.

<img src="doc/assembly_cybercube/assembly_7.jpg" width="400"/>

8. Install the two branches for the power supply. 

# Main Assembly:

1. Insert the battery into the baseplate's battery compartment

<img src="doc/assembly_cybercube/assembly_8.jpg" width="400"/>

2. Screw in the six spacers. 

3. Insert the cybercube into the baseplate

<img src="doc/assembly_cybercube/assembly_9.jpg" width="600"/>

4. Connect the camera cable (comming from the camera) with the connector.

<img src="doc/assembly_cybercube/assembly_11.JPG" width="400"/>

5. Connect a USB-cable with the USB-port facing the side of the case. Connect a Wifi-Stick with this USB-cable.

6. Screw the LoRa-Antenna into the cybercube´s lid. 

<img src="doc/assembly_cybercube/assembly_12.JPG" width="400"/> <img src="doc/assembly_cybercube/assembly_13.JPG" width="400"/>

7. Screw two antennas into the case lid.

<img src="doc/assembly_cybercube/assembly_14.jpg" width="400"/>

8. Connect all electrical components (WIFI-Stick with Antennas, Ethernet-cable into Ethernet-Port)

<img src="doc/assembly_cybercube/assembly_15.jpg" width="400"/>

9. Close the baseplate with the coverplate and secure it´s fit with six screws. 

<img src="doc/assembly_cybercube/assembly_16.jpg" width="400"/>

10. Attach the latch and the lid of the case. 

<img src="doc/assembly_cybercube/assembly_17.jpg" width="1000"/>

**Congratulations! You completed the hardware assembly.**


