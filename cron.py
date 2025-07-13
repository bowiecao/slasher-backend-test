import os
import redis
from app import create_app
from app.models import Stashpoint


def sync_stashpoints_to_redis():
    app = create_app()
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    r = redis.Redis.from_url(redis_url)
    with app.app_context():
        stashpoints = Stashpoint.query.all()
        tmp_key = "stashpoints_tmp"
        r.delete(tmp_key)
        for sp in stashpoints:
            r.geoadd(tmp_key, (sp.longitude, sp.latitude, sp.id))
        r.rename(tmp_key, "stashpoints")  # Atomic swap
        print(f"Synced {len(stashpoints)} stashpoints to Redis.")


if __name__ == "__main__":
    sync_stashpoints_to_redis()
