# Automatic Reddit Account Maker

![Reddit Logo](https://www.redditstatic.com/about/assets/reddit-logo.png)

A python script on selenium to automatically create Reddit accounts.

## Table of Contents

- [Introducing](#introducing)
    - [Features](#features)
    - [Quick info](#quick-info)
- [Getting started](#getting-started)
    - [Script Installation](#script-installation)
    - [Script Usage](#script-usage)
    - [Package Installation](#package-installation)
    - [Package Usage](#package-usage-example)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

# Introducing

## Features
- **Automatic captcha bypass**: The script automatically solves captchas during the account creation process.
- **Automatic email verification**: The script automatically verifies the email address used for the account.
- **Proxy Support**: Since reddit allows you to create 1 account per IP every 10 minutes, this is very important.
- **Resilience**: The script is able to handle most errors that may occur during the account creation process.

## Quick info

Chrome should be installed on your system for the script to work.

It is recommended to use proxies, because you can only create 1 account per IP in 10 minutes. See file **proxies.txt** or run `python run_tor.py`

To access the auto-generated email, visit https://1secmail.com

If you are using auto-generated email, you should not show anyone its address. Having the address of this email, anyone can access it.

# Getting started

> **Note** Python 3.7+ is required

## Script installation

1. Clone this repository to your local machine:

```shell
git clone https://github.com/cubicbyte/reddit-account-generator.git
cd reddit-account-generator
```

2. Install the required dependencies:

```shell
pip install -r requirements.txt
```

3. Install chrome and other things:

    - Windows/macOS: Just install chrome
    - Linux amd64 (Choose this if not sure):
    ```shell
    sudo apt update
    sudo apt install wget
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo dpkg -i google-chrome-stable_current_amd64.deb
    sudo apt-get install -f
    ```
   
    - Linux arm64:
    ```shell
    sudo apt update
    sudo apt install chromium-browser
    ```

    - Android (Termux):
    ```shell
    pkg update
    pkg install x11-repo -y
    pkg install tur-repo -y
    pkg install chromium -y
    pkg install ffmpeg -y
    ```
## Script usage

### Configuring

Configuring is optional. But if you want, you can change the settings in the [config.py](config.py) file.

### Proxies (Optional)

Script supports proxies, which can bypass the limit of 1 account per IP in 10 minutes.

Here is list of supported proxy types:
- `python run_tor.py` - Tor proxy (Works bad at the moment)
- **Proxies from file** - You can add your own proxies to the file [proxies.txt](proxies.txt)

### Starting

1. Run the script:

```shell
python create_accounts.py
```

2. Enter the number of accounts you want to create
3. Sit back and relax while the script generates Reddit accounts for you :)

## Package installation

There are two ways to install the library:

- Installation using pip (a Python package manager):

```shell
pip install reddit-account-generator
```

- Installation from source (requires git):

```shell
git clone https://github.com/cubicbyte/reddit-account-generator.git
cd reddit-account-generator
python setup.py install
```

or:

```shell
pip install git+https://github.com/eternnoir/pyTelegramBotAPI.git
```

It is generally recommended to use the first option.

Update package:

```shell
pip install reddit-account-generator --upgrade
```

## Package Usage Example

```python
from reddit_account_generator import create_account, verify_email

# Create account
email, username, password = create_account()

# Verify email
verify_email(email)

# Done!
print(f'Email: {email}\nUsername: {username}\nPassword: {password}')
```

Advanced usage:

```python
from reddit_account_generator import create_account
from reddit_account_generator.proxies import DefaultProxy

email = 'your-email@gmail.com'
username = 'PolishCardinal69'
password = '31vV3X1zy8YP'

# Load proxies from file
with open('proxies.txt', 'r') as f:
    proxy = DefaultProxy(f.read().splitlines())

# Create account using proxy
create_account(email, username, password, proxy=proxy.get_next())

# Verify email (proxy is not required)
verify_email(email)

# Done!
```


## Requirements

- Python 3.8+
- [selenium](https://pypi.org/project/selenium/)
- [selenium-recaptcha-solver](https://pypi.org/project/selenium-recaptcha-solver/)
- [random-username](https://pypi.org/project/random-username/)
- [webdriver-manager](https://pypi.org/project/webdriver-manager/)
- [stem](https://pypi.org/project/stem/)
- [static-ffmpeg](https://pypi.org/project/static-ffmpeg/)
- [tempmail-python](https://pypi.org/project/tempmail-python/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- [coloredlogs](https://pypi.org/project/coloredlogs/) *optional

## Contributing

Contributions to this project are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Disclaimer:** Please use this script responsibly and abide by Reddit's terms of service. Automated account creation might be against Reddit's policies, and using this script could potentially lead to consequences. The creator and maintainers of this project are not responsible for any misuse or damages caused by its usage.
