from uuid import uuid4
import random 

ServerURL = 'https://URL' #For example: 'https://DomainName'
MQTT_broker = None # MQTT Broker address, for example: 'DomainName' or None = no MQTT support
MQTT_port = 1883
MQTT_encryption = False
MQTT_User = 'ID'
MQTT_PW = 'PW'

device_model = 'Dummy_Device'
IDF_list = ['Dummy_Sensor']
ODF_list = ['Dummy_Control']
device_id = uuid4().hex #if None, device_id = MAC address
device_name = None
exec_interval = 1  # IDF/ODF interval

def Dummy_Sensor():
    #After obtaining the IDF value (e.g., a sensor value), simply use return value to send the value back to the IoTtalk platform.
    value = random.randint(0, 100), random.randint(0, 100)  #Multidimensional data can be returned as "," comma-separated values.
    return value

def Dummy_Control(data:list):
    #The ODF value from IoTtalk is automatically assigned to the "data" variable.
    #The "data" variable is then used in the required actuator function.
    #The type of "data" variable is LIST.
    print(data[0])

def on_register(r):
    print(f'Device name: {r["d_name"]}')    
    '''
    #You can write some SA routine code here, for example: 
    import time, DAI
    while True:
        DAI.push('Dummy_Sensor', [100, 200])  
        time.sleep(exec_interval)    
    '''


