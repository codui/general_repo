import os

ASITE_BASE_URL = "https://system.asite.com"
ASITE_LOGIN_URL = f"{ASITE_BASE_URL}/login"

ASITE_USERNAME = "morosan12@yahoo.com"
ASITE_PASSWORD = "kysfyr-3nemfa-difcYx"

# Путь к ChromeDriver
# Пример: CHROME_DRIVER_PATH = "/usr/local/bin/chromedriver" (для Linux/macOS)
# Пример: CHROME_DRIVER_PATH = "C:\\path\\to\\chromedriver.exe" (для Windows)
# CHROME_DRIVER_PATH = os.path.join(os.path.dirname(__file__), "chromedriver")
CHROME_DRIVER_PATH = None

DEFAULT_WAIT_TIME = 15
PAGE_LOAD_TIMEOUT = 45

LOG_LEVEL = "INFO" 
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

ASITE_LOGIN_IFRAME_ID = "iFrameAsite"
ASITE_USERNAME_FIELD_ID = "_58_login"
ASITE_PASSWORD_FIELD_ID = "_58_password"
ASITE_LOGIN_BUTTON_ID = "login-cloud"
