from datetime import datetime, timezone

def utcnow()-> datetime:
    """Returns the current datetime, guaranteed to be in UTC."""
    return datetime.now(timezone.utc)