# Thanks to https://www.hivemq.com/blog/mqtt-client-library-paho-python/
# See example titled "Subscribe"

import paho.mqtt.client as paho
import json, os.path


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))    


with open(os.path.dirname(__file__) + '/../msb_mqtt.json') as json_file:
    config = json.load(json_file)
    print('Working with config:')
    print(config)
    user = config['user']
    password = config['password']
    url = config['url']
    port = config['port']
    edge_id = config['edge_id']
    device_id = config['device_id']
    mqtt_topic = "ppmpv3/3/DDATA/" + edge_id + "/" + device_id


client = paho.Client()
client.on_subscribe = on_subscribe
client.on_message = on_message
client.username_pw_set(user, password)
client.connect(url, port)
client.subscribe(mqtt_topic, qos=1)

client.loop_forever()