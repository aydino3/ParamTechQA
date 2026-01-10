"""
Login functionality UI tests.
Tests cover positive, negative, and edge case scenarios for user authentication.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class TestLoginPositive:
    """Positive test cases for login functionality."""
    
    def test_valid_teacher_login(self, driver, base_url):
        """
        Test: Valid teacher login with correct credentials.
        Expected: User is redirected to teacher dashboard.
        Locators: ID (username, password), CSS Selector (submit button)
        """
        driver.get(f"{base_url}/login")
        
        # Wait for login page to load
        wait = WebDriverWait(driver, 10)
        
        # Enter valid teacher credentials using ID locator
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_field.send_keys("emily.clark")
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("teacher123")
        
        # Click login button using CSS selector
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Verify redirect to dashboard
        wait.until(EC.url_contains("/teacher/dashboard"))
        assert "/teacher/dashboard" in driver.current_url
        
        # Verify dashboard page elements
        dashboard_heading = wait.until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Teacher Dashboard')]"))
        )
        assert dashboard_heading.is_displayed()
    
    def test_valid_student_login(self, driver, base_url):
        """
        Test: Valid student login with correct credentials.
        Expected: User is redirected to student dashboard.
        Locators: ID (username, password), XPath (submit button)
        """
        driver.get(f"{base_url}/login")
        
        wait = WebDriverWait(driver, 10)
        
        # Enter valid student credentials using ID locator
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_field.send_keys("nicole.martinez")
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("student123")
        
        # Click login button using XPath
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Verify redirect to student dashboard
        wait.until(EC.url_contains("/student/dashboard"))
        assert "/student/dashboard" in driver.current_url
    
    def test_valid_admin_login(self, driver, base_url):
        """
        Test: Valid admin login with correct credentials.
        Expected: User is redirected to admin dashboard.
        Locators: NAME (username, password), CSS Selector (submit button)
        """
        driver.get(f"{base_url}/login")
        
        wait = WebDriverWait(driver, 10)
        
        # Enter valid admin credentials using NAME locator
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_field.send_keys("admin")
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys("admin123")
        
        # Click login button
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Verify redirect to admin dashboard
        wait.until(EC.url_contains("/admin/dashboard"))
        assert "/admin/dashboard" in driver.current_url


class TestLoginNegative:
    """Negative test cases for login functionality."""
    
    def test_invalid_password(self, driver, base_url):
        """
        Test: Login with valid username but invalid password.
        Expected: Error message is displayed, user stays on login page.
        Locators: ID (username, password), CSS Selector (error alert)
        """
        driver.get(f"{base_url}/login")
        
        wait = WebDriverWait(driver, 10)
        
        # Enter valid username with wrong password
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_field.send_keys("emily.clark")
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("wrongpassword")
        
        # Click login button
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Verify error message is displayed using CSS selector
        error_alert = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-danger"))
        )
        assert error_alert.is_displayed()
        assert "Invalid" in error_alert.text or "invalid" in error_alert.text.lower()
        
        # Verify still on login page
        assert "/login" in driver.current_url
    
    def test_invalid_username(self, driver, base_url):
        """
        Test: Login with non-existent username.
        Expected: Error message is displayed.
        Locators: ID (username, password), XPath (error message)
        """
        driver.get(f"{base_url}/login")
        
        wait = WebDriverWait(driver, 10)
        
        # Enter non-existent username
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_field.send_keys("nonexistentuser")
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("somepassword")
        
        # Click login button
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Verify error message using XPath
        error_alert = wait.until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'alert-danger')]"))
        )
        assert error_alert.is_displayed()
    
    def test_case_sensitive_password(self, driver, base_url):
        """
        Test: Login with correct username but wrong case password.
        Expected: Login fails (passwords are case-sensitive).
        Locators: ID (form fields), CSS Selector (alert)
        """
        driver.get(f"{base_url}/login")
        
        wait = WebDriverWait(driver, 10)
        
        # Enter credentials with wrong case password
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_field.send_keys("emily.clark")
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys("TEACHER123")  # Wrong case
        
        # Click login button
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Verify login fails
        error_alert = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-danger"))
        )
        assert error_alert.is_displayed()


class TestLoginEdgeCases:
    """Edge case tests for login functionality."""
    
    def test_empty_username(self, driver, base_url):
        """
        Test: Submit login form with empty username.
        Expected: Form validation prevents submission or shows error.
        Locators: ID (password), CSS Selector (submit button)
        """
        driver.get(f"{base_url}/login")
        
        wait = WebDriverWait(driver, 10)
        
        # Only fill password, leave username empty
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_field.send_keys("student123")
        
        # Try to submit form
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Verify form validation (HTML5 required attribute)
        username_field = driver.find_element(By.ID, "username")
        is_valid = driver.execute_script("return arguments[0].checkValidity()", username_field)
        assert not is_valid, "Username field should be invalid when empty"
    
    def test_empty_password(self, driver, base_url):
        """
        Test: Submit login form with empty password.
        Expected: Form validation prevents submission or shows error.
        Locators: ID (username), NAME (password)
        """
        driver.get(f"{base_url}/login")
        
        wait = WebDriverWait(driver, 10)
        
        # Only fill username, leave password empty
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_field.send_keys("emily.clark")
        
        # Try to submit form
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Verify form validation (HTML5 required attribute)
        password_field = driver.find_element(By.NAME, "password")
        is_valid = driver.execute_script("return arguments[0].checkValidity()", password_field)
        assert not is_valid, "Password field should be invalid when empty"
    
    def test_empty_both_fields(self, driver, base_url):
        """
        Test: Submit login form with both fields empty.
        Expected: Form validation prevents submission.
        Locators: ID (username, password), XPath (submit button)
        """
        driver.get(f"{base_url}/login")
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "username")))
        
        # Try to submit empty form using CSS selector for button
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Verify form validation
        username_field = driver.find_element(By.ID, "username")
        is_valid = driver.execute_script("return arguments[0].checkValidity()", username_field)
        assert not is_valid, "Form should not submit with empty fields"
    
    def test_login_page_title(self, driver, base_url):
        """
        Test: Verify login page has correct title.
        Expected: Page title contains 'Login'.
        Locators: N/A (uses page title)
        """
        driver.get(f"{base_url}/login")
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "username")))
        
        # Verify page title
        assert "Login" in driver.title or "Exam" in driver.title
    
    def test_login_form_elements_present(self, driver, base_url):
        """
        Test: Verify all required login form elements are present.
        Expected: Username field, password field, and submit button exist.
        Locators: ID, NAME, CSS Selector, XPath
        """
        driver.get(f"{base_url}/login")
        
        wait = WebDriverWait(driver, 10)
        
        # Verify username field (by ID)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        assert username_field.is_displayed()
        assert username_field.get_attribute("type") == "text"
        
        # Verify password field (by NAME)
        password_field = driver.find_element(By.NAME, "password")
        assert password_field.is_displayed()
        assert password_field.get_attribute("type") == "password"
        
        # Verify submit button (by CSS Selector)
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        assert submit_button.is_displayed()
        assert submit_button.is_enabled()
        
        # Verify form exists (by XPath)
        form = driver.find_element(By.XPATH, "//form[@method='post']")
        assert form.is_displayed()
