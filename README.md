# Automatic Reddit Account Maker

![Reddit Logo](https://www.redditstatic.com/about/assets/reddit-logo.png)

A python script on selenium to automatically create Reddit accounts.

## Table of Contents

- [Features](#features)
- [Quick info](#quick-info)
- [Installation](#installation)
- [Usage](#usage)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Automatic captcha bypass**: The script automatically solves captchas during the account creation process.
- **Proxy Support**: Since reddit allows you to create 1 account per IP every 10 minutes, this is very important.
- **Resilience**: The script is able to handle most errors that may occur during the account creation process.

## Quick info

You still need to activate the accounts via email. But it doesn't take much time.

#### TODO:
- [x] Add automatic browser driver download
- [x] Add Tor support for easier proxy management
- [ ] Handle error when sub is not available
- [ ] Automatic email verification
- [ ] Make this a python package and document it

## Installation

1. Clone this repository to your local machine:

```shell
git clone https://github.com/cubicbyte/reddit-account-generator.git
cd reddit-account-generator
```

2. Install the required dependencies:

```shell
pip install -r requirements.txt
```

## Usage

> **Note** **You need to use Tor (not browser) or proxy, because you can only create 1 account per IP.**

#### Using Tor (recommended)
Run this command and follow the instructions:
```shell
python run_tor.py
```

#### Using proxies
Add your proxies to the proxies.txt file

### Configuration

Open the `config.py` file and put your email to be used on your accounts. Other settings are optional.

### Command Line Usage

1. Run the script:

```shell
python create_accounts.py
```

2. Enter the number of accounts you want to create
3. Sit back and relax while the script generates Reddit accounts for you :)

## Requirements

- Python 3.5+
- [selenium](https://pypi.org/project/selenium/)
- [selenium-recaptcha-solver](https://pypi.org/project/selenium-recaptcha-solver/)
- [random-username](https://pypi.org/project/random-username/)
- [webdriverdownloader](https://pypi.org/project/webdriverdownloader/)

## Contributing

Contributions to this project are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Disclaimer:** Please use this script responsibly and abide by Reddit's terms of service. Automated account creation might be against Reddit's policies, and using this script could potentially lead to consequences. The creators and maintainers of this project are not responsible for any misuse or damages caused by its usage.
