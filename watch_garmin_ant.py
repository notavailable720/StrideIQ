import time
import requests
from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.heart_rate import HeartRate, HeartRateData

# --- CONFIGURE THESE ---
SERVER_URL = "http://<YOUR_SERVER_IP>:8000/api/hr_data"  # replace with your own server's LAN IP
DEVICE_ID = "G1"  # pick a new ID and add it (+ name + zones) to roster in server.py
# ------------------------


def on_found():
    print("Strap found, receiving broadcast...")


def on_device_data(page: int, page_name: str, data):
    if isinstance(data, HeartRateData):
        hr = data.heart_rate
        payload = {
            "device_id": DEVICE_ID,
            "heart_rate": hr,
            "timestamp": int(time.time()),
        }
        try:
            requests.post(SERVER_URL, json=payload, timeout=2)
            print(f"Sent: {hr} BPM")
        except Exception as e:
            print(f"Could not reach server: {e}")


node = Node()
node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

# device_id set to your specific strap's ANT+ ID (found via `openant scan`)
# avoids a wildcard-search-then-reconnect step that was erroring out
device = HeartRate(node, device_id=3212)
device.on_found = on_found
device.on_device_data = on_device_data

print("Starting ANT+ HR bridge... (Press Ctrl+C to stop)")
try:
    node.start()
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    device.close_channel()
    node.stop()
