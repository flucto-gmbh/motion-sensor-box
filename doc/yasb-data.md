# YASB Data

The YASB boxes transmit the following data. 

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


