import time
import logging

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_recaptcha_solver import RecaptchaSolver

from .utils import setup_firefox_driver
from .exceptions import *

PAGE_LOAD_TIMEOUT_S = 60
DRIVER_TIMEOUT_S = 60
MICRO_DELAY_S = 1

_logger = logging.getLogger(__name__)

def make_script(username, password, proxies: dict[str, str] | None = None, hide_browser: bool = True) -> tuple[str, str]:
    driver = setup_firefox_driver(proxies, hide_browser)

    if PAGE_LOAD_TIMEOUT_S is not None:
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_S)

    try:
        # Open login website
        _logger.debug('Opening login page')
        try:
            driver.get('https://www.reddit.com/login/')
        except WebDriverException:
            raise TimeoutException('Website takes too long to load. Probably a problem with the proxy.')

        _logger.debug('Entering username and password')
        # Enter username and password
        username_input = driver.find_element(By.ID, 'loginUsername')
        password_input = driver.find_element(By.ID, 'loginPassword')
        username_input.click()
        username_input.send_keys(username)
        password_input.click()
        password_input.send_keys(password)

        _logger.debug('Submitting login')
        # Submit login
        time.sleep(MICRO_DELAY_S)
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
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

        # Go to scripts page
        _logger.debug('Going to script page')
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.url_matches('https://www.reddit.com*'))
        driver.get(f'https://www.reddit.com/prefs/apps/')

        # Wait till loading screen ends
        _logger.debug('Waiting till loading screen ends')
        driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/button').click()
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[2]/form/button')))

        # Username
        _logger.debug('Entering script username')
        name = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/form/table/tbody/tr[1]/td/input')
        name.click()
        name.send_keys(username)

        # Script type
        _logger.debug('Choosing script type')
        driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/form/table/tbody/tr[4]/td[1]/input').click()

        # Redirect
        _logger.debug('Typing in script redirect')
        redirect = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/form/table/tbody/tr[7]/td/input')
        redirect.click()
        redirect.send_keys('http://127.0.0.1')

        # Captcha
        _logger.debug('Solving captcha')
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.element_to_be_clickable((By.XPATH, '//iframe[@title="reCAPTCHA"]')))
        recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')

        if recaptcha_iframe.is_displayed():
            solver = RecaptchaSolver(driver)
            solver.click_recaptcha_v2(iframe=recaptcha_iframe)

        # Submit
        _logger.debug('Submitting script')
        time.sleep(MICRO_DELAY_S)
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="create-app"]/button')))
        submit_btn = driver.find_element(By.XPATH, '//*[@id="create-app"]/button')
        time.sleep(MICRO_DELAY_S)
        submit_btn.click()
        time.sleep(5)

        # Get info
        _logger.debug('Getting script details')
        WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[1]/ul/li/div[4]/div[2]/table/tbody/tr/td/ul/li/form/span[1]/a')))
        clientID = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/ul/li/div[2]/h3[2]').text
        clientSecret = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/ul/li/div[4]/div[1]/form/table/tbody/tr[1]/td').text

        driver.quit()
        return clientID, clientSecret

    except Exception as e:  # quit driver if error occurs
        driver.quit()
        raise e