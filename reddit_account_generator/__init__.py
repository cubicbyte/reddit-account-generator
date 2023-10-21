"""A library for generating Reddit accounts.

Documentation can be found at
https://github.com/cubicbyte/reddit-account-generator
"""

import static_ffmpeg
import logging as _logging
_logger = _logging.getLogger('reddit_account_generator')

# Download necessary ffmpeg binary
_logger.info('Downloading ffmpeg binary...')
static_ffmpeg.add_paths()
del static_ffmpeg

from ._maker import create_account
from ._verifier import verify_email

def install_driver():
    # TODO: use webdriver-manager
    """Install chrome driver binary."""
    import webdriverdownloader
    try:
        webdriverdownloader.ChromeDriverDownloader().download_and_install()
    except RuntimeError:
        raise RuntimeError('Failed to install chrome driver. You\'re probably running the application too many times. Try again later. Limit: 60 requests per hour')
