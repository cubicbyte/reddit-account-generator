"""General exceptions for the reddit_account_generator package."""

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
    pass

NetworkException = (RecaptchaException, IPCooldownException, TimeoutException)
