import uuid

def generate_uuid() -> str:
    """Generates a random UUID string."""
    return str(uuid.uuid4())
