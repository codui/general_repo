from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
import logging
import time
import config


logger = logging.getLogger(__name__)
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)

class AsiteAuthService:
    def __init__(self):
        self.driver = None
        logger.info("Initializing AsiteAuthService.")

    def _initialize_driver(self):
        logger.info("Initializing WebDriver...")
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--log-level={config.LOG_LEVEL}")
        
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "download.default_directory": config.DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safeBrowse.enabled": True,
            "credentials_enable_service": False, 
            "profile.password_manager_enabled": False,
        }
        options.add_experimental_option("prefs", prefs)

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

        if config.CHROME_DRIVER_PATH:
            self.driver = webdriver.Chrome(executable_path=config.CHROME_DRIVER_PATH, options=options)
        else:
            self.driver = webdriver.Chrome(options=options)
        time.sleep(3)
        self.driver.implicitly_wait(config.DEFAULT_WAIT_TIME)
        self.driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
        logger.info("WebDriver initialized.")

    def login(self):
        if not self.driver:
            self._initialize_driver()

        try:
            logger.info(f"Navigating to URL: {config.ASITE_LOGIN_URL}")
            self.driver.get(config.ASITE_LOGIN_URL)
            time.sleep(5)

            logger.info(f"Waiting for iframe '{config.ASITE_LOGIN_IFRAME_ID}' to appear and switching to it...")
            iframe = WebDriverWait(self.driver, config.DEFAULT_WAIT_TIME).until(
                EC.presence_of_element_located((By.ID, config.ASITE_LOGIN_IFRAME_ID))
            )
            self.driver.switch_to.frame(iframe)
            logger.info("Focus successfully switched to iFrame.")

            logger.info(f"Waiting for username field '{config.ASITE_USERNAME_FIELD_ID}' to appear inside iframe...")
            login_field = WebDriverWait(self.driver, config.DEFAULT_WAIT_TIME).until(
                EC.presence_of_element_located((By.ID, config.ASITE_USERNAME_FIELD_ID))
            )
            logger.info("Username field found.")
            login_field.send_keys(config.ASITE_USERNAME)
            logger.info(f"Entered username: {config.ASITE_USERNAME}")
            time.sleep(2)

            password_field = WebDriverWait(self.driver, config.DEFAULT_WAIT_TIME).until(
                EC.presence_of_element_located((By.ID, config.ASITE_PASSWORD_FIELD_ID))
            )
            logger.info("Password field found.")
            password_field.send_keys(config.ASITE_PASSWORD)
            time.sleep(2)
            logger.info("Entered password.")

            logger.info(f"Waiting for 'Login' button with ID '{config.ASITE_LOGIN_BUTTON_ID}'...")
            login_button = WebDriverWait(self.driver, config.DEFAULT_WAIT_TIME).until(
                EC.element_to_be_clickable((By.ID, config.ASITE_LOGIN_BUTTON_ID))
            )
            logger.info("Login button found and clickable. Clicking...")
            login_button.click()

            logger.info("Authentication completed successfully!")
        
            try:
                self.driver.switch_to.default_content() 
                logger.info("Switched to default content to check for modal.")

                btn_modal_xpath: str = (
                    '//div[contains(@class, "modal-scrollable")]//*[@id="myModal-annoucement"]/div[1]/button'
                )
                logger.info(f"Attempting to close modal window using XPath: {btn_modal_xpath}")
                
                btn_modal = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, btn_modal_xpath))
                )
                btn_modal.click()
                logger.info("Modal window closed.")
            except Exception:
                logger.info("No modal window found or unable to close it.")

            return True

        except TimeoutException as e:
            logger.error(f"Timeout: Element not found or operation could not be completed. {e}")
            self._log_error_page_info()
        except NoSuchElementException as e:
            logger.error(f"NoSuchElement: Element not found. {e}")
            self._log_error_page_info()
        except WebDriverException as e:
            logger.error(f"WebDriver error: {e}")
            logger.error("Possible Chrome/ChromeDriver version incompatibility or ChromeDriver not in PATH.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        return False

    def _log_error_page_info(self):
        if self.driver:
            logger.error(f"Current URL: {self.driver.current_url}")
            logger.error(f"Page title: {self.driver.title}")
            try:
                logger.error(f"Page HTML (after error, first 2000 characters):\n{self.driver.page_source[:2000]}...")
            except Exception:
                logger.error("Could not retrieve page HTML after error.")

    def quit_driver(self):
        if self.driver:
            logger.info("Closing browser.")
            self.driver.quit()
            self.driver = None

    def get_driver(self):
        return self.driver