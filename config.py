
# You can set here your email if you want, but in that case you need to manually verify account
EMAIL = ''

# Should we hide browser window? Must be True if using VPS
# True / False, default: True
HEADLESS = True

PAGE_LOAD_TIMEOUT_S = 120   # int, float or None
DRIVER_TIMEOUT_S = 120    # int, float
MICRO_DELAY_S = 1       # int, float
MAX_RETRIES = 10  # Max retries for email verification
LOG_LEVEL = 'DEBUG'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Tor proxy config
TOR_IP = '127.0.0.1'
TOR_PORT = 1881
TOR_SOCKS5_PORT = 9050
TOR_CONTROL_PORT = 9051
TOR_PASSWORD = 'Passwort'
TOR_DELAY = 5

PROXIES_FILE = 'proxies.txt'
ACCOUNTS_FILE = 'accounts.csv'
