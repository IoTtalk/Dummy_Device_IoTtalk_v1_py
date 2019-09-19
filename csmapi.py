import requests
'''把網路請求的函式庫加進來'''
ENDPOINT = None
TIMEOUT=10
IoTtalk = requests.Session()
passwordKey = None
'''
斷點參數
逾時參數
透過session語法讓一些請求參數能夠保存(通常用於登入)
密碼參數
'''
class CSMError(Exception):
    pass

'''
錯誤
'''

def register(mac_addr, profile, UsingSession=IoTtalk):
    global passwordKey
    r = UsingSession.post(
        ENDPOINT + '/' + mac_addr,
        json={'profile': profile}, timeout=TIMEOUT
    )
    if r.status_code != 200: raise CSMError(r.text)
    else: 
        passwordKey = r.json().get('password')
        d_name = r.json().get('d_name')
    return d_name

'''
叫做register的函式，引入三個參數
將密碼設為全域變數
r為網路請求session下的post要求，發出斷點參數、mac位址、逾時參數
並取得profile資訊的json
如果r狀態不等於200，報錯
其餘狀況下
將密碼參數設置為r發送中的密碼參數並從jaon解碼
將d_mane參數設置為r發送中的d_name(應該是你的裝置名稱)
'''
def deregister(mac_addr, UsingSession=IoTtalk):
    r = UsingSession.delete(ENDPOINT + '/' + mac_addr)
    if r.status_code != 200: raise CSMError(r.text)
    return True
'''
取消註冊
r為刪除session中的斷點、mac位址
如果狀態代碼不為200，報錯
回傳真
'''

def push(mac_addr, df_name, data, UsingSession=IoTtalk):
    r = UsingSession.put(
        ENDPOINT + '/' + mac_addr + '/' + df_name,
        json={'data': data},
        timeout=TIMEOUT,
        headers = {'password-key': passwordKey}
    )
    if r.status_code != 200: raise CSMError(r.text)
    return True
'''
push，透過mac、df名稱、資料、初始的session
進行put要求，發送斷點、mac、df名稱
資料的json
頭中用密碼
返回真

'''

def pull(mac_addr, df_name, UsingSession=IoTtalk):
    r = UsingSession.get(
        ENDPOINT + '/' + mac_addr + '/' + df_name,
        timeout=TIMEOUT,
        headers = {'password-key': passwordKey}
    )
    if r.status_code != 200: raise CSMError(r.text)
    return r.json()['samples']
'''
pull，透過mac、df名稱、資料、初始的session
進行get要求，發送斷點、mac、df名稱
資料的json
頭中用密碼
返回取得的資料並解碼
'''


def get_alias(mac_addr, df_name, UsingSession=IoTtalk):
    r = UsingSession.get(ENDPOINT + '/get_alias/' + mac_addr + '/' + df_name, timeout=TIMEOUT)
    if r.status_code != 200: raise CSMError(r.text)
    return r.json()['alias_name']
"""
如果有別的要取得的資料
回傳新的欄位名
"""
	
def set_alias(mac_addr, df_name, s, UsingSession=IoTtalk):
    r = UsingSession.get(ENDPOINT + '/set_alias/' + mac_addr + '/' + df_name + '/alias?name=' + s, timeout=TIMEOUT)
    if r.status_code != 200: raise CSMError(r.text)
    return True
"""
設定替代欄位的名稱
"""
	
def tree(UsingSession=IoTtalk):
    r = UsingSession.get(ENDPOINT + '/tree')
    if r.status_code != 200: raise CSMError(r.text)
    return r.json()

"""
tree函式，暫時還不知道後面會出現在哪裡
進行一個呼叫
"""	
