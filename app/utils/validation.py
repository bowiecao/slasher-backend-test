from datetime import datetime
from flask import request, jsonify
from typing import Tuple, Optional, Dict, Any
from app.constants import DEFAULT_RADIUS_KM


def validate_params() -> Tuple[Optional[Dict[str, Any]], Optional[Tuple]]:
    """
    Validate query parameters for stashpoint availability endpoint.

    Returns:
        Tuple of (validated_params, error_response)
        If validation fails, validated_params is None and error_response contains the error
        If validation succeeds, error_response is None and validated_params contains the validated data.

    The returned validated_params dict contains:
        lat (float): Latitude of the search location
        lng (float): Longitude of the search location
        dropoff_dt (datetime): Parsed dropoff datetime (UTC)
        pickup_dt (datetime): Parsed pickup datetime (UTC)
        bag_count (int): Number of bags requested
        radius_km (float): Search radius in kilometers
    """
    # Parse and validate query parameters
    try:
        lat = float(request.args.get("lat"))
        lng = float(request.args.get("lng"))
        dropoff = request.args.get("dropoff")
        pickup = request.args.get("pickup")
        bag_count = int(request.args.get("bag_count"))
        radius_km = float(request.args.get("radius_km", DEFAULT_RADIUS_KM))
    except (TypeError, ValueError):
        return None, (jsonify({"error": "Invalid or missing parameters"}), 400)

    # Parse datetimes
    try:
        dropoff_dt = datetime.fromisoformat(dropoff.replace("Z", "+00:00"))
        pickup_dt = datetime.fromisoformat(pickup.replace("Z", "+00:00"))
    except Exception:
        return None, (jsonify({"error": "Invalid datetime format"}), 400)

    # Validate that pickup is after dropoff
    if pickup_dt <= dropoff_dt:
        return None, (jsonify({"error": "Pickup time must be after dropoff time"}), 400)

    # Validate latitude and longitude ranges
    if not (-90 <= lat <= 90):
        return None, (jsonify({"error": "Latitude must be between -90 and 90"}), 400)

    if not (-180 <= lng <= 180):
        return None, (jsonify({"error": "Longitude must be between -180 and 180"}), 400)

    # Validate bag_count is positive
    if bag_count <= 0:
        return None, (jsonify({"error": "Bag count must be positive"}), 400)

    # Validate radius is positive
    if radius_km <= 0:
        return None, (jsonify({"error": "Radius must be positive"}), 400)

    validated_params = {
        "lat": lat,
        "lng": lng,
        "dropoff_dt": dropoff_dt,
        "pickup_dt": pickup_dt,
        "bag_count": bag_count,
        "radius_km": radius_km,
    }

    return validated_params, None
