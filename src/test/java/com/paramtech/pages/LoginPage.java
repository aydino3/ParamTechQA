package com.paramtech.pages;

import com.paramtech.locators.LoginLocators;
import com.paramtech.utils.ConfigReader;
import org.openqa.selenium.WebDriver;

public class LoginPage extends BasePage {

    public LoginPage(WebDriver driver) {
        super(driver);
    }

    public void open() {
        driver.get(ConfigReader.getProperty("baseUrl") + "/login");
    }

    public void login(String username, String password) {
        sendKeys(LoginLocators.USERNAME, username);
        sendKeys(LoginLocators.PASSWORD, password);
        click(LoginLocators.SUBMIT);
    }

    public void submitEmpty() {
        click(LoginLocators.SUBMIT);
    }

}
