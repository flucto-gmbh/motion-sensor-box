# Architecture

## Hardware

## Software

The software needed to run the motion sensor box is subdivided into a number of systemd service units. The reasoning behind this architecture is the following:

1. complexity: dissecting the software into pieces, each focusing on one single task allows for compartmentalization of the overall complexity
2. robustness: implementing each task as single service that communicates with the broker will increase overall robustness. If a service fails, it will (hopefully) not impair other services (except for the ones directly depending on the failed service)
3. extensibility: adding or removing a serivce is much easier

All interprocess communication between services is implemented using [zeroMQ](https://zeromq.org/)

![software_architecture](./doc/software_architecture.png)

### List of Services

- **msb_imu.service:** manages the inertial measurement uni present on the sense hat. For more documentation, please see [doc/waveshare_sense_hat/ICM-20948.md](doc/waveshare_sense_hat/ICM-20948.md). Code is located at [src/imu](src/imu)
- **msb_gps.service:** samples gnss data from `gpsd`'s socket and provides it to other motion sensor box services. Further documentation is available [here](doc/gpsd/gpds.md). Code is located at [src/gps](src/gps)
- **msb_broker.service:** Creates and manages the publisher/subscriber model of motion sensor box services. code is located at [src/broker](src/broker)
- **msb_fusionlog.service:** Subscribes to **all** available data and logs it to a specified location on disc. source is located at [src/fusionlog](src/fusionlog)

### Data format

Each process must provide its data in the form of a json package:

```javascript
// inertial measurement unit
{
    "imu" : [timestamp, uptime, acc_x, acc_y, acc_z, rot_x, rot_y, rot_z, mag_x, mag_y, mag_z, temp]
}

// gpsd data
{
    "gnss" : 
}
```
