package com.paramtech.pages;

import com.paramtech.driver.DriverFactory;
import com.paramtech.utils.ConfigReader;
import com.paramtech.utils.WaitUtils;
import org.openqa.selenium.*;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.interactions.MoveTargetOutOfBoundsException;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;
import java.util.List;

public abstract class BasePage {

    protected final WebDriver driver;

    // Ham selenium wait (gerekirse)
    protected final WebDriverWait webWait;

    // Page’lerde kullanacağın asıl helper
    protected final WaitUtils wait;

    /**
     * Primary constructor used by Page Objects.
     */
    protected BasePage(WebDriver driver) {
        this.driver = driver;
        int timeoutSeconds = Integer.parseInt(ConfigReader.get("timeoutSeconds", "20"));
        this.webWait = new WebDriverWait(this.driver, Duration.ofSeconds(timeoutSeconds));
        this.wait = new WaitUtils(this.webWait);
    }

    /**
     * Backward-compatible constructor (uses DriverFactory).
     */
    protected BasePage() {
        this(DriverFactory.getDriver());
    }

    // -------------------- Common actions --------------------

    protected void click(By locator) { wait.click(locator); }

    /** Compatibility alias used by existing page objects. */
    protected void sendKeys(By locator, String text) { wait.type(locator, text); }

    /** Preferred name. */
    protected void type(By locator, String text) { wait.type(locator, text); }

    protected void pressEnter(By locator) { wait.pressEnter(locator); }

    protected String getText(By locator) { return wait.visible(locator).getText(); }

    protected boolean isDisplayed(By locator) {
        try { return driver.findElement(locator).isDisplayed(); }
        catch (NoSuchElementException e) { return false; }
    }

    protected int count(By locator) {
        List<WebElement> els = driver.findElements(locator);
        return els.size();
    }

    // -------------------- Robust click helpers --------------------

    /**
     * Scroll + normal click, intercept olursa JS click fallback.
     * (popup / cookie / overlay / slider yüzünden tıklanamama için)
     */
    protected void safeClick(By locator) {
        WebElement el = wait.clickable(locator);
        try {
            ((JavascriptExecutor) driver).executeScript(
                    "arguments[0].scrollIntoView({block:'center', inline:'nearest'});", el
            );
            el.click();
        } catch (ElementClickInterceptedException | MoveTargetOutOfBoundsException e) {
            ((JavascriptExecutor) driver).executeScript("arguments[0].click();", el);
        }
    }

    public void jsClick(By by) {
        WebElement el = webWait.until(ExpectedConditions.presenceOfElementLocated(by));
        ((JavascriptExecutor) driver).executeScript(
                "arguments[0].scrollIntoView({block:'center', inline:'center'});", el
        );
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", el);
    }

    protected void scrollIntoView(By locator) {
        WebElement el = wait.visible(locator);
        ((JavascriptExecutor) driver).executeScript(
                "arguments[0].scrollIntoView({block:'center'});", el);
    }

    protected void hover(By locator) {
        WebElement el = wait.visible(locator);
        new Actions(driver).moveToElement(el).perform();
    }

    public String getCurrentUrl() { return driver.getCurrentUrl(); }
}
