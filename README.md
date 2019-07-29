# the_pad

## Install

You can install as package from pip.

1. First connect to the REPL with a serial terminal.
2. Connect to wifi

```python
import network

SSID = <WIFI SSID>
PWD = <WIFI PASSWORD>

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect(SSID, PWD)
    while not wlan.isconnected():
        pass
print('network config:', wlan.ifconfig())
```

```python
import upip
upip.install('micropython-the-pad')
```