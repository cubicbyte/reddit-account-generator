import time
import requests
import logging
import json

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_recaptcha_solver import RecaptchaSolver

from .utils import setup_firefox_driver
from .exceptions import *

_logger = logging.getLogger(__name__)

PAGE_LOAD_TIMEOUT_S = 60
DRIVER_TIMEOUT_S = 60
MICRO_DELAY_S = 1

def gen():
    try:
        _logger.info('Creating email')
        return json.loads(requests.get('https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1').text)[0]
    except:
        return Exception

def verify(email, proxies: dict[str, str] | None = None, hide_browser: bool = True):
    username = email.split('@')[0].replace('@', '')
    domain = email.split('@')[1].replace('@', '')
    while True:
        _logger.debug('Waiting for email...')
        resp = json.loads(requests.get(f'https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}').text)
        if len(resp) > 0:
            for item in resp:
                if item['subject'] == 'Verify your Reddit email address':
                    _logger.debug('Found email')
                    msg = json.loads(requests.get(f'https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={item["id"]}').text)
                    body = msg['body']
                    main = body.split('https://www.reddit.com/verification/')[1]
                    link = main.split('&amp;ref=verify_email&amp;ref_campaign=verify_email')[0]
                    link = 'https://www.reddit.com/verification/' + link
                    _logger.debug('Found link. Opening browser.')
                    driver = setup_firefox_driver(proxies, hide_browser)

                    if PAGE_LOAD_TIMEOUT_S is not None:
                        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT_S)

                    try:
                        driver.get(f'{link}')
                    except Exception:
                        raise TimeoutException('Website takes too long to load. Probably a problem with the proxy.')

                    WebDriverWait(driver, DRIVER_TIMEOUT_S).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="verify-email"]/button')))
                    driver.find_element(By.XPATH, '//*[@id="verify-email"]/button').click()
                    _logger.debug('Clicked button. Waiting for response.')
                    i = 0
                    while True:
                        if i < 60:
                            if driver.find_element(By.XPATH, '//*[@id="verify-email"]/span').text == 'Success!' or driver.find_element(By.XPATH, '//*[@id="verify-email"]/span').text == 'Success!' == 'This email has already been verified.':
                                _logger.info('Email successfully verified!')
                                driver.quit()
                                return
                            else:
                                i = i + 1
                                time.sleep(0.5)
                        else:
                            return Exception
        time.sleep(5)