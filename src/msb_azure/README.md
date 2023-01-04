# msb_azure
Motion sensor box azure connectivity

## prerequisities
To successfully connect a motion sensor box to an Azure IoT-Hub, the `azure-iot-device` python package needs to be installed:

```bash
pip3 install azure-iot-device --user
```

Further, a connectivity string for the IoT edge device is needed to successfully send data to the IoT-Hub. To set the connectivity string, copy the following into bash and replace all in quotes with the respective connectivity string:

```bash
export IOTHUB_DEVICE_CONNECTION_STRING="<your_connection_string_here>"
```

To test if the string is correct, run the `test_msb_connectivity.py` available in the `test` directory:
```bash
python test/test_msb_connectivity.py
```


