package com.paramtech.locators;

import org.openqa.selenium.By;

public final class TeacherQuestionsLocators {
    private TeacherQuestionsLocators() {}

    public static final By H1_QUESTIONS = By.xpath("//h1[contains(text(),'Questions')]");
    public static final By NEW_QUESTION_LINK = By.xpath("//a[contains(@href, '/teacher/questions/new')]");

    // Form
    public static final By FIELD_QUESTION_TEXT = By.xpath("//textarea[@name='question_text']");
    public static final By SELECT_QUESTION_TYPE = By.xpath("//select[@name='question_type']");
    public static final By FIELD_OPTION_A = By.xpath("//input[@name='option_a']");
    public static final By FIELD_OPTION_B = By.xpath("//input[@name='option_b']");
    public static final By FIELD_OPTION_C = By.xpath("//input[@name='option_c']");
    public static final By FIELD_OPTION_D = By.xpath("//input[@name='option_d']");
    public static final By SELECT_CORRECT_ANSWER = By.xpath("//select[@name='correct_answer']");
    public static final By FIELD_TAGS = By.xpath("//input[@name='tags']");
    public static final By BTN_CREATE = By.xpath("//button[contains(text(),'Create')]");

    public static By questionRowContains(String text) {
        return By.xpath("//td[contains(text(),\"" + escapeXpath(text) + "\")]" );
    }

    // Minimal escaping for double quotes in xpath literal.
    private static String escapeXpath(String s) {
        return s.replace("\"", "'");
    }
}
