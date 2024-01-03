"""General exceptions for the reddit_account_generator package."""

from datetime import timedelta

from selenium.common.exceptions import TimeoutException
from selenium_recaptcha_solver.exceptions import RecaptchaException


class RedditException(Exception):
    """Base class for reddit_account_generator exceptions"""


class UsernameException(RedditException):
    """Base class for username exceptions"""

    def __init__(self, message: str, username: str):
        super().__init__(message)
        self.username = username


class UsernameTakenException(UsernameException):
    pass


class UsernameLengthException(UsernameException):
    pass


class UsernameSymbolsException(UsernameException):
    pass


class PasswordLengthException(RedditException):
    pass


class SessionExpiredException(RedditException):
    """Sometimes occurs on email entry page"""


class EmailVerificationException(RedditException):
    pass


class IPCooldownException(RedditException):
    """Raised when you have created a reddit account from this IP too recently."""

    @property
    def cooldown(self) -> timedelta:
        """Cooldown in minutes."""
        start = self.args[0].index('break for ') + len('break for ')
        end = self.args[0].index(' ', start)

        try:
            cooldown = int(self.args[0][start:end]) + 1
        except ValueError:
            raise ValueError('Failed to parse cooldown from IPCooldownException')

        if 'minutes' in self.args[0]:
            return timedelta(minutes=cooldown)
        elif 'seconds' in self.args[0]:
            return timedelta(seconds=cooldown)
        else:
            raise ValueError('Failed to parse cooldown from IPCooldownException')


class UserAgentException(RedditException):
    """Raised when the user agent is empty or invalid"""


IPException = (RecaptchaException, IPCooldownException, TimeoutException)
"""IP-related exceptions"""
