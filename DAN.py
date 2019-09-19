import time, random, threading, requests
import csmapi

# example
profile = {
#    'd_name': None,
    'dm_name': 'MorSensor',
    'u_name': 'yb',
    'is_sim': False,
    'df_list': ['Acceleration', 'Temperature'],
}
mac_addr = None
'''
範例，建立一個字典
設定裝置名稱
使用者名稱
一個未動用的函數
裝置狀態名

宣告一個mac位址
'''
state = 'SUSPEND'     #for control channel
#state = 'RESUME'

SelectedDF = []
'''
建立一個空的字典
'''
def ControlChannel():
    global state, SelectedDF
    print('Device state:', state)
    NewSession=requests.Session()
    control_channel_timestamp = None
    while True:
        time.sleep(2)
        try:
            CH = csmapi.pull(MAC,'__Ctl_O__', NewSession)
            if CH != []:
                if control_channel_timestamp == CH[0][0]: continue
                control_channel_timestamp = CH[0][0]
                cmd = CH[0][1][0]
                if cmd == 'RESUME':  
                    print('Device state: RESUME.') 
                    state = 'RESUME'
                elif cmd == 'SUSPEND': 
                    print('Device state: SUSPEND.') 
                    state = 'SUSPEND'
                elif cmd == 'SET_DF_STATUS':
                    csmapi.push(MAC,'__Ctl_I__',['SET_DF_STATUS_RSP',{'cmd_params':CH[0][1][1]['cmd_params']}], NewSession)
                    DF_STATUS = list(CH[0][1][1]['cmd_params'][0])
                    SelectedDF = []
                    index=0            
                    profile['df_list'] = csmapi.pull(MAC, 'profile')['df_list']              #new
                    for STATUS in DF_STATUS:
                        if STATUS == '1':
                            SelectedDF.append(profile['df_list'][index])
                        index=index+1
        except Exception as e:
            print ('Control error:', e)
            if str(e).find('mac_addr not found:') != -1:
                print('Reg_addr is not found. Try to re-register...')
                device_registration_with_retry()
            else:
                print('ControlChannel failed due to unknow reasons.')
                time.sleep(1)    
'''
這個叫做控制頻道的function
宣告兩個全域變數
引印出裝置狀態
定義網路請求session
定義控制頻道的時間戳記

當回傳為真
每次間隔為兩秒
嘗試透過mac跟session進行csmapi資料提取

如果取回的資料不為空(還是不為陣列?)則進行下面的一些形況判斷或報錯
'''


def get_mac_addr():
    from uuid import getnode
    mac = getnode()
    mac = ''.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
    return mac

'''
生成一個mac位址
'''

def detect_local_ec():
    EASYCONNECT_HOST=None
    import socket
    UDP_IP = ''
    UDP_PORT = 17000
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((UDP_IP, UDP_PORT))
    while EASYCONNECT_HOST==None:
        print ('Searching for the IoTtalk server...')
        data, addr = s.recvfrom(1024)
        if str(data.decode()) == 'easyconnect':
            EASYCONNECT_HOST = 'http://{}:9999'.format(addr[0])
            csmapi.ENDPOINT=EASYCONNECT_HOST
            #print('IoTtalk server = {}'.format(csmapi.ENDPOINT))

'''
確認本地位址
'''

timestamp={}
MAC=get_mac_addr()
thx=None

'''
變數的宣告
'''
def register_device(addr):
    global MAC, profile, timestamp, thx

    if csmapi.ENDPOINT == None: detect_local_ec()

    if addr != None: MAC = addr

    for i in profile['df_list']: timestamp[i] = ''

    print('IoTtalk Server = {}'.format(csmapi.ENDPOINT))
    profile['d_name'] = csmapi.register(MAC,profile)
    print ('This device has successfully registered.')
    print ('Device name = ' + profile['d_name'])
         
    if thx == None:
        print ('Create control threading')
        thx=threading.Thread(target=ControlChannel)     #for control channel
        thx.daemon = True                               #for control channel
        thx.start()                                     #for control channel 

'''
註冊此裝置
'''
def device_registration_with_retry(URL=None, addr=None):
    if URL != None:
        csmapi.ENDPOINT = URL
    success = False
    while not success:
        try:
            register_device(addr)
            success = True
        except Exception as e:
            print ('Attach failed: '),
            print (e)
        time.sleep(1)
'''
重試連結
'''
def pull(FEATURE_NAME):
    global timestamp

    if state == 'RESUME': data = csmapi.pull(MAC,FEATURE_NAME)
    else: data = []
        
    if data != []:
        if timestamp[FEATURE_NAME] == data[0][0]:
            return None
        timestamp[FEATURE_NAME] = data[0][0]
        if data[0][1] != []:
            return data[0][1]
        else: return None
    else:
        return None
'''
在可繼續狀態下取值
'''
def push(FEATURE_NAME, *data):
    if state == 'RESUME':
        return csmapi.push(MAC, FEATURE_NAME, list(data))
    else: return None
'''
在可繼續狀態下發送list中的資料
'''
def get_alias(FEATURE_NAME):
    try:
        alias = csmapi.get_alias(MAC,FEATURE_NAME)
    except Exception as e:
        #print (e)
        return None
    else:
        return alias
'''
取得一個別名
'''
def set_alias(FEATURE_NAME, alias):
    try:
        alias = csmapi.set_alias(MAC, FEATURE_NAME, alias)
    except Exception as e:
        #print (e)
        return None
    else:
        return alias
'''
建立別名
'''
		
def deregister():
    return csmapi.deregister(MAC)
'''
取消註冊，調用csma裡面的取消註冊功能
'''
