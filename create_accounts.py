from selenium.common.exceptions import NoSuchWindowException

from config import *
from utils import *
from exceptions import *
from maker import make_account
from protector import protect_account

if BUILTIN_DRIVER:
    # Download firefox binary (very lightweight, 16mb)
    import webdriverdownloader
    webdriverdownloader.GeckoDriverDownloader().download_and_install()

def save_account(email: str, username: str, password: str):
    """Save account credentials to a file."""
    with open(ACCOUNTS_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{email};{username};{password}\n')


num_of_accounts = int(input('How many accounts do you want to make? '))

proxies = load_proxies(PROXIES_FILE)
proxy_i = 0

if len(proxies) == 0:
    print('No proxies loaded. Using local IP address.')

for i in range(num_of_accounts):
    username = generate_username()
    password = generate_password()

    print(f'Creating account with username {username} ({i+1}/{num_of_accounts})')

    while True:
        # If proxies are loaded, use them
        if len(proxies) != 0:
            if proxy_i >= len(proxies):
                print('No more proxies. Restarting from the beginning...')
                proxy_i = 0

            proxy = {
                'socks': proxies[proxy_i]
            }

            print(f'Using proxy {proxies[proxy_i]}')
        else:
            proxy = None
            proxy_i = 0

        try:
            make_account(EMAIL, username, password,
                         proxies=proxy, hide_browser=HIDE_BROWSER)
            break

        except UsernameTakenException:
            username = generate_username()
            print(f'Username taken. Trying {username}...')

        except ProxyException as e:
            if proxy is None and (isinstance(e, IPCooldownException) or
                                  isinstance(e, EMailCooldownException)):
                print(e)
                print(f'IP cooldown. Try again later or use proxies.')
                exit(0)
            print(f'Network failed with {e.__class__.__name__}. Trying again...')
            proxy_i += 1

        except NoSuchWindowException:
            print('Browser window closed. Trying next proxy...')
            proxy_i += 1

        except (KeyboardInterrupt, SystemExit):
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

    proxy_i += 1
