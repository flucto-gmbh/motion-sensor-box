# Hardware assembly

The Motion-Sensor-Box may be subdivided in the cybercube and all the other inner components within the housing. 
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
   8. Fan

Before you assemble the main components it is higly recommended to prepare the components first, this includes the cybercube power supply and the GPS cable.

# 1. GPS-cable:

First you need a USB-A cable, a GNSS connector and cables as well as soldering equipment. 
You start by cutting the USB-A cable to a length of 6-8cm. After cutting you prepare the USB for soldering. 
This preparation includes pulling of the cable cover (about 1cm) and removing the aluminum protection. Additionally
you cut off the glass fiber and remove the cable cover from each cable. 

To prepare the cables comming from the GNNSS connector you only have to remove the individual cable cover, cut the 
cables coming from the middle of the connector and cut the other cables to a length of 4-6cm. 

Before soldering the two ends together it is highly recommended to twist the cable ends and to apply tin on each cable. **Be aware of the cable order** 
|GNSS side   | A     | B     | C   | D     | E    | 
|---         | :---: |:---:  |:---:|:---:  |:---: | 
|USB side    | white | green |*cut*| black | red  |

<img src="doc/assembly_cybercube/GNSS_Wires.png"/>  
and pull the shrink tubing over the cables before beeing soldered together. 
**Before using the GPS-Module make sure that the GNSS connector is correctly oriented.** 

# 2. Cybercube power supply
................




After preparing the necessary parts you may start by screwing the four spacers into the Raspberry Pi. 

<img src="doc/assembly_cybercube/IMG_1277.JPG" width="500"/>

You continue by connecting the StromPi with the Raspberry Pi through the 40-Pin connector. Then you attach the power supply cable to the StromPi. 

<img src="doc/assembly_cybercube/IMG_1290.JPG" width="500"/>

On top of the StromPi you put the LoRa-Hat, also connected though the 40-Pin connector.

<img src="doc/assembly_cybercube/IMG_1292.JPG" width="500"/>

Now you need to use a 40-Pin extension which is plugged into the the 40-Pin connector of the LoRa-Hat. 

<img src="doc/assembly_cybercube/IMG_1293.JPG" width="500"/>

After that  you connect the Sense-Hat to the 40-Pin Adapter.

<img src="doc/assembly_cybercube/IMG_1294.JPG" width="500"/>

As the last step you hold the USB-Hat against the underside of the Raspberry Pi and put one side of the stack into the 
stack attachmant. Then you attach the other side attachmant to the stack and start by screwing in the 4 screws at the 
bottom. 

<img src="doc/assembly_cybercube/IMG_1296.JPG" width="500"/>

You follow with the 4 screws on the top and connect the USB-A cable with the USB-A port of the StromPi. 

<img src="doc/assembly_cybercube/IMG_1298.JPG" width="500"/>

After connecting all electronic parts within the cybercube you put the electronic stack into the cybercube housing. Now you may close the cybercube´s lid with four screws. 

<img src="doc/assembly_cybercube/IMG_1236.JPG" width="500"/>


## Assembly of the inncomponents

### The inner components are:

   1. base-Plate (3D-Print)
   <img src="doc/assembly_cybercube/baseplate_render.png" width="250"/>
   
   2. coverplate (3D-Print)
   <img src="doc/assembly_cybercube/coverplate_render.png" width="250"/>
   
   3. housing 
   <img src="doc/assembly_cybercube/MSB-Hülle_Front.jpg" width="250"/>
   
   4. housing´s Lid
   5. spacer Bolds
   6. camera (glass, cable, lense)
   <img src="doc/assembly_cybercube/camera.png" width="250"/>
   
   7. battery
   8. power supply
   9. screws and nuts

### Assembly guide for the inner components:

1. You start by mounting the camera glass and the camera holder. 

2. Then you mount the camara on the camera holder. 

3. You follow by mounting the six spacers in to the housing. 

<img src="doc/assembly_cybercube/housing_with_spacers.PNG" width="250"/>

4. Then you insert the camera cable in the base plate's camera cable channel. After that you connect the camera cable with the camera.

5.Insert the base plate into the housing.

<img src="doc/assembly_cybercube/housing_with_baseplate.PNG" width="250"/>

## Main Assembly:

1. Insert the battery into the base plate's battery compartement
<img src="doc/assembly_cybercube/housing_with_baseplate_battery.PNG" width="500"/>

2. Insert the Cybercube into the baseplate
<img src="doc/assembly_cybercube/housing_with_baseplate_battery_cybercube.PNG" width="500"/>

3. Close the compartement 
<img src="doc/assembly_cybercube/housing_with_coverplate.PNG" width="500"/>

4.Screw in the two WLAN-Antenna

<img src="doc/assembly_cybercube/housing_with_coverplate_antenna.PNG" width="500"/>

5.Attach the case lid 

<img src="doc/assembly_cybercube/housing_with_coverplate_antenna_lid.PNG" width="500"/>



