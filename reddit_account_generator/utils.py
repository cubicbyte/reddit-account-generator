import os
import time
import random
import string
import secrets

import requests
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
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


def check_tor_running(ip: str, port: int) -> bool:
    try:
        r = requests.get('https://check.torproject.org/api/ip', proxies={'https': f'socks5h://{ip}:{port}'}, timeout=5)
        return r.json()['IsTor'] is True
    except Exception:
        return False


def setup_firefox_driver(proxies: dict[str, str] | None = None, hide_browser: bool = True) -> webdriver.Firefox:
    options = webdriver.FirefoxOptions()

    if hide_browser:
        options.add_argument('--headless')

    # Set up proxies if available
    if proxies is not None:
        options.set_preference('network.proxy.type', 1)

        if 'http' in proxies:
            http_ip, http_port = proxies['http'].split(':')
            options.set_preference('network.proxy.http', http_ip)
            options.set_preference('network.proxy.http_port', int(http_port))
        if 'https' in proxies:
            https_ip, https_port = proxies['https'].split(':')
            options.set_preference('network.proxy.ssl', https_ip)
            options.set_preference('network.proxy.ssl_port', int(https_port))
        if 'socks' in proxies:
            # Only SOCKS5 is supported
            socks_ip, socks_port = proxies['socks'].split(':')
            options.set_preference('network.proxy.socks', socks_ip)
            options.set_preference('network.proxy.socks_port', int(socks_port))
            options.set_preference('network.proxy.socks_remote_dns', False)

    return webdriver.Firefox(options=options, service_log_path=os.devnull)


def try_to_click(element: WebElement, delay: int | float = 0.5, max_tries: int = 10) -> bool:
    """Try to click an element multiple times."""
    while max_tries > 0:
        try:
            element.click()
            return
        except Exception as e:
            max_tries -= 1
            time.sleep(delay)
    raise e
