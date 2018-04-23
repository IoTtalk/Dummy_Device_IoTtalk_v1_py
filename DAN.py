import random
import threading
import time

from csmapi import CSMAPI
# example
"""
profile = {
    'd_name': None,
    'dm_name': 'MorSensor',
    'u_name': 'yb',
    'is_sim': False,
    'df_list': ['Acceleration', 'Temperature'],
}
"""


class DAN():
    def __init__(self, profile, host, mac_addr):
        self.profile = profile
        if host:
            self.csmapi = CSMAPI('http://{host}:9999'.format(host=host))
        else:
            self.detect_local_ec()

        if mac_addr:
            self.mac_addr = mac_addr
        else:
            self.mac_addr = DAN.get_mac_addr()

        # for control channel
        self.state = 'SUSPEND'
        # self.state = 'RESUME'

        self.selected_DF = set()
        self.pre_data_timestamp = {}
        self.control_channel_timestamp = None
        self.control_channel_thread = None

    @staticmethod
    def get_mac_addr():
        from uuid import getnode
        mac = getnode()
        mac = ''.join(("%012X" % mac)[i:i + 2] for i in range(0, 12, 2))
        return mac

    def control_channel(self):
        while True:
            time.sleep(2)
            try:
                cc = self.csmapi.pull(self.mac_addr, '__Ctl_O__')
                if not cc:
                    continue

                if self.control_channel_timestamp == cc[0][0]:
                    continue

                self.control_channel_timestamp = cc[0][0]
                self.state = cc[0][1][0]
                if self.state == 'SET_DF_STATUS':
                    self.csmapi.push(self.mac_addr,
                                     '__Ctl_I__',
                                     ['SET_DF_STATUS_RSP',
                                      {'cmd_params': cc[0][1][1]['cmd_params']}])
                    df_status = list(cc[0][1][1]['cmd_params'][0])

                    self.selected_DF.clear
                    for index, status in enumerate(df_status):
                        if status == '1':
                            self.selected_DF.add(self.profile['df_list'][index])
            except Exception as e:
                print ('Control error', e)

    def detect_local_ec(self):
        import socket
        udp_ip = ''
        udp_port = 17000

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((udp_ip, udp_port))

        while True:
            print ('Searching for the IoTtalk server...')
            data, addr = s.recvfrom(1024)
            if str(data.decode()) == 'easyconnect':
                self.csmapi.host = 'http://{}:9999'.format(addr[0])
                break

    def register_device(self):
        """
        profile = {
            'd_name': None,
            'dm_name': 'MorSensor',
            'u_name': 'yb',
            'is_sim': False,
            'df_list': ['Acceleration', 'Temperature'],
        }
        """
        if not self.profile.get('dm_name'):
            raise Exception('dm_name should be given in profile.')

        if not self.profile.get('d_name'):
            self.profile['d_name'] = str(int(random.uniform(1, 100))) + '.' + self.profile['dm_name']

        if not self.profile.get('u_name'):
            self.profile['u_name'] = 'yb'

        if not self.profile.get('is_sim'):
            self.profile['is_sim'] = False

        if not self.profile.get('df_list'):
            raise Exception('df_list should be given in profile.')

        print('IoTtalk Server = {}'.format(self.csmapi.host))
        if self.csmapi.register(self.mac_addr, self.profile):
            print ('This device has successfully registered.')
            print ('Device name = ' + self.profile['d_name'])

            if self.control_channel_thread is None:
                print ('Create control threading')
                # for control channel
                self.control_channel_thread = threading.Thread(target=self.control_channel)
                self.control_channel_thread.daemon = True
                self.control_channel_thread.start()

            return True
        else:
            print ('Registration failed.')
            return False

    def device_registration_with_retry(self):

        while True:
            try:
                if self.register_device():
                    break
            except Exception as e:
                print ('Attach failed: '),
                print (e)
            time.sleep(1)

    def pull(self, df_name):
        if self.state == 'RESUME':
            data = self.csmapi.pull(self.mac_addr, df_name)
            if self.pre_data_timestamp.get(df_name) != data[0][0]:
                self.pre_data_timestamp[df_name] = data[0][0]

                if data[0][1]:
                    return data[0][1]

        return None

    def pull_with_timestamp(self, df_name):
        if self.state == 'RESUME':
            data = self.csmapi.pull(self.mac_addr, df_name)
            if self.pre_data_timestamp.get(df_name) != data[0][0]:
                self.pre_data_timestamp[df_name] = data[0][0]

                if data[0][1]:
                    return (data[0][0], data[0][1])

        return None

    def push(self, df_name, *data):
        if self.state == 'RESUME':
            return self.csmapi.push(self.mac_addr, df_name, list(data))

        return None

    def get_alias(self, df_name):
        try:
            alias = self.csmapi.get_alias(self.mac_addr, df_name)
        except Exception as e:
            # print (e)
            return None

        return alias

    def set_alias(self, df_name, new_alias_name):
        try:
            alias = self.csmapi.set_alias(self.mac_addr, df_name, new_alias_name)
        except Exception as e:
            # print (e)
            return None

        return alias

    def deregister(self):
        return self.csmapi.deregister(self.mac_addr)
