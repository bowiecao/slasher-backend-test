# write me a route to get all stashpoints

from flask import Blueprint, jsonify
from app.models import Stashpoint
from app.utils.validation import validate_params
from app.utils.filter import StashpointFilter

bp = Blueprint("stashpoints", __name__)


@bp.route("/", methods=["GET"])
def get_stashpoints():
    stashpoints = Stashpoint.query.all()
    return jsonify([stashpoint.to_dict() for stashpoint in stashpoints])


@bp.route("/availability", methods=["GET"])
def available_stashpoints():
    # Validate query parameters using utility function
    validated_params, error_response = validate_params()
    if error_response:
        return error_response

    try:
        filter_obj = StashpointFilter(**validated_params)
    except Exception as e:
        return jsonify({"error": f"Failed to create filter: {str(e)}"}), 400

    stashpoints = filter_obj.filtered_stashpoints
    distance_mapping = filter_obj.nearby_stashpoint_distance_mapping
    available_capacity_mapping = filter_obj.stashpoint_available_capacity_mapping

    sorted_stashpoints = sorted(stashpoints, key=lambda sp: distance_mapping[sp.id])

    available = [
        {
            "id": sp.id,
            "name": sp.name,
            "address": sp.address,
            "latitude": sp.latitude,
            "longitude": sp.longitude,
            "distance_km": round(distance_mapping[sp.id], 1),
            "capacity": sp.capacity,
            "available_capacity": available_capacity_mapping[sp.id],
            "open_from": sp.open_from.strftime("%H:%M"),
            "open_until": sp.open_until.strftime("%H:%M"),
        }
        for sp in sorted_stashpoints
    ]
    return jsonify(available)
