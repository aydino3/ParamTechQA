package com.paramtech.pages;

import com.paramtech.locators.DashboardLocators;
import com.paramtech.utils.ConfigReader;
import org.openqa.selenium.WebDriver;

public class StudentDashboardPage extends BasePage {
    public StudentDashboardPage(WebDriver driver) {
        super(driver);
    }

    public void open() {
        driver.get(ConfigReader.getProperty("baseUrl") + "/student/dashboard");
    }

    public boolean isAt() {
        return isDisplayed(DashboardLocators.STUDENT_H1);
    }
}
