package com.paramtech.locators;

import org.openqa.selenium.By;

public final class TeacherExamsLocators {

    public static final By H1_EXAMS = By.xpath("//h1[contains(text(),'Exams')]");
    public static final By NAME = By.xpath("//input[@id='name']");
    public static final By DESCRIPTION = By.xpath("//textarea[@id='description']");
    public static final By DURATION_MINUTES = By.xpath("//input[@id='duration_minutes']");

    public static final By MAX_ATTEMPTS = By.xpath("//input[@id='max_attempts']");
    public static final By GRADING_POLICY = By.xpath("//select[@id='grading_policy']");
    public static final By SUBMIT = By.xpath("//button[@type='submit']");
}
