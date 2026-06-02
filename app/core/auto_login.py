import time
import pyotp

from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from kiteconnect import KiteConnect

from app.core.config import settings
from app.core.token_manager import save_access_token

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def auto_generate_access_token():

    kite = KiteConnect(
        api_key=settings.KITE_API_KEY
    )

    options = webdriver.ChromeOptions()
    
    options.binary_location = "/usr/bin/chromium-browser"

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--single-process")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(
        service=Service("/usr/bin/chromedriver"),
        options=options
    )

    try:

        # -----------------------------------
        # Open login page
        # -----------------------------------

        driver.get(kite.login_url())

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "userid"))
        )

        # -----------------------------------
        # Enter user ID
        # -----------------------------------

        driver.find_element(
            By.ID,
            "userid"
        ).send_keys(settings.ZERODHA_USER_ID)

        # -----------------------------------
        # Enter password
        # -----------------------------------

        driver.find_element(
            By.ID,
            "password"
        ).send_keys(settings.ZERODHA_PASSWORD)

        # -----------------------------------
        # Login button
        # -----------------------------------

        driver.find_element(
            By.XPATH,
            "//button[@type='submit']"
        ).click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "userid"))
        )

        # -----------------------------------
        # Generate TOTP
        # -----------------------------------

        otp = pyotp.TOTP(
            settings.ZERODHA_TOTP_SECRET
        ).now()

        # -----------------------------------
        # Enter OTP
        # -----------------------------------

        driver.find_element(
            By.XPATH,
            "//input[@type='number']"
        ).send_keys(otp)

        # -----------------------------------
        # Continue
        # -----------------------------------

        driver.find_element(
            By.XPATH,
            "//button[@type='submit']"
        ).click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "userid"))
        )

        # -----------------------------------
        # Capture request token
        # -----------------------------------

        current_url = driver.current_url

        parsed = urlparse(current_url)

        request_token = parse_qs(
            parsed.query
        )["request_token"][0]

        # -----------------------------------
        # Generate access token
        # -----------------------------------

        data = kite.generate_session(
            request_token,
            api_secret=settings.KITE_API_SECRET
        )

        access_token = data["access_token"]

        # -----------------------------------
        # Save token
        # -----------------------------------

        save_access_token(access_token)

        return access_token

    finally:

        driver.quit()