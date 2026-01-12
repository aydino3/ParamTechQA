package com.paramtech.locators;

import org.openqa.selenium.By;

public final class DashboardLocators {

    public static final By ADMIN_H1 = By.xpath("//h1[contains(text(),'Admin Dashboard')]");
    public static final By TEACHER_H1 = By.xpath("//h1[contains(text(),'Teacher Dashboard')]");
    public static final By STUDENT_H1 = By.xpath("//h1[contains(text(),'Student Dashboard')]");
    public static final By STUDENT_ASSIGNMENTS_TABLE = By.xpath("//div[@class='card-body']");
}
