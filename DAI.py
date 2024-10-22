import re, time, json, threading, requests, traceback, sys, importlib
from datetime import datetime as dt
import paho.mqtt.client as mqtt

def df_func_name(df_name):
    return re.sub(r'-', r'_', df_name)

def on_connect(client, userdata, flags, reason_code, properties):
    #print(f"Connected with result code: {reason_code}")
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        print('[{}] MQTT broker: {}'.format(dt.now().strftime('%Y-%m-%d %H:%M:%S'), MQTT_broker))
        if ODF_list == []:
            print('ODF_list is not exist.')
            return
        topic_list=[]
        for odf in ODF_list:
            topic = '{}//{}'.format(device_id, odf)
            topic_list.append((topic,0))
        if topic_list != []:
            client.subscribe(topic_list)

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    # Since we subscribed only for a single channel, reason_code_list contains
    # a single entry
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        #print(f"Broker granted the following QoS: {reason_code_list[0].value}") 
        pass

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print('[{}] MQTT disconnected.'.format(dt.now().strftime('%Y-%m-%d %H:%M:%S')))

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
    sample = [str(dt.today()), data]
    payload  = json.dumps({'samples':[sample]})
    msg_info = client.publish(topic, payload)
    #print(msg_info)

def on_publish(client, userdata, mid, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to publish: {reason_code}.")

def check_df_funcs_exist(IDF_list, ODF_list):
    for idf in IDF_list:
        if not IDF_funcs.get(idf):
            print('IDF function "{}" is not existed. IDF Pass.'.format(idf))
    for odf in ODF_list:
        if not ODF_funcs.get(odf):
            print('ODF function "{}" is not existed. ODF Pass.'.format(odf))

def on_register(result):
    func = getattr(SA, 'on_register', None)
    print(f'[{dt.now().strftime("%Y-%m-%d %H:%M:%S")}] Register successfully. {result["server"]}')
    time.sleep(0.3)
    if func: func(result)



def MQTT_config(client, MQTT_broker, MQTT_port, MQTT_User, MQTT_PW, MQTT_encryption):
    client.username_pw_set(MQTT_User, MQTT_PW)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish
    if MQTT_encryption: client.tls_set()
    client.connect(MQTT_broker, MQTT_port, keepalive=60)

def push(idf, IDF_data):
    MQTT_broker = getattr(SA,'MQTT_broker', None)
    if MQTT_broker:
        MQTT_port = getattr(SA,'MQTT_port', 1883)
        MQTT_User = getattr(SA,'MQTT_User', None)
        MQTT_PW = getattr(SA,'MQTT_PW', None)
        MQTT_encryption = getattr(SA,'MQTT_encryption', None)
        device_id = getattr(SA,'device_id', None)
        if device_id==None: device_id = DAN.get_mac_addr()
        mqttc = mqtt.Client()
        MQTT_config(mqttc, MQTT_broker, MQTT_port, MQTT_User, MQTT_PW, MQTT_encryption)
        if type(IDF_data) is not tuple and type(IDF_data) is not list  : IDF_data=[IDF_data]
        mqtt_pub(mqttc, device_id, idf, IDF_data)
    else: 
        DAN.push(idf, IDF_data)

def DF_function_handler(mqttc):
    for idf in IDF_list:
        if not IDF_funcs.get(idf): continue
        IDF_data = IDF_funcs.get(idf)()
        if IDF_data == None: continue
        if type(IDF_data) is not tuple: IDF_data=[IDF_data]
        if MQTT_broker: mqtt_pub(mqttc, device_id, idf, IDF_data)
        else: DAN.push(idf, IDF_data)
        time.sleep(0.001)
    if not MQTT_broker: 
        for odf in ODF_list:
            if not ODF_funcs.get(odf): continue
            ODF_data = DAN.pull(odf)
            if ODF_data == None: continue
            ODF_funcs.get(odf)(ODF_data)
            time.sleep(0.001)

def reconnect(client):
    client.disconnect()
    time.sleep(0.5)
    print('[{}] MQTT reconnect...'.format(dt.now().strftime('%Y-%m-%d %H:%M:%S')))
    while True:
        try:
            client.reconnect()
            t = threading.Thread(target=mqttc.loop_forever)
            t.daemon = True
            t.start()
            break
        except BaseException as err:
            ExceptionHandler(err)
    time.sleep(0.5)

def ExceptionHandler(err, ServerURL=None, device_id=None, mqttc=None):
    if isinstance(err, KeyboardInterrupt):
        DAN.deregister()
        print(' Bye~')
        exit()
    elif str(err).find('mac_addr not found:') != -1 or str(err).find('RECONNECT') != -1:
        print('Device ID is not found. Try to re-register...')
        result = DAN.device_registration_with_retry(ServerURL, device_id)
        #if mqttc: reconnect(mqttc)
        print(f'[{dt.now().strftime("%Y-%m-%d %H:%M:%S")}] {result}')
    else:
        exception = traceback.format_exc()
        print(exception)
        time.sleep(1)    

import DAN
SA_module_name = 'SA'
if len(sys.argv)>1: SA_module_name = ((sys.argv[1]).split('.'))[0]    
SA = importlib.import_module(SA_module_name)

def main(ServerURL, device_id, exec_interval, mqttc):
    while True:
        try:
            DF_function_handler(mqttc)
            if DAN.iottalk_server_disconnect == True:
                ExceptionHandler('RECONNECT', ServerURL, device_id, mqttc)
            time.sleep(exec_interval)
        except BaseException as err:
            ExceptionHandler(err, ServerURL, device_id, mqttc)

if __name__ == '__main__':
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
    DAN.profile['dm_name'] = device_model
    DAN.profile['df_list'] = IDF_list + ODF_list
    if device_name: DAN.profile['d_name']= device_name
    if MQTT_broker: DAN.profile['mqtt_enable'] = True

    check_df_funcs_exist(IDF_list, ODF_list)
    result = DAN.device_registration_with_retry(ServerURL, device_id)   

    mqttc = None
    if MQTT_broker:
        mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        MQTT_config(mqttc, MQTT_broker, MQTT_port, MQTT_User, MQTT_PW, MQTT_encryption)
    
    sa_p = threading.Thread(target=on_register, args=(result,))
    sa_p.daemon = True
    sa_p.start()    
    
    main_p = threading.Thread(target=main, args=(ServerURL, device_id, exec_interval, mqttc))
    main_p.daemon = True 
    main_p.start()
    
    if MQTT_broker:
        try:
            mqttc.loop_forever()
        except BaseException as err:  
            ExceptionHandler(err)          
    else:
        main_p.join()
        
