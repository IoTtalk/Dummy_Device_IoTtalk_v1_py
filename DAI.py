import time, random, requests
import DAN
'''
導入時間、隨機、網路要求函式庫
導入DAN
'''
ServerURL = 'http://IP:9999'      #with non-secure connection
#ServerURL = 'https://DomainName' #with SSL connection
'''
選用兩種不型態的連結
'''
Reg_addr = None #if None, Reg_addr = MAC address
'''
設定mac adress
'''
DAN.profile['dm_name']='Dummy_Device'
DAN.profile['df_list']=['Dummy_Sensor', 'Dummy_Control',]
#DAN.profile['d_name']= 'Assign a Device Name' 
'''
設定自己跟要感測的裝置的名稱
'''
DAN.device_registration_with_retry(ServerURL, Reg_addr)
#DAN.deregister()  #if you want to deregister this device, uncomment this line
#exit()            #if you want to deregister this device, uncomment this line

while True:
    try:
        IDF_data = random.uniform(1, 10)
        DAN.push ('Dummy_Sensor', IDF_data) #Push data to an input device feature "Dummy_Sensor"

        #==================================

        ODF_data = DAN.pull('Dummy_Control')#Pull data from an output device feature "Dummy_Control"
        if ODF_data != None:
            print (ODF_data[0])
'''
當為真的時候不斷嘗試對IDF賦予一個值
不斷地對DS發送這個值
也不斷地把值從DC抓下來
如果ODF抓不到，就印出第一格的值
'''
    except Exception as e:
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)    

    time.sleep(0.2)

'''
如果發生了甚麼神奇的錯誤
印出錯誤
如果是mac錯誤就印出原因
是其他原因就推給其他人
最後讓他進入下一次之前留個0.2秒
'''
