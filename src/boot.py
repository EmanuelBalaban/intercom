import gc

def connect_to_wifi():
    import network, time
    import config

    print("Connecting to WiFi")

    wlan = network.WLAN(network.WLAN.IF_STA)
    wlan.active(config.ENABLE_WIFI)

    if not config.ENABLE_WIFI:
        return
    
    # Reset connection status
    if wlan.isconnected():
        wlan.disconnect()
        return
    
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWD)

    while not wlan.isconnected():
        time.sleep(0.1)

    
    if wlan.status() == network.STAT_GOT_IP:
        print("Successfully connected to Wi-Fi network!")
        print("IP Address: {}".format(wlan.ifconfig()[0]))

connect_to_wifi()

gc.collect()

try:
    import ntptime

    print("Updating time from NTP server...")
    ntptime.settime()
except:
    print("Failed to update time from NTP server...")