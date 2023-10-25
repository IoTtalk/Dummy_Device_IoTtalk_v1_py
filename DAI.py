import re, time, json, threading, requests, traceback
from datetime import datetime
import paho.mqtt.client as mqtt
import DAN, SA

def df_func_name(df_name):
    return re.sub(r'-', r'_', df_name)

MQTT_broker = getattr(SA,'MQTT_broker', None)
MQTT_port = getattr(SA,'MQTT_port', 1883)
MQTT_User = getattr(SA,'MQTT_User', None)
MQTT_PW = getattr(SA,'MQTT_PW', None)
MQTT_encryption = getattr(SA,'MQTT_encryption', None)
device_model = getattr(SA,'device_model', None)
device_name = getattr(SA,'device_name', None)
ServerURL = getattr(SA,'ServerURL', None)
device_id = getattr(SA,'device_id', None)
if device_id==None: device_id = DAN.get_mac_addr()
IDF_list = getattr(SA,'IDF_list', [])
ODF_list = getattr(SA,'ODF_list', [])
exec_interval = getattr(SA,'exec_interval', 1)
IDF_funcs = {}
for idf in IDF_list:
    IDF_funcs[idf] = getattr(SA, df_func_name(idf), None)
ODF_funcs = {}
for odf in ODF_list:
    ODF_funcs[odf] = getattr(SA, df_func_name(odf), None)

def on_connect(client, userdata, flags, rc):
    if not rc:
        print('MQTT broker: {}'.format(MQTT_broker))
        if ODF_list == []:
            print('ODF_list is not exist.')
            return
        topic_list=[]
        for odf in ODF_list:
            topic = '{}//{}'.format(device_id, odf)
            topic_list.append((topic,0))
        if topic_list != []:
            r = client.subscribe(topic_list)
            if r[0]: print('Failed to subscribe topics. Error code:{}'.format(r))
    else: print('Connect to MQTT borker failed. Error code:{}'.format(rc))
        
def on_disconnect(client, userdata,  rc):
    print('MQTT Disconnected. Re-connect...')
    client.reconnect()

def on_message(client, userdata, msg):
    samples = json.loads(msg.payload)
    ODF_name = msg.topic.split('//')[1]
    if ODF_funcs.get(ODF_name):
        ODF_data = samples['samples'][0][1]
        ODF_funcs[ODF_name](ODF_data)
    else:
        print('ODF function "{}" is not existed.'.format(ODF_name))

def mqtt_pub(client, deviceId, IDF, data):
    topic = '{}//{}'.format(deviceId, IDF)
    sample = [str(datetime.today()), data]
    payload  = json.dumps({'samples':[sample]})
    status = client.publish(topic, payload)
    if status[0]: print('topic:{}, status:{}'.format(topic, status))

def on_register(result):
    func = getattr(SA, 'on_register', None)
    if func: func(result)

def MQTT_config(client):
    client.username_pw_set(MQTT_User, MQTT_PW)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    if MQTT_encryption: client.tls_set()
    client.connect(MQTT_broker, MQTT_port, keepalive=60)

DAN.profile['dm_name'] = device_model
DAN.profile['df_list'] = IDF_list + ODF_list  
if device_name: DAN.profile['d_name']= device_name
if MQTT_broker: DAN.profile['mqtt_enable'] = True

result = DAN.device_registration_with_retry(ServerURL, device_id)
on_register(result)

if MQTT_broker:
    mqttc = mqtt.Client()
    MQTT_config(mqttc)
    mqttc.loop_start()

def DF_function_handler():
    for idf in IDF_list:
        if not IDF_funcs.get(idf): 
            print('IDF function "{}" is not existed.'.format(idf))
            continue
        IDF_data = IDF_funcs.get(idf)()
        if IDF_data == None: continue
        if type(IDF_data) is not tuple: IDF_data=[IDF_data]
        if MQTT_broker: mqtt_pub(mqttc, device_id, idf, IDF_data)
        else: DAN.push(idf, IDF_data)
        time.sleep(0.001)
    if not MQTT_broker: 
        for odf in ODF_list:
            if not ODF_funcs.get(odf): 
                print('ODF function "{}" is not existed.'.format(odf))
                continue
            ODF_data = DAN.pull(odf)
            if ODF_data == None: continue
            ODF_funcs.get(odf)(ODF_data)
            time.sleep(0.001)

def ExceptionHandler(err):
    if isinstance(err, KeyboardInterrupt):
        DAN.deregister()
        print(' Bye~')
        exit()
    elif str(err).find('mac_addr not found:') != -1:
        print('Reg_addr is not found. Try to re-register...')
        DAN.device_registration_with_retry(ServerURL, device_id)
    else:
        exception = traceback.format_exc()
        print(exception)
        time.sleep(1)    
    if MQTT_broker: mqttc.reconnect()

if __name__ == '__main__':
    while True:
        try:
            DF_function_handler()
            time.sleep(exec_interval)
        except BaseException as err:
            ExceptionHandler(err)
