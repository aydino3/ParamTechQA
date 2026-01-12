package com.paramtech.locators;

import org.openqa.selenium.By;

public final class TeacherQuestionsLocators {

    public static final By TITLE = By.xpath("//input[@id='title']");
    public static final By BODY  = By.xpath("//textarea[@id='body']");
    public static final By DIFFICULTY_INPUT = By.xpath("//input[@id='difficulty']");
    public static final By DIFFICULTY_SELECT = By.xpath("//select[@id='difficulty']");
    public static final By QUESTION_TYPE = By.xpath("//select[@id='question_type']");

    public static final By OPTION_TEXT_INPUTS = By.xpath("//div[@id='optionsContainer']//input[@name='option_text']");
    public static final By OPTION_CORRECT_CHECKBOXES = By.xpath("//div[@id='optionsContainer']//input[@type='checkbox']");
    public static final By ADD_OPTION_BUTTON = By.xpath("//button[@id='addOptionBtn']");

    public static final By TRUE_CORRECT  = By.xpath("//input[@id='true_correct']");
    public static final By FALSE_CORRECT = By.xpath("//input[@id='false_correct']");

    public static final By TAGS = By.xpath("//input[@name='tags']");
    public static final By SUBMIT = By.xpath("//button[@type='submit']");
}

