# Assembly guide for the msb rev8´s cybercube

## The cybercube consists of the following electronic components:

   1. Raspberry Pi Zero W V 1.1
   
        <img src="img/IMG_1264.JPG" width="250"/> <img src="img/IMG_1266.JPG" width="250"/> 
   2. StromPi 3
   
        <img src="img/IMG_1261.JPG" width="250"/> <img src="img/IMG_1260.JPG" width="250"/> 
   3. Waveshare Ethernet/USB Hub-Hat
   
        <img src="img/IMG_1270.JPG" width="250"/> <img src="img/IMG_1271.JPG" width="250"/> 
   4. LoRa-Hat
   
        <img src="img/IMG_1262.JPG" width="250"/> <img src="img/IMG_1263.JPG" width="250"/> 
   5. GPS-Module
   
        <img src="img/IMG_1272.JPG" width="250"/> <img src="img/IMG_1273.JPG" width="250"/> 
   6. Sense-Hat
   
        <img src="img/IMG_1267.JPG" width="250"/> <img src="img/IMG_1269.JPG" width="250"/> 
   7. SD-Card
   8. Fan

Before you assemble the main components it is recommended to prepare the components first, this includes the cybercube power supply and the GPS cable.

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

<img src="img/GNSS_Wires.png"/>  
and pull the shrink tubing over the cables before beeing soldered together. **Before using the GPS-Module make sure that the GNSS connector is correctly oriented.** 

# 2. Cybercube power supply
................




After preparing the necessary parts you may start by screwing the four spacers into the Raspberry Pi. 

<img src="img/IMG_1277.JPG" width="500"/>

You continue by connecting the StromPi with the Raspberry Pi through the 40-Pin connector. Then you attach the power supply cable to the StromPi. 

<img src="img/IMG_1290.JPG" width="500"/>

On top of the StromPi you put the LoRa-Hat, also connected though the 40-Pin connector.

<img src="img/IMG_1292.JPG" width="500"/>

Now you need to use a 40-Pin extension which is plugged into the the 40-Pin connector of the LoRa-Hat. 

<img src="img/IMG_1293.JPG" width="500"/>

After that  you connect the Sense-Hat to the 40-Pin Adapter.

<img src="img/IMG_1294.JPG" width="500"/>

As the last step you hold the USB-Hat against the underside of the Raspberry Pi and put one side of the stack into the 
stack attachmant. Then you attach the other side attachmant to the stack and start by screwing in the 4 screws at the 
bottom. 

<img src="img/IMG_1296.JPG" width="500"/>

You follow with the 4 screws on the top and connect the USB-A cable with the USB-A port of the StromPi. 

<img src="img/IMG_1298.JPG" width="500"/>

After connecting all electronic parts within the cybercube you put the electronic stack into the cybercube housing. Now you may close the cybercube´s lid with four screws. 

<img src="img/IMG_1236.JPG" width="500"/>




