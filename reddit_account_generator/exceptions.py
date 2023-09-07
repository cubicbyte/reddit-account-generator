"""General exceptions for the reddit_account_generator package."""

from datetime import timedelta

from selenium.common.exceptions import TimeoutException
from selenium_recaptcha_solver.exceptions import RecaptchaException


class RedditException(Exception):
    pass

class UsernameTakenException(RedditException):
    pass

class UsernameLengthException(RedditException):
    pass

class UsernameSymbolsException(RedditException):
    pass

class PasswordLengthException(RedditException):
    pass

class SessionExpiredException(RedditException):
    pass

class IncorrectUsernameOrPasswordException(RedditException):
    pass

class EmailVerificationException(RedditException):
    pass

class AuthException(RedditException):
    pass

class IPCooldownException(RedditException):
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


NetworkException = (RecaptchaException, IPCooldownException, TimeoutException)
