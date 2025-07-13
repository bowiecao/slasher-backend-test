#!/usr/bin/env python3
"""
Realistic Load Test with Varied Parameters
Simulates real users with different search parameters.
"""

import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import statistics

# London coordinates for realistic testing
LONDON_COORDS = [
    (51.5074, -0.1278),  # Central London
    (51.5107, -0.1246),  # Covent Garden
    (51.5014, -0.1246),  # Westminster
    (51.5200, -0.1050),  # Kings Cross
    (51.4890, -0.1440),  # Chelsea
    (51.5130, -0.0890),  # Canary Wharf
    (51.5400, -0.1400),  # Camden
    (51.4700, -0.4500),  # Heathrow
]


def generate_random_params():
    """Generate random but realistic search parameters."""
    # Random location
    lat, lng = random.choice(LONDON_COORDS)
    lat += random.uniform(-0.01, 0.01)  # Small variation
    lng += random.uniform(-0.01, 0.01)

    # Random date (next 30 days)
    base_date = datetime.now() + timedelta(days=random.randint(1, 30))

    # Random time window (1-8 hours)
    start_hour = random.randint(8, 18)  # 8 AM to 6 PM
    duration_hours = random.randint(1, 8)

    dropoff_time = base_date.replace(hour=start_hour, minute=0, second=0)
    pickup_time = dropoff_time + timedelta(hours=duration_hours)

    # Random bag count
    bag_count = random.randint(1, 5)

    # Random radius
    radius_km = random.choice([1, 2, 5, 10, 15])

    return {
        "lat": round(lat, 4),
        "lng": round(lng, 4),
        "dropoff": dropoff_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pickup": pickup_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "bag_count": bag_count,
        "radius_km": radius_km,
    }


def make_request(request_id):
    """Make a single request with random parameters."""
    params = generate_random_params()
    url = "http://localhost:5001/api/v1/stashpoints/availability"

    start_time = time.time()
    try:
        response = requests.get(url, params=params, timeout=10)
        end_time = time.time()

        return {
            "request_id": request_id,
            "status_code": response.status_code,
            "response_time": (end_time - start_time) * 1000,  # Convert to ms
            "params": params,
            "success": response.status_code == 200,
        }
    except Exception as e:
        end_time = time.time()
        return {
            "request_id": request_id,
            "status_code": 0,
            "response_time": (end_time - start_time) * 1000,
            "params": params,
            "success": False,
            "error": str(e),
        }


def run_load_test(total_requests=100, concurrent_users=10):
    """Run load test with varied parameters."""
    print(
        f"🚀 Starting load test: {total_requests} requests, {concurrent_users} concurrent users"
    )
    print("=" * 60)

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        results = list(executor.map(make_request, range(total_requests)))

    end_time = time.time()

    # Analyze results
    successful_requests = [r for r in results if r["success"]]
    failed_requests = [r for r in results if not r["success"]]
    response_times = [r["response_time"] for r in successful_requests]

    # Calculate statistics
    total_time = end_time - start_time
    requests_per_second = total_requests / total_time
    success_rate = len(successful_requests) / total_requests * 100

    if response_times:
        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
        p99_response_time = sorted(response_times)[int(len(response_times) * 0.99)]
    else:
        avg_response_time = median_response_time = min_response_time = (
            max_response_time
        ) = p95_response_time = p99_response_time = 0

    # Print results
    print("📊 Test Results:")
    print(f"   Total requests: {total_requests}")
    print(f"   Successful: {len(successful_requests)}")
    print(f"   Failed: {len(failed_requests)}")
    print(f"   Success rate: {success_rate:.1f}%")
    print(f"   Total time: {total_time:.2f} seconds")
    print(f"   Requests/sec: {requests_per_second:.1f}")
    print()
    print("⏱️  Response Times (ms):")
    print(f"   Average: {avg_response_time:.1f}")
    print(f"   Median: {median_response_time:.1f}")
    print(f"   Min: {min_response_time:.1f}")
    print(f"   Max: {max_response_time:.1f}")
    print(f"   95th percentile: {p95_response_time:.1f}")
    print(f"   99th percentile: {p99_response_time:.1f}")
    print()

    # Show some example parameters
    print("🎯 Example Parameters Used:")
    for i, result in enumerate(results[:3]):
        params = result['params']
        print(f"   Request {i+1}: lat={params['lat']}, lng={params['lng']}, "
              f"bags={params['bag_count']}, radius={params['radius_km']}km")

    if failed_requests:
        print("\n❌ Failed Requests:")
        for req in failed_requests[:3]:
            print(f"   Request {req['request_id']}: {req.get('error', 'Unknown error')}")

    return {
        "total_requests": total_requests,
        "successful": len(successful_requests),
        "failed": len(failed_requests),
        "success_rate": success_rate,
        "requests_per_second": requests_per_second,
        "avg_response_time": avg_response_time,
        "p95_response_time": p95_response_time,
        "p99_response_time": p99_response_time,
    }


if __name__ == "__main__":
    # Run different load tests
    print("🧪 Realistic Load Testing with Varied Parameters")
    print("=" * 60)

    # Test 1: Light load
    print("\n📈 Test 1: Light Load (50 requests, 5 concurrent)")
    run_load_test(50, 5)

    # Test 2: Medium load
    print("\n📈 Test 2: Medium Load (100 requests, 10 concurrent)")
    run_load_test(100, 10)

    # Test 3: Heavy load
    print("\n📈 Test 3: Heavy Load (200 requests, 20 concurrent)")
    run_load_test(200, 20)
