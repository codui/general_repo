import os
from dotenv import load_dotenv

load_dotenv()

ASITE_BASE_URL = "https://system.asite.com"
ASITE_LOGIN_URL = f"{ASITE_BASE_URL}/login"

ASITE_USERNAME = os.getenv("ASITE_USERNAME", "morosan12@yahoo.com")
ASITE_PASSWORD = os.getenv("ASITE_PASSWORD", "kysfyr-3nemfa-difcYx")

# Путь к ChromeDriver
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", None)

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", os.path.join(os.path.expanduser("~"), "Downloads", "asite_downloads"))

DEFAULT_WAIT_TIME = 15
PAGE_LOAD_TIMEOUT = 45

LOG_LEVEL = "INFO" 
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

ASITE_LOGIN_IFRAME_ID = "iFrameAsite"
ASITE_USERNAME_FIELD_ID = "_58_login"
ASITE_PASSWORD_FIELD_ID = "_58_password"
ASITE_LOGIN_BUTTON_ID = "login-cloud"