"""Module for creating a reddit account"""

import time
import logging
from typing import Optional, Tuple

from tempmail import EMail
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_recaptcha_solver import RecaptchaSolver, RecaptchaException

from .utils import (
    setup_chrome_driver,
    try_to_click,
    generate_password,
    generate_username,
    Proxy,
)
from .config import PAGE_LOAD_TIMEOUT_S, DRIVER_TIMEOUT_S, MICRO_DELAY_S
from .exceptions import (
    IPCooldownException,
    SessionExpiredException,
    UsernameTakenException,
    UsernameLengthException,
    UsernameSymbolsException,
    PasswordLengthException,
)


logger = logging.getLogger("reddit_account_generator")


def select_first_continue_button(driver):
    shadow_root_script = 'return document.querySelector("body > shreddit-app > shreddit-overlay-display").shadowRoot.querySelector("shreddit-signup-drawer").shadowRoot.querySelector("shreddit-drawer > div > shreddit-async-loader > div > shreddit-slotter").shadowRoot.querySelector("#register > faceplate-tabpanel > auth-flow-modal:nth-child(1) > div.w-100 > faceplate-tracker > button")'
    continue_button = driver.execute_script(shadow_root_script)
    return continue_button


def select_second_continue_button(driver):
    shadow_root_script = 'return document.querySelector("body > shreddit-app > shreddit-overlay-display").shadowRoot.querySelector("shreddit-signup-drawer").shadowRoot.querySelector("shreddit-drawer > div > shreddit-async-loader > div > shreddit-slotter").shadowRoot.querySelector("#register > faceplate-tabpanel > auth-flow-modal:nth-child(2) > div.w-100 > faceplate-tracker > button")'
    continue_button = driver.execute_script(shadow_root_script)
    return continue_button


def did_element_dissapear(driver, element_id, timeout=10):
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            # Attempt to find and check the element's visibility
            element = driver.find_element(By.ID, element_id)
            if not element.is_displayed():
                return True
        except (NoSuchElementException, StaleElementReferenceException):
            return False
        # Sleep briefly to allow for DOM updates
        time.sleep(0.5)


def create_account(
    email: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    proxy: Optional[Proxy] = None,
    hide_browser: bool = True,
) -> Tuple[str, str, str]:
    """Create a Reddit account.

    :param email: Email address to use. If None, a random email will be generated.
    :param username: Username to use. If None, a random username will be generated.
    :param password: Password to use. If None, a random password will be generated.
    :param proxy: Proxy to use
    :param hide_browser: Hide browser window
    :return: Tuple of email, username and password
    """

    logger.info("Creating reddit account")
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
        logger.debug("Opening registration page")
        try:
            driver.get("https://www.reddit.com/register/")
        except WebDriverException:
            raise TimeoutException(
                "Website takes too long to load. Probably a problem with the proxy."
            )

        # Checking if IP is blocked
        try:
            first_h1 = driver.find_element(By.TAG_NAME, "h1")
            if first_h1.text == "whoa there, pardner!":
                # FIXME: this will throw error when accessing err.cooldown
                raise IPCooldownException(
                    "Your IP is temporarily blocked. Try again later."
                )
        except NoSuchElementException:
            pass

        # Enter email and go to next page
        logger.debug("Entering email")

        wait = WebDriverWait(driver, 20)

        email_input = wait.until(EC.element_to_be_clickable((By.ID, "register-email")))
        email_input.click()
        email_input.send_keys(email)

        continue_button = select_first_continue_button(driver)

        # Click the "Continue" button
        continue_button.click()

        # Check for email error
        time.sleep(MICRO_DELAY_S)
        try:
            email_err = driver.find_element(By.CLASS_NAME, "AnimatedForm__errorMessage")
        except:
            pass
        else:
            if email_err.text != "":
                if "again" in email_err.text.lower():
                    raise SessionExpiredException(email_err.text)
                raise Exception(email_err.text)

        # Wait until page loads
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(
            EC.element_to_be_clickable((By.ID, "register-username"))
        )

        # Enter username
        logger.debug("Entering username and password")
        try:
            # Get random username suggested by reddit
            random_username = driver.find_element(
                By.XPATH,
                "/html/body/div/main/div[2]/div/div/div[2]/div[2]/div/div/a[1]",
            )
        except NoSuchElementException:
            # Sometimes reddit doesn't suggest any username
            username = generate_username()

        username_input = driver.find_element(By.ID, "register-username")
        if username is not None:
            # Enter given username
            try_to_click(username_input, delay=MICRO_DELAY_S)
            username_input.send_keys(username)
        else:
            # Click first reddit sugegsted name
            try_to_click(random_username, delay=MICRO_DELAY_S)
            username = random_username.text

        # Enter password
        password_input = driver.find_element(By.ID, "register-password")
        try_to_click(password_input, delay=MICRO_DELAY_S)
        password_input.send_keys(password)

        # Check for username and password errors
        username_err = driver.execute_script(
            'return document.querySelector("body > shreddit-app > shreddit-overlay-display").shadowRoot.querySelector("shreddit-signup-drawer").shadowRoot.querySelector("shreddit-drawer > div > shreddit-async-loader > div > shreddit-slotter").shadowRoot.querySelector("#register-username").shadowRoot.querySelector("faceplate-form-helper-text").shadowRoot.querySelector("#helper-text");'
        )
        password_err = driver.execute_script(
            'return document.querySelector("body > shreddit-app > shreddit-overlay-display").shadowRoot.querySelector("shreddit-signup-drawer").shadowRoot.querySelector("shreddit-drawer > div > shreddit-async-loader > div > shreddit-slotter").shadowRoot.querySelector("#register-password").shadowRoot.querySelector("faceplate-form-helper-text").shadowRoot.querySelector("#helper-text");'
        )
        try_to_click(username_input, delay=MICRO_DELAY_S)
        time.sleep(MICRO_DELAY_S)

        if (
            "nice" not in username_err.text.lower().strip()
            and username_err.text.strip() != ""
        ):
            if "taken" in username_err.text.lower():
                raise UsernameTakenException(username_err.text)
            if "character" in username_err.text.lower():
                raise UsernameLengthException(username_err.text)
            if "symbols" in username_err.text.lower():
                raise UsernameSymbolsException(username_err.text)
            raise Exception(username_err.text)

        if password_err.text.strip() != "":
            print("PW error: " + password_err.text)
            if "character" in password_err.text.lower():
                raise PasswordLengthException(password_err.text)
            raise Exception(password_err.text)

        # Solve captcha
        logger.debug("Solving captcha")
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(
            EC.element_to_be_clickable((By.XPATH, '//iframe[@title="reCAPTCHA"]'))
        )
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
                raise RecaptchaException("Could not solve captcha")

        # Submit registration
        logger.debug("Submitting registration")
        submit_btn = select_second_continue_button(driver)
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(
            EC.element_to_be_clickable(submit_btn)
        )
        try_to_click(submit_btn, delay=MICRO_DELAY_S)

        # Check if submitted
        has_username_dissapeared = did_element_dissapear(driver, "register-username")
        if not has_username_dissapeared:
            raise Exception("Submit failed")

        # Account created!

    finally:  # quit driver if error occurs
        if driver is not None:
            logger.debug("Quitting driver")
            driver.quit()

    return email, username, password
