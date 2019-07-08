
def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('essid', 'password')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())


def do_webrepl():
	import webrepl
	import machine
	webrepl.start()
	pwd = machine.unique_id()
	# or, start with a specific password
	webrepl.start(password=pwd)

def no_debug():
    import esp
    # this can be run from the REPL as well
    esp.osdebug(None)
