from flask import Flask
from app.utils.validation import validate_params
from app.constants import DEFAULT_RADIUS_KM

app = Flask(__name__)


def make_query(args):
    """Helper to call validate_params with a test request context."""
    with app.test_request_context(query_string=args):
        return validate_params()


def test_valid_params():
    args = {
        "lat": "51.5",
        "lng": "-0.1",
        "dropoff": "2024-06-01T10:00:00Z",
        "pickup": "2024-06-01T12:00:00Z",
        "bag_count": "2",
        "radius_km": "10",
    }
    validated, error = make_query(args)
    assert error is None
    assert validated["lat"] == 51.5
    assert validated["lng"] == -0.1
    assert validated["bag_count"] == 2
    assert validated["radius_km"] == 10


def test_missing_params():
    args = {}
    validated, error = make_query(args)
    assert validated is None
    assert error[1] == 400
    assert "Invalid or missing parameters" in error[0].json["error"]


def test_invalid_lat_lng():
    args = {
        "lat": "abc",
        "lng": "def",
        "dropoff": "2024-06-01T10:00:00Z",
        "pickup": "2024-06-01T12:00:00Z",
        "bag_count": "1",
    }
    validated, error = make_query(args)
    assert validated is None
    assert error[1] == 400


def test_invalid_datetime():
    args = {
        "lat": "51.5",
        "lng": "-0.1",
        "dropoff": "notadate",
        "pickup": "alsonotadate",
        "bag_count": "1",
    }
    validated, error = make_query(args)
    assert validated is None
    assert error[1] == 400
    assert "datetime" in error[0].json["error"]


def test_pickup_before_dropoff():
    args = {
        "lat": "51.5",
        "lng": "-0.1",
        "dropoff": "2024-06-01T12:00:00Z",
        "pickup": "2024-06-01T10:00:00Z",
        "bag_count": "1",
    }
    validated, error = make_query(args)
    assert validated is None
    assert error[1] == 400
    assert "Pickup time must be after dropoff time" in error[0].json["error"]


def test_lat_lng_range():
    args = {
        "lat": "100",
        "lng": "200",
        "dropoff": "2024-06-01T10:00:00Z",
        "pickup": "2024-06-01T12:00:00Z",
        "bag_count": "1",
    }
    validated, error = make_query(args)
    assert validated is None
    assert error[1] == 400
    assert "Latitude" in error[0].json["error"] or "Longitude" in error[0].json["error"]


def test_negative_bag_count():
    args = {
        "lat": "51.5",
        "lng": "-0.1",
        "dropoff": "2024-06-01T10:00:00Z",
        "pickup": "2024-06-01T12:00:00Z",
        "bag_count": "-1",
    }
    validated, error = make_query(args)
    assert validated is None
    assert error[1] == 400
    assert "Bag count must be positive" in error[0].json["error"]


def test_zero_radius():
    args = {
        "lat": "51.5",
        "lng": "-0.1",
        "dropoff": "2024-06-01T10:00:00Z",
        "pickup": "2024-06-01T12:00:00Z",
        "bag_count": "1",
        "radius_km": "0",
    }
    validated, error = make_query(args)
    assert validated is None
    assert error[1] == 400
    assert "Radius must be positive" in error[0].json["error"]


def test_default_radius():
    args = {
        "lat": "51.5",
        "lng": "-0.1",
        "dropoff": "2024-06-01T10:00:00Z",
        "pickup": "2024-06-01T12:00:00Z",
        "bag_count": "1",
    }
    validated, error = make_query(args)
    assert error is None
    assert validated["radius_km"] == DEFAULT_RADIUS_KM
