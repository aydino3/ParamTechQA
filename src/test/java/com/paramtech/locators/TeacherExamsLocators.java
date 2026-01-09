package com.paramtech.locators;

import org.openqa.selenium.By;

public final class TeacherExamsLocators {
    private TeacherExamsLocators() {}

    public static final By H1_EXAMS = By.xpath("//h1[contains(text(),'Exams')]");
    public static final By NEW_EXAM_LINK = By.xpath("//a[contains(@href, '/teacher/exams/new')]");

    // New Exam form
    public static final By TITLE = By.xpath("//input[@name='title']");
    public static final By DESCRIPTION = By.xpath("//textarea[@name='description']");
    public static final By DURATION_MINUTES = By.xpath("//input[@name='duration_minutes']");
    public static final By MAX_ATTEMPTS = By.xpath("//input[@name='max_attempts']");
    public static final By GRADING_POLICY = By.xpath("//select[@name='grading_policy']");
    public static final By SUBMIT = By.xpath("//button[@type='submit' or contains(., 'Create') or contains(., 'Save')]");
}
