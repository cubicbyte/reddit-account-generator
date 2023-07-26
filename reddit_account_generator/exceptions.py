from selenium.common.exceptions import TimeoutException
from selenium_recaptcha_solver.exceptions import RecaptchaException


class UsernameTakenException(Exception):
    pass

class UsernameLengthException(Exception):
    pass

class UsernameSymbolsException(Exception):
    pass

class PasswordLengthException(Exception):
    pass

class IPCooldownException(Exception):
    pass

class EMailCooldownException(Exception):
    pass

class IncorrectUsernameOrPasswordException(Exception):
    pass

NetworkException = (RecaptchaException, IPCooldownException, TimeoutException)
