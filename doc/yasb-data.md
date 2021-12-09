# Motion sensor box datastructure

The motion sensor boxes transmit the following data. 

- **Acceleration vector**
- **Velocity vector**
- **Position vector**
- **Orientation Vector**
- **GNSS**
- Pressure
- Humidity
- Temperature
- ... 
  
Independent of the interface used, sensor recordings are transmitted/stored as a JSON record. In the following, acceleration data is shown in the correpsonding format. 


```
{
    # unique ID of the recording device
    'uID' : 'HASH',
    
    # timestamp at which the data was recorded
    'timestamp' : time.time(),
    
    # data label to add a identfier to the data
    'data_label' = 'acceleration',

    # data record
    'data_value' : 
        # a data record starts with a data_name field, followed by an arbitrary number of data entries 
        {
            'X' : float()
            'Y' : float()
            'Z' : float()
        },
        
    # data unit vector, describing the SI-Units of the transmitted data        
    #   kg  m   s  T  Ca  A Deg
    # [  0, 1, -2, 0,  0, 0   0 ]
    # for each data record, a corresponding units vector needs to be specified
    'data_units' : 
        {
            'X' : [ 0, 1, -2, 0,  0, 0   0],
            'Y' : [ 0, 1, -2, 0,  0, 0   0],
            'Z' : [ 0, 1, -2, 0,  0, 0   0],
        },
}
```

## Format of log file
MSB writes a log file, which uses a different format.
Each line represents one measurement value.

### IMU
```
imu: [unix epoch, uptime in seconds, accx, accy, accz, rotx_speed, roty_speed, rotz_speed, magnet_fieldx, magnet_fieldy, magnet_fieldz]
unit: [X, s, m/s2, m/s2, m/s2, deg/s, deg/s, deg/s, mu tesla, mu tesla, mu tesla]
```

### GPS
```
gps: [unix epoch, uptime in seconds, JSON from receiver]
```

JSON keys from receiver: 
 - 'mode' = [0,3], 0 = I have nothing, 1 = I have time fix (one satellite), 2 = 2D fix (at least two satellites), 3 = 3D fix (more than two satellites)
 - 'tune' = unix epoch in an ISO format (jahr-monat-tagThh:minmin:secsec:timezone)
 - 'leapseconds' = Schaltsekunden
 - 'ept' = we dont know
 - 'lat' = latitude
 - 'lon' = longitude
 - 'altHAE' = altitude
 - 'altMSL' = altitude from mean sea level
 - 'epx', 'epy' = current size of error (m)
 - 'epv' = current size of error (m/s)
 - 'magvar' = correction factor for lat/lon


