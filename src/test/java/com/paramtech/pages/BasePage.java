package com.paramtech.pages;

import com.paramtech.driver.DriverFactory;
import com.paramtech.utils.ConfigReader;
import com.paramtech.utils.WaitUtils;
import org.openqa.selenium.*;
import org.openqa.selenium.support.ui.WebDriverWait;
import java.time.Duration;
import java.util.List;

public abstract class BasePage {

    protected final WebDriver driver;

    protected final WebDriverWait webWait;

    protected final WaitUtils wait;


    protected BasePage(WebDriver driver) {
        this.driver = driver;
        int timeoutSeconds = Integer.parseInt(ConfigReader.get("timeoutSeconds", "20"));
        this.webWait = new WebDriverWait(this.driver, Duration.ofSeconds(timeoutSeconds));
        this.wait = new WaitUtils(this.webWait);
    }
    protected void click(By locator) {
        wait.click(locator);
    }

    protected void sendKeys(By locator, String text) {
        wait.type(locator, text);
    }
    protected boolean isDisplayed(By locator) {
        try {
            return driver.findElement(locator).isDisplayed();
        } catch (NoSuchElementException e) {
            return false;
        }
    }

    protected int count(By locator) {
        List<WebElement> els = driver.findElements(locator);
        return els.size();
    }
}
