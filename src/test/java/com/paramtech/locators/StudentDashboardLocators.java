package com.paramtech.locators;

import org.openqa.selenium.By;

public final class StudentDashboardLocators {
    private StudentDashboardLocators() {}

    public static final By PAGE_H1 = By.xpath("//h1[contains(text(),'Student Dashboard')]");
    public static final By ASSIGNMENTS_TABLE = By.xpath("//table");
    public static final By START_BUTTON = By.xpath("//a[contains(text(),'Start')]");
}
