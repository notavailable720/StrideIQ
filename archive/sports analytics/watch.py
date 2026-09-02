import requests
import time
import random

url = "http:// "ur ip"/api/hr_data"
device_id = "C3D4"

# start at a resting jogging heart rate
current_hr = 140 

print("Starting continuous fake watch stream... (Press Ctrl+C to stop)")

while True:
    # make the heart rate drift up or down by a few beats randomly
    current_hr += random.randint(-5, 5)
    
    # keep it realistic so it doesnt drop to 0 or hit 300
    if current_hr > 195: current_hr = 195
    if current_hr < 100: current_hr = 100
    
    # generate a real unix timestamp for right now
    current_time = int(time.time())
    
    payload = {
        "device_id": device_id, 
        "heart_rate": current_hr, 
        "timestamp": current_time
    }

    try:
        # shoot it to the server
        requests.post(url, json=payload)
        print(f"Sent: {current_hr} BPM at {current_time}")
    except Exception as e:
        print("Could not connect to server...")
        
    # wait exactly 1 second before sending the next heartbeat
    time.sleep(1)