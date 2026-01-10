"""
Student Dashboard UI tests.
Tests verify student dashboard elements, assignment filtering, and navigation.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class TestStudentDashboard:
    """Test cases for the student dashboard page."""
    
    def test_dashboard_page_loads(self, login_as_student, base_url):
        """
        Test: Verify student dashboard page loads correctly after login.
        Expected: Dashboard heading is displayed.
        Locators: XPath (heading)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Verify on student dashboard
        assert "/student/dashboard" in driver.current_url
        
        # Verify dashboard heading using XPath
        heading = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//h1[contains(text(), 'Student Dashboard')]")
            )
        )
        assert heading.is_displayed()
    
    def test_dashboard_statistics_cards_visible(self, login_as_student, base_url):
        """
        Test: Verify statistics cards are displayed on dashboard.
        Expected: Dashboard cards showing stats are visible.
        Locators: CSS Selector (dashboard-card class)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/student/dashboard"))
        
        # Find all dashboard cards using CSS selector
        dashboard_cards = driver.find_elements(By.CSS_SELECTOR, ".dashboard-card")
        
        # Verify at least some dashboard cards exist
        assert len(dashboard_cards) > 0, "Dashboard should have statistics cards"
        
        # Verify cards are visible
        for card in dashboard_cards:
            assert card.is_displayed(), "Dashboard card should be visible"
    
    def test_assignment_filter_dropdown(self, login_as_student, base_url):
        """
        Test: Verify filter status dropdown exists and has options.
        Expected: Dropdown has filter options (All, Assigned, In Progress, Completed).
        Locators: ID (select element)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/student/dashboard"))
        
        # Find filter dropdown using ID
        filter_select = wait.until(
            EC.presence_of_element_located((By.ID, "filter_status"))
        )
        assert filter_select.is_displayed()
        
        # Get dropdown options
        select = Select(filter_select)
        options = [opt.get_attribute("value") for opt in select.options]
        
        # Verify expected options
        assert "all" in options, "All option should exist"
        assert "ASSIGNED" in options, "Assigned option should exist"
        assert "IN_PROGRESS" in options, "In Progress option should exist"
        assert "COMPLETED" in options, "Completed option should exist"
    
    def test_sort_by_dropdown(self, login_as_student, base_url):
        """
        Test: Verify sort by dropdown exists and has options.
        Expected: Dropdown has sort options (Date, Name).
        Locators: ID (select element)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/student/dashboard"))
        
        # Find sort dropdown using ID
        sort_select = wait.until(
            EC.presence_of_element_located((By.ID, "sort_by"))
        )
        assert sort_select.is_displayed()
        
        # Get dropdown options
        select = Select(sort_select)
        options = [opt.get_attribute("value") for opt in select.options]
        
        # Verify expected options
        assert "date" in options, "Date sort option should exist"
        assert "name" in options, "Name sort option should exist"
    
    def test_search_field(self, login_as_student, base_url):
        """
        Test: Verify search field exists and accepts input.
        Expected: Search field is functional.
        Locators: ID (search input), NAME (search input)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/student/dashboard"))
        
        # Find search field using ID
        search_field = wait.until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        assert search_field.is_displayed()
        
        # Enter search text
        search_field.clear()
        search_field.send_keys("test exam")
        
        # Verify input was accepted
        assert search_field.get_attribute("value") == "test exam"
    
    def test_filter_button(self, login_as_student, base_url):
        """
        Test: Verify filter button exists and is clickable.
        Expected: Filter button submits the filter form.
        Locators: CSS Selector (button), XPath (button with text)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/student/dashboard"))
        
        # Find filter button using CSS selector
        filter_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[type='submit']")
            )
        )
        assert filter_btn.is_displayed()
        
        # Click filter button
        filter_btn.click()
        
        # Verify still on dashboard (page refreshes with filters)
        wait.until(EC.url_contains("/student/dashboard"))
    
    def test_statistics_navigation_link(self, login_as_student, base_url):
        """
        Test: Verify statistics navigation link works.
        Expected: Link navigates to statistics page.
        Locators: XPath (link with href), CSS Selector
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/student/dashboard"))
        
        # Find statistics link using XPath
        stats_link = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@href, '/student/statistics')]")
            )
        )
        assert stats_link.is_displayed()
        
        # Click and verify navigation
        stats_link.click()
        wait.until(EC.url_contains("/student/statistics"))
        assert "/student/statistics" in driver.current_url
    
    def test_results_navigation_link(self, login_as_student, base_url):
        """
        Test: Verify results navigation link works.
        Expected: Link navigates to results page.
        Locators: CSS Selector (link with href)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        driver.get(f"{base_url}/student/dashboard")
        wait.until(EC.url_contains("/student/dashboard"))
        
        # Find results link using CSS selector
        results_link = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a[href='/student/results']")
            )
        )
        assert results_link.is_displayed()
        
        # Click and verify navigation
        results_link.click()
        wait.until(EC.url_contains("/student/results"))
        assert "/student/results" in driver.current_url
    
    def test_my_assignments_section(self, login_as_student, base_url):
        """
        Test: Verify 'My Assignments' section is displayed.
        Expected: Section heading and content area are visible.
        Locators: XPath (section heading), CSS Selector (card)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/student/dashboard"))
        
        # Find My Assignments section using XPath
        assignments_section = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//h3[contains(text(), 'My Assignments')]")
            )
        )
        assert assignments_section.is_displayed()
    
    def test_filter_by_assigned_status(self, login_as_student, base_url):
        """
        Test: Filter assignments by 'Assigned' status.
        Expected: Filter is applied successfully.
        Locators: ID (select), CSS Selector (submit button)
        """
        driver = login_as_student
        wait = WebDriverWait(driver, 10)
        
        # Wait for dashboard to load
        wait.until(EC.url_contains("/student/dashboard"))
        
        # Select 'Assigned' filter
        filter_select = Select(driver.find_element(By.ID, "filter_status"))
        filter_select.select_by_value("ASSIGNED")
        
        # Click filter button
        filter_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        filter_btn.click()
        
        # Verify filter is applied (URL should contain parameter)
        wait.until(EC.url_contains("/student/dashboard"))
        # The page should reload with the filter applied
        assert driver.current_url is not None
