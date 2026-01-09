package com.paramtech.pages;

import com.paramtech.driver.DriverFactory;
import com.paramtech.utils.ConfigReader;
import com.paramtech.utils.WaitUtils;
import org.openqa.selenium.*;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;
import java.util.List;

public abstract class BasePage {

    protected final WebDriver driver;
    protected final WebDriverWait wait;
    protected final WaitUtils wu;

    protected BasePage() {
        this.driver = DriverFactory.getDriver();
        int timeoutSeconds = Integer.parseInt(ConfigReader.get("timeoutSeconds", "20"));
        this.wait = new WebDriverWait(this.driver, Duration.ofSeconds(timeoutSeconds));
        this.wu = new WaitUtils(this.wait);
    }

    protected void click(By locator) { wu.click(locator); }
    protected void type(By locator, String text) { wu.type(locator, text); }
    protected void pressEnter(By locator) { wu.pressEnter(locator); }

    protected boolean isDisplayed(By locator) {
        try { return driver.findElement(locator).isDisplayed(); }
        catch (NoSuchElementException e) { return false; }
    }

    protected int count(By locator) {
        List<WebElement> els = driver.findElements(locator);
        return els.size();
    }

    public void jsClick(By by) {
        WebElement el = new WebDriverWait(driver, Duration.ofSeconds(20))
                .until(ExpectedConditions.presenceOfElementLocated(by));

        ((JavascriptExecutor) driver).executeScript(
                "arguments[0].scrollIntoView({block:'center', inline:'center'});", el
        );
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", el);
    }



    protected void scrollIntoView(By locator) {
        WebElement el = wu.visible(locator);
        ((JavascriptExecutor) driver).executeScript(
                "arguments[0].scrollIntoView({block:'center'});", el);
    }

    protected void hover(By locator) {
        WebElement el = wu.visible(locator);
        new Actions(driver).moveToElement(el).perform();
    }
    public String getCurrentUrl() {
        return driver.getCurrentUrl();
    }

}
