import random 

ServerURL = 'https://iottalk.tw'
MQTT_broker = 'iottalk.tw'
MQTT_port = 5566 
MQTT_encryption = True

device_model = 'Dummy_Device'
IDF_list = ['Dummy_Sensor']
ODF_list = ['Dummy_Control']
device_id = None #if None, device_id = MAC address
device_name = None
exec_interval = 1  # IDF/ODF interval

def on_register(r):
    print('Server: {}\nDevice name: {}\nRegister successfully.'.format(r['server'], r['d_name']))

def Dummy_Sensor():
    return random.randint(0, 100), random.randint(0, 100), random.randint(0, 100), random.randint(0, 100) 

def Dummy_Control(data:list):
    print(data[0])
