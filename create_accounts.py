import logging

from selenium.common.exceptions import NoSuchWindowException, WebDriverException

from reddit_account_generator import maker, protector, create_account, protect_account, install_driver
from reddit_account_generator.proxies import DefaultProxy, TorProxy, EmptyProxy
from reddit_account_generator.utils import *
from reddit_account_generator.exceptions import *
from config import *


num_of_accounts = int(input('How many accounts do you want to make? '))


# Set logging
_logger = logging.getLogger('script')
logging.getLogger('webdriverdownloader').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('selenium').setLevel(logging.WARNING)

try:
    import coloredlogs
    coloredlogs.install(level=LOG_LEVEL, fmt='%(asctime)s %(levelname)s %(message)s')
except ImportError:
    logging.basicConfig(level=LOG_LEVEL)
    logging.warning('Coloredlogs is not installed. Install it with "pip install coloredlogs" to get cool logs!')

# Set config variables
maker.PAGE_LOAD_TIMEOUT_S = PAGE_LOAD_TIMEOUT_S
maker.DRIVER_TIMEOUT_S = DRIVER_TIMEOUT_S
maker.MICRO_DELAY_S = MICRO_DELAY_S
protector.PAGE_LOAD_TIMEOUT_S = PAGE_LOAD_TIMEOUT_S
protector.DRIVER_TIMEOUT_S = DRIVER_TIMEOUT_S
protector.MICRO_DELAY_S = MICRO_DELAY_S

if BUILTIN_DRIVER:
    # Install firefox driver binary
    _logger.info('Installing firefox driver...')
    install_driver()


def save_account(email: str, username: str, password: str):
    """Save account credentials to a file."""
    _logger.debug('Saving account credentials')
    with open(ACCOUNTS_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{email};{username};{password}\n')


# Check for tor and proxies
_logger.info('Checking if tor is running...')
is_tor_running = check_tor_running(TOR_IP, TOR_SOCKS5_PORT)
proxies = load_proxies(PROXIES_FILE)
is_proxies_loaded = len(proxies) != 0

# Define proxy manager: Tor, Proxies file or local IP
if is_tor_running:
    _logger.info('Tor is running. Connecting to Tor...')
    proxy = TorProxy(TOR_IP, TOR_PORT, TOR_PASSWORD, TOR_CONTROL_PORT, TOR_DELAY)
    _logger.info('Connected to Tor.')
    _logger.info('You will probably see a lot of RecaptchaException, but it\'s ok.')

else:
    _logger.info('Tor is not running.')

    if is_proxies_loaded:
        proxy = DefaultProxy(proxies)
        logging.info('Loaded %s proxies.', len(proxies))

    else:
        proxy = EmptyProxy()
        _logger.warning('No proxies loaded. Using local IP address.')
        _logger.warning('Tor is not running. It is recommended to run Tor to avoid IP cooldowns.\n\n' +
                        'Please, run command "python run_tor.py" or add proxies to file %s\n', PROXIES_FILE)


# Create accounts
for i in range(num_of_accounts):
    proxy_ = proxy.get_next()
    retries = 0

    _logger.info('Creating account (%s/%s)', i+1, num_of_accounts)
    _logger.info('Using proxy: %s', proxy)

    while retries < MAX_RETRIES:
        try:
            username, password = create_account(EMAIL, proxies=proxy_, hide_browser=HIDE_BROWSER)
            break

        except UsernameTakenException:
            _logger.error('Username %s taken. Trying again.', username)

        except SessionExpiredException:
            _logger.error('Page session expired. Trying again.')

        except NetworkException as e:
            # If we are using local IP address, we can't bypass IP cooldown
            if isinstance(proxy, EmptyProxy) and (
                    isinstance(e, IPCooldownException)):
                _logger.error(e)
                _logger.error('IP cooldown. Try again later or use tor/proxies.')
                exit(0)

            _logger.error('Network failed with %s.', e.__class__.__name__)
            proxy_ = proxy.get_next()
            _logger.info('Using next proxy: %s', proxy)

        except (KeyboardInterrupt, SystemExit, NoSuchWindowException):
            _logger.info('Exiting...')
            exit(0)

        except WebDriverException as e:
            _logger.error(e)
            logging.error('An error occurred during account creation. Trying again %s more times...', MAX_RETRIES - retries)
            retries += 1
            username, password = None, None
    else:
        _logger.error('An error occurred during account creation. Exiting...')
        exit(1)

    save_account(EMAIL, username, password)
    _logger.info('Account created! Protecting account...')

    # Try to protect account
    for i in range(MAX_RETRIES):
        try:
            protect_account(username, password, hide_browser=HIDE_BROWSER)
            _logger.info('Account protected!\n')
            break

        except IncorrectUsernameOrPasswordException:
            _logger.error('Seems like the account was not created or was deleted. Skipping...')
            break
        except WebDriverException as e:
            _logger.error(e)
            _logger.error('An error occurred during account protection. Trying again... [%s/%s]', i+1, MAX_RETRIES)
    else:
        _logger.error('Account protection failed. Skipping...')

_logger.info('Done!')
