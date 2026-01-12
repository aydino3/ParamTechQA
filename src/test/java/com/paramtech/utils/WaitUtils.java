package com.paramtech.utils;

import org.openqa.selenium.*;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

public class WaitUtils {

    private final WebDriverWait wait;

    public WaitUtils(WebDriverWait wait) {
        this.wait = wait;
    }

    public WebElement visible(By locator) {
        return wait.until(ExpectedConditions.visibilityOfElementLocated(locator));
    }

    public WebElement clickable(By locator) {
        return wait.until(ExpectedConditions.elementToBeClickable(locator));
    }

    public void click(By locator) {
        WebDriver driver = waitDriver();

        WebElement el = wait.until(ExpectedConditions.presenceOfElementLocated(locator));
        scrollIntoViewCenter(driver, el);

        sleep(150);

        el = clickable(locator);

        try {
            el.click();
            return;
        } catch (ElementNotInteractableException ignored) {}

        try {
            new Actions(driver).moveToElement(el).pause(Duration.ofMillis(150)).click().perform();
            return;
        } catch (WebDriverException ignored) {}

        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", el);
    }

    public void type(By locator, String text) {
        WebElement el = visible(locator);
        el.clear();
        el.sendKeys(text);
    }

    // -------------------- Static helpers (compatibility) --------------------
    public static WebElement waitForVisibility(WebDriver driver, By locator) {
        int timeout = Integer.parseInt(ConfigReader.get("timeoutSeconds", "20"));
        WebDriverWait w = new WebDriverWait(driver, Duration.ofSeconds(timeout));
        return w.until(ExpectedConditions.visibilityOfElementLocated(locator));
    }

    public static void waitForPageToLoad(WebDriver driver, long timeoutSeconds) {
        new WebDriverWait(driver, Duration.ofSeconds(timeoutSeconds))
                .until(d -> ((JavascriptExecutor) d)
                        .executeScript("return document.readyState")
                        .equals("complete"));
    }

    // -------------------- internal helpers --------------------
    private WebDriver waitDriver() {
        return com.paramtech.driver.DriverFactory.getDriver();
    }

    private void scrollIntoViewCenter(WebDriver driver, WebElement el) {
        try {
            ((JavascriptExecutor) driver).executeScript(
                    "arguments[0].scrollIntoView({block:'center', inline:'center'});", el
            );
        } catch (JavascriptException ignored) {}
    }

    private void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException ignored) {}
    }
}
