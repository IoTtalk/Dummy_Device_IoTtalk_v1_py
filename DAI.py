import re, time, json, threading, requests
from datetime import datetime
import paho.mqtt.client as mqtt
import DAN, SA

def df_func_name(df_name):
    return re.sub(r'-', r'_', df_name)

def on_connect(client, userdata, flags, rc):
    if not rc:
        print('MQTT broker: {}'.format(SA.MQTT_broker))
        topic_list=[]
        for odf in SA.ODF_list:
            topic = '{}//{}'.format(SA.device_id, odf)
            topic_list.append((topic,0))
        if topic_list != []:
            r = client.subscribe(topic_list)
            if r[0]: print('Failed to subscribe topics. Error code:{}'.format(r))
    else: print('Connect to MQTT borker failed. Error code:{}'.format(rc))
        
def on_disconnect(client, userdata,  rc):
    print('MQTT Disconnected. Re-connect...')
    client.connect(SA.MQTT_broker, SA.MQTT_port, keepalive=60)

def on_message(client, userdata, msg):
    samples = json.loads(msg.payload)
    ODF_name = msg.topic.split('//')[1]
    ODF_func = getattr(SA, df_func_name(ODF_name), None)
    if ODF_func:
        ODF_data = samples['samples'][0][1]
        ODF_func(ODF_data)

def mqtt_pub(client, deviceId, IDF, data):
    topic = '{}//{}'.format(deviceId, IDF)
    sample = [str(datetime.today()), data]
    payload  = json.dumps({'samples':[sample]})
    status = client.publish(topic, payload)
    if status[0]: print('topic:{}, status:{}'.format(topic, status))

def on_register(result):
    if SA.MQTT_broker: result['MQTT_broker'] = SA.MQTT_broker
    SA.on_register(result)

def MQTT_config(client):
    client.username_pw_set(SA.MQTT_User, SA.MQTT_PW)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    if SA.MQTT_encryption: client.tls_set()
    client.connect(SA.MQTT_broker, SA.MQTT_port, keepalive=60)

if SA.MQTT_broker:
    mqttc = mqtt.Client()
    MQTT_config(mqttc)
    qt = threading.Thread(target=mqttc.loop_forever)
    qt.daemon = True
    qt.start()
    time.sleep(1)
    
DAN.profile['dm_name'] = SA.device_model
DAN.profile['df_list'] = SA.IDF_list + SA.ODF_list
if SA.device_name: DAN.profile['d_name']= SA.device_name
if SA.MQTT_broker: DAN.profile['mqtt_enable'] = True

result = DAN.device_registration_with_retry(SA.ServerURL, SA.device_id)
on_register(result)

while True:
    try:
        for idf in SA.IDF_list:
            IDF_func = getattr(SA, df_func_name(idf), None)
            if not IDF_func: continue
            IDF_data = IDF_func()
            if not IDF_data: continue
            if type(IDF_data) is not tuple: IDF_data=[IDF_data]
            if SA.MQTT_broker: mqtt_pub(mqttc, SA.device_id, idf, IDF_data)
            else: DAN.push(idf, IDF_data)
            time.sleep(0.001)

        if not SA.MQTT_broker: 
            for odf in SA.ODF_list:
                ODF_func = getattr(SA, df_func_name(odf), None)
                ODF_data = DAN.pull(odf)
                if not ODF_data: continue
                ODF_func(ODF_data)
                time.sleep(0.001)

    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(SA.ServerURL, SA.device_id)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)    

    time.sleep(SA.exec_interval)

