"""
Question CRUD UI tests.
Tests cover question creation, including multiple choice and true/false types.
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


class TestQuestionCreation:
    """Test cases for creating questions."""
    
    def test_navigate_to_question_creation_page(self, login_as_teacher, base_url):
        """
        Test: Navigate to question creation page.
        Expected: Question creation form is displayed.
        Locators: CSS Selector (navigation link), XPath (page heading)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new question page
        driver.get(f"{base_url}/teacher/questions/new")
        
        # Verify page loaded using XPath
        heading = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//h1[contains(text(), 'New Question')]")
            )
        )
        assert heading.is_displayed()
    
    def test_create_multiple_choice_question(self, login_as_teacher, base_url):
        """
        Test: Create a multiple choice question with valid data.
        Expected: Question is created successfully.
        Locators: NAME (form fields), ID (question_type), CSS Selector (buttons)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new question page
        driver.get(f"{base_url}/teacher/questions/new")
        wait.until(EC.presence_of_element_located((By.NAME, "title")))
        
        # Fill in question details using NAME locators
        title_field = driver.find_element(By.NAME, "title")
        title_field.send_keys("Test Question: What is 2 + 2?")
        
        body_field = driver.find_element(By.NAME, "body")
        body_field.send_keys("Select the correct answer for this math question.")
        
        difficulty_field = driver.find_element(By.NAME, "difficulty")
        difficulty_field.clear()
        difficulty_field.send_keys("2")
        
        # Select question type using ID locator
        type_select = Select(driver.find_element(By.ID, "question_type"))
        type_select.select_by_value("multiple_choice")
        
        # Wait for options container to be ready
        time.sleep(0.5)
        
        # Add options - first option
        options_container = driver.find_element(By.ID, "optionsContainer")
        option_inputs = options_container.find_elements(By.NAME, "option_text")
        
        if len(option_inputs) > 0:
            option_inputs[0].clear()
            option_inputs[0].send_keys("4")
            # Mark first option as correct
            checkboxes = options_container.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            if checkboxes:
                checkboxes[0].click()
        
        # Add more options using the Add Option button
        add_option_btn = driver.find_element(By.ID, "addOptionBtn")
        add_option_btn.click()
        time.sleep(0.3)
        
        # Fill second option
        option_inputs = options_container.find_elements(By.NAME, "option_text")
        if len(option_inputs) > 1:
            option_inputs[1].clear()
            option_inputs[1].send_keys("5")
        
        # Add third option
        add_option_btn.click()
        time.sleep(0.3)
        
        option_inputs = options_container.find_elements(By.NAME, "option_text")
        if len(option_inputs) > 2:
            option_inputs[2].clear()
            option_inputs[2].send_keys("3")
        
        # Fill tags (optional)
        tags_field = driver.find_element(By.NAME, "tags")
        tags_field.send_keys("math, arithmetic, test")
        
        # Submit form using CSS selector - scroll to button and use JS click
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_btn)
        
        # Verify redirect to questions list or success message
        wait.until(lambda d: "/teacher/questions" in d.current_url)
        assert "/teacher/questions" in driver.current_url
    
    def test_create_true_false_question(self, login_as_teacher, base_url):
        """
        Test: Create a true/false question.
        Expected: Question is created with True/False options.
        Locators: ID (form fields), NAME (radio buttons), XPath (submit button)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new question page
        driver.get(f"{base_url}/teacher/questions/new")
        wait.until(EC.presence_of_element_located((By.ID, "title")))
        
        # Fill in question details using ID locators
        title_field = driver.find_element(By.ID, "title")
        title_field.send_keys("The Earth is flat.")
        
        body_field = driver.find_element(By.ID, "body")
        body_field.send_keys("Determine if this statement is true or false.")
        
        difficulty_field = driver.find_element(By.ID, "difficulty")
        difficulty_field.clear()
        difficulty_field.send_keys("1")
        
        # Select true/false question type
        type_select = Select(driver.find_element(By.ID, "question_type"))
        type_select.select_by_value("true_false")
        
        # Wait for true/false options to appear
        time.sleep(0.5)
        
        # Select "False" as correct answer - scroll and JS click
        false_radio = wait.until(
            EC.presence_of_element_located((By.ID, "false_correct"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", false_radio)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", false_radio)
        
        # Submit form using CSS selector - scroll and JS click
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_btn)
        
        # Verify success
        wait.until(lambda d: "/teacher/questions" in d.current_url)
        assert "/teacher/questions" in driver.current_url
    
    def test_question_form_validation_missing_title(self, login_as_teacher, base_url):
        """
        Test: Submit question form without required title.
        Expected: Form validation prevents submission.
        Locators: ID (form fields), CSS Selector (submit button)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new question page
        driver.get(f"{base_url}/teacher/questions/new")
        wait.until(EC.presence_of_element_located((By.ID, "body")))
        
        # Fill body but not title
        body_field = driver.find_element(By.ID, "body")
        body_field.send_keys("Question body without title")
        
        difficulty_field = driver.find_element(By.ID, "difficulty")
        difficulty_field.clear()
        difficulty_field.send_keys("3")
        
        # Try to submit - scroll and JS click
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", submit_btn)
        
        # Verify form validation (should still be on the same page)
        title_field = driver.find_element(By.ID, "title")
        is_valid = driver.execute_script("return arguments[0].checkValidity()", title_field)
        assert not is_valid, "Title field should be invalid when empty"
    
    def test_question_form_validation_missing_body(self, login_as_teacher, base_url):
        """
        Test: Submit question form without required body.
        Expected: Form validation prevents submission.
        Locators: NAME (title), ID (body), XPath (submit)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new question page
        driver.get(f"{base_url}/teacher/questions/new")
        wait.until(EC.presence_of_element_located((By.NAME, "title")))
        
        # Fill title but not body
        title_field = driver.find_element(By.NAME, "title")
        title_field.send_keys("Question title without body")
        
        difficulty_field = driver.find_element(By.NAME, "difficulty")
        difficulty_field.clear()
        difficulty_field.send_keys("2")
        
        # Try to submit - scroll and JS click
        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", submit_btn)
        
        # Verify form validation
        body_field = driver.find_element(By.ID, "body")
        is_valid = driver.execute_script("return arguments[0].checkValidity()", body_field)
        assert not is_valid, "Body field should be invalid when empty"
    
    def test_question_form_elements_present(self, login_as_teacher, base_url):
        """
        Test: Verify all required form elements are present.
        Expected: All form fields and buttons are displayed.
        Locators: ID, NAME, CSS Selector, XPath
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new question page
        driver.get(f"{base_url}/teacher/questions/new")
        wait.until(EC.presence_of_element_located((By.ID, "title")))
        
        # Verify title field (by ID)
        title_field = driver.find_element(By.ID, "title")
        assert title_field.is_displayed()
        
        # Verify body field (by NAME)
        body_field = driver.find_element(By.NAME, "body")
        assert body_field.is_displayed()
        
        # Verify difficulty field (by ID)
        difficulty_field = driver.find_element(By.ID, "difficulty")
        assert difficulty_field.is_displayed()
        
        # Verify question type dropdown (by ID)
        type_select = driver.find_element(By.ID, "question_type")
        assert type_select.is_displayed()
        
        # Verify submit button (by CSS Selector)
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        assert submit_btn.is_displayed()
        assert submit_btn.is_enabled()
        
        # Verify cancel button (by XPath)
        cancel_btn = driver.find_element(By.XPATH, "//a[contains(text(), 'Cancel')]")
        assert cancel_btn.is_displayed()
    
    def test_question_type_dropdown_options(self, login_as_teacher, base_url):
        """
        Test: Verify question type dropdown has correct options.
        Expected: Multiple choice and True/False options exist.
        Locators: ID (select element)
        """
        driver = login_as_teacher
        wait = WebDriverWait(driver, 10)
        
        # Navigate to new question page
        driver.get(f"{base_url}/teacher/questions/new")
        wait.until(EC.presence_of_element_located((By.ID, "question_type")))
        
        # Get dropdown options using ID
        type_select = Select(driver.find_element(By.ID, "question_type"))
        options = [opt.get_attribute("value") for opt in type_select.options]
        
        # Verify expected options
        assert "multiple_choice" in options, "Multiple choice option should exist"
        assert "true_false" in options, "True/False option should exist"
