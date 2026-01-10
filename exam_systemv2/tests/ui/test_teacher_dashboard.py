"""
Teacher Dashboard UI tests.
Tests verify dashboard elements, statistics cards, and navigation functionality.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestTeacherDashboard:
    """Test cases for the teacher dashboard page."""
    
    def test_dashboard_page_loads(self, login_as_teacher, base_url):
        """
        Test: Verify teacher dashboard page loads correctly after login.
        Expected: Dashboard heading is displayed.
        Locators: XPath (heading)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Verify on teacher dashboard
        assert "/teacher/dashboard" in driver.current_url
        
        # Verify dashboard heading using XPath
        heading = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//h1[contains(text(), 'Teacher Dashboard')]")
            )
        )
        assert heading.is_displayed()
    
    def test_dashboard_statistics_cards_visible(self, login_as_teacher, base_url):
        """
        Test: Verify statistics cards are displayed on dashboard.
        Expected: Dashboard cards showing stats are visible.
        Locators: CSS Selector (dashboard-card class)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/teacher/dashboard"))
        
        # Find all dashboard cards using CSS selector
        dashboard_cards = driver.find_elements(By.CSS_SELECTOR, ".dashboard-card")
        
        # Verify at least some dashboard cards exist
        assert len(dashboard_cards) > 0, "Dashboard should have statistics cards"
        
        # Verify cards are visible
        for card in dashboard_cards:
            assert card.is_displayed(), "Dashboard card should be visible"
    
    def test_create_new_question_button(self, login_as_teacher, base_url):
        """
        Test: Verify 'Create New Question' button is present and clickable.
        Expected: Button exists and navigates to question creation page.
        Locators: XPath (link containing text)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/teacher/dashboard"))
        
        # Find 'Create New Question' button using XPath
        create_question_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@href, '/teacher/questions/new')]")
            )
        )
        assert create_question_btn.is_displayed()
        
        # Click and verify navigation
        create_question_btn.click()
        wait.until(EC.url_contains("/teacher/questions/new"))
        assert "/teacher/questions/new" in driver.current_url
    
    def test_create_new_exam_button(self, login_as_teacher, base_url):
        """
        Test: Verify 'Create New Exam' button is present and clickable.
        Expected: Button exists and navigates to exam creation page.
        Locators: CSS Selector (href attribute)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/teacher/dashboard"))
        
        # Find 'Create New Exam' button using CSS selector
        create_exam_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a[href='/teacher/exams/new']")
            )
        )
        assert create_exam_btn.is_displayed()
        
        # Click and verify navigation
        create_exam_btn.click()
        wait.until(EC.url_contains("/teacher/exams/new"))
        assert "/teacher/exams/new" in driver.current_url
    
    def test_view_all_questions_button(self, login_as_teacher, base_url):
        """
        Test: Verify 'View All Questions' button navigates correctly.
        Expected: Button navigates to questions list page.
        Locators: XPath (link with text)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/teacher/dashboard"))
        
        # Find 'View All Questions' link using XPath
        view_questions_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@href, '/teacher/questions') and contains(@class, 'btn')]")
            )
        )
        view_questions_btn.click()
        
        # Verify navigation
        wait.until(EC.url_contains("/teacher/questions"))
        assert "/teacher/questions" in driver.current_url
    
    def test_view_all_exams_button(self, login_as_teacher, base_url):
        """
        Test: Verify 'View All Exams' button navigates correctly.
        Expected: Button navigates to exams list page.
        Locators: CSS Selector (href pattern)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/teacher/dashboard"))
        
        # Find 'View All Exams' link using CSS selector
        view_exams_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a.btn[href='/teacher/exams']")
            )
        )
        view_exams_btn.click()
        
        # Verify navigation
        wait.until(EC.url_contains("/teacher/exams"))
        assert "/teacher/exams" in driver.current_url
    
    def test_recent_questions_section(self, login_as_teacher, base_url):
        """
        Test: Verify 'Recent Questions' section is displayed.
        Expected: Section heading and content area are visible.
        Locators: XPath (section heading), CSS Selector (card)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/teacher/dashboard"))
        
        # Find Recent Questions section using XPath
        questions_section = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//h5[contains(text(), 'Recent Questions')]")
            )
        )
        assert questions_section.is_displayed()
    
    def test_recent_exams_section(self, login_as_teacher, base_url):
        """
        Test: Verify 'Recent Exams' section is displayed.
        Expected: Section heading and content area are visible.
        Locators: XPath (section heading)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/teacher/dashboard"))
        
        # Find Recent Exams section using XPath
        exams_section = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//h5[contains(text(), 'Recent Exams')]")
            )
        )
        assert exams_section.is_displayed()
    
    def test_dashboard_cards_structure(self, login_as_teacher, base_url):
        """
        Test: Verify dashboard cards have proper structure.
        Expected: Cards contain heading (h3) and description (p).
        Locators: CSS Selector (card elements)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/teacher/dashboard"))
        
        # Find dashboard cards
        cards = driver.find_elements(By.CSS_SELECTOR, ".dashboard-card")
        
        if len(cards) > 0:
            # Check first card has expected structure
            first_card = cards[0]
            
            # Verify card contains a number/heading
            heading = first_card.find_element(By.CSS_SELECTOR, "h3")
            assert heading.is_displayed()
            
            # Verify card contains description text
            description = first_card.find_element(By.CSS_SELECTOR, "p")
            assert description.is_displayed()
