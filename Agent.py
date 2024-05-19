PYTHON = 'python'
DAIpath = r'.\\DAI.py' #NOTE: Slash in Uinx is '/', and is '\' in Windows.
RestartTime = '03:00'

import requests, time, subprocess, shlex
from datetime import datetime as dt
from datetime import timedelta as td

import SA

def IsServerAlive(ServerURL):
    Alive = False
    S = requests.Session()
    try:
        r = S.get( ServerURL, timeout=10)
        #print('State code: {}'.format(r.status_code))
        if r.status_code == 200: Alive = True
        if r.status_code == 403: print('403 Forbidden. Should you use HTTPS connection?')
    except Exception as e:
        #print (e)
        pass
    S.close()
    return Alive

def restartDA(DAIpath, proc=None):
    if proc: 
        try:
            subprocess.Popen.kill(proc)
            print('Kill existed DA. DA Restarting ...')
        except Exception as e:
            print (e)
    option = '{} {}'.format(PYTHON, DAIpath)
    print(option)
    args = shlex.split(option)
    proc = subprocess.Popen(args)
    return proc

def checkTime(RestartTime):
    second_delta = 600 
    try:
        RT = dt.strptime(RestartTime,'%H:%M')
    except Exception as e:
        print('Please specify a correct RestartTime format in "config.py".')
        return False
    NowT = dt.strptime(dt.now().strftime('%H:%M:%S'), '%H:%M:%S')
    if RT < NowT and RT+td(seconds=second_delta) > NowT :
        return True
    else:
        return False



URL = SA.ServerURL
conn_check_interval = 30
conn_retry_interval = 5 
DEADcount=0
RestartFlag=False
proc = restartDA(DAIpath)
while True:
    if IsServerAlive(URL):
       # print ('Server is alive. Sleep 5 seconds.')
        if DEADcount > 2: proc = restartDA(DAIpath, proc)
        DEADcount=0

        proc_state = proc.poll()
        if proc_state:
            print('DA is dead. ReturnCode: {}'.format(proc.returncode))
            proc = restartDA(DAIpath, proc)

        if RestartTime and checkTime(RestartTime): 
            if not RestartFlag:
                 RestartFlag = True
                 proc = restartDA(DAIpath, proc)
        elif RestartFlag: RestartFlag=False

        time.sleep(conn_check_interval)
    else:
        print ('[{}] Connection loss. Retry after {} second.'.format(dt.now().strftime('%Y-%m-%d %H:%M:%S'), conn_retry_interval))
        DEADcount += 1
        time.sleep(conn_retry_interval)
