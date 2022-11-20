import random
import string

_ALPHABET = string.ascii_lowercase + string.digits

def random_uuid(length: int) -> str:
    """Generates a random UUID from the lower-case letters of the ASCII alphabet and digits.

    NOTE: This should not be used for cryptography purposes.

    :param length: The length of the generated UUID.
    :type length: int
    :return: The generated UUID.
    :rtype: str
    """

    return ''.join(random.choices(_ALPHABET, k=length))
