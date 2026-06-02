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

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options
    )
    
    wait = WebDriverWait(driver, 20)

    try:

        # -----------------------------------
        # Open login page
        # -----------------------------------

        driver.get(kite.login_url())

        # -----------------------------------
        # Enter user ID
        # -----------------------------------

        userid_input = wait.until(
            EC.presence_of_element_located((By.ID, "userid"))
        )

        userid_input.send_keys(settings.ZERODHA_USER_ID)

        # -----------------------------------
        # Enter password
        # -----------------------------------

        password_input = wait.until(
            EC.presence_of_element_located((By.ID, "password"))
        )

        password_input.send_keys(settings.ZERODHA_PASSWORD)

        # -----------------------------------
        # Login button
        # -----------------------------------

        login_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@type='submit']")
            )
        )

        login_button.click()

        # -----------------------------------
        # Generate TOTP
        # -----------------------------------

        otp = pyotp.TOTP(
            settings.ZERODHA_TOTP_SECRET
        ).now()

        # -----------------------------------
        # Enter OTP
        # -----------------------------------

        otp_input = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@type='number']")
            )
        )

        otp_input.send_keys(otp)

        # -----------------------------------
        # Continue
        # -----------------------------------

        continue_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@type='submit']")
            )
        )

        continue_button.click()
        # -----------------------------------
        # Capture request token
        # -----------------------------------
        
        wait.until(
            lambda d: "request_token" in d.current_url
        )

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