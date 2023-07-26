import time
from abc import ABC, abstractmethod

from stem import Signal
from stem.control import Controller


class ProxyManager(ABC):
    """
    Abstract class for proxy managers

    Proxy manager needed to switch proxies after each account creation
    """

    @abstractmethod
    def get_next(self) -> dict[str, str] | None:
        ...


class DefaultProxy(ProxyManager):
    """Proxy manager based on proxies list"""

    def __init__(self, proxies: list[str]):
        self.proxies = proxies
        self.i = 0

    def get_next(self):
        proxy = {
            'socks': self.proxies[self.i]
        }

        self.i += 1
        if self.i >= len(self.proxies):
            self.i = 0

        return proxy

    def __str__(self) -> str:
        return self.proxies[self.i]


class TorProxy(ProxyManager):
    """Proxy manager based on Tor"""

    def __init__(self, ip: str, port: int, password: str, control_port: int, delay: int = 5):
        self.ip = ip
        self.port = port
        self.password = password
        self.control_port = control_port
        self.delay = delay

        self.controller = Controller.from_port(port=self.control_port)
        self.controller.authenticate(self.password)

    @property
    def proxy(self) -> dict[str, str]:
        return {
            'http': f'{self.ip}:{self.port}',
            'https': f'{self.ip}:{self.port}',
        }

    def get_next(self):
        self.controller.signal(Signal.NEWNYM)
        time.sleep(self.delay)

        return self.proxy

    def __str__(self) -> str:
        return f'{self.ip}:{self.port}'


class EmptyProxy(ProxyManager):
    """In case if we want to use local IP address"""
    def get_next(self):
        return None

    def __str__(self) -> str:
        return 'No proxy'
