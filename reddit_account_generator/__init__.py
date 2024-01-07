"""A library for generating Reddit accounts.

Documentation can be found at
https://github.com/cubicbyte/reddit-account-generator
"""

import static_ffmpeg
import logging

from ._maker import create_account
from ._verifier import verify_email

__all__ = [
    'create_account',
    'verify_email',
]

logger = logging.getLogger('reddit_account_generator')

# Download necessary ffmpeg binary
logger.info('Downloading ffmpeg binary...')
static_ffmpeg.add_paths()
