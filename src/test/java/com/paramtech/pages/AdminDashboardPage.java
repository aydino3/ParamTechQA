package com.paramtech.pages;

import com.paramtech.locators.DashboardLocators;
import com.paramtech.utils.ConfigReader;
import org.openqa.selenium.WebDriver;

public class AdminDashboardPage extends BasePage {
    public AdminDashboardPage(WebDriver driver) {
        super(driver);
    }

    public void open() {
        driver.get(ConfigReader.getProperty("baseUrl") + "/admin/dashboard");
    }

    public boolean isAt() {
        return isDisplayed(DashboardLocators.ADMIN_H1);
    }
}
