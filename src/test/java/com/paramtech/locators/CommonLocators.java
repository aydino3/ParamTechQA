package com.paramtech.locators;

import org.openqa.selenium.By;

public final class CommonLocators {
    private CommonLocators() {}

    // Many templates render logout as a link, some as a form button. We'll try both.
    public static final By LOGOUT_LINK = By.xpath("//a[contains(@href, '/logout')]");
    public static final By LOGOUT_FORM = By.xpath("//form[contains(@action,'/logout')]//button");

    public static final By LOGOUT_BUTTON_FALLBACK = By.xpath("//button[@type='submit' and (normalize-space()='Logout' or normalize-space()='Log out')]");
    public static final By ALERT = By.xpath("//div[@role='alert']");
    public static final By NAV_DASHBOARD = By.xpath("//a[contains(@href, '/dashboard')]");


    // Teacher nav
    public static final By NAV_TEACHER_DASH = By.xpath("//a[@href='/teacher/dashboard']");
    public static final By NAV_TEACHER_QUESTIONS = By.xpath("//a[@class='nav-link' and @href='/teacher/questions' and normalize-space(.)='❓ Questions']");
    public static final By NAV_TEACHER_EXAMS = By.xpath("//a[@href='/teacher/exams']");

    // Student nav
    public static final By NAV_STUDENT_DASH = By.xpath("//a[@href='/student/dashboard']");

    public static final By PAGE_ALERT = By.xpath("//div[contains(@class, 'alert')]");
    public static final By ANY_H1 = By.xpath("//h1");
}
