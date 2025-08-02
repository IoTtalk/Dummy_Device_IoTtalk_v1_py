import random 
import uuid

ServerURL = 'https://class.iottalk.tw' #For example: 'https://DomainName'
MQTT_broker = 'iot.iottalk.tw' # MQTT Broker address, for example: 'DomainName' or None = no MQTT support
MQTT_port = 8883
MQTT_encryption = True
MQTT_User = 'iottalk'
MQTT_PW = 'iottalk2023'

device_model = 'Dummy_Device'
ODF_list = ['Dummy_Sensor']
device_id = str(uuid.uuid4())#if None, device_id = MAC address
device_name = device_id 
exec_interval = 1  # IDF/ODF interval

def Dummy_Sensor(data):
    print(data)

def on_register(r):
    print(f'Device name: {r["d_name"]}')    
    import time, DAI, numpy as np

    fixed_time_interval = None #seconds 
    LAMBDA=4 # 4 times per minutes, i.e., 15 seconds.
    tts = 0 # time to send
    if fixed_time_interval: print('Using fixed time interval:', fixed_time_interval, 'seconds.')
    else: print('Using Poisson distribution, the mean of interval is', (1/LAMBDA)*60, 'seconds.')

    while True:
        if time.time() < tts: 
            time.sleep(0.1)
            continue

        #在 Poisson 過程中，第 1 次事件發生的時間（也就是 Poisson 過程第一次跳躍的時間）服從 exponential distribution
        #描Exponential 分布述兩次事件之間的時間間隔（也就是Poisson 過程中第一次事件發生要等多久）
        #Using Poisson distribution
        if fixed_time_interval: t_interval = fixed_time_interval
        else: t_interval = (np.random.exponential(1/LAMBDA)*60) # seconds
        for idx in range(1,6):
            DAI.push('Dummy_Sensor', [random.randint(20, 40), idx, t_interval, device_id])         
            time.sleep(0.05)
        tts = time.time() + t_interval   

