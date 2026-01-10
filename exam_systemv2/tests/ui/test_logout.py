"""
Logout functionality UI tests.
Tests verify logout behavior and session handling.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestLogout:
    """Test cases for logout functionality."""
    
    def test_logout_redirects_to_login_page(self, login_as_teacher, base_url):
        """
        Test: Clicking logout redirects user to login page.
        Expected: User is redirected to /login after logout.
        Locators: XPath (logout link), CSS Selector (login form)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Verify logged in first
        assert "/dashboard" in driver.current_url or "/teacher" in driver.current_url
        
        # Find and click logout link using XPath
        logout_link = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@href, '/logout')]")
            )
        )
        logout_link.click()
        
        # Verify redirect to login page
        wait.until(EC.url_contains("/login"))
        assert "/login" in driver.current_url
        
        # Verify login form is displayed
        login_form = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form[method='post']"))
        )
        assert login_form.is_displayed()
    
    def test_logout_clears_session(self, login_as_student, base_url):
        """
        Test: After logout, accessing protected page redirects to login.
        Expected: Session is cleared and user cannot access dashboard.
        Locators: CSS Selector (logout link), ID (login fields)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Verify logged in first
        wait.until(EC.url_contains("/student/dashboard"))
        
        # Find and click logout link using CSS selector
        logout_link = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a[href='/logout']")
            )
        )
        logout_link.click()
        
        # Wait for redirect to login
        wait.until(EC.url_contains("/login"))
        
        # Verify we are on login page
        assert "/login" in driver.current_url
        
        # Verify login form is present (session is cleared)
        username_field = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        assert username_field.is_displayed()
    
    def test_logout_button_visible_for_teacher(self, login_as_teacher, base_url):
        """
        Test: Logout button is visible in navbar for teacher.
        Expected: Logout link is displayed and clickable.
        Locators: XPath (logout link with text)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Find logout link using XPath with text
        logout_link = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href, '/logout') and contains(text(), 'Logout')]")
            )
        )
        assert logout_link.is_displayed()
        assert logout_link.is_enabled()
    
    def test_logout_button_visible_for_student(self, login_as_student, base_url):
        """
        Test: Logout button is visible in navbar for student.
        Expected: Logout link is displayed and clickable.
        Locators: CSS Selector (href pattern)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Find logout link using CSS selector
        logout_link = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href='/logout']")
            )
        )
        assert logout_link.is_displayed()
        assert logout_link.is_enabled()
    
    def test_multiple_logout_login_cycles(self, driver, base_url):
        """
        Test: User can login, logout, and login again successfully.
        Expected: Multiple authentication cycles work correctly.
        Locators: ID (form fields), XPath (logout), CSS Selector (buttons)
        """
        wait = WebDriverWait(driver, 10)
        
        # First login cycle
        driver.get(f"{base_url}/login")
        wait.until(EC.presence_of_element_located((By.ID, "username")))
        
        # Login as teacher
        driver.find_element(By.ID, "username").send_keys("emily.clark")
        driver.find_element(By.ID, "password").send_keys("teacher123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        wait.until(EC.url_contains("/dashboard"))
        assert "/dashboard" in driver.current_url
        
        # Logout
        logout_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/logout')]"))
        )
        logout_link.click()
        
        wait.until(EC.url_contains("/login"))
        assert "/login" in driver.current_url
        
        # Second login cycle - different user
        wait.until(EC.presence_of_element_located((By.ID, "username")))
        
        driver.find_element(By.ID, "username").send_keys("nicole.martinez")
        driver.find_element(By.ID, "password").send_keys("student123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        wait.until(EC.url_contains("/dashboard"))
        assert "/student/dashboard" in driver.current_url
        
        # Final logout
        logout_link = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/logout']"))
        )
        logout_link.click()
        
        wait.until(EC.url_contains("/login"))
        assert "/login" in driver.current_url
    
    def test_logout_via_direct_url(self, login_as_teacher, base_url):
        """
        Test: Navigating directly to /logout logs out the user.
        Expected: Direct URL access logs out and redirects to login.
        Locators: ID (login form fields)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Verify logged in
        assert "/teacher/dashboard" in driver.current_url or "/dashboard" in driver.current_url
        
        # Navigate directly to logout URL
        driver.get(f"{base_url}/logout")
        
        # Should redirect to login
        wait.until(EC.url_contains("/login"))
        assert "/login" in driver.current_url
        
        # Verify login form is displayed
        username_field = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        assert username_field.is_displayed()
    
    def test_cannot_access_teacher_dashboard_after_logout(self, login_as_teacher, base_url):
        """
        Test: After logout, user is on login page.
        Expected: User stays on login page after logout.
        Locators: XPath (logout), CSS Selector (form)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Logout
        logout_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/logout')]"))
        )
        logout_link.click()
        
        wait.until(EC.url_contains("/login"))
        
        # Verify on login page
        assert "/login" in driver.current_url
        
        # Verify login form is displayed
        username_field = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        assert username_field.is_displayed()
    
    def test_cannot_access_teacher_questions_after_logout(self, login_as_teacher, base_url):
        """
        Test: After logout, user is on login page.
        Expected: User stays on login page after logout.
        Locators: CSS Selector (logout, login form)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Logout
        logout_link = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/logout']"))
        )
        logout_link.click()
        
        wait.until(EC.url_contains("/login"))
        
        # Verify on login page
        assert "/login" in driver.current_url
        
        # Verify login form is displayed
        username_field = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        assert username_field.is_displayed()
