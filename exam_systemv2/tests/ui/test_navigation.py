"""
Navigation UI tests.
Tests verify navbar links, role-based menu items, and navigation functionality.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestTeacherNavigation:
    """Test cases for teacher navigation menu."""
    
    def test_navbar_is_visible(self, login_as_teacher, base_url):
        """
        Test: Verify navbar is visible after login.
        Expected: Navbar element is displayed.
        Locators: CSS Selector (navbar class)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Verify navbar is visible using CSS selector
        navbar = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".navbar"))
        )
        assert navbar.is_displayed()
    
    def test_teacher_dashboard_link(self, login_as_teacher, base_url):
        """
        Test: Verify teacher dashboard link works.
        Expected: Link navigates to teacher dashboard.
        Locators: CSS Selector (nav-link class)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to a different page first
        driver.get(f"{base_url}/teacher/questions")
        wait.until(EC.url_contains("/teacher/questions"))
        
        # Find and click dashboard link using CSS selector
        dashboard_link = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.nav-link[href='/teacher/dashboard']")
            )
        )
        dashboard_link.click()
        
        # Verify navigation
        wait.until(EC.url_contains("/teacher/dashboard"))
        assert "/teacher/dashboard" in driver.current_url
    
    def test_teacher_questions_link(self, login_as_teacher, base_url):
        """
        Test: Verify questions link works for teacher.
        Expected: Link navigates to questions page.
        Locators: XPath (nav-link with href)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Find and click questions link using XPath
        questions_link = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@class, 'nav-link') and contains(@href, '/teacher/questions')]")
            )
        )
        questions_link.click()
        
        # Verify navigation
        wait.until(EC.url_contains("/teacher/questions"))
        assert "/teacher/questions" in driver.current_url
    
    def test_teacher_exams_link(self, login_as_teacher, base_url):
        """
        Test: Verify exams link works for teacher.
        Expected: Link navigates to exams page.
        Locators: CSS Selector (href attribute)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Find and click exams link using CSS selector
        exams_link = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.nav-link[href='/teacher/exams']")
            )
        )
        exams_link.click()
        
        # Verify navigation
        wait.until(EC.url_contains("/teacher/exams"))
        assert "/teacher/exams" in driver.current_url
    
    def test_teacher_profile_link(self, login_as_teacher, base_url):
        """
        Test: Verify profile link works for teacher.
        Expected: Link navigates to profile page.
        Locators: XPath (nav-link with text)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Find and click profile link using XPath
        profile_link = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@class, 'nav-link') and contains(@href, '/teacher/profile')]")
            )
        )
        profile_link.click()
        
        # Verify navigation (might redirect to edit if no profile exists)
        wait.until(lambda d: "/teacher/profile" in d.current_url)
        assert "/teacher/profile" in driver.current_url
    
    def test_brand_link_navigates_to_dashboard(self, login_as_teacher, base_url):
        """
        Test: Verify brand/logo link navigates to dashboard.
        Expected: Clicking brand takes user to dashboard.
        Locators: CSS Selector (navbar-brand class)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to a different page first
        driver.get(f"{base_url}/teacher/questions")
        wait.until(EC.url_contains("/teacher/questions"))
        
        # Find and click brand link using CSS selector
        brand_link = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".navbar-brand")
            )
        )
        brand_link.click()
        
        # Verify navigation to dashboard
        wait.until(EC.url_contains("/dashboard"))
        assert "/dashboard" in driver.current_url
    
    def test_logout_link_visible(self, login_as_teacher, base_url):
        """
        Test: Verify logout link is visible in navbar.
        Expected: Logout link is displayed.
        Locators: XPath (link with href containing logout)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Find logout link using XPath
        logout_link = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href, '/logout')]")
            )
        )
        assert logout_link.is_displayed()


class TestStudentNavigation:
    """Test cases for student navigation menu."""
    
    def test_student_dashboard_link(self, login_as_student, base_url):
        """
        Test: Verify student dashboard link works.
        Expected: Link navigates to student dashboard.
        Locators: CSS Selector (nav-link)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Navigate to a different page first
        driver.get(f"{base_url}/student/results")
        wait.until(EC.url_contains("/student/results"))
        
        # Find and click dashboard link using CSS selector
        dashboard_link = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.nav-link[href='/student/dashboard']")
            )
        )
        dashboard_link.click()
        
        # Verify navigation
        wait.until(EC.url_contains("/student/dashboard"))
        assert "/student/dashboard" in driver.current_url
    
    def test_student_exams_link(self, login_as_student, base_url):
        """
        Test: Verify My Exams link works for student.
        Expected: Link navigates to student exams page.
        Locators: XPath (nav-link with href)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Find and click exams link using XPath
        exams_link = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@class, 'nav-link') and contains(@href, '/student/exams')]")
            )
        )
        exams_link.click()
        
        # Verify navigation
        wait.until(EC.url_contains("/student/exams"))
        assert "/student/exams" in driver.current_url
    
    def test_student_results_link(self, login_as_student, base_url):
        """
        Test: Verify Results link works for student.
        Expected: Link navigates to results page.
        Locators: CSS Selector (href pattern)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Find and click results link using CSS selector
        results_link = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.nav-link[href='/student/results']")
            )
        )
        results_link.click()
        
        # Verify navigation
        wait.until(EC.url_contains("/student/results"))
        assert "/student/results" in driver.current_url
    
    def test_student_statistics_link(self, login_as_student, base_url):
        """
        Test: Verify Statistics link works for student.
        Expected: Link navigates to statistics page.
        Locators: XPath (nav-link containing statistics)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Find and click statistics link using XPath
        stats_link = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@class, 'nav-link') and contains(@href, '/student/statistics')]")
            )
        )
        stats_link.click()
        
        # Verify navigation
        wait.until(EC.url_contains("/student/statistics"))
        assert "/student/statistics" in driver.current_url
    
    def test_username_displayed_in_navbar(self, login_as_student, base_url):
        """
        Test: Verify username is displayed in navbar.
        Expected: Logged-in username is shown.
        Locators: CSS Selector (navbar-text), XPath (strong tag)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Find username display using CSS selector
        navbar_text = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".navbar-text"))
        )
        assert navbar_text.is_displayed()
        
        # Verify username is displayed using XPath
        username_element = driver.find_element(By.XPATH, "//span[contains(@class, 'navbar-text')]//strong")
        assert username_element.is_displayed()
        assert username_element.text != ""
    
    def test_role_badge_displayed(self, login_as_student, base_url):
        """
        Test: Verify role badge is displayed in navbar.
        Expected: Badge showing user role is visible.
        Locators: CSS Selector (badge class)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Find role badge using CSS selector
        role_badge = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".navbar-text .badge")
            )
        )
        assert role_badge.is_displayed()
        assert "STUDENT" in role_badge.text.upper()


class TestRoleBasedMenus:
    """Test cases to verify role-based menu differences."""
    
    def test_teacher_has_questions_menu(self, login_as_teacher, base_url):
        """
        Test: Verify teacher has access to Questions menu.
        Expected: Questions link is present in navbar.
        Locators: XPath (nav-link with Questions text)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Find Questions link using XPath
        questions_links = driver.find_elements(
            By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Questions')]"
        )
        assert len(questions_links) > 0, "Teacher should see Questions menu"
    
    def test_student_no_questions_menu(self, login_as_student, base_url):
        """
        Test: Verify student does NOT have Questions menu.
        Expected: Questions link is not present in navbar.
        Locators: XPath (nav-link with Questions text)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        wait.until(EC.url_contains("/student/dashboard"))
        
        # Check that Questions link is not present
        questions_links = driver.find_elements(
            By.XPATH, "//a[contains(@class, 'nav-link') and contains(text(), 'Questions') and contains(@href, '/teacher')]"
        )
        assert len(questions_links) == 0, "Student should NOT see teacher's Questions menu"
