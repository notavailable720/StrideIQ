from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI()

roster = {
    "A1B2": {"name": "Tyler", "zones": [135, 150, 165, 180]},
    "C3D4": {"name": "Henry McFasterson", "zones": [140, 155, 170, 185]},
    "E5F6": {"name": "Tony", "zones": [130, 145, 160, 175]}
}

active_runners = {}

# 1. THE RECEIVER (Catches data from watches)
@app.post("/api/hr_data")
async def receive_data(request: Request):
    try:
        data = await request.json()
        
        if not data or "device_id" not in data:
            return {"status": "error", "message": "bad payload"}
            
        device_id = data["device_id"]
        runner_info = roster.get(device_id, {"name": "Unknown", "zones": [130, 150, 170, 190]})
        
        active_runners[device_id] = {
            "name": runner_info["name"],
            "zones": runner_info["zones"],
            "heart_rate": data.get("heart_rate", 0),
            "timestamp": data.get("timestamp", 0)
        }

        print(f"Updated {device_id}: {active_runners[device_id]}")
        return {"status": "success"}
        
    except Exception as e:
        print(f"Dropped packet: {e}")
        return {"status": "error"}

# 2. THE PROVIDER (Gives data to the UI)
@app.get("/api/get_runners")
async def get_runners():
    return active_runners

# 3. THE UI DASHBOARD (Serves the separate HTML file)
@app.get("/")
async def serve_ui():
    return FileResponse("index.html")

# 4. THE SETTINGS CATCHER (Updates zones on the fly)
@app.post("/api/update_zones")
async def update_zones(request: Request):
    try:
        data = await request.json()
        device_id = data.get("device_id")
        new_zones = data.get("zones")
        
        # Make sure the device exists and they sent exactly 4 zone thresholds
        if device_id in roster and isinstance(new_zones, list) and len(new_zones) == 4:
            
            # STRICT CHECK: Make sure the zones are actually in ascending order
            if not (new_zones[0] < new_zones[1] < new_zones[2] < new_zones[3]):
                return {"status": "error", "message": "Zones must be in ascending order"}

            # Update the main roster
            roster[device_id]["zones"] = new_zones
            # Update the active runner if they are currently running
            if device_id in active_runners:
                active_runners[device_id]["zones"] = new_zones
            
            print(f"Updated zones for {device_id}: {new_zones}")
            return {"status": "success"}
            
        return {"status": "error", "message": "Invalid device or zones"}
    except Exception as e:
        return {"status": "error"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)