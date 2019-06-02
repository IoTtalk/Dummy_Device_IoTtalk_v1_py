import requests

ENDPOINT = None
TIMEOUT=10
IoTtalk = requests.Session()
passwordKey = None

class CSMError(Exception):
    pass

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


def deregister(mac_addr, UsingSession=IoTtalk):
    r = UsingSession.delete(ENDPOINT + '/' + mac_addr)
    if r.status_code != 200: raise CSMError(r.text)
    return True


def push(mac_addr, df_name, data, UsingSession=IoTtalk):
    r = UsingSession.put(
        ENDPOINT + '/' + mac_addr + '/' + df_name,
        json={'data': data},
        timeout=TIMEOUT,
        headers = {'password-key': passwordKey}
    )
    if r.status_code != 200: raise CSMError(r.text)
    return True


def pull(mac_addr, df_name, UsingSession=IoTtalk):
    r = UsingSession.get(
        ENDPOINT + '/' + mac_addr + '/' + df_name,
        timeout=TIMEOUT,
        headers = {'password-key': passwordKey}
    )
    if r.status_code != 200: raise CSMError(r.text)
    return r.json()['samples']


def get_alias(mac_addr, df_name, UsingSession=IoTtalk):
    r = UsingSession.get(ENDPOINT + '/get_alias/' + mac_addr + '/' + df_name, timeout=TIMEOUT)
    if r.status_code != 200: raise CSMError(r.text)
    return r.json()['alias_name']

	
def set_alias(mac_addr, df_name, s, UsingSession=IoTtalk):
    r = UsingSession.get(ENDPOINT + '/set_alias/' + mac_addr + '/' + df_name + '/alias?name=' + s, timeout=TIMEOUT)
    if r.status_code != 200: raise CSMError(r.text)
    return True

	
def tree(UsingSession=IoTtalk):
    r = UsingSession.get(ENDPOINT + '/tree')
    if r.status_code != 200: raise CSMError(r.text)
    return r.json()

	
