# 🧳 Stasher Backend

A Flask-based API for finding available bag storage locations (stashpoints) based on location, time, and capacity requirements.

## 📁 Project Structure

```
backend-test/
├── 📁 app/                          # Main application package
│   ├── 📁 models/                   # Database models
│   ├── 📁 routes/                   # API routes
│   ├── 📁 utils/                    # Utility modules
│   └── __init__.py                  # App factory
├── 📁 tests/                        # Test suite
├── 📁 migrations/                   # Database migrations
├── 📄 config.py                     # Configuration settings
├── 📄 requirements.txt              # Python dependencies
├── 📄 docker-compose.yml           # Docker orchestration
├── 📄 Dockerfile                    # Container definition
├── 📄 Dockerfile.cron               # Cron container definition
├── 📄 cron.py                       # Data sync script
└── 📄 README.md                    # This file
```

## 🚀 Getting Started

### 🛠️ Prerequisites

- 🐳 Docker and Docker Compose installed on your machine
- 🧬 Git

### ⚡ Setup

1. 📥 Clone this repository
2. 📂 Navigate to the project directory
3. ▶️ Start the application using Docker Compose:

```bash
docker-compose up -d
```

4. 🌐 The API will be available at `http://localhost:5001`
5. ✅ You can verify it's running with:

```bash
curl http://localhost:5001/healthcheck
```

## 📚 API Endpoints

### 📋 Get All Stashpoints
```
GET /api/v1/stashpoints/
```

### 🔎 Get Available Stashpoints
```
GET /api/v1/stashpoints/availability?lat=51.5&lng=-0.1&dropoff=2024-06-01T10:00:00Z&pickup=2024-06-01T12:00:00Z&bag_count=2&radius_km=10
```

**Query Parameters:**
- 🗺️ `lat` (float): Latitude for the search location
- 🗺️ `lng` (float): Longitude for the search location
- 🕒 `dropoff` (ISO datetime): When the user wants to drop off their bags
- 🕒 `pickup` (ISO datetime): When the user wants to pick up their bags
- 🎒 `bag_count` (integer): Number of bags to store
- 📏 `radius_km` (float, optional): Search radius in kilometers

**Response Format:**
```json
[
  {
    "id": "abc123",
    "name": "Central Cafe Storage",
    "address": "123 Main Street",
    "latitude": 51.5107,
    "longitude": -0.1246,
    "distance_km": 0.5,
    "capacity": 20,
    "available_capacity": 15,
    "open_from": "08:00",
    "open_until": "22:00"
  }
]
```

## 🏗️ Architecture

- 🐍 **Flask** - Web framework
- 🐘 **PostgreSQL** - Primary database
- 🟧 **Redis** - Secondary database for geospatial indexing (cron.py syncs stashpoints daily)
- 🦄 **Gunicorn** - WSGI server with 8 workers
- 🐳 **Docker Compose** - Container orchestration

## 📈 Benchmark: Realistic Load Testing Results

The following benchmarks were obtained using a custom load test script simulating real users with varied parameters (location, time, bag count, radius).

### 🧪 Test 1: Light Load (50 requests, 5 concurrent)
- ✅ Success rate: 100%
- ⚡ Requests/sec: 159.2
- ⏱️ Average response time: 31.0 ms
- 🪙 Median: 15.4 ms
- 95th percentile: 142.9 ms
- 99th percentile: 148.9 ms
- 🚩 Max: 148.9 ms

### 🧪 Test 2: Medium Load (100 requests, 10 concurrent)
- ✅ Success rate: 100%
- ⚡ Requests/sec: 178.8
- ⏱️ Average response time: 54.9 ms
- 🪙 Median: 25.0 ms
- 95th percentile: 290.4 ms
- 99th percentile: 356.4 ms
- 🚩 Max: 356.4 ms

### 🧪 Test 3: Heavy Load (200 requests, 20 concurrent)
- ✅ Success rate: 100%
- ⚡ Requests/sec: 489.4
- ⏱️ Average response time: 38.8 ms
- 🪙 Median: 36.4 ms
- 95th percentile: 62.7 ms
- 99th percentile: 98.9 ms
- 🚩 Max: 103.1 ms

**Interpretation:**
- 🚀 The API is robust and scales well with increased concurrency.
- 🟢 All requests succeeded, with no errors or timeouts.
- 📉 Response times remain low and predictable, even under heavy load.
- 🏆 The system is ready for production-level traffic.

## 👩‍💻 Development

### 🧪 Running Tests
```bash
pytest tests/
```

### 🎨 Code Formatting
```bash
black .
flake8 .
```

### 🏋️ Load Testing
```bash
python3 load_test_varied.py
```
