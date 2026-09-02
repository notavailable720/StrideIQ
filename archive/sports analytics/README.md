# Sports Analytics Server

A FastAPI-based server for collecting and monitoring heart rate data from wearable devices during sports training sessions.

## Features

- Real-time heart rate data collection from multiple devices
- Simple HTTP endpoint for data submission
- In-memory data storage with device tracking
- Error handling for malformed or corrupted packets

## Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Server

```bash
python server.py
```

The server will start on `0.0.0.0:8000` and listen for incoming heart rate data.

## API Endpoints

### POST `/api/hr_data`

Submit heart rate data from a device.

**Request Body:**
```json
{
  "device_id": "watch_1",
  "heart_rate": 145,
  "timestamp": 1234567890
}
```

**Response:**
```json
{
  "status": "success"
}
```

## Architecture

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Data Storage**: In-memory dictionary (temporary)
- **Network**: Listens on all local network interfaces

## Future Enhancements

- Persistent database storage
- Data visualization dashboard
- Historical data retrieval endpoints
- Device authentication
- Rate limiting and validation
