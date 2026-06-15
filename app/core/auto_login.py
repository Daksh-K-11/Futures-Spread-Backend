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
import logging

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)
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
    
    driver.implicitly_wait(5)
    
    wait = WebDriverWait(driver, 20)

    try:

        # -----------------------------------
        # Open login page
        # -----------------------------------

        logger.info("Opening login page")
        driver.get(kite.login_url())

        # -----------------------------------
        # Enter user ID
        # -----------------------------------

        logger.info("Entering user ID")
        wait.until(
            EC.element_to_be_clickable((By.ID, "userid"))
        ).send_keys(settings.ZERODHA_USER_ID)

        # -----------------------------------
        # Enter password
        # -----------------------------------

        logger.info("Entering password")
        wait.until(
            EC.element_to_be_clickable((By.ID, "password"))
        ).send_keys(settings.ZERODHA_PASSWORD)

        # -----------------------------------
        # Login button
        # -----------------------------------

        logger.info("Clicking login")
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@type='submit']")
            )
        ).click()
        
        time.sleep(5)

        # -----------------------------------
        # Enter OTP
        # -----------------------------------

        logger.info("Entering OTP")

        otp_input = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@type='number']")
            )
        )
        
        #Generate OTP using pyotp
        otp = pyotp.TOTP(
            settings.ZERODHA_TOTP_SECRET
        ).now()

        otp_input.send_keys(otp)

        # -----------------------------------
        # Continue
        # -----------------------------------

        logger.info("Submitting OTP")
        submit_button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@type='submit']")
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            submit_button
        )
        
        time.sleep(10)
        # -----------------------------------
        # Capture request token
        # -----------------------------------
        
        current_url = ""

        for _ in range(30):

            try:

                current_url = driver.current_url

                logger.info(current_url)

                if "request_token" in current_url:
                    break

            except Exception:
                pass

            time.sleep(1)

        else:
            raise Exception(
                "Request token not found"
            )

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