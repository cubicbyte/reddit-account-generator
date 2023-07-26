import time
import logging

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_recaptcha_solver import RecaptchaSolver

from .utils import setup_firefox_driver, try_to_click
from .exceptions import *

PAGE_LOAD_TIMEOUT_S = 60
DRIVER_TIMEOUT_S = 60
MICRO_DELAY_S = 1


def create_account(email: str, username: str, password: str,
                   proxies: dict[str, str] | None = None, hide_browser: bool = True):
    """Create a Reddit account."""

    logging.info('Creating account with username %s', username)
    driver = setup_firefox_driver(proxies, hide_browser)

    if PAGE_LOAD_TIMEOUT_S is not None:
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_S)

    try:  # try/except to quit driver if error occurs

        # Open website
        try:
            driver.get('https://www.reddit.com/register/')
        except WebDriverException:
            raise TimeoutException('Website takes too long to load. Probably a problem with the proxy.')

        # Enter email and go to next page
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
                    raise EMailCooldownException(email_err.text)
                raise Exception(email_err.text)

        # Wait until page loads
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.element_to_be_clickable((By.ID, 'regUsername')))

        # Enter username
        username_input = driver.find_element(By.ID, 'regUsername')
        try_to_click(username_input, delay=MICRO_DELAY_S)
        username_input.send_keys(username)

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
                raise UsernameTakenException(username_err.text)
            if 'character' in username_err.text.lower():
                raise UsernameLengthException(username_err.text)
            if 'symbols' in username_err.text.lower():
                raise UsernameSymbolsException(username_err.text)
            raise Exception(username_err.text)

        if password_err.text != '':
            if 'character' in password_err.text.lower():
                raise PasswordLengthException(password_err.text)
            raise Exception(password_err.text)
        
        # Solve captcha
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.element_to_be_clickable((By.XPATH, '//iframe[@title="reCAPTCHA"]')))
        recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')

        if recaptcha_iframe.is_displayed():
            solver = RecaptchaSolver(driver)
            solver.click_recaptcha_v2(iframe=recaptcha_iframe)

        # Submit registration
        submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[data-step="username-and-password"]')
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.element_to_be_clickable(submit_btn))
        try_to_click(submit_btn, delay=MICRO_DELAY_S)

        # Check if submitted
        time.sleep(MICRO_DELAY_S)
        submit_err = driver.find_element(By.CSS_SELECTOR, 'span[data-step="username-and-password"]')

        if submit_err.text != '':
            if 'again' in submit_err.text.lower():
                raise IPCooldownException(submit_err.text)
            raise Exception(submit_err.text)

        # Wait until button is pressed
        time.sleep(MICRO_DELAY_S)

        # Account created!

    except Exception as e:  # quit driver if error occurs
        driver.quit()
        raise e

    driver.quit()
