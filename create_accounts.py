from selenium.common.exceptions import NoSuchWindowException

from reddit_account_generator import maker, protector, create_account, protect_account
from reddit_account_generator.proxies import DefaultProxy, TorProxy, EmptyProxy
from reddit_account_generator.utils import *
from reddit_account_generator.exceptions import *
from config import *


# Set config variables
maker.PAGE_LOAD_TIMEOUT_S = PAGE_LOAD_TIMEOUT_S
maker.DRIVER_TIMEOUT_S = DRIVER_TIMEOUT_S
maker.MICRO_DELAY_S = MICRO_DELAY_S
protector.PAGE_LOAD_TIMEOUT_S = PAGE_LOAD_TIMEOUT_S
protector.DRIVER_TIMEOUT_S = DRIVER_TIMEOUT_S
protector.MICRO_DELAY_S = MICRO_DELAY_S

if BUILTIN_DRIVER:
    # Download firefox binary (very lightweight, 16mb)
    import webdriverdownloader
    webdriverdownloader.GeckoDriverDownloader().download_and_install()


def save_account(email: str, username: str, password: str):
    """Save account credentials to a file."""
    with open(ACCOUNTS_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{email};{username};{password}\n')


num_of_accounts = int(input('How many accounts do you want to make? '))


# Check for tor and proxies
print('Checking if tor is running...')
is_tor_running = check_tor_running(TOR_IP, TOR_SOCKS5_PORT)
proxies = load_proxies(PROXIES_FILE)
is_proxies_loaded = len(proxies) != 0

# Define proxy manager: Tor, Proxies file or local IP
if is_tor_running:
    print('Tor is running. Connecting to Tor...')
    proxy = TorProxy(TOR_IP, TOR_PORT, TOR_PASSWORD, TOR_CONTROL_PORT, TOR_DELAY)
    print('Connected to Tor.')

else:
    print('Tor is not running.')

    if is_proxies_loaded:
        proxy = DefaultProxy(proxies)
        print(f'Loaded {len(proxies)} proxies.')

    else:
        proxy = EmptyProxy()
        print('No proxies loaded. Using local IP address.')
        print('Tor is not running. It is recommended to run Tor to avoid IP cooldowns.\n\n' +
             f'Please, run command "python run_tor.py" or add proxies to file {PROXIES_FILE}')


# Create accounts
for i in range(num_of_accounts):
    username = generate_username()
    password = generate_password()
    proxy_ = proxy.get_next()

    print(f'Creating account with username {username} ({i+1}/{num_of_accounts})')
    print(f'Using proxy: {proxy}')

    while True:
        try:
            create_account(EMAIL, username, password,
                         proxies=proxy_, hide_browser=HIDE_BROWSER)
            break

        except UsernameTakenException:
            username = generate_username()
            print(f'Username taken. Trying {username}...')

        except NetworkException as e:
            # If we are using local IP address, we can't bypass IP cooldown
            if isinstance(proxy, EmptyProxy) and (
                    isinstance(e, IPCooldownException) or
                    isinstance(e, EMailCooldownException)):
                print(e)
                print(f'IP cooldown. Try again later or use tor/proxies.')
                exit(0)

            print(f'Network failed with {e.__class__.__name__}.')
            proxy_ = proxy.get_next()
            print(f'Using next proxy: {proxy}')

        except (KeyboardInterrupt, SystemExit, NoSuchWindowException):
            print('Exiting...')
            exit(0)

        except Exception as e:
            print(e)
            print(f'An error occurred during account creation. Trying again...')

    save_account(EMAIL, username, password)
    print('Account created! Protecting account...')

    # Try to protect account
    for i in range(ACCOUNT_PROTECTION_RETRIES):
        try:
            protect_account(username, password, hide_browser=HIDE_BROWSER)
            print('Account protected!')
            break

        except IncorrectUsernameOrPasswordException:
            print('Seems like the account was not created or was deleted. Skipping...')
            break
        except Exception as e:
            print(e)
            print(f'An error occurred during account protection. Trying again... [{i+1}/{ACCOUNT_PROTECTION_RETRIES}]')
    else:
        print('Account protection failed. Skipping...')

    proxy_ = proxy.get_next()
    print(f'Using next proxy: {proxy}')
