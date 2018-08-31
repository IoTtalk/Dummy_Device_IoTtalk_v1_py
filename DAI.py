import time, DAN, requests, random

# Change to your IoTtalk IP or None for autoSearching
# Use (http/https)://(domain/IP)[:port]
# ex: http://192.168.1.1:9999
#     https://test.domain
ServerIP = ''
Reg_addr = None #None # if None, Reg_addr = MAC address

profile = {
    'dm_name': 'Dummy_Device',
    'df_list': ['Dummy_Sensor', 'Dummy_Control'],
    'd_name': None # None for autoNaming
}
dan = DAN.DAN(profile, ServerIP, Reg_addr)
dan.device_registration_with_retry()

while True:
    try:
    #Pull data from a device feature called "Dummy_Control"
        value1=dan.pull('Dummy_Control')
        if value1 != None:
            print (value1[0])

    #Push data to a device feature called "Dummy_Sensor"
        value2=random.uniform(1, 10)
        dan.push ('Dummy_Sensor', value2)

    except Exception as e:
        print(e)
        dan.device_registration_with_retry()

    time.sleep(0.2)
