import secrets
import string
from random import random


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_fake_phone_number(prefix="+998", length=9):
    return prefix + ''.join(str(random.randint(0, 9)) for _ in range(length))