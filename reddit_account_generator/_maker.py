"""Module for creating a reddit account"""

import time
import logging
from typing import Optional, Tuple

from tempmail import EMail
from selenium.common.exceptions import TimeoutException, WebDriverException, \
    NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_recaptcha_solver import RecaptchaSolver, RecaptchaException

from .utils import setup_chrome_driver, try_to_click, generate_password, generate_username, Proxy
from .config import PAGE_LOAD_TIMEOUT_S, DRIVER_TIMEOUT_S, MICRO_DELAY_S
from .exceptions import IPCooldownException, SessionExpiredException, UsernameTakenException, \
    UsernameLengthException, UsernameSymbolsException, PasswordLengthException, BotDetectedException, \
    RedditException


logger = logging.getLogger('reddit_account_generator')


def create_account(email: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None,
                   proxy: Optional[Proxy] = None, hide_browser: bool = True) -> Tuple[str, str, str]:
    """Create a Reddit account.

    :param email: Email address to use. If None, a random email will be generated.
    :param username: Username to use. If None, a random username will be generated.
    :param password: Password to use. If None, a random password will be generated.
    :param proxy: Proxy to use
    :param hide_browser: Hide browser window
    :return: Tuple of email, username and password
    """

    logger.info('Creating reddit account')
    driver = None

    try:  # try/except to quit driver if error occurs
        driver = setup_chrome_driver(proxy, hide_browser)

        if PAGE_LOAD_TIMEOUT_S is not None:
            driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_S)

        if email is None:
            email = EMail().address

        if password is None:
            password = generate_password()

        # Open website
        logger.debug('Opening registration page')
        try:
            driver.get('https://www.reddit.com/register/')
        except WebDriverException:
            raise TimeoutException('Website takes too long to load. Probably a proxy is too slow.')

        # Checking for user agent error
        try:
            first_h1 = driver.find_element(By.TAG_NAME, 'h1')
            if first_h1.text == 'whoa there, pardner!':
                raise BotDetectedException('Reddit didn\'t like your user-agent. Maybe it\'s empty?')
        except NoSuchElementException:
            pass

        # Enter email and go to next page
        logger.debug('Entering email')
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.element_to_be_clickable((By.ID, 'regEmail')))
        email_input = driver.find_element(By.ID, 'regEmail')
        email_submit = driver.find_element(By.CSS_SELECTOR, 'button[data-step="email"]')
        email_input.click()
        email_input.send_keys(email)
        try_to_click(email_submit, delay=MICRO_DELAY_S)

        # Check for email error
        time.sleep(MICRO_DELAY_S)
        try:
            email_err = driver.find_element(By.CLASS_NAME, 'AnimatedForm__errorMessage')
        except:
            pass
        else:
            if email_err.text != '':
                if 'again' in email_err.text.lower():
                    raise SessionExpiredException(email_err.text)
                raise RedditException(email_err.text)

        # Wait until page loads
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.element_to_be_clickable((By.ID, 'regUsername')))

        # Enter username
        logger.debug('Entering username and password')
        try:
            # Get random username suggested by reddit
            random_username_el = driver.find_element(By.CLASS_NAME, 'Onboarding__usernameSuggestion')
        except NoSuchElementException:
            # Sometimes reddit doesn't suggest any username
            username = generate_username()

        username_input = driver.find_element(By.ID, 'regUsername')
        if username is not None:
            # Enter given username
            try_to_click(username_input, delay=MICRO_DELAY_S)
            username_input.send_keys(username)
        else:
            # Click first reddit sugegsted name
            try_to_click(random_username_el, delay=MICRO_DELAY_S)
            username = random_username_el.text

        # Enter password
        password_input = driver.find_element(By.ID, 'regPassword')
        try_to_click(password_input, delay=MICRO_DELAY_S)
        password_input.send_keys(password)

        # Check for username and password errors
        username_err = driver.find_element(By.XPATH, '//div[@data-for="username"]')
        password_err = driver.find_element(By.XPATH, '//div[@data-for="password"]')
        try_to_click(username_input, delay=MICRO_DELAY_S)
        time.sleep(MICRO_DELAY_S)

        if username_err.text != '':
            if 'taken' in username_err.text.lower():
                raise UsernameTakenException(username_err.text, username)
            if 'character' in username_err.text.lower():
                raise UsernameLengthException(username_err.text, username)
            if 'symbols' in username_err.text.lower():
                raise UsernameSymbolsException(username_err.text, username)
            raise RedditException(username_err.text)

        if password_err.text != '':
            if 'character' in password_err.text.lower():
                raise PasswordLengthException(password_err.text)
            raise RedditException(password_err.text)

        # Solve captcha
        logger.debug('Solving captcha')
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.element_to_be_clickable((By.XPATH, '//iframe[@title="reCAPTCHA"]')))
        recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')

        if recaptcha_iframe.is_displayed():
            solver = RecaptchaSolver(driver)
            for _ in range(5):
                try:
                    solver.click_recaptcha_v2(iframe=recaptcha_iframe)
                    break
                except ElementClickInterceptedException:
                    pass
            else:
                raise RecaptchaException('Could not solve captcha')

        # Submit registration
        logger.debug('Submitting registration')
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[data-step="username-and-password"]')
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.element_to_be_clickable(submit_btn))
        try_to_click(submit_btn, delay=MICRO_DELAY_S)

        # Check if submitted
        time.sleep(MICRO_DELAY_S)
        submit_err = driver.find_element(By.CSS_SELECTOR, 'span[data-step="username-and-password"]')

        if submit_err.text != '':
            if 'again' in submit_err.text.lower():
                raise IPCooldownException(submit_err.text)
            raise RedditException(submit_err.text)

        # Wait until button is pressed
        time.sleep(MICRO_DELAY_S * 3)

        # Account created!

    finally:
        # quit driver even if error occurs
        if driver is not None:
            logger.debug('Quitting driver')
            driver.quit()

    return email, username, password
