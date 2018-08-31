import requests
import threading

from functools import wraps

session_pool = {}

class CSMError(Exception):
    pass

def session_wrapper(func):

    @wraps(func)
    def wrap(interface, *args, **kwargs):
        global session_pool
        t_id = threading.get_ident()
        if t_id in (session_pool):
            session = session_pool.get(t_id)
        else:
            session = requests.Session()
            session_pool[t_id] = session

        if not interface.host:
            raise CSMError('no host given')

        if interface.session:
            result = func(interface, *args, **kwargs)
        else:
            interface.session = session

            try:
                result = func(interface, *args, **kwargs)
            except Exception as e:
                if interface.session:
                    interface.session = None

                raise e

            interface.session = None

        return result

    return wrap


class CSMAPI():
    def __init__(self, host):
        self.TIMEOUT = 10
        self.host = host
        self.session = None
        self.password = None

    @session_wrapper
    def register(self, mac_addr, profile):
        url = '{host}/{mac_addr}'.format(
            host=self.host,
            mac_addr=mac_addr
        )
        response = self.session.post(
            url,
            json={'profile': profile},
            timeout=self.TIMEOUT
        )

        response.close()
        if response.status_code != 200:
            raise CSMError(response.text)

        self.password = response.json().get('password')
        return True

    @session_wrapper
    def deregister(self, mac_addr):
        url = '{host}/{mac_addr}'.format(
            host=self.host,
            mac_addr=mac_addr
        )
        response = self.session.delete(url)

        response.close()
        if response.status_code != 200:
            raise CSMError(response.text)

        return True

    @session_wrapper
    def push(self, mac_addr, df_name, data):
        url = '{host}/{mac_addr}/{df_name}'.format(
            host=self.host,
            mac_addr=mac_addr,
            df_name=df_name
        )
        response = self.session.put(
            url,
            json={'data': data},
            headers = {'password-key': self.password},
            timeout=self.TIMEOUT
        )

        response.close()
        if response.status_code != 200:
            raise CSMError(response.text)

        return True

    @session_wrapper
    def pull(self, mac_addr, df_name):
        url = '{host}/{mac_addr}/{df_name}'.format(
            host=self.host,
            mac_addr=mac_addr,
            df_name=df_name
        )
        response = self.session.get(
            url,
            headers = {'password-key': self.password},
            timeout=self.TIMEOUT
        )

        response.close()
        if response.status_code != 200:
            raise CSMError(response.text)

        return response.json()['samples']

    @session_wrapper
    def get_alias(self, mac_addr, df_name):
        url = '{host}/get_alias/{mac_addr}/{df_name}'.format(
            host=self.host,
            mac_addr=mac_addr,
            df_name=df_name
        )
        response = self.session.get(
            url,
            timeout=self.TIMEOUT)

        response.close()
        if response.status_code != 200:
            raise CSMError(response.text)

        return response.json()['alias_name']

    @session_wrapper
    def set_alias(self, mac_addr, df_name, new_alias):
        url = '{host}/set_alias/{mac_addr}/{df_name}/alias?name={new_alias}'.format(
            host=self.host,
            mac_addr=mac_addr,
            df_name=df_name,
            new_alias=new_alias
        )
        response = self.session.get(
            url,
            timeout=self.TIMEOUT)

        response.close()
        if response.status_code != 200:
            raise CSMError(response.text)
        return True

    @session_wrapper
    def tree(self):
        url = '{host}/tree'.format(host=self.host)
        response = self.session.get(url)

        response.close()
        if response.status_code != 200:
            raise CSMError(response.text)

        return response.json()
