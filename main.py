import logging
import time
import config
from services.asite_auth_service import AsiteAuthService
from selenium.common.exceptions import WebDriverException

logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

def run_asite_automation():
    auth_service = AsiteAuthService()
    try:
        if auth_service.login():
            logger.info("Authentication successful! The browser will remain open until you close it manually.")

            while True:
                try:
                    if auth_service.get_driver():
                        auth_service.get_driver().current_url
                        time.sleep(1)
                    else:
                        break
                except WebDriverException:
                    break
        else:
            logger.error("Authentication failed. Please check the logs above.")

    finally:
        auth_service.quit_driver()

if __name__ == "__main__":
    run_asite_automation()