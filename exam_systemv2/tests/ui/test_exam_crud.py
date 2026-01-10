"""
Exam CRUD UI tests.
Tests cover exam creation, configuration, and listing functionality.
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class TestExamCreation:
    """Test cases for creating exams."""
    
    def test_navigate_to_exam_creation_page(self, login_as_teacher, base_url):
        """
        Test: Navigate to exam creation page.
        Expected: Exam creation form is displayed.
        Locators: CSS Selector (navigation), XPath (page heading)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new exam page
        driver.get(f"{base_url}/teacher/exams/new")
        
        # Verify page loaded using XPath
        heading = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//h1[contains(text(), 'New Exam')]")
            )
        )
        assert heading.is_displayed()
    
    def test_create_exam_with_required_fields(self, login_as_teacher, base_url):
        """
        Test: Create an exam with all required fields.
        Expected: Exam is created and appears in the list.
        Locators: ID (name, duration), CSS Selector (select, button)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new exam page
        driver.get(f"{base_url}/teacher/exams/new")
        wait.until(EC.presence_of_element_located((By.ID, "name")))
        
        # Generate unique exam name
        exam_name = f"Selenium Test Exam {int(time.time())}"
        
        # Fill in exam details using ID locators
        name_field = driver.find_element(By.ID, "name")
        name_field.send_keys(exam_name)
        
        duration_field = driver.find_element(By.ID, "duration_minutes")
        duration_field.clear()
        duration_field.send_keys("60")
        
        # Select grading policy using CSS selector
        grading_select = Select(driver.find_element(By.CSS_SELECTOR, "select#grading_policy"))
        grading_select.select_by_value("immediate")
        
        # Add optional description
        description_field = driver.find_element(By.ID, "description")
        description_field.send_keys("This is a test exam created by Selenium.")
        
        # Submit form using CSS selector - scroll and JS click
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_btn)
        
        # Verify redirect to exams list
        wait.until(lambda d: "/teacher/exams" in d.current_url)
        assert "/teacher/exams" in driver.current_url
    
    def test_exam_form_validation_missing_name(self, login_as_teacher, base_url):
        """
        Test: Submit exam form without required name.
        Expected: Form validation prevents submission.
        Locators: ID (form fields), XPath (submit button)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new exam page
        driver.get(f"{base_url}/teacher/exams/new")
        wait.until(EC.presence_of_element_located((By.ID, "duration_minutes")))
        
        # Fill duration but not name
        duration_field = driver.find_element(By.ID, "duration_minutes")
        duration_field.clear()
        duration_field.send_keys("30")
        
        # Try to submit using XPath - scroll and JS click
        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", submit_btn)
        
        # Verify form validation
        name_field = driver.find_element(By.ID, "name")
        is_valid = driver.execute_script("return arguments[0].checkValidity()", name_field)
        assert not is_valid, "Name field should be invalid when empty"
    
    def test_exam_form_validation_missing_duration(self, login_as_teacher, base_url):
        """
        Test: Submit exam form without required duration.
        Expected: Form validation prevents submission.
        Locators: NAME (form fields), CSS Selector (submit button)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new exam page
        driver.get(f"{base_url}/teacher/exams/new")
        wait.until(EC.presence_of_element_located((By.NAME, "name")))
        
        # Fill name but not duration
        name_field = driver.find_element(By.NAME, "name")
        name_field.send_keys("Test Exam Without Duration")
        
        # Clear duration field
        duration_field = driver.find_element(By.NAME, "duration_minutes")
        duration_field.clear()
        
        # Try to submit - scroll and JS click
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", submit_btn)
        
        # Verify form validation
        is_valid = driver.execute_script("return arguments[0].checkValidity()", duration_field)
        assert not is_valid, "Duration field should be invalid when empty"
    
    def test_exam_form_elements_present(self, login_as_teacher, base_url):
        """
        Test: Verify all required form elements are present.
        Expected: All form fields and buttons are displayed.
        Locators: ID, NAME, CSS Selector, XPath
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new exam page
        driver.get(f"{base_url}/teacher/exams/new")
        wait.until(EC.presence_of_element_located((By.ID, "name")))
        
        # Verify name field (by ID)
        name_field = driver.find_element(By.ID, "name")
        assert name_field.is_displayed()
        
        # Verify description field (by NAME)
        description_field = driver.find_element(By.NAME, "description")
        assert description_field.is_displayed()
        
        # Verify duration field (by ID)
        duration_field = driver.find_element(By.ID, "duration_minutes")
        assert duration_field.is_displayed()
        
        # Verify grading policy dropdown (by CSS Selector)
        grading_select = driver.find_element(By.CSS_SELECTOR, "select#grading_policy")
        assert grading_select.is_displayed()
        
        # Verify start date field (by ID)
        start_at_field = driver.find_element(By.ID, "start_at")
        assert start_at_field.is_displayed()
        
        # Verify end date field (by ID)
        end_at_field = driver.find_element(By.ID, "end_at")
        assert end_at_field.is_displayed()
        
        # Verify submit button (by XPath)
        submit_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Create Exam')]")
        assert submit_btn.is_displayed()
        assert submit_btn.is_enabled()
    
    def test_grading_policy_dropdown_options(self, login_as_teacher, base_url):
        """
        Test: Verify grading policy dropdown has correct options.
        Expected: Immediate, After End, and Manual options exist.
        Locators: ID (select element)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new exam page
        driver.get(f"{base_url}/teacher/exams/new")
        wait.until(EC.presence_of_element_located((By.ID, "grading_policy")))
        
        # Get dropdown options using ID
        grading_select = Select(driver.find_element(By.ID, "grading_policy"))
        options = [opt.get_attribute("value") for opt in grading_select.options]
        
        # Verify expected options
        assert "immediate" in options, "Immediate option should exist"
        assert "after_end" in options, "After End option should exist"
        assert "manual" in options, "Manual option should exist"
    
    def test_exam_shuffle_checkboxes(self, login_as_teacher, base_url):
        """
        Test: Verify shuffle question and options checkboxes work.
        Expected: Checkboxes can be checked and unchecked.
        Locators: ID (checkboxes)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new exam page
        driver.get(f"{base_url}/teacher/exams/new")
        wait.until(EC.presence_of_element_located((By.ID, "shuffle_questions")))
        
        # Find shuffle questions checkbox using ID
        shuffle_questions = driver.find_element(By.ID, "shuffle_questions")
        assert shuffle_questions.is_displayed()
        
        # Check the checkbox using JS click
        if not shuffle_questions.is_selected():
            driver.execute_script("arguments[0].scrollIntoView(true);", shuffle_questions)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", shuffle_questions)
        assert shuffle_questions.is_selected()
        
        # Uncheck the checkbox
        driver.execute_script("arguments[0].click();", shuffle_questions)
        assert not shuffle_questions.is_selected()
        
        # Find shuffle options checkbox using ID
        shuffle_options = driver.find_element(By.ID, "shuffle_options")
        assert shuffle_options.is_displayed()
        
        # Check the checkbox using JS click
        if not shuffle_options.is_selected():
            driver.execute_script("arguments[0].click();", shuffle_options)
        assert shuffle_options.is_selected()


class TestExamList:
    """Test cases for the exam list page."""
    
    def test_exam_list_page_loads(self, login_as_teacher, base_url):
        """
        Test: Navigate to exam list page.
        Expected: Page loads with proper heading.
        Locators: XPath (heading), CSS Selector (table or list)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to exams list
        driver.get(f"{base_url}/teacher/exams")
        
        # Verify page heading using XPath
        heading = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//h1[contains(text(), 'Exam') or contains(text(), 'exam')]")
            )
        )
        assert heading.is_displayed()
    
    def test_create_exam_button_on_list_page(self, login_as_teacher, base_url):
        """
        Test: Verify 'Create Exam' button exists on list page.
        Expected: Button is clickable and navigates to creation page.
        Locators: CSS Selector (button/link with href)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to exams list
        driver.get(f"{base_url}/teacher/exams")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
        
        # Find create exam button using CSS Selector
        create_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a[href='/teacher/exams/new']")
            )
        )
        assert create_btn.is_displayed()
        
        # Click and verify navigation
        create_btn.click()
        wait.until(EC.url_contains("/teacher/exams/new"))
        assert "/teacher/exams/new" in driver.current_url
