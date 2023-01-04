# MQTT client for Motion Sensor Box in project WindIO

In the project WindIO measurements are conducted using motion sensor boxes. They send their data to a digital twin using the MQTT protocol.

WindIO's digital twin is being developed at https://github.com/project-windio/wt-digital-twin .

Motion Sensor Box is an open-source design: https://github.com/flucto-gmbh/motion-sensor-box

## Concept of client

Motion Sensor Box uses ZMQ for internal datastreams.

The MQTT client  listen to ZMQ to receive live data and sends them via MQTT to the WindIO broker.

An example payload is shown in [example_payload.json](example_payload.json).

This issue describes the idea: https://github.com/flucto-gmbh/motion-sensor-box/issues/27

## Installation on sensor box

Clone the package:

```
git clone https://github.com/ahaselsteiner/mqtt-client-msb.git
```

Install the requirements:

```
pip install -r requirements.txt
```

Adapt the config to fit the specific sensor box by opening the JSON config file:

```
nano src/msb_mqtt.json
```

## Run the client

```
python src/msb_mqtt.py
```
