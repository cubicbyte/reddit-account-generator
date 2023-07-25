import os
import sys
from pathlib import Path

_no_tor_help = '''
Tor executable not found.

Are you sure you put the Tor folder in the directory where this script is located?

If you haven't downloaded Tor yet, please follow this link: https://www.torproject.org/download/tor/ (you need Tor Expert Bundle)

No installation is required, just download Tor for your system and unzip the archive into the root reddit-account-generator folder
'''

root_dir = os.path.dirname(os.path.abspath(__file__))
_tor_exec_names = ['tor', 'tor.exe']

# Find tor executable
for path in Path(root_dir).rglob('tor*'):
    if path.name in _tor_exec_names and path.is_file():
        tor_executable = path
        break
else:
    print(_no_tor_help)
    sys.exit(1)

# Run tor
torrc_file = os.path.join(root_dir, 'torrc')
os.system(fr'{tor_executable} --defaults-torrc {torrc_file} --HTTPTunnelPort 1881')
# TODO: Try to move --HTTPTunnelPort 1881 to torrc file
