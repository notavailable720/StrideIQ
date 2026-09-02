import asyncio
import time
import requests
from bleak import BleakScanner, BleakClient

# --- CONFIGURE THESE ---
SERVER_URL = "http://<YOUR_SERVER_IP>:8000/api/hr_data"  # replace with your own server's LAN IP
DEVICE_ID = "G1"  # pick a new ID and add it (+ name + zones) to roster in server.py
# ------------------------

HR_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HR_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"


def parse_hr_measurement(data: bytearray) -> int:
    """Decode a standard Bluetooth SIG Heart Rate Measurement value."""
    flags = data[0]
    if flags & 0x1:  # HR value is 16-bit
        return int.from_bytes(data[1:3], byteorder="little")
    return data[1]  # HR value is 8-bit


async def find_garmin():
    print("Scanning for the watch's HR broadcast... (start 'Broadcast Heart Rate' on the Garmin now)")
    devices = await BleakScanner.discover(timeout=10.0, return_adv=True)
    for device, adv in devices.values():
        if HR_SERVICE_UUID in (adv.service_uuids or []):
            print(f"Found HR broadcaster: {device.name or 'unknown'} ({device.address})")
            return device
    return None


async def stream_hr():
    device = await find_garmin()
    while device is None:
        print("Not found yet, retrying in 5s...")
        await asyncio.sleep(5)
        device = await find_garmin()

    async with BleakClient(device.address) as client:
        print(f"Connected to {device.address}")

        def handle_notification(_, data: bytearray):
            hr = parse_hr_measurement(data)
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

        await client.start_notify(HR_MEASUREMENT_UUID, handle_notification)

        while client.is_connected:
            await asyncio.sleep(1)

    print("Disconnected, will retry...")


async def main():
    print("Starting real Garmin HR bridge... (Press Ctrl+C to stop)")
    while True:
        try:
            await stream_hr()
        except Exception as e:
            print(f"Error: {e}, retrying in 5s...")
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
