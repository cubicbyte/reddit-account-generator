# Download necessary ffmpeg binary
import static_ffmpeg
static_ffmpeg.add_paths()
del static_ffmpeg

from .maker import create_account
from .protector import protect_account


def install_driver():
    """Install firefox driver binary."""
    import webdriverdownloader
    try:
        webdriverdownloader.GeckoDriverDownloader().download_and_install()
    except RuntimeError:
        raise RuntimeError('Failed to install firefox driver. You\'re probably running the application too many times. Try again later. Limit: 60 requests per hour')
