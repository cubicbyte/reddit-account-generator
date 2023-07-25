
EMAIL = ''

PROXIES_FILE = 'proxies.txt'
ACCOUNTS_FILE = 'accounts.csv'

PAGE_LOAD_TIMEOUT_S = 120   # int, float or None
DRIVER_TIMEOUT_S = 120    # int, float
MICRO_DELAY_S = 1       # int, float
HIDE_BROWSER = False
ACCOUNT_PROTECTION_RETRIES = 3
# You can set to False if you have Firefox installed
BUILTIN_DRIVER = True

# Tor proxy config
TOR_IP = '127.0.0.1'
TOR_PORT = 1881
TOR_SOCKS5_PORT = 9050
TOR_CONTROL_PORT = 9051
TOR_PASSWORD = 'Passwort'
TOR_DELAY = 5


assert EMAIL != '', 'Please enter your email in config.py file'
