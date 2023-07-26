import time
import random
import logging

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .utils import setup_firefox_driver
from .exceptions import IncorrectUsernameOrPasswordException

PAGE_LOAD_TIMEOUT_S = 60
DRIVER_TIMEOUT_S = 60
MICRO_DELAY_S = 1

# Random subreddits to subscribe to
subs = [
    'gaming',
    'csgo',
    'memes',
    'tf2',
    'askreddit',
    'abruptchaos',
    'perfectlycutscreams',
    'askouija',
    'apple',
    'linux',
    'pcmasterrace',
    'clashroyale',
    'minecraft',
    'cursed_comments',
    'shitposting',
]


def protect_account(username: str, password: str,
                    proxies: dict[str, str] | None = None, hide_browser: bool = True):
    """
    Prevent account blocking due to suspicion of being a bot.

    This function will:
    - Subscribe to random subreddit
    - For now, that's all
    """

    logging.info('Protecting account with username %s', username)
    driver = setup_firefox_driver(proxies, hide_browser)

    if PAGE_LOAD_TIMEOUT_S is not None:
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_S)

    try:  # try/except to quit driver if error occurs

        # Open login website
        try:
            driver.get('https://www.reddit.com/login/')
        except WebDriverException:
            raise TimeoutException('Website takes too long to load. Probably a problem with the proxy.')
        
        # Enter username and password
        username_input = driver.find_element(By.ID, 'loginUsername')
        password_input = driver.find_element(By.ID, 'loginPassword')
        username_input.click()
        username_input.send_keys(username)
        password_input.click()
        password_input.send_keys(password)

        # Submit login
        time.sleep(MICRO_DELAY_S)
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()

        # Check if submitted
        time.sleep(MICRO_DELAY_S)
        submit_err = driver.find_element(By.CLASS_NAME, 'AnimatedForm__errorMessage')

        if submit_err.text != '':
            if 'incorrect' in submit_err.text.lower():
                raise IncorrectUsernameOrPasswordException(submit_err.text)
            raise Exception(submit_err.text)

        # Logged in!

        # Go to random subreddit
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.url_matches('https://www.reddit.com*'))
        driver.get(f'https://www.reddit.com/r/{random.choice(subs)}/')

        # Subscribe
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Join"]')))
        subscribe_btn = driver.find_element(By.XPATH, '//button[text()="Join"]')
        subscribe_btn.click()

        # Done!

    except Exception as e:  # quit driver if error occurs
        driver.quit()
        raise e

    driver.quit()
