package com.paramtech.locators;

import org.openqa.selenium.By;

public final class TeacherDashboardLocators {
    private TeacherDashboardLocators() {}

    public static final By PAGE_H1 = By.xpath("//h1[contains(text(),'Teacher Dashboard')]");
    public static final By QUESTIONS_LINK = By.xpath("//a[contains(@href, '/teacher/questions')]");
    public static final By EXAMS_LINK = By.xpath("//a[contains(@href, '/teacher/exams')]");
    public static final By ASSIGNMENTS_LINK = By.xpath("//a[contains(@href, '/teacher/assignments')]");
}
