package com.paramtech.locators;

import org.openqa.selenium.By;

public final class TeacherQuestionsLocators {
    private TeacherQuestionsLocators() {}

    // List page
    public static final By H1_QUESTIONS = By.xpath("//h1[contains(text(),'Questions')]");
    public static final By NEW_QUESTION_LINK = By.xpath("//a[@href='/teacher/questions/new']");

    // New Question form (aligned with exam_systemv2 UI tests)
    public static final By TITLE = By.xpath("//input[@id='title']");
    public static final By BODY  = By.xpath("//textarea[@id='body']");
    public static final By DIFFICULTY_INPUT = By.xpath("//input[@id='difficulty']");
    public static final By DIFFICULTY_SELECT = By.xpath("//select[@id='difficulty']");
    public static final By QUESTION_TYPE = By.xpath("//select[@id='question_type']");

    public static final By OPTIONS_CONTAINER = By.xpath("//div[@id='optionsContainer']");
    public static final By OPTION_TEXT_INPUTS = By.xpath("//div[@id='optionsContainer']//input[@name='option_text']");
    public static final By OPTION_CORRECT_CHECKBOXES = By.xpath("//div[@id='optionsContainer']//input[@type='checkbox']");
    public static final By ADD_OPTION_BUTTON = By.xpath("//button[@id='addOptionBtn']");

    public static final By TRUE_CORRECT  = By.xpath("//input[@id='true_correct']");
    public static final By FALSE_CORRECT = By.xpath("//input[@id='false_correct']");

    public static final By TAGS = By.xpath("//input[@name='tags']");
    public static final By SUBMIT = By.xpath("//button[@type='submit']");

    // Backward-compatible aliases used in older page code (keep to avoid compile errors if referenced)
    public static final By QUESTION_TEXT = TITLE;
    public static final By OPTION_A = By.xpath("//*[@id='optionsContainer']/div[1]/div/input[2]");
    public static final By OPTION_B = By.xpath("//*[@id='optionsContainer']/div[2]/div/input[2]");
    public static final By OPTION_C = By.xpath("//*[@id='optionsContainer']/div[3]/div/input[2]");
    public static final By OPTION_D = By.xpath("//*[@id='optionsContainer']/div[4]/div/input[2]");
    public static final By OPTION_E = By.xpath("//*[@id='optionsContainer']/div[5]/div/input[2]");

    public static final By CORRECT_ANSWER = By.xpath("//input[@type='checkbox' and @checked]");
    // Soru metni (textarea / input)

    // Tag input (opsiyonel)
    public static final By TAG_INPUT = By.xpath("//input[@name='tag' or @id='tag' or @name='tags' or @id='tags']");

    // True/False seçimleri (radio / button)
    public static final By TF_TRUE  = By.xpath("//input[@type='radio' and (@value='true' or @value='True')] | //button[normalize-space(.)='True']");
    public static final By TF_FALSE = By.xpath("//input[@type='radio' and (@value='false' or @value='False')] | //button[normalize-space(.)='False']");

    // Kaydet / Create butonu
    public static final By SAVE_BUTTON = By.xpath("//button[@type='submit' and normalize-space(.)='✅ Create Question']");

    public static final By CORRECT_A = By.xpath("//*[@id='optionsContainer']/div[1]/div/input[1]");
    public static final By CORRECT_B = By.xpath("//*[@id='optionsContainer']/div[2]/div/input[1]");
    public static final By CORRECT_C = By.xpath("//*[@id='optionsContainer']/div[3]/div/input[1]");
    public static final By CORRECT_D = By.xpath("//*[@id='optionsContainer']/div[4]/div/input[1]");
    public static final By CORRECT_E = By.xpath("//*[@id='optionsContainer']/div[5]/div/input[1]");

    private static final By SUCCESS_ALERT_CREATED = By.xpath("//div[@class='alert alert-success alert-dismissible fade show']");
    // Success alert (bazı sayfalarda var, bazı sayfalarda yok)
    public static final By SUCCESS_ALERT = By.cssSelector("div.alert.alert-success");

    // New Question form (formda olduğumuzu anlamak için)
    public static final By QUESTION_FORM = By.cssSelector("form");
    // List table + pagination + flash
    public static final By QUESTIONS_TABLE_ROWS =
            By.xpath("//table//tbody//tr");

    public static final By PAGINATION_NEXT =
            By.xpath("//a[contains(normalize-space(.),'Next') or contains(normalize-space(.),'›') or contains(normalize-space(.),'»')]"
                    + "[not(contains(@class,'disabled')) and not(@aria-disabled='true')]");

    public static final By FLASH_SUCCESS =
            By.xpath("//*[contains(@class,'alert') and contains(@class,'success')]");



}

