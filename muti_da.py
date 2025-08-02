import requests, time, subprocess, shlex, signal, sys
from datetime import datetime as dt
from datetime import timedelta as td

PYTHON = 'python3'
DAIpath = r'./DAI.py' #NOTE: Slash in Uinx is '/', and is '\' in Windows.

def activate_one_da(args):
    proc = subprocess.Popen(args)
    return proc

if __name__ == '__main__':
    if len(sys.argv)>1: num_of_da = int(sys.argv[1])
    else: num_of_da = 10

    option = '{} {}'.format(PYTHON, DAIpath)
    args = shlex.split(option)
    proc_list = []
    for p in range(num_of_da):
        p_id = activate_one_da(args)
        proc_list.append(p_id)
        time.sleep(0.5)

    signal.pause()







