import random 

ServerURL = '' #For example: 'https://DomainName'
MQTT_broker = None # MQTT Broker address, for example: 'DomainName' or None = no MQTT support
MQTT_port = 1883
MQTT_encryption = False
MQTT_User = 'ID'
MQTT_PW = 'PW'

device_model = 'Dummy_Device'
IDF_list = ['Dummy_Sensor']
ODF_list = ['Dummy_Control']
device_id = None #if None, device_id = MAC address
device_name = None
exec_interval = 1  # IDF/ODF interval

def on_register(r):
    print('Server: {}\nDevice name: {}'.format(r['server'], r['d_name']))

def Dummy_Sensor():
    return random.randint(0, 100), random.randint(0, 100) 

def Dummy_Control(data:list):
    print(data[0])
