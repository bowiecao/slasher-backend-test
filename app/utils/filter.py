import redis
import os
from app.models import Stashpoint, Booking
from sqlalchemy import and_, or_, func

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.Redis.from_url(
    REDIS_URL,
    max_connections=10,  # Conservative connection pool
    socket_connect_timeout=2,  # Fast connection timeout
    socket_timeout=2,  # Fast operation timeout
    retry_on_timeout=True,  # Retry on timeout
    health_check_interval=30,  # Health check every 30 seconds
    decode_responses=True,  # Decode responses automatically
)


class StashpointFilter:
    """
    Stateful filter for stashpoints based on location, time window, and bag count.

    After initialization with the required parameters, the full filtering pipeline is executed automatically:
      1. Find nearby stashpoints using Redis geosearch.
      2. Filter by opening/closing time.
      3. Calculate used capacity from overlapping bookings.
      4. Calculate available capacity and filter out stashpoints with no availability.

    Results are available in the following instance variables:
      - self.nearby_stashpoint_distance_mapping: {stashpoint_id: distance_km, ...}
      - self.filtered_stashpoint_ids: set of stashpoint_id (updated at each step)
      - self.filtered_stashpoints: list of Stashpoint objects (updated after the final filtering step)
      - self.stashpoint_capacity_mapping: {stashpoint_id: capacity, ...}
      - self.stashpoint_used_capacity_mapping: {stashpoint_id: used_capacity, ...}
      - self.stashpoint_available_capacity_mapping: {stashpoint_id: available_capacity, ...}
    """

    def __init__(self, lat, lng, radius_km, dropoff_dt, pickup_dt, bag_count):
        self.lat = lat
        self.lng = lng
        self.radius_km = radius_km
        self.dropoff_dt = dropoff_dt
        self.pickup_dt = pickup_dt
        self.bag_count = bag_count
        self.filtered_stashpoint_ids = set()
        self.filtered_stashpoints = []
        self.nearby_stashpoint_distance_mapping = {}
        self.stashpoint_capacity_mapping = {}
        self.stashpoint_used_capacity_mapping = {}
        self.stashpoint_available_capacity_mapping = {}
        self.run()

    def run(self):
        """
        Execute the full filtering pipeline, updating all relevant instance variables in order.
        This is called automatically on initialization.
        After the final filtering step, self.filtered_stashpoints is updated to match self.filtered_stashpoint_ids.
        """
        self.find_nearby_stashpoints()
        self.filter_by_opening_time()
        self.get_stashpoint_used_capacity_mapping()
        self.calculate_available_capacity()
        self.filtered_stashpoints = [
            sp
            for sp in self.filtered_stashpoints
            if sp.id in self.filtered_stashpoint_ids
        ]

    def find_nearby_stashpoints(self, key="stashpoints"):
        """
        Find nearby stashpoints using Redis geosearch.
        Updates:
          - self.nearby_stashpoint_distance_mapping: {stashpoint_id: distance_km, ...}
          - self.filtered_stashpoint_ids: set of stashpoint_id
        """
        results = redis_client.geosearch(
            key,
            longitude=self.lng,
            latitude=self.lat,
            radius=self.radius_km,
            unit="km",
            withdist=True,
        )
        self.nearby_stashpoint_distance_mapping = {
            stashpoint_id: distance for stashpoint_id, distance in results
        }
        self.filtered_stashpoint_ids = set(
            self.nearby_stashpoint_distance_mapping.keys()
        )

    def filter_by_opening_time(self):
        """
        Filter stashpoints by opening and closing time.
        Updates:
          - self.filtered_stashpoints: list of Stashpoint objects (initial set, will be further filtered after the final step)
          - self.stashpoint_capacity_mapping: {stashpoint_id: capacity, ...}
          - self.filtered_stashpoint_ids: set of stashpoint_id
        """
        self.filtered_stashpoints = (
            Stashpoint.query.filter(Stashpoint.id.in_(self.filtered_stashpoint_ids))
            .filter(
                Stashpoint.open_from <= self.dropoff_dt.time(),
                Stashpoint.open_until >= self.pickup_dt.time(),
            )
            .all()
        )
        self.stashpoint_capacity_mapping = {
            stashpoint.id: stashpoint.capacity
            for stashpoint in self.filtered_stashpoints
        }
        self.filtered_stashpoint_ids = set(
            stashpoint.id for stashpoint in self.filtered_stashpoints
        )

    def get_stashpoint_used_capacity_mapping(self):
        """
        Calculate used capacity for each stashpoint from overlapping bookings, excluding cancelled bookings.
        Updates:
          - self.stashpoint_used_capacity_mapping: {stashpoint_id: used_capacity, ...}
          - self.filtered_stashpoint_ids: set of stashpoint_id
        """
        used_capacity_each_stashpoint = (
            Booking.query.with_entities(
                Booking.stashpoint_id, func.sum(Booking.bag_count)
            )
            .filter(
                Booking.stashpoint_id.in_(self.filtered_stashpoint_ids),
                Booking.is_cancelled.is_(False),
                or_(
                    and_(
                        Booking.dropoff_time <= self.dropoff_dt,
                        Booking.pickup_time > self.dropoff_dt,
                    ),
                    and_(
                        Booking.dropoff_time < self.pickup_dt,
                        Booking.pickup_time >= self.pickup_dt,
                    ),
                    and_(
                        Booking.dropoff_time >= self.dropoff_dt,
                        Booking.pickup_time <= self.pickup_dt,
                    ),
                ),
            )
            .group_by(Booking.stashpoint_id)
            .all()
        )
        self.stashpoint_used_capacity_mapping = {
            stashpoint_id: used_capacity or 0
            for stashpoint_id, used_capacity in used_capacity_each_stashpoint
        }
        self.filtered_stashpoint_ids = set(self.stashpoint_used_capacity_mapping.keys())

    def calculate_available_capacity(self):
        """
        Calculate available capacity for each stashpoint and filter out those with no availability.
        Updates:
          - self.stashpoint_available_capacity_mapping: {stashpoint_id: available_capacity, ...}
          - self.filtered_stashpoint_ids: set of stashpoint_id
          - self.filtered_stashpoints: list of Stashpoint objects (final filtered set)
        """
        self.stashpoint_available_capacity_mapping = {
            sp_id: cap
            for sp_id in self.stashpoint_capacity_mapping
            if (
                cap := self.stashpoint_capacity_mapping[sp_id]
                - self.stashpoint_used_capacity_mapping.get(sp_id, 0)
            )
            >= self.bag_count
        }
        self.filtered_stashpoint_ids = set(
            self.stashpoint_available_capacity_mapping.keys()
        )
