import os
import string
import secrets
import random

from random_username.generate import generate_username as _generate_username


def generate_username() -> str:
    username = _generate_username(1)[0] + str(random.randint(100, 1000))
    return username


def generate_password(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


def load_proxies(path: str) -> list[str]:
    """
    Load proxies from file

    File format:
    IP:PORT without protocol
    """

    if not os.path.exists(path):
        return []

    proxies = []

    with open(path, 'r', encoding='utf-8') as f:
        for _, line in enumerate(f):
            line = line.strip()
            if line == '' or line.startswith('#'):
                continue
            proxies.append(line)

    return proxies
