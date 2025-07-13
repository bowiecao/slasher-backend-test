import pytest
from datetime import datetime, time, timedelta
from unittest.mock import Mock, patch
from app.models import Stashpoint, Booking, Customer
from app.utils.filter import StashpointFilter
from app import create_app

@pytest.fixture(scope="module")
def app_context():
    app = create_app()
    with app.app_context():
        yield

@pytest.fixture
def valid_params():
    return {
        "lat": 51.5,
        "lng": -0.1,
        "radius_km": 10,
        "dropoff_dt": datetime(2024, 6, 1, 10, 0),
        "pickup_dt": datetime(2024, 6, 1, 12, 0),
        "bag_count": 2,
    }

def make_mock_stashpoint(id, capacity, open_from, open_until):
    sp = Mock()
    sp.id = id
    sp.capacity = capacity
    sp.open_from = open_from
    sp.open_until = open_until
    return sp

def make_mock_booking_results(results):
    return [(str(id), used) for id, used in results]

@patch("app.utils.filter.redis_client")
def test_find_nearby_stashpoints(mock_redis, valid_params, app_context):
    """Test that Redis geosearch results are properly parsed"""
    mock_redis.geosearch.return_value = [("1", 2.5), ("2", 3.1), ("3", 8.0)]
    
    # Create filter but mock the database operations
    with patch.object(StashpointFilter, 'filter_by_opening_time'), \
         patch.object(StashpointFilter, 'get_stashpoint_used_capacity_mapping'), \
         patch.object(StashpointFilter, 'calculate_available_capacity'):
        
        filter_obj = StashpointFilter(**valid_params)
        assert filter_obj.nearby_stashpoint_distance_mapping == {
            "1": 2.5,
            "2": 3.1,
            "3": 8.0,
        }
        assert filter_obj.filtered_stashpoint_ids == {"1", "2", "3"}

def test_invalid_parameters():
    """Test that invalid parameters raise appropriate errors"""
    with pytest.raises(TypeError):
        StashpointFilter()
    with pytest.raises(TypeError):
        StashpointFilter(lat=51.5)

@patch("app.utils.filter.redis_client")
def test_redis_connection_error(mock_redis, valid_params, app_context):
    """Test that Redis connection errors are properly handled"""
    mock_redis.geosearch.side_effect = Exception("Redis connection failed")
    with pytest.raises(Exception):
        StashpointFilter(**valid_params)

@patch("app.utils.filter.redis_client")
def test_no_nearby_stashpoints(mock_redis, valid_params, app_context):
    """Test behavior when no stashpoints are found"""
    mock_redis.geosearch.return_value = []
    
    # Create filter but mock the database operations
    with patch.object(StashpointFilter, 'filter_by_opening_time'), \
         patch.object(StashpointFilter, 'get_stashpoint_used_capacity_mapping'), \
         patch.object(StashpointFilter, 'calculate_available_capacity'):
        
        filter_obj = StashpointFilter(**valid_params)
        assert filter_obj.nearby_stashpoint_distance_mapping == {}
        assert filter_obj.filtered_stashpoint_ids == set()
        assert filter_obj.filtered_stashpoints == []
        assert filter_obj.stashpoint_available_capacity_mapping == {}

def test_filter_initialization(valid_params, app_context):
    """Test that filter initializes with correct parameters"""
    with patch.object(StashpointFilter, 'run'):
        filter_obj = StashpointFilter(**valid_params)
        assert filter_obj.lat == 51.5
        assert filter_obj.lng == -0.1
        assert filter_obj.radius_km == 10
        assert filter_obj.dropoff_dt == datetime(2024, 6, 1, 10, 0)
        assert filter_obj.pickup_dt == datetime(2024, 6, 1, 12, 0)
        assert filter_obj.bag_count == 2

@patch("app.utils.filter.redis_client")
def test_bag_count_filtering(mock_redis, app_context):
    """Test that stashpoints are filtered based on bag count requirement"""
    mock_redis.geosearch.return_value = [("1", 2.5), ("2", 3.1), ("3", 4.0)]
    
    # Test with bag_count = 3
    params = {
        "lat": 51.5,
        "lng": -0.1,
        "radius_km": 10,
        "dropoff_dt": datetime(2024, 6, 1, 10, 0),
        "pickup_dt": datetime(2024, 6, 1, 12, 0),
        "bag_count": 3,
    }
    
    # Mock the database operations but NOT calculate_available_capacity
    with patch.object(StashpointFilter, 'filter_by_opening_time'), \
         patch.object(StashpointFilter, 'get_stashpoint_used_capacity_mapping'):
        
        filter_obj = StashpointFilter(**params)
        
        # Manually set up the filter's internal state to test bag count filtering
        filter_obj.stashpoint_capacity_mapping = {"1": 10, "2": 8, "3": 15}
        filter_obj.stashpoint_used_capacity_mapping = {"1": 5, "2": 6, "3": 10}
        
        # Call the method that uses the new bag count logic
        filter_obj.calculate_available_capacity()
        
        # Should only include stashpoints with enough capacity for 3 bags
        assert "1" in filter_obj.stashpoint_available_capacity_mapping  # 10 - 5 = 5 >= 3 ✓
        assert "3" in filter_obj.stashpoint_available_capacity_mapping  # 15 - 10 = 5 >= 3 ✓
        assert "2" not in filter_obj.stashpoint_available_capacity_mapping  # 8 - 6 = 2 < 3 ✗
        assert filter_obj.stashpoint_available_capacity_mapping["1"] == 5
        assert filter_obj.stashpoint_available_capacity_mapping["3"] == 5

@pytest.mark.integration
def test_stashpoint_filter_integration(app_context):
    """Integration test with real database"""
    from app import db
    
    # Use unique IDs to avoid conflicts
    stashpoint_id = "test_sp_" + str(int(datetime.now().timestamp()))
    customer_id = "test_cust_" + str(int(datetime.now().timestamp()))
    
    # Create a stashpoint
    sp = Stashpoint(
        id=stashpoint_id,
        name="Test Stashpoint",
        address="123 Test St",
        postal_code="SW1A 1AA",
        latitude=51.5,
        longitude=-0.1,
        capacity=10,
        open_from=time(8, 0),
        open_until=time(20, 0),
    )
    db.session.add(sp)
    db.session.commit()

    # Create a customer
    customer = Customer(
        id=customer_id,
        name="Test Customer",
        email="test@example.com",
    )
    db.session.add(customer)
    db.session.commit()

    # Create bookings: one active, one cancelled, both overlap
    dropoff = datetime(2024, 6, 1, 10, 0)
    pickup = datetime(2024, 6, 1, 12, 0)
    booking_active = Booking(
        stashpoint_id=stashpoint_id,
        bag_count=3,
        dropoff_time=dropoff,
        pickup_time=pickup + timedelta(hours=1),
        is_cancelled=False,
        is_paid=True,
        checked_in=True,
        checked_out=False,
        customer_id=customer_id,
    )
    booking_cancelled = Booking(
        stashpoint_id=stashpoint_id,
        bag_count=5,
        dropoff_time=dropoff,
        pickup_time=pickup + timedelta(hours=2),
        is_cancelled=True,
        is_paid=True,
        checked_in=True,
        checked_out=False,
        customer_id=customer_id,
    )
    db.session.add_all([booking_active, booking_cancelled])
    db.session.commit()

    try:
        # Run the filter
        params = {
            "lat": 51.5,
            "lng": -0.1,
            "radius_km": 10,
            "dropoff_dt": dropoff,
            "pickup_dt": pickup,
            "bag_count": 1,
        }
        
        # Mock Redis for integration test
        with patch("app.utils.filter.redis_client") as mock_redis:
            mock_redis.geosearch.return_value = [(stashpoint_id, 0.1)]
            
            filter_obj = StashpointFilter(**params)
            # Only the non-cancelled booking should be counted
            assert filter_obj.stashpoint_used_capacity_mapping[stashpoint_id] == 3
            assert stashpoint_id in filter_obj.stashpoint_available_capacity_mapping
            assert filter_obj.stashpoint_available_capacity_mapping[stashpoint_id] == 7
    finally:
        # Clean up test data
        db.session.delete(booking_active)
        db.session.delete(booking_cancelled)
        db.session.delete(customer)
        db.session.delete(sp)
        db.session.commit()
