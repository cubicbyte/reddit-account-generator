"""General utility functions"""

import os
import time
import shutil
import random
import string
import logging
import secrets
import tempfile
from typing import Optional, Dict, Tuple, Union
from dataclasses import dataclass

import requests
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.selenium_manager import SeleniumManager
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from random_username.generate import generate_username as _generate_username
from fake_useragent import UserAgent

logger = logging.getLogger('reddit_account_generator')


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


def setup_chrome_driver(proxy: Optional[Proxy] = None, headless: bool = True) -> uc.Chrome:
    user_agent = UserAgent()

    logger.info('Installing Chrome driver...')
    driver_executable_path, browser_executable_path = get_chrome_driver_path()

    options = uc.ChromeOptions()
    options.add_argument(f'--user-agent={user_agent.random}')  # Set random user agent to avoid detection
    options.add_argument('--lang=en')  # Not sure if this line is needed
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US,en'})

    if proxy is not None:
        setup_proxy(options, proxy)

    logger.debug('Starting Chrome...')
    logger.debug('If it\'s stuck here, try to change HEADLESS to True in config.py file')

    return uc.Chrome(
        options=options,
        headless=headless,
        driver_executable_path=driver_executable_path,
        browser_executable_path=browser_executable_path,
        no_sandbox=False,  # Enabling this can cause chrome process to stay alive after script is finished
    )


def setup_proxy(options: uc.ChromeOptions, proxy: Proxy):
    """
    Set up proxy for Chrome webdriver

    :param options: :class:`uc.ChromeOptions` object
    :param proxy: :class:`Proxy` object
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

    tmpdir = tempfile.mkdtemp()

    with open(os.path.join(tmpdir, 'manifest.json'), 'w') as f:
        f.write(manifest_json)

    with open(os.path.join(tmpdir, 'background.js'), 'w') as f:
        f.write(background_js)

    options.add_argument(f'--load-extension={tmpdir}')
    # FIXME: This will create a new extension dir for each session and will not delete it until system reboot


def try_to_click(element: WebElement, delay: Union[int, float] = 0.5, max_tries: int = 20):
    """Try to click an element multiple times."""
    retries = 0
    while retries < max_tries:
        try:
            element.click()
            return
        except Exception:
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


def get_chrome_driver_path() -> Tuple[str, str | None]:
    """Get the path to the Chrome driver executable

    :return: Tuple of (driver_path, browser_path)
    """

    # Try to find in PATH
    path = shutil.which('chromedriver')
    if path is not None:
        return path, None

    try:
        return ChromeDriverManager().install(), None

    except AttributeError as e:
        # This error occurs when we can't find Chrome
        if "'NoneType' object has no attribute 'split'" in str(e):
            if os.name == 'nt':
                # Windows
                logging.warning('Chrome is not installed. Trying to fix it...')

                # Use Selenium built-in manager to get the executable paths.
                manager = SeleniumManager()
                args = [str(manager.get_binary()), '--browser', 'chrome']
                output = manager.run(args)

                driver_path = output["driver_path"]
                browser_path = output["browser_path"]

                return driver_path, browser_path

            else:
                # Other OS, can't fix it
                raise Exception('Chrome is not installed. Please install it manually.')

        else:
            raise e
