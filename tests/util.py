import random
import string
import uuid

def random_ip() -> str:
    # TODO: Actually randomise
    return "192.168.0.2"

def random_string(size: int) -> str:
    chars = string.ascii_lowercase+string.ascii_uppercase+string.digits
    return ''.join(random.choice(chars) for _ in range(size))

def random_uuid() -> str:
    return uuid.uuid4()
