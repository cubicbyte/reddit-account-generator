from .maker import create_account
from .protector import protect_account
from .verifier import verify_email

def install_driver():
    """Install firefox driver binary."""
    import webdriverdownloader
    webdriverdownloader.GeckoDriverDownloader().download_and_install()
