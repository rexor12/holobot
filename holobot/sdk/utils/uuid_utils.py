import random
import string

_ALPHABET = string.ascii_lowercase + string.digits

def random_uuid(length: int) -> str:
    return ''.join(random.choices(_ALPHABET, k=length))
