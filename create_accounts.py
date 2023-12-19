import time
import logging

from selenium.common.exceptions import NoSuchWindowException, WebDriverException

from reddit_account_generator import config as generator_config, create_account, verify_email
from reddit_account_generator.proxies import DefaultProxy, TorProxy, EmptyProxy
from reddit_account_generator.utils import *
from reddit_account_generator.exceptions import *
from config import *


num_of_accounts = int(input('How many accounts do you want to make? '))


# Set logging
logger = logging.getLogger('script')
logging.getLogger('WDM').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('selenium').setLevel(logging.WARNING)

try:
    import coloredlogs
    coloredlogs.install(level=LOG_LEVEL, fmt='%(asctime)s %(levelname)s %(message)s')
except ImportError:
    logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s %(levelname)s %(message)s')
    logging.warning('Coloredlogs is not installed. Install it with "pip install coloredlogs" to get cool logs!')

# Set config variables
generator_config.PAGE_LOAD_TIMEOUT_S = PAGE_LOAD_TIMEOUT_S
generator_config.DRIVER_TIMEOUT_S = DRIVER_TIMEOUT_S
generator_config.MICRO_DELAY_S = MICRO_DELAY_S


def save_account(email: str, username: str, password: str):
    """Save account credentials to a file."""
    logger.debug('Saving account credentials')
    with open(ACCOUNTS_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{email};{username};{password}\n')


# Define proxy manager: Tor, Proxies file or local IP

# Check if proxies file contains proxies
proxies = load_proxies(PROXIES_FILE)
is_proxies_loaded = len(proxies) != 0

if is_proxies_loaded:
    proxy_manager = DefaultProxy(proxies)
    logging.info('Loaded %s proxies.', len(proxies))

else:
    # Try to use Tor
    logger.info('Checking if tor is running...')

    if check_tor_running(TOR_IP, TOR_SOCKS5_PORT):
        logger.info('Tor is running. Connecting to Tor...')
        proxy_manager = TorProxy(TOR_IP, TOR_PORT, TOR_PASSWORD, TOR_CONTROL_PORT, TOR_DELAY)
        logger.info('Connected to Tor.')

    else:
        # Use local IP address
        proxy_manager = EmptyProxy()
        logger.warning('Tor is not running. Using local IP address.')
        logger.warning('It is recommended to use proxies or Tor to avoid IP cooldowns.\n\n' +
                        'Please, run command "python run_tor.py" or add proxies to file %s\n', PROXIES_FILE)


# Create accounts
IP_COOLDOWN_S = 60 * 10  # 10 minutes
latest_account_created_timestamp = time.time() - IP_COOLDOWN_S

try:
    for i in range(num_of_accounts):
        # Check if we need to wait for IP cooldown
        delta = time.time() - latest_account_created_timestamp
        if isinstance(proxy_manager, EmptyProxy) and delta < IP_COOLDOWN_S:
            logger.warning(f'IP cooldown. Waiting {(IP_COOLDOWN_S - delta) / 60 :.1f} minutes. Use tor/proxies to avoid this.')
            time.sleep(IP_COOLDOWN_S - delta)

        logger.info('Creating account (%s/%s)', i+1, num_of_accounts)
        proxy = proxy_manager.get_next()

        # Create account
        retries = 0
        while True:
            # Every 5 retries, change proxy
            retries += 1
            if retries % 5 == 0:
                proxy = proxy_manager.get_next()
                logger.warning('Failed 5 times in a row. Using next proxy: %s', proxy)

            try:
                email, username, password = create_account(
                    email=EMAIL or None,
                    proxy=proxy,
                    hide_browser=HIDE_BROWSER
                )
                latest_account_created_timestamp = time.time()
                break

            except UsernameTakenException:
                logger.error('Username %s taken. Trying again.', username)

            except SessionExpiredException:
                logger.error('Page session expired. Trying again.')

            except NetworkException as e:
                # If we are using local IP address, we can't bypass IP cooldown
                if isinstance(proxy_manager, EmptyProxy) and (
                        isinstance(e, IPCooldownException)):
                    logger.error(e)
                    logger.error(f'IP cooldown. Trying again in {e.cooldown}. Use tor/proxies to avoid this.')
                    time.sleep(e.cooldown.total_seconds())
                    continue

                logger.error('Network failed with %s.', e.__class__.__name__)
                if isinstance(e, IPCooldownException) and isinstance(proxy_manager, TorProxy):
                    logger.info('If you\'re using tor proxy, it will take a few of RecaptchaException per 1 account.')

                proxy = proxy_manager.get_next()
                retries = 0
                logger.info('Using next proxy: %s', proxy)

            except (KeyboardInterrupt, SystemExit, NoSuchWindowException) as e:
                # Handle this in top level try-except
                raise e

            except Exception as e:
                logger.error(e)
                logging.error('An error occurred during account creation. Trying again...')

        save_account(email, username, password)
        logger.info('Account created!')

        # Verify email
        if EMAIL != '':
            # You need to manually verify email if you are using your own email
            pass
        else:
            for i in range(MAX_RETRIES):
                try:
                    verify_email(email, proxy=proxy)
                    logger.info('Email verified!\n')
                    break

                except TimeoutError as e:
                    logger.error(f'Timeout error: {e}\nProbably email message was not received. Creating next account...')
                    break

                except Exception as e:
                    logger.error(e)
                    logger.error('An error occurred during email verification. Trying again... [%s/%s]', i+1, MAX_RETRIES)
            else:
                logger.warning('Email verification failed. Skipping...')

except (KeyboardInterrupt, SystemExit, NoSuchWindowException):
    logger.info('Exiting...')
    exit(0)

logger.info('Done!')
