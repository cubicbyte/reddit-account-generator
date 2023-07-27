from .maker import create_account
from .protector import protect_account
from .scriptCreator import make_script
from .emailVerification import gen, verify

def install_driver():
    """Install firefox driver binary."""
    import webdriverdownloader
    webdriverdownloader.GeckoDriverDownloader().download_and_install()
