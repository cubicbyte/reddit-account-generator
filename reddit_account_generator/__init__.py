from .maker import create_account
from .protector import protect_account

def install_driver():
    """Install firefox binary."""
    import webdriverdownloader
    webdriverdownloader.GeckoDriverDownloader().download_and_install()
