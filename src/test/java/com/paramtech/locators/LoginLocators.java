package com.paramtech.locators;

import org.openqa.selenium.By;

public final class LoginLocators {
    private LoginLocators() {}

    public static final By USERNAME = By.xpath("//input[@id='username']");
    public static final By PASSWORD = By.xpath("//input[@id='password']");
    public static final By SUBMIT   = By.xpath("//button[@type='submit']");

    public static final By ALERT    = By.xpath("//div[@role='alert'] | //div[@class='alert alert-danger'] | //div[@class='alert alert-success'] | //div[@class='alert']");
public static final By ADMIN_DASH_H1   = By.xpath("//h1[contains(text(),'Admin Dashboard')]");
    public static final By TEACHER_DASH_H1 = By.xpath("//h1[contains(text(),'Teacher Dashboard')]");
    public static final By STUDENT_DASH_H1 = By.xpath("//h1[contains(text(),'Student Dashboard')]");
}
