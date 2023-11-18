"""General utility functions"""

import os
import time
import shutil
import random
import string
import logging
import secrets
import zipfile
import tempfile
from typing import Optional, Dict, Tuple, Union
from dataclasses import dataclass

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.remote.webelement import WebElement
from random_username.generate import generate_username as _generate_username
from webdriver_manager.chrome import ChromeDriverManager

from .exceptions import NoSuchDriverException

logger = logging.getLogger('reddit_account_generator')
chrome_driver_path = None


@dataclass
class Proxy:
    """
    Proxy dataclass
    """
    host: str
    port: int
    scheme: str = 'http'
    user: Optional[str] = None
    password: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        """
        Convert proxy to dict for requests library
        """
        return {
            'http': str(self),
            'https': str(self),
        }

    def to_string(self) -> str:
        """
        Get proxy string representation
        """
        if self.password is None:
            return f'{self.scheme}://{self.host}:{self.port}'
        return f'{self.scheme}://{self.user}:{self.password}@{self.host}:{self.port}'

    @property
    def auth(self) -> Optional[Tuple[str, str]]:
        """
        Get proxy auth tuple
        """
        if self.user is None or self.password is None:
            return None
        return self.user, self.password

    @classmethod
    def from_str(cls, proxy: str) -> 'Proxy':
        """
        Create proxy from string. Alias for :func:`parse_proxy`

        :param proxy: Proxy string
        :return: Proxy object
        """
        return parse_proxy(proxy)

    def __str__(self) -> str:
        return self.to_string()


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


def setup_chrome_driver(proxy: Optional[Proxy] = None, hide_browser: bool = True) -> webdriver.Chrome:
    install_chrome_driver()

    service = ChromeService(executable_path=chrome_driver_path)

    options = webdriver.ChromeOptions()
    options.add_argument('--lang=en')                # Not sure if this line is needed
    options.add_argument('--no-sandbox')             # Needed to work on servers without GUI
    options.add_argument('--disable-dev-shm-usage')  # Needed to work on servers without GUI
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US,en'})
    options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Disable logging

    if hide_browser:
        options.add_argument('--headless')

    if proxy is not None:
        setup_proxy(options, proxy)

    try:
        return webdriver.Chrome(options=options, service=service)
    except WebDriverException:
        logger.warning('Failed to create Chrome session. Trying with headless mode...')
        options.add_argument('--headless')
        return webdriver.Chrome(options=options, service=service)


def setup_proxy(options: webdriver.ChromeOptions, proxy: Proxy):
    """
    Set up proxy for Chrome webdriver

    :param opts: :class:`selenium.webdriver.ChromeOptions` object
    :param proxy: Proxy tuple (scheme, host, port)
    :param auth: Proxy auth tuple (user, password)
    """

    if proxy.auth is None:
        options.add_argument(f'--proxy-server={proxy.to_string()}')
        return

    user, password = proxy.auth

    # Evil hacks to set up proxy with auth
    # https://stackoverflow.com/questions/55582136/how-to-set-proxy-with-authentication-in-selenium-chromedriver-python 
    manifest_json = '''
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    '''

    background_js = '''
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "%s",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    ''' % (proxy.scheme, proxy.host, proxy.port, user, password)

    with tempfile.NamedTemporaryFile('w', suffix='.zip') as fp:
        plugin_file = fp.name

    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr('manifest.json', manifest_json)
        zp.writestr('background.js', background_js)

    options.add_extension(plugin_file)


def try_to_click(element: WebElement, delay: Union[int, float] = 0.5, max_tries: int = 20) -> bool:
    """Try to click an element multiple times."""
    retries = 0
    while retries < max_tries:
        try:
            element.click()
            return
        except:
            retries += 1
            time.sleep(delay)
    raise TimeoutException(f'Could not click element after {max_tries} tries.')


def parse_proxy(proxy: str) -> Proxy:
    """
    Parse proxy string

    Formats:
    * scheme://USER:PASS@HOST:PORT
    * scheme://HOST:PORT
    * HOST:PORT (default scheme is http)

    Returns: :class:`Proxy` object
    """

    # Get scheme
    if '://' in proxy:
        scheme, proxy = proxy.split('://')
    else:
        scheme = 'http'

    # Get user and password
    if '@' in proxy:
        auth, proxy = proxy.split('@')
        user, password = auth.split(':')
    else:
        user, password = None, None

    host, port = proxy.split(':')
    port = int(port)

    return Proxy(host, port, scheme, user, password)


def install_chrome_driver():
    """
    Download and install chrome driver
    """
    # Return if already installed
    global chrome_driver_path
    if chrome_driver_path is not None:
        return
    
    # Try to find in PATH
    path = shutil.which('chromedriver')
    if path is not None:
        chrome_driver_path = path
        return

    # Download driver
    logger.info('Downloading chrome driver...')

    try:
        chrome_driver_path = ChromeDriverManager().install()
    except AttributeError:
        raise NoSuchDriverException('Failed to download chrome driver for your browser version. Make sure that Chrome is installed.')

    logger.debug('Chrome driver downloaded to %s', chrome_driver_path)
