# Dummy_Device
#### Before using this example, please install the python modules 'requests' and 'paho-mqtt (~=2.1.0)' correctly.


  `pip install requests paho-mqtt~=2.1.0`
    

Modify your user-defined code in "SA.py", and execute "DAI.py" to run the DA by `python DAI.py`

If you change the file name of SA.py to i.e., "new_SA.py", you can execute it by `python DAI.py new_SA`.

#### SA's routine jobs can be written in on_register().
https://github.com/IoTtalk/Dummy_Device_IoTtalk_v1_py/blob/7591046a34a7e3f5b6855eec51f67946c051c8ee/SA.py#L23C5-L23C20

#### For long-running applications, Agent.py can assistant you to run and monitor DAI.py. Agent.py has three abilities.
1. Monitor the execution state of DAI.py. If DAI.py is dead or crash, Agent.py executes DAI.py again.
2. Restart DAI.py at a specified time everyday.
3. If the server is out of service for a while (longer than 15 seconds),  once the server is back, Agent.py will restart DAI.py to make sure the connection is good.

To execute DAI.py by Agent.py, you just run Agent.py by `python Agent.py`.
