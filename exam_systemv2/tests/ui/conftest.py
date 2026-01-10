"""
Pytest fixtures for Selenium UI tests.
Provides WebDriver setup, login helpers, and common utilities.
"""
import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Sleep duration between actions (for visibility during manual observation)
SLEEP_DURATION = 1


# Base URL for the application
BASE_URL = "http://localhost:8000"

# Test user credentials (from realistic_seed.py)
# Admin: admin / admin123
# Teachers: {first_name}.{last_name} / teacher123
# Students: {first_name}.{last_name} / student123
TEACHER_USERNAME = "emily.clark"
TEACHER_PASSWORD = "teacher123"
STUDENT_USERNAME = "nicole.martinez"
STUDENT_PASSWORD = "student123"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


@pytest.fixture(scope="function")
def driver():
    """
    Create a Chrome WebDriver instance for each test.
    Uses visible browser mode (not headless).
    """
    chrome_options = Options()
    # Visible mode - no headless flag
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-infobars")
    
    # Initialize the Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    
    # Cleanup after test
    driver.quit()


@pytest.fixture
def base_url():
    """Return the base URL for the application."""
    return BASE_URL


@pytest.fixture
def wait(driver):
    """Return a WebDriverWait instance with 10 second timeout."""
    return WebDriverWait(driver, 10)


def login(driver, username, password, base_url=BASE_URL):
    """
    Helper function to log in a user.
    
    Args:
        driver: Selenium WebDriver instance
        username: Username to log in with
        password: Password for the user
        base_url: Base URL of the application
    
    Returns:
        bool: True if login successful, False otherwise
    """
    driver.get(f"{base_url}/login")
    time.sleep(SLEEP_DURATION)  # Wait to observe
    
    # Wait for login page to load
    wait = WebDriverWait(driver, 10)
    username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
    
    # Enter credentials using ID locators
    username_field.clear()
    username_field.send_keys(username)
    time.sleep(1)  # Brief pause after typing username
    
    password_field = driver.find_element(By.ID, "password")
    password_field.clear()
    password_field.send_keys(password)
    time.sleep(1)  # Brief pause after typing password
    
    # Click login button using CSS selector
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()
    time.sleep(SLEEP_DURATION)  # Wait to observe result
    
    # Wait for redirect (dashboard or error)
    try:
        wait.until(EC.url_contains("/dashboard"))
        return True
    except:
        return False


@pytest.fixture
def login_as_teacher(driver, base_url):
    """
    Fixture to log in as a teacher.
    Returns the driver after successful login.
    """
    success = login(driver, TEACHER_USERNAME, TEACHER_PASSWORD, base_url)
    assert success, "Failed to log in as teacher"
    return driver


@pytest.fixture
def login_as_student(driver, base_url):
    """
    Fixture to log in as a student.
    Returns the driver after successful login.
    """
    success = login(driver, STUDENT_USERNAME, STUDENT_PASSWORD, base_url)
    assert success, "Failed to log in as student"
    return driver


@pytest.fixture
def login_as_admin(driver, base_url):
    """
    Fixture to log in as an admin.
    Returns the driver after successful login.
    """
    success = login(driver, ADMIN_USERNAME, ADMIN_PASSWORD, base_url)
    assert success, "Failed to log in as admin"
    return driver


def logout(driver, base_url=BASE_URL):
    """
    Helper function to log out the current user.
    
    Args:
        driver: Selenium WebDriver instance
        base_url: Base URL of the application
    """
    # Find and click logout link using XPath
    try:
        logout_link = driver.find_element(By.XPATH, "//a[contains(@href, '/logout')]")
        logout_link.click()
        time.sleep(SLEEP_DURATION)  # Wait to observe
        
        # Wait for redirect to login page
        wait = WebDriverWait(driver, 10)
        wait.until(EC.url_contains("/login"))
        return True
    except:
        return False


def wait_for_element(driver, by, value, timeout=10):
    """
    Wait for an element to be present and visible.
    
    Args:
        driver: Selenium WebDriver instance
        by: Locator strategy (By.ID, By.NAME, etc.)
        value: Locator value
        timeout: Maximum wait time in seconds
    
    Returns:
        WebElement: The found element
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.visibility_of_element_located((by, value)))


def wait_for_clickable(driver, by, value, timeout=10):
    """
    Wait for an element to be clickable.
    
    Args:
        driver: Selenium WebDriver instance
        by: Locator strategy (By.ID, By.NAME, etc.)
        value: Locator value
        timeout: Maximum wait time in seconds
    
    Returns:
        WebElement: The clickable element
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable((by, value)))
