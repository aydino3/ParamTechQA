package com.paramtech.pages;

import com.paramtech.locators.DashboardLocators;
import com.paramtech.utils.ConfigReader;
import org.openqa.selenium.WebDriver;

public class TeacherDashboardPage extends BasePage {
    public TeacherDashboardPage(WebDriver driver) {
        super(driver);
    }

    public void open() {
        driver.get(ConfigReader.getProperty("baseUrl") + "/teacher/dashboard");
    }

    public boolean isAt() {
        return isDisplayed(DashboardLocators.TEACHER_H1);
    }
}
