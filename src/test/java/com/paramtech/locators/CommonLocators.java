package com.paramtech.locators;

import org.openqa.selenium.By;

public final class CommonLocators {

    public static final By LOGOUT_LINK = By.xpath("//a[contains(@href, '/logout')]");
    public static final By ALERT = By.xpath("//div[@role='alert']");
    public static final By NAV_TEACHER_QUESTIONS = By.xpath("//a[@class='nav-link' and @href='/teacher/questions' and normalize-space(.)='❓ Questions']");
    public static final By NAV_TEACHER_EXAMS = By.xpath("//a[@href='/teacher/exams']");
}
