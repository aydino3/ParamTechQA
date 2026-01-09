package com.paramtech.locators;

import org.openqa.selenium.By;

public final class AdminDashboardLocators {
    private AdminDashboardLocators() {}

    public static final By PAGE_H1 = By.xpath("//h1[contains(text(),'Admin Dashboard')]");
    public static final By USERS_LINK = By.xpath("//a[contains(@href, '/admin/users')]");
    public static final By EXAMS_LINK = By.xpath("//a[contains(@href, '/admin/exams')]");
    public static final By LOGS_LINK = By.xpath("//a[contains(@href, '/admin/audit')]");
}
