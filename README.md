# Dummy_Device
This is a DA example with ControlChannels.

Changes:
1. Separate sessions into  data and control sessions:
    This version adds two sessions, data and control sessions. The data session is used for data transmission (reg/push/pull/dereg). The control session is used for push/pull I/O control channels. (In the earier version, both data and control transmission uses the same session, and causes some issues.)

2. The control channel will create only one threading.
