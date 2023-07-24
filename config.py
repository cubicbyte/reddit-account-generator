
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


assert EMAIL != '', 'Please enter your email in config.py file'
