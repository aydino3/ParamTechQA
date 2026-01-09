package com.paramtech.locators;

import org.openqa.selenium.By;

public final class DashboardLocators {
    private DashboardLocators() {}

    public static final By ADMIN_H1 = By.xpath("//h1[contains(text(),'Admin Dashboard')]");
    public static final By TEACHER_H1 = By.xpath("//h1[contains(text(),'Teacher Dashboard')]");
    public static final By STUDENT_H1 = By.xpath("//h1[contains(text(),'Student Dashboard')]");

    // Teacher dashboard cards/links
    public static final By TEACHER_LINK_QUESTIONS = By.xpath("//a[contains(@href, '/teacher/questions')]");
    public static final By TEACHER_LINK_EXAMS = By.xpath("//a[contains(@href, '/teacher/exams')]");

    // Student dashboard table and start buttons
    public static final By STUDENT_ASSIGNMENTS_TABLE = By.xpath("//table");
    public static final By STUDENT_START_BUTTONS = By.xpath("//a[contains(@href, '/student/attempts/start') or contains(., 'Start')]");
}
